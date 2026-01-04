# Certificate Verification System v2

Advanced AI-powered certificate verification system with fuzzy matching, intelligent verification, enhanced OCR, security hardening, and a modern responsive UI.

## 🎯 Key Features

### 1. Intelligent Verification Engine
- **Fuzzy Matching**: Uses similarity scoring for flexible certificate matching
- **Weighted Confidence Scoring**: 
  - Person Name: 40%
  - Organization: 30%
  - Certificate Title: 20%
  - Issue Date: 10%
- **Detailed Mismatch Reports**: Shows exactly what doesn't match
- **Confidence Score (0-100)**: Quantified verification reliability

### 2. OCR Accuracy Improvement
- **Image Preprocessing**: Grayscale conversion, noise removal, thresholding, deskewing
- **Quality Assessment**: Automatic detection of low-quality OCR output
- **Adaptive Thresholding**: Handles varying lighting conditions
- **Contrast Enhancement**: CLAHE for better text visibility

### 3. Security Hardening
- **File Validation**: MIME type checking and magic bytes verification
- **Filename Sanitization**: Prevents path traversal attacks
- **Dangerous File Blocking**: Blocks executable and script files
- **Rate Limiting**: Prevents abuse (100 requests/minute by default)

### 4. Database & Persistence
- **PostgreSQL**: Enterprise-grade database with ORM
- **Comprehensive Storage**: Certificates, entities, verification results, audit logs
- **Full Indexing**: Fast queries on certificate ID, status, and dates
- **Transaction Support**: ACID compliance

### 5. Enhanced Email Notifications
- **HTML-Formatted Emails**: Professional email templates
- **Smart Sending**: Only sends for PARTIALLY_VERIFIED or NOT_VERIFIED
- **Async Processing**: Background task handling
- **Detailed Reports**: Includes confidence scores and mismatches

### 6. API Improvements
- **New Endpoints**:
  - `POST /api/verify/{id}` - Verify with fuzzy matching
  - `GET /api/certificate/{id}/report` - Comprehensive verification report
  - `GET /api/search` - Advanced search with filters
  - `GET /api/stats` - System statistics
- **Better Error Handling**: Structured error responses
- **Rate Limiting**: Per-client request throttling

### 7. Logging & Observability
- **Structured Logging**: JSON-formatted logs with levels
- **Audit Trail**: Complete history of certificate operations
- **Performance Metrics**: OCR quality scores and verification confidence
- **Log Rotation**: Automatic log management

### 8. Deployment Ready
- **Docker Support**: Complete containerization
- **Docker Compose**: Multi-service orchestration
- **Environment Configuration**: Flexible via .env
- **Health Checks**: Built-in container health monitoring

### 9. Modern Responsive UI
- **Advanced Dashboard**: Upload, verify, search, and statistics
- **Real-time Feedback**: Progress indicators and instant results
- **Mobile-Friendly**: Responsive design for all devices
- **Professional Styling**: Modern gradient UI with smooth animations

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis (for async tasks)
- Docker & Docker Compose (optional)

### Installation

#### Option 1: Local Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

2. **Configure Database**
```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE certificate_verification;
CREATE USER certuser WITH PASSWORD 'certpassword';
ALTER ROLE certuser GRANT ALL PRIVILEGES ON DATABASE certificate_verification TO certuser;
```

3. **Environment Setup**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Run Application**
```bash
python main.py
```

#### Option 2: Docker Setup

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database
- Redis cache
- Certificate Verification API
- Celery worker (optional)

### Access the Application

- **Web UI**: http://localhost:8000/ui
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📚 API Endpoints

### Upload Certificate
```bash
POST /api/upload
Content-Type: multipart/form-data

# Returns: certificate_id, extracted_entities, ocr_confidence
```

### Verify Certificate
```bash
POST /api/verify/{certificate_id}

# Returns: verification_status, confidence_score, field_scores, mismatches
```

### Get Certificate Report
```bash
GET /api/certificate/{certificate_id}/report

# Returns: Complete verification report with history and audit logs
```

### Search Certificates
```bash
GET /api/search?status=VERIFIED&filename=test&limit=50

# Returns: Filtered list of certificates
```

### Get Statistics
```bash
GET /api/stats

# Returns: Total, verified, partially_verified, not_verified counts
```

## 🔒 Security Features

- **File Validation**: Only PDFs, images, and Word documents allowed
- **Magic Bytes Check**: Verifies file content matches extension
- **Filename Sanitization**: Removes dangerous characters
- **Path Traversal Prevention**: Blocks "../" and absolute paths
- **Rate Limiting**: 100 requests per minute per client
- **CORS Protection**: Configurable CORS headers

## 📊 Verification Logic

| Confidence Score | Status |
|---|---|
| ≥ 85% | ✅ VERIFIED |
| 60-84% | ⚠️ PARTIALLY_VERIFIED |
| < 60% | ❌ NOT_VERIFIED |

Field scores use fuzzy matching (fuzzywuzzy) with token-based comparison for flexible matching.

## 📁 Project Structure

