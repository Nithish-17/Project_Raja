# Certificate Verification System

A Python-based backend application for Certificate Verification with OCR, NER, and automated verification.

## Features

1. **Certificate Upload** - Accept any certificate file type (PDF, JPG, PNG, DOCX)
2. **OCR Text Extraction** - Extract text from images and PDFs
3. **Named Entity Recognition (NER)** - Extract person names, organizations, dates, etc.
4. **Dummy Database Verification** - Cross-verify against sample valid certificates
5. **Email Alerts** - Send SMTP email notifications with verification results
6. **REST API** - FastAPI endpoints for upload, retrieval, and verification

## Project Structure

```
Project Raja/
├── api/                    # API endpoints
│   ├── __init__.py
│   └── routes.py          # FastAPI routes
├── services/              # Business logic services
│   ├── __init__.py
│   ├── upload_service.py  # File upload handling
│   ├── email_service.py   # Email notifications
│   └── verification_service.py  # Verification workflow
├── ocr/                   # OCR text extraction
│   ├── __init__.py
│   └── ocr_service.py     # PDF and image OCR
├── ner/                   # Named Entity Recognition
│   ├── __init__.py
│   └── ner_service.py     # Entity extraction with spaCy
├── database/              # Data storage
│   ├── __init__.py
│   ├── models.py          # Pydantic models
│   └── dummy_db.py        # In-memory database
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── logger.py          # Logging setup
│   └── helpers.py         # Helper functions
├── uploads/               # Uploaded certificates storage
├── logs/                  # Application logs
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Tesseract OCR (required for image text extraction)
- poppler-utils (required for PDF to image conversion)

#### Install Tesseract OCR

**Windows:**
```powershell
# Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
# Add Tesseract to PATH or set pytesseract.pytesseract.tesseract_cmd in code
```

**Linux/Ubuntu:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install poppler-utils
```

**macOS:**
```bash
brew install tesseract
brew install poppler
```

### Setup Steps

1. **Clone or navigate to the project directory**

2. **Create virtual environment**
```powershell
python -m venv venv
```

3. **Activate virtual environment**
```powershell
# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

4. **Install Python dependencies**
```powershell
pip install -r requirements.txt
```

5. **Download spaCy language model**
```powershell
python -m spacy download en_core_web_sm
```

6. **Configure environment variables**
```powershell
# Copy .env.example to .env
Copy-Item .env.example .env

# Edit .env with your SMTP credentials
```

7. **Create uploads directory (if not exists)**
```powershell
New-Item -ItemType Directory -Force -Path uploads
```

## Configuration

Edit the `.env` file with your settings:

```env
# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_TO_EMAIL=recipient@example.com

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=True
```

**Note:** For Gmail, you need to use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

## Running the Application

### Start the server

```powershell
python main.py
```

Or using uvicorn directly:
```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## API Endpoints

### 1. Upload Certificate
```http
POST /api/upload
Content-Type: multipart/form-data

Body: file (PDF, JPG, PNG, DOCX)
```

**Response:**
```json
{
  "success": true,
  "message": "Certificate uploaded and processed successfully",
  "certificate_id": "CERT-20240103-A1B2C3D4",
  "filename": "certificate.pdf",
  "extracted_entities": {
    "person_name": "John Smith",
    "organization": "Stanford University",
    "certificate_name": "Machine Learning",
    "date_of_issue": "2023-06-15",
    "registration_number": "ML-2023-001234"
  },
  "upload_timestamp": "2024-01-03T10:30:00"
}
```

### 2. Get Certificate Details
```http
GET /api/certificate/{certificate_id}
```

**Response:**
```json
{
  "success": true,
  "certificate_id": "CERT-20240103-A1B2C3D4",
  "filename": "certificate.pdf",
  "file_type": "application/pdf",
  "upload_timestamp": "2024-01-03T10:30:00",
  "extracted_text": "Certificate text...",
  "entities": {...},
  "verification_status": "VERIFIED",
  "verified_timestamp": "2024-01-03T10:35:00"
}
```

### 3. Verify Certificate
```http
POST /api/verify/{certificate_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Certificate verification completed",
  "certificate_id": "CERT-20240103-A1B2C3D4",
  "verification_status": "VERIFIED",
  "entities": {...},
  "verified_timestamp": "2024-01-03T10:35:00",
  "email_sent": true
}
```

### 4. Health Check
```http
GET /api/health
```

## Testing the API

### Using cURL

**Upload a certificate:**
```powershell
curl -X POST "http://localhost:8000/api/upload" `
  -F "file=@certificate.pdf"
```

**Get certificate:**
```powershell
curl "http://localhost:8000/api/certificate/CERT-20240103-A1B2C3D4"
```

**Verify certificate:**
```powershell
curl -X POST "http://localhost:8000/api/verify/CERT-20240103-A1B2C3D4"
```

### Using Python requests

```python
import requests

# Upload
files = {'file': open('certificate.pdf', 'rb')}
response = requests.post('http://localhost:8000/api/upload', files=files)
print(response.json())

# Get
cert_id = response.json()['certificate_id']
response = requests.get(f'http://localhost:8000/api/certificate/{cert_id}')
print(response.json())

# Verify
response = requests.post(f'http://localhost:8000/api/verify/{cert_id}')
print(response.json())
```

## Verification Logic

The system verifies certificates against a dummy database containing valid certificates. The verification status is determined by matching extracted entities:

- **VERIFIED**: 4+ fields match
- **PARTIALLY VERIFIED**: 2-3 fields match
- **NOT VERIFIED**: 0-1 fields match

Matched fields:
- Person Name
- Organization
- Certificate Name
- Date of Issue
- Registration Number

## Dummy Database

Sample valid certificates are stored in `database/dummy_db.py`. You can add more certificates to the `VALID_CERTIFICATES` list for testing.

## Logging

Logs are stored in the `logs/` directory:
- `logs/app.log` - Application logs

Logs are also printed to console for real-time monitoring.

## Error Handling

The API includes comprehensive error handling:
- File upload errors
- OCR extraction failures
- Database errors
- SMTP/email errors
- Invalid certificate IDs

All errors return appropriate HTTP status codes and error messages.

## Dependencies

See `requirements.txt` for complete list:
- **FastAPI** - Web framework
- **pytesseract** - OCR engine
- **spaCy** - NLP/NER library
- **PyPDF2** - PDF text extraction
- **Pillow** - Image processing
- **pdf2image** - PDF to image conversion

## Troubleshooting

### Tesseract not found
```
pytesseract.pytesseract.TesseractNotFoundError
```
**Solution:** Install Tesseract OCR and add to PATH, or set the path in code:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### spaCy model not found
```
OSError: [E050] Can't find model 'en_core_web_sm'
```
**Solution:**
```powershell
python -m spacy download en_core_web_sm
```

### Email not sending
- Check SMTP credentials in `.env`
- For Gmail, use App Password
- Check firewall/antivirus settings

## Future Enhancements

- Database integration (PostgreSQL, MongoDB)
- User authentication and authorization
- Batch certificate processing
- Advanced NER models
- Certificate templates
- Web frontend interface
- Docker containerization

## License

This project is for educational and development purposes.

## Support

For issues or questions, please check the logs in `logs/app.log` for detailed error messages.
