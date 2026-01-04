# Quick Start Guide

## Certificate Verification System

Your Python backend application for Certificate Verification is now **RUNNING** on `http://localhost:8000`

---

## ✅ Project Status

- **Server Status**: Running on port 8000
- **All Services**: Initialized successfully
  - Upload Service ✓
  - OCR Service ✓
  - NER Service (with spaCy) ✓
  - Email Service ✓
  - Verification Service ✓
- **Database**: Dummy database loaded with sample certificates

---

## 🚀 Quick Access

- **API Base URL**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

---

## 📋 API Endpoints

### 1. Health Check
```bash
curl http://localhost:8000/api/health
```

### 2. Upload Certificate
```bash
curl -X POST "http://localhost:8000/api/upload" -F "file=@certificate.pdf"
```

**Response**: Returns certificate_id and extracted entities

### 3. Get Certificate Details
```bash
curl http://localhost:8000/api/certificate/{certificate_id}
```

### 4. Verify Certificate
```bash
curl -X POST "http://localhost:8000/api/verify/{certificate_id}"
```

**Response**: Returns verification status (VERIFIED / PARTIALLY VERIFIED / NOT VERIFIED)

---

## 🧪 Testing the API

### Option 1: Use the provided test script
```powershell
# Basic tests (health and endpoints)
python test_api.py

# Test with a certificate file
python test_api.py --file path/to/certificate.pdf
```

### Option 2: Use Swagger UI
1. Open browser: http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

### Option 3: Use Python requests
```python
import requests

# Upload a certificate
files = {'file': open('certificate.pdf', 'rb')}
response = requests.post('http://localhost:8000/api/upload', files=files)
result = response.json()
cert_id = result['certificate_id']

# Get certificate details
response = requests.get(f'http://localhost:8000/api/certificate/{cert_id}')
print(response.json())

# Verify certificate
response = requests.post(f'http://localhost:8000/api/verify/{cert_id}')
print(response.json())
```

---

## 📁 Supported File Types

- PDF (.pdf)
- Images (.jpg, .jpeg, .png)
- Word Documents (.docx, .doc)

No file size restrictions!

---

## 🔍 What Gets Extracted

The NER system extracts:
- **Person Name** (certificate holder)
- **Organization** (issuing institution)
- **Certificate Name** (course/program name)
- **Date of Issue**
- **Registration/Certificate Number**

---

## ✉️ Email Notifications

After verification, an email alert is sent containing:
- Certificate ID
- All extracted entities
- Verification status
- Formatted HTML report

**To enable emails**: Edit `.env` file with your SMTP credentials
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_TO_EMAIL=recipient@example.com
```

---

## 📊 Verification Logic

Certificates are verified against a dummy database:

| Matches | Status |
|---------|--------|
| 4-5 fields | ✅ VERIFIED |
| 2-3 fields | ⚠️ PARTIALLY VERIFIED |
| 0-1 fields | ❌ NOT VERIFIED |

---

## 📝 Sample Dummy Certificates

The system has 5 pre-loaded valid certificates for testing:

1. **John Smith** - Machine Learning Specialization (Stanford)
2. **Jane Doe** - Data Science Certificate (MIT)
3. **Alice Johnson** - Python Programming (Harvard)
4. **Bob Williams** - Cloud Architecture (Google)
5. **Carol Martinez** - AI Engineering (IBM)

---

## 🛑 Stopping the Server

In the terminal where the server is running, press: **CTRL+C**

---

## 🔄 Restarting the Server

```powershell
cd "e:\Project Raja"
python main.py
```

---

## 📂 Project Structure

```
Project Raja/
├── api/                    # REST API endpoints
├── services/              # Business logic
├── ocr/                   # OCR text extraction
├── ner/                   # Named Entity Recognition
├── database/              # Data models and dummy DB
├── utils/                 # Configuration and helpers
├── uploads/               # Uploaded certificates
├── logs/                  # Application logs
├── main.py               # Application entry point
└── test_api.py           # API test script
```

---

## 📖 Logs

Check application logs at: `logs/app.log`

Or view real-time logs in the terminal where the server is running.

---

## 🐛 Troubleshooting

### Server not starting?
- Check if port 8000 is already in use
- Check `logs/app.log` for errors

### OCR not working?
- Install Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
- For PDFs, install poppler-utils

### NER errors?
- Ensure spaCy model is installed: `python -m spacy download en_core_web_sm`

### Email not sending?
- Configure SMTP settings in `.env` file
- For Gmail, use App Password (not regular password)

---

## 🎯 Next Steps

1. **Test the API** with sample certificate files
2. **Configure email** settings in `.env`
3. **Customize** the dummy database in `database/dummy_db.py`
4. **Add more features** as needed

---

## 📚 Full Documentation

See `README_PROJECT.md` for complete documentation including:
- Installation instructions
- Configuration details
- API reference
- Development guide

---

## ✨ Features Implemented

✅ Certificate upload (any file type)  
✅ OCR text extraction  
✅ Named Entity Recognition (NER)  
✅ Dummy database verification  
✅ Email alerts via SMTP  
✅ REST API with FastAPI  
✅ Comprehensive error handling  
✅ Logging system  
✅ Clean project structure  

---

**Your Certificate Verification System is ready to use! 🎉**
