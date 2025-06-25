# DigiBharat-app
An Age &amp; Identity Verification System Using Simulated Government ID Cards
DigiBharat-app

DigiBharat is a Flask-based web application for Aadhaar-based identity verification using OCR and face matching.  
It uses Tesseract for text extraction and OpenCV for facial similarity — optimized for mobile devices and multilingual use.

Start Guide

Follow these steps to clone and run the app locally.

 1. Clone the Repository

bash
git clone https://github.com/Chanchall24/DigiBharat-app.git
cd DigiBharat-app


2. Create and Activate Virtual Environment

*macOS/Linux:*

bash
python3 -m venv venv
source venv/bin/activate

*Windows:*

bash
python -m venv venv
venv\Scripts\activate

 3. Install Required Python Dependencies

bash
pip install flask flask_sqlalchemy opencv-python pillow pytesseract sqlalchemy werkzeug gunicorn


 (Optional) Save Installed Packages

bash
pip freeze > requirements.txt


To reinstall in the future:

bash
pip install -r requirements.txt

 5. Open Project in VS Code (Optional)

bash
code . --new-window


> Tip: If code doesn’t work, open VS Code → Cmd+Shift+P → “Install 'code' command in PATH”.

6. Run the Flask App

*macOS/Linux:*

bash
export FLASK_APP=main.py
flask run


*Windows (CMD):*

bash
set FLASK_APP=main.py
flask run

 7. View in Browser

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## Tesseract OCR Setup

Tesseract is required for Aadhaar OCR functionality.

*macOS:*

bash
brew install tesseract


*Ubuntu/Linux:*

bash
sudo apt install tesseract-ocr


*Windows:*

Download from: https://github.com/tesseract-ocr/tesseract  
➤ Don’t forget to add the install path to your system’s *Environment Variables*.

 Project Structure


DigiBharat-app/
├── app.py                  # Flask app config
├── main.py                 # Entry point
├── models.py               # Database models
├── routes.py               # Web routes
├── templates/              # HTML files
├── static/
│   ├── css/styles.css
│   └── js/
├── utils/
│   ├── face_matcher.py
│   ├── ocr_processor.py
│   └── image_processor.py
├── venv/                   # Virtual environment
└── requirements.txt        # (Optional)




Features

-  Aadhaar OCR using Tesseract
-  Face Matching using OpenCV (no dlib required)
-  🇮🇳 Bilingual interface (Hindi & English)
-  Live camera/selfie support
-  Mobile-friendly and responsive

##  Requirements

- Python 3.8 or higher
- pip
- Tesseract OCR (installed separately)
- Git
- OpenCV, Pillow, Flask, SQLAlchemy, Pytesseract (installed via pip)

