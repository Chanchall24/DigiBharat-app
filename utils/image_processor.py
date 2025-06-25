import cv2
import numpy as np
from PIL import Image, ImageEnhance
import os
import logging

class ImageProcessor:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def preprocess_document(self, image_path):
        """Preprocess document image for better OCR results"""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not read image")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply adaptive threshold
            threshold = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Apply morphological operations to clean up
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernel)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
            
            # Save preprocessed image
            processed_path = image_path.replace('.', '_processed.')
            cv2.imwrite(processed_path, cleaned)
            
            logging.info(f"Preprocessed image saved to: {processed_path}")
            return processed_path
            
        except Exception as e:
            logging.error(f"Error preprocessing document: {str(e)}")
            return image_path  # Return original if preprocessing fails
    
    def extract_face_from_document(self, image_path):
        """Extract face from ID document"""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not read image")
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            
            if len(faces) > 0:
                # Get the largest face (assuming it's the main subject)
                largest_face = max(faces, key=lambda x: x[2] * x[3])
                x, y, w, h = largest_face
                
                # Extract face region with some padding
                padding = 20
                face_region = image[
                    max(0, y-padding):min(image.shape[0], y+h+padding),
                    max(0, x-padding):min(image.shape[1], x+w+padding)
                ]
                
                # Save extracted face
                face_path = image_path.replace('.', '_face.')
                cv2.imwrite(face_path, face_region)
                
                logging.info(f"Face extracted and saved to: {face_path}")
                return face_path
            else:
                logging.warning("No face detected in document")
                return None
                
        except Exception as e:
            logging.error(f"Error extracting face from document: {str(e)}")
            return None
    
    def check_image_quality(self, image_path):
        """Check image quality and provide suggestions"""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return 0, ["Could not read image"]
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate image quality metrics
            quality_score = 0
            suggestions = []
            
            # 1. Check brightness
            brightness = np.mean(gray)
            if brightness < 50:
                suggestions.append("Image is too dark. Try better lighting.")
            elif brightness > 200:
                suggestions.append("Image is too bright. Reduce lighting or avoid flash.")
            else:
                quality_score += 25
            
            # 2. Check contrast
            contrast = gray.std()
            if contrast < 30:
                suggestions.append("Image has low contrast. Ensure good lighting conditions.")
            else:
                quality_score += 25
            
            # 3. Check sharpness (Laplacian variance)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            if laplacian_var < 100:
                suggestions.append("Image appears blurry. Hold camera steady and focus properly.")
            else:
                quality_score += 25
            
            # 4. Check image size
            height, width = gray.shape
            if width < 300 or height < 300:
                suggestions.append("Image resolution is too low. Use a higher quality camera.")
            else:
                quality_score += 25
            
            if quality_score == 100:
                suggestions = ["Image quality is excellent!"]
            
            return quality_score, suggestions
            
        except Exception as e:
            logging.error(f"Error checking image quality: {str(e)}")
            return 0, ["Error analyzing image quality"]
    
    def resize_image(self, image_path, max_size=(800, 600)):
        """Resize image while maintaining aspect ratio"""
        try:
            with Image.open(image_path) as img:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                img.save(image_path, optimize=True)
                logging.info(f"Image resized and optimized: {image_path}")
        except Exception as e:
            logging.error(f"Error resizing image: {str(e)}")
