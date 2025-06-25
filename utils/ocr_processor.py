import pytesseract
import cv2
import re
from datetime import datetime
import logging

class OCRProcessor:
    def __init__(self):
        # Configure Tesseract for better OCR results
        self.config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz./-: '
    
    def extract_aadhaar_data(self, image_path):
        """Extract name, DOB, and other data from Aadhaar card"""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not read image")
            
            # Extract text using OCR
            text = pytesseract.image_to_string(image, config=self.config)
            logging.info(f"Extracted text: {text}")
            
            # Initialize result dictionary
            extracted_data = {
                'name': None,
                'dob': None,
                'age': None,
                'gender': None,
                'aadhaar_number': None
            }
            
            # Extract DOB (Date of Birth)
            dob_patterns = [
                r'DOB[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})',
                r'Birth[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})',
                r'(\d{2}[/-]\d{2}[/-]\d{4})',
                r'(\d{2}\s+\d{2}\s+\d{4})'
            ]
            
            for pattern in dob_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    dob_str = match.group(1)
                    extracted_data['dob'] = self.standardize_date(dob_str)
                    extracted_data['age'] = self.calculate_age(extracted_data['dob'])
                    break
            
            # Extract name (usually appears after specific keywords)
            name_patterns = [
                r'Name[:\s]*([A-Za-z\s]+)',
                r'नाम[:\s]*([A-Za-z\s]+)',
                r'^([A-Z][A-Za-z\s]+)$'  # All caps name
            ]
            
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if len(line) > 3 and line.replace(' ', '').isalpha():
                    # Check if it looks like a name
                    words = line.split()
                    if 2 <= len(words) <= 4 and all(word.isalpha() for word in words):
                        extracted_data['name'] = line.title()
                        break
            
            # Extract gender
            if re.search(r'\b(MALE|पुरुष)\b', text, re.IGNORECASE):
                extracted_data['gender'] = 'Male'
            elif re.search(r'\b(FEMALE|महिला)\b', text, re.IGNORECASE):
                extracted_data['gender'] = 'Female'
            
            # Extract Aadhaar number (12 digits)
            aadhaar_pattern = r'\b(\d{4}\s*\d{4}\s*\d{4})\b'
            match = re.search(aadhaar_pattern, text)
            if match:
                extracted_data['aadhaar_number'] = match.group(1).replace(' ', '')
            
            logging.info(f"Extracted data: {extracted_data}")
            return extracted_data
            
        except Exception as e:
            logging.error(f"Error extracting Aadhaar data: {str(e)}")
            return {
                'name': None,
                'dob': None,
                'age': None,
                'gender': None,
                'aadhaar_number': None
            }
    
    def standardize_date(self, date_str):
        """Convert various date formats to DD/MM/YYYY"""
        try:
            # Remove extra spaces and normalize separators
            date_str = re.sub(r'\s+', ' ', date_str.strip())
            date_str = date_str.replace('-', '/').replace(' ', '/')
            
            # Try different date formats
            formats = ['%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d', '%d-%m-%Y', '%m-%d-%Y']
            
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%d/%m/%Y')
                except ValueError:
                    continue
            
            return date_str  # Return original if no format matches
            
        except Exception as e:
            logging.error(f"Error standardizing date: {str(e)}")
            return date_str
    
    def calculate_age(self, dob_str):
        """Calculate age from date of birth string"""
        try:
            if not dob_str:
                return None
            
            # Parse date
            date_obj = datetime.strptime(dob_str, '%d/%m/%Y')
            today = datetime.now()
            
            # Calculate age
            age = today.year - date_obj.year
            if today.month < date_obj.month or (today.month == date_obj.month and today.day < date_obj.day):
                age -= 1
            
            return age
            
        except Exception as e:
            logging.error(f"Error calculating age: {str(e)}")
            return None
    
    def is_adult(self, age):
        """Check if person is adult (18+)"""
        return age is not None and age >= 18
