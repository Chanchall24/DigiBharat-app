# DigiBharat - Identity Verification System

## Overview

DigiBharat is a comprehensive age and identity verification system built with Flask and Python. The application provides a secure, user-friendly 3-step verification process that includes document upload, face recognition, and verification results. It features multilingual support (English/Hindi), advanced OCR processing for Aadhaar cards, and real-time face matching capabilities.

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework with SQLAlchemy ORM
- **Database**: SQLite for development (configured for PostgreSQL support)
- **ORM**: SQLAlchemy with declarative base model
- **Session Management**: Flask sessions with configurable secret key
- **File Handling**: Werkzeug secure filename handling with 16MB upload limit

### Frontend Architecture
- **Template Engine**: Jinja2 templates with base template inheritance
- **UI Framework**: Bootstrap 5 for responsive design
- **JavaScript**: Vanilla JS with modular class-based architecture
- **Styling**: Custom CSS with CSS variables for theming
- **Icons**: Font Awesome for consistent iconography

### Processing Pipeline
- **Image Processing**: OpenCV-based preprocessing for document enhancement
- **OCR**: Tesseract OCR for text extraction from documents
- **Face Recognition**: face_recognition library for biometric matching
- **File Storage**: Local filesystem with organized upload directory structure

## Key Components

### Models (`models.py`)
- **VerificationSession**: Tracks user verification progress through all steps
  - Session management with unique session IDs
  - Step tracking (1: upload, 2: selfie, 3: results)
  - Document and selfie path storage
  - Extracted data storage (name, DOB, age)
  - Face match confidence scoring
  - Verification status tracking with error handling

### Routes (`routes.py`)
- **Multi-step workflow**: Progressive verification process
- **File upload handling**: Secure file processing with validation
- **Session state management**: Maintains user progress across steps
- **Error handling**: Comprehensive error management with user feedback

### Utility Modules
- **ImageProcessor**: Document preprocessing and face extraction
- **OCRProcessor**: Aadhaar card data extraction with pattern matching
- **FaceMatcher**: Biometric face comparison with confidence scoring

### Frontend Components
- **Responsive Design**: Mobile-first approach with Bootstrap
- **Progressive Enhancement**: JavaScript enhancements for better UX
- **Camera Integration**: Real-time selfie capture functionality
- **Language Toggle**: Dynamic English/Hindi language switching

## Data Flow

1. **Document Upload**: User uploads ID document → Server validates and stores file → OCR extracts personal information
2. **Selfie Capture**: User takes selfie → Image stored securely → Face detection validation
3. **Verification**: System compares faces → Generates confidence score → Returns verification result
4. **Session Management**: Progress tracked in database → State maintained across requests

## External Dependencies

### Python Libraries
- **Flask**: Web framework and routing
- **SQLAlchemy**: Database ORM and migrations
- **OpenCV**: Image processing and computer vision
- **Tesseract**: OCR text extraction
- **face_recognition**: Facial recognition and matching
- **Pillow**: Image manipulation utilities
- **psycopg2-binary**: PostgreSQL database adapter

### Frontend Dependencies
- **Bootstrap 5**: CSS framework for responsive design
- **Font Awesome**: Icon library for UI elements
- **Vanilla JavaScript**: No additional framework dependencies

## Deployment Strategy

### Production Configuration
- **WSGI Server**: Gunicorn with automatic scaling
- **Process Management**: Multi-worker configuration with port reuse
- **Static Assets**: Direct serving through Flask (production should use nginx)
- **Database**: PostgreSQL for production environments
- **File Storage**: Local filesystem (production should use cloud storage)

### Environment Variables
- `DATABASE_URL`: Database connection string
- `SESSION_SECRET`: Flask session encryption key
- `UPLOAD_FOLDER`: File upload directory path

### Security Measures
- CSRF protection through Flask sessions
- Secure filename handling for uploads
- File type validation and size limits
- Proxy fix for production deployment behind reverse proxy

## Changelog
- June 24, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.