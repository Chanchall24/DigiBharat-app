import cv2
import numpy as np
import logging

class FaceMatcher:
    def __init__(self):
        self.tolerance = 0.6
        # Initialize face detector
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        # Initialize ORB detector for feature matching
        self.orb = cv2.ORB_create(nfeatures=1000)
        # Initialize FLANN matcher
        FLANN_INDEX_LSH = 6
        index_params = dict(algorithm=FLANN_INDEX_LSH,
                           table_number=6,
                           key_size=12,
                           multi_probe_level=1)
        search_params = dict(checks=50)
        self.flann = cv2.FlannBasedMatcher(index_params, search_params)
    
    def compare_faces(self, image1_path, image2_path):
        """Compare two face images and return confidence score using OpenCV"""
        try:
            # Load images
            img1 = cv2.imread(image1_path)
            img2 = cv2.imread(image2_path)
            
            if img1 is None or img2 is None:
                logging.error("Could not load one or both images")
                return 0.0
            
            # Convert to grayscale
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces1 = self.face_cascade.detectMultiScale(gray1, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            faces2 = self.face_cascade.detectMultiScale(gray2, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            if len(faces1) == 0:
                logging.warning(f"No face found in {image1_path}")
                return 0.0
            
            if len(faces2) == 0:
                logging.warning(f"No face found in {image2_path}")
                return 0.0
            
            # Get the largest face from each image
            face1 = max(faces1, key=lambda x: x[2] * x[3])
            face2 = max(faces2, key=lambda x: x[2] * x[3])
            
            # Extract face regions
            x1, y1, w1, h1 = face1
            x2, y2, w2, h2 = face2
            
            face_roi1 = gray1[y1:y1+h1, x1:x1+w1]
            face_roi2 = gray2[y2:y2+h2, x2:x2+w2]
            
            # Resize faces to same size for comparison
            face_roi1 = cv2.resize(face_roi1, (100, 100))
            face_roi2 = cv2.resize(face_roi2, (100, 100))
            
            # Method 1: Histogram comparison
            hist1 = cv2.calcHist([face_roi1], [0], None, [256], [0, 256])
            hist2 = cv2.calcHist([face_roi2], [0], None, [256], [0, 256])
            hist_correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            
            # Method 2: Template matching
            result = cv2.matchTemplate(face_roi1, face_roi2, cv2.TM_CCOEFF_NORMED)
            template_score = np.max(result)
            
            # Method 3: Feature matching with ORB
            kp1, des1 = self.orb.detectAndCompute(face_roi1, None)
            kp2, des2 = self.orb.detectAndCompute(face_roi2, None)
            
            feature_score = 0.0
            if des1 is not None and des2 is not None and len(des1) > 10 and len(des2) > 10:
                try:
                    matches = self.flann.knnMatch(des1, des2, k=2)
                    good_matches = []
                    for match_pair in matches:
                        if len(match_pair) == 2:
                            m, n = match_pair
                            if m.distance < 0.7 * n.distance:
                                good_matches.append(m)
                    
                    if len(good_matches) > 5:
                        feature_score = min(len(good_matches) / 50.0, 1.0)
                except Exception as e:
                    logging.warning(f"Feature matching failed: {str(e)}")
            
            # Combine all methods for final confidence score
            confidence = (hist_correlation * 0.3 + template_score * 0.4 + feature_score * 0.3)
            confidence = max(0.0, min(1.0, confidence))  # Clamp between 0 and 1
            
            logging.info(f"Face comparison - Hist: {hist_correlation:.3f}, Template: {template_score:.3f}, Features: {feature_score:.3f}, Final: {confidence:.3f}")
            return confidence
            
        except Exception as e:
            logging.error(f"Error comparing faces: {str(e)}")
            return 0.0
    
    def detect_faces_in_image(self, image_path):
        """Detect all faces in an image using OpenCV"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return []
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            # Convert to format similar to face_recognition
            face_locations = []
            for (x, y, w, h) in faces:
                # Convert to (top, right, bottom, left) format
                face_locations.append((y, x + w, y + h, x))
            
            logging.info(f"Found {len(face_locations)} faces in {image_path}")
            return face_locations
            
        except Exception as e:
            logging.error(f"Error detecting faces: {str(e)}")
            return []
    
    def is_face_clear(self, image_path):
        """Check if face in image is clear and suitable for matching"""
        try:
            # Load image with OpenCV
            image = cv2.imread(image_path)
            if image is None:
                return False, "Could not read image"
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Check image quality
            # 1. Brightness check
            brightness = np.mean(gray)
            if brightness < 50:
                return False, "Image is too dark"
            elif brightness > 200:
                return False, "Image is too bright"
            
            # 2. Blur detection using Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            if laplacian_var < 100:
                return False, "Image is too blurry"
            
            # 3. Face detection
            face_locations = self.detect_faces_in_image(image_path)
            if len(face_locations) == 0:
                return False, "No face detected"
            elif len(face_locations) > 1:
                return False, "Multiple faces detected"
            
            return True, "Face is clear and suitable for matching"
            
        except Exception as e:
            logging.error(f"Error checking face clarity: {str(e)}")
            return False, "Error analyzing image"