```
Project Raja/
├── api/                           # REST API endpoints
│   ├── routes.py                 # Original endpoints
│   └── routes_v2.py              # Enhanced endpoints
├── services/                      # Business logic
│   ├── upload_service.py
│   ├── email_service.py
│   ├── verification_service.py
│   ├── intelligent_verification.py  # Fuzzy matching
│   └── security_validator.py      # File validation
├── ocr/                          # OCR processing
│   ├── ocr_service.py
│   └── preprocessor.py           # Image enhancement
├── ner/                          # Entity extraction
│   └── ner_service.py
├── database/                     # Database layer
│   ├── models_orm.py            # SQLAlchemy models
│   ├── connection.py            # PostgreSQL connection
│   ├── dummy_db.py              # Legacy in-memory DB
│   └── sqlite_db.py             # SQLite fallback
├── core/                         # Core utilities
│   └── rate_limiting.py         # Rate limiting & async tasks
├── utils/                        # Configuration & logging
│   ├── config.py
│   ├── logger.py
│   └── helpers.py
├── frontend/                     # Modern responsive UI
│   └── index.html
├── logs/                         # Application logs
├── uploads/                      # Uploaded certificates
├── data/                         # Database files
├── main.py                       # Application entry point
├── Dockerfile                    # Container image
├── docker-compose.yml            # Multi-service setup
├── requirements.txt              # Python dependencies
└── .env.example                  # Configuration template
```

## 🛠️ Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://certuser:certpassword@localhost:5432/certificate_verification

# SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_TO_EMAIL=recipient@example.com

# Application
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=True
LOG_LEVEL=INFO

# Security
REQUESTS_PER_MINUTE=100
MAX_FILE_SIZE_MB=100

# Redis
REDIS_URL=redis://localhost:6379/0
```

## 📊 Database Schema

### Certificates Table
- `certificate_id`: Unique identifier
- `filename`: Original filename
- `file_path`: Storage path
- `file_type`: MIME type
- `extracted_text`: OCR results
- `ocr_confidence`: Quality score

### Extracted Entities Table
- `person_name`: Certificate holder
- `organization`: Issuing institution
- `certificate_title`: Course/program name
- `issue_date`: Certification date
- `registration_number`: Reference ID

### Verification Results Table
- `status`: VERIFIED / PARTIALLY_VERIFIED / NOT_VERIFIED
- `confidence_score`: 0-100
- `field_scores`: Individual field scores
- `mismatches`: Detailed mismatch information

### Verification Logs Table
- `action`: UPLOADED / OCR_PROCESSED / VERIFIED / EMAILED
- `status`: Success/failure status
- `timestamp`: Operation time
- `ip_address`: Client IP

## 🧪 Testing

### Using the Web UI
1. Go to http://localhost:8000/ui
2. Upload a certificate file
3. View extracted entities
4. Verify the certificate
5. Check confidence score and mismatches

### Using cURL
```bash
# Upload
curl -X POST http://localhost:8000/api/upload -F "file=@cert.pdf"

# Verify
curl -X POST http://localhost:8000/api/verify/CERT-20240103-ABC123

# Search
curl http://localhost:8000/api/search?status=VERIFIED

# Stats
curl http://localhost:8000/api/stats
```

### Using Python
```python
import requests

# Upload
with open('certificate.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/upload',
        files={'file': f}
    )
    cert_id = response.json()['certificate_id']

# Verify
response = requests.post(f'http://localhost:8000/api/verify/{cert_id}')
print(response.json()['confidence_score'])

# Get Report
response = requests.get(f'http://localhost:8000/api/certificate/{cert_id}/report')
print(response.json()['report'])
```

## 🚀 Production Deployment

### Docker Deployment
```bash
docker-compose -f docker-compose.yml up -d
```

### Kubernetes (Optional)
- Add Kubernetes manifests in `k8s/` directory
- Use PostgreSQL managed service (RDS, CloudSQL, etc.)
- Use external Redis cache
- Configure ingress for API access

### Environment Considerations
- Use managed PostgreSQL service
- Enable database backups
- Configure SSL/TLS for SMTP
- Use strong database passwords
- Enable firewall rules
- Set up monitoring and alerting

## 📈 Performance Optimization

- **Caching**: Redis for frequent lookups
- **Indexing**: Database indexes on frequent queries
- **Async Processing**: Background email tasks
- **Connection Pooling**: Efficient database connections
- **Rate Limiting**: Prevents resource exhaustion

## 🔍 Logging

View logs:
```bash
tail -f logs/app.log
```

Log levels:
- INFO: General information
- WARNING: Potential issues
- ERROR: Errors requiring attention
- DEBUG: Detailed debugging info

## 📝 License

This project is for educational and development purposes.

## 🤝 Contributing

Contributions are welcome! Please ensure code follows SOLID principles and includes proper documentation.

## 📞 Support

For issues or questions:
1. Check application logs in `logs/app.log`
2. Review the API documentation at `/docs`
3. Check database connectivity
4. Verify environment variables

## 🎉 Features Implemented

✅ Intelligent fuzzy matching verification  
✅ Advanced OCR preprocessing and quality assessment  
✅ Comprehensive security hardening  
✅ PostgreSQL persistence  
✅ Rate limiting and abuse prevention  
✅ Async email notifications  
✅ Comprehensive audit logging  
✅ Advanced search and filtering  
✅ System statistics and dashboards  
✅ Modern responsive web UI  
✅ Docker containerization  
✅ Production-ready code quality  

---

**Certificate Verification System v2** - Advanced AI-powered verification platform 🎓
