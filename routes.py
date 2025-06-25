import os
import uuid
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from app import app, db
from models import VerificationSession
from utils.image_processor import ImageProcessor
from utils.face_matcher import FaceMatcher
from utils.ocr_processor import OCRProcessor
import logging

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Welcome screen with onboarding"""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Step 1: Upload ID document"""
    if request.method == 'POST':
        # Check if file was uploaded
        if 'id_document' not in request.files:
            flash('कृपया एक आईडी दस्तावेज़ अपलोड करें / Please upload an ID document', 'error')
            return redirect(request.url)
        
        file = request.files['id_document']
        if file.filename == '':
            flash('कोई फ़ाइल चुनी नहीं गई / No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                # Generate unique session ID if not exists
                if 'session_id' not in session:
                    session['session_id'] = str(uuid.uuid4())
                
                # Save file
                filename = secure_filename(file.filename)
                unique_filename = f"{session['session_id']}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                # Create or update verification session
                verification_session = VerificationSession.query.filter_by(
                    session_id=session['session_id']
                ).first()
                
                if not verification_session:
                    verification_session = VerificationSession(
                        session_id=session['session_id'],
                        step=1,
                        id_document_path=file_path
                    )
                    db.session.add(verification_session)
                else:
                    verification_session.id_document_path = file_path
                    verification_session.step = 1
                
                db.session.commit()
                
                # Process the uploaded document
                try:
                    image_processor = ImageProcessor()
                    ocr_processor = OCRProcessor()
                    
                    # Preprocess image
                    processed_image_path = image_processor.preprocess_document(file_path)
                    
                    # Extract text using OCR
                    extracted_data = ocr_processor.extract_aadhaar_data(processed_image_path)
                    
                    # Update session with extracted data
                    verification_session.extracted_name = extracted_data.get('name')
                    verification_session.extracted_dob = extracted_data.get('dob')
                    verification_session.extracted_age = extracted_data.get('age')
                    verification_session.step = 2
                    db.session.commit()
                    
                    flash('आईडी दस्तावेज़ सफलतापूर्वक अपलोड किया गया / ID document uploaded successfully', 'success')
                    return redirect(url_for('selfie'))
                    
                except Exception as e:
                    logging.error(f"Error processing document: {str(e)}")
                    flash('दस्तावेज़ प्रसंस्करण में त्रुटि / Error processing document', 'error')
                    return redirect(request.url)
                    
            except Exception as e:
                logging.error(f"Error uploading file: {str(e)}")
                flash('फ़ाइल अपलोड करने में त्रुटि / Error uploading file', 'error')
                return redirect(request.url)
        else:
            flash('अमान्य फ़ाइल प्रकार / Invalid file type', 'error')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/selfie', methods=['GET', 'POST'])
def selfie():
    """Step 2: Take selfie"""
    if 'session_id' not in session:
        flash('कृपया पहले आईडी दस्तावेज़ अपलोड करें / Please upload ID document first', 'error')
        return redirect(url_for('upload'))
    
    verification_session = VerificationSession.query.filter_by(
        session_id=session['session_id']
    ).first()
    
    if not verification_session or verification_session.step < 2:
        flash('कृपया पहले आईडी दस्तावेज़ अपलोड करें / Please upload ID document first', 'error')
        return redirect(url_for('upload'))
    
    if request.method == 'POST':
        if 'selfie' not in request.files:
            flash('कृपया एक सेल्फी अपलोड करें / Please upload a selfie', 'error')
            return redirect(request.url)
        
        file = request.files['selfie']
        if file.filename == '':
            flash('कोई फ़ाइल चुनी नहीं गई / No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                # Save selfie
                filename = secure_filename(file.filename)
                unique_filename = f"selfie_{session['session_id']}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                # Update verification session
                verification_session.selfie_path = file_path
                verification_session.step = 3
                db.session.commit()
                
                # Process face matching
                try:
                    face_matcher = FaceMatcher()
                    image_processor = ImageProcessor()
                    
                    # Extract face from ID document
                    id_face_path = image_processor.extract_face_from_document(
                        verification_session.id_document_path
                    )
                    
                    if id_face_path:
                        # Compare faces
                        match_confidence = face_matcher.compare_faces(id_face_path, file_path)
                        
                        # Update session with results
                        verification_session.face_match_confidence = match_confidence
                        
                        # Determine verification status
                        if match_confidence > 0.6:  # 60% threshold
                            verification_session.verification_status = 'verified'
                        else:
                            verification_session.verification_status = 'failed'
                            verification_session.error_message = 'Face match confidence too low'
                    else:
                        verification_session.verification_status = 'failed'
                        verification_session.error_message = 'Could not extract face from ID document'
                    
                    db.session.commit()
                    
                    flash('सेल्फी सफलतापूर्वक अपलोड की गई / Selfie uploaded successfully', 'success')
                    return redirect(url_for('results'))
                    
                except Exception as e:
                    logging.error(f"Error processing selfie: {str(e)}")
                    flash('सेल्फी प्रसंस्करण में त्रुटि / Error processing selfie', 'error')
                    return redirect(request.url)
                    
            except Exception as e:
                logging.error(f"Error uploading selfie: {str(e)}")
                flash('सेल्फी अपलोड करने में त्रुटि / Error uploading selfie', 'error')
                return redirect(request.url)
        else:
            flash('अमान्य फ़ाइल प्रकार / Invalid file type', 'error')
            return redirect(request.url)
    
    return render_template('selfie.html', verification_session=verification_session)

@app.route('/results')
def results():
    """Step 3: Show verification results"""
    if 'session_id' not in session:
        flash('कृपया सत्यापन प्रक्रिया पूरी करें / Please complete verification process', 'error')
        return redirect(url_for('upload'))
    
    verification_session = VerificationSession.query.filter_by(
        session_id=session['session_id']
    ).first()
    
    if not verification_session or verification_session.step < 3:
        flash('कृपया सत्यापन प्रक्रिया पूरी करें / Please complete verification process', 'error')
        return redirect(url_for('upload'))
    
    return render_template('results.html', verification_session=verification_session)

@app.route('/help')
def help():
    """Help and FAQ page"""
    return render_template('help.html')

@app.route('/restart')
def restart():
    """Restart verification process"""
    session.clear()
    flash('नई सत्यापन प्रक्रिया शुरू की गई / New verification process started', 'info')
    return redirect(url_for('index'))

@app.route('/api/check_image_quality', methods=['POST'])
def check_image_quality():
    """API endpoint to check image quality"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Save temporary file
        temp_filename = f"temp_{uuid.uuid4().hex}.jpg"
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        file.save(temp_path)
        
        # Check image quality
        image_processor = ImageProcessor()
        quality_score, suggestions = image_processor.check_image_quality(temp_path)
        
        # Clean up
        os.remove(temp_path)
        
        return jsonify({
            'quality_score': quality_score,
            'suggestions': suggestions
        })
        
    except Exception as e:
        logging.error(f"Error checking image quality: {str(e)}")
        return jsonify({'error': 'Failed to check image quality'}), 500
