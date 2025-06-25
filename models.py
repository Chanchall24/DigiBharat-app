from app import db
from datetime import datetime
from sqlalchemy import Text

class VerificationSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), unique=True, nullable=False)
    step = db.Column(db.Integer, default=1)  # Current step (1, 2, or 3)
    id_document_path = db.Column(db.String(255))
    selfie_path = db.Column(db.String(255))
    extracted_name = db.Column(db.String(255))
    extracted_dob = db.Column(db.String(20))
    extracted_age = db.Column(db.Integer)
    face_match_confidence = db.Column(db.Float)
    verification_status = db.Column(db.String(20))  # 'pending', 'verified', 'failed'
    error_message = db.Column(Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<VerificationSession {self.session_id}>'
