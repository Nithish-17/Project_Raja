# Certificate Verification System v2 - Quick Reference Guide

## 🚀 Quick Start (5 minutes)

### 1. Automated Setup
```bash
python setup_v2.py
```
This will:
- ✅ Check prerequisites (Python, PostgreSQL)
- ✅ Install dependencies
- ✅ Create directory structure
- ✅ Download spaCy model
- ✅ Create PostgreSQL database
- ✅ Generate configuration file

### 2. Configure
Edit `.env` with your settings:
```env
DATABASE_URL=postgresql://certuser:certpassword@localhost:5432/certificate_verification
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
TESSERACT_PATH=/usr/bin/tesseract  # or C:\Program Files\Tesseract-OCR\tesseract.exe
```

### 3. Start Application
```bash
python main.py
```
Access at: **http://localhost:8000/ui**

### 4. Start with Docker
```bash
docker-compose up -d
```
Access at: **http://localhost:8000/ui**

---

## 📡 API Quick Reference

### Health Check
```bash
curl http://localhost:8000/api/health
```
Response: `{"status": "healthy", "checks": {...}}`

### Upload Certificate
```bash
curl -X POST -F "file=@certificate.pdf" \
  http://localhost:8000/api/upload
```
Response: `{"certificate_id": "CERT-001", "filename": "certificate.pdf", ...}`

### Verify Certificate
```bash
curl -X POST http://localhost:8000/api/verify/CERT-001 \
  -H "Content-Type: application/json" \
  -d '{
    "expected_person_name": "John Doe",
    "expected_organization": "ABC Corp",
    "expected_certificate_title": "Senior Engineer",
    "expected_issue_date": "2023-01-15"
  }'
```
Response:
```json
{
  "verification_status": "VERIFIED",
  "confidence_score": 92.5,
  "field_scores": {
    "person_name": 95.0,
    "organization": 90.0,
    "certificate_title": 85.0,
    "issue_date": 95.0
  },
  "mismatches": []
}
```

### Get Certificate Report
```bash
curl http://localhost:8000/api/certificate/CERT-001/report
```
Response: Complete certificate data with entities, verification history, audit log

### Search Certificates
```bash
# By status
curl "http://localhost:8000/api/search?status=VERIFIED"

# By filename
curl "http://localhost:8000/api/search?filename=john"

# By date range
curl "http://localhost:8000/api/search?date_from=2024-01-01&date_to=2024-12-31"

# Combined
curl "http://localhost:8000/api/search?status=VERIFIED&filename=john&date_from=2024-01-01"
```

### Get Statistics
```bash
curl http://localhost:8000/api/stats
```
Response:
```json
{
  "total_certificates": 10,
  "verified": 7,
  "partially_verified": 2,
  "not_verified": 1,
  "average_confidence_score": 85.5
}
```

### API Documentation
Visit: **http://localhost:8000/docs** (Swagger UI)
Or: **http://localhost:8000/redoc** (ReDoc)

---

## 🗄️ Database Commands

### Connect to PostgreSQL
```bash
psql -U certuser -d certificate_verification -h localhost
```

### View Certificates
```sql
SELECT certificate_id, filename, upload_timestamp FROM certificate LIMIT 10;
```

### View Verification Results
```sql
SELECT 
  c.certificate_id,
  vr.verification_status,
  vr.confidence_score
FROM certificate c
JOIN verification_result vr ON c.id = vr.certificate_id;
```

### View Audit Log
```sql
SELECT * FROM verification_log ORDER BY timestamp DESC LIMIT 20;
```

### Database Statistics
```sql
SELECT 
  verification_status,
  COUNT(*) as count,
  ROUND(AVG(confidence_score), 2) as avg_score
FROM verification_result
GROUP BY verification_status;
```

---

## 🐳 Docker Quick Reference

### Start Services
```bash
docker-compose up -d
```

### Check Status
```bash
docker-compose ps
```

### View Logs
```bash
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Stop Services
```bash
docker-compose down
```

### Remove Data (Clean Reset)
```bash
docker-compose down -v
```

### Rebuild Image
```bash
docker-compose build --no-cache
```

### Access PostgreSQL Container
```bash
docker-compose exec postgres psql -U certuser -d certificate_verification
```

### Restart Single Service
```bash
docker-compose restart api
```

---

## 🔧 Configuration Quick Reference

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Security
REQUESTS_PER_MINUTE=100
MAX_FILE_SIZE_MB=100

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com

# OCR
TESSERACT_PATH=/usr/bin/tesseract  # Linux/Mac
# TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe  # Windows

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Optional Services
REDIS_URL=redis://localhost:6379/0

# Features
ENABLE_OCR_PREPROCESSING=True
ENABLE_FUZZY_MATCHING=True
ENABLE_RATE_LIMITING=True
```

### File Size Limits
```python
# In utils/config.py
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
```

### Rate Limiting
```python
# In utils/config.py
REQUESTS_PER_MINUTE = 100  # Per client IP
```

### Verification Thresholds
```python
# In services/intelligent_verification.py
VERIFIED_THRESHOLD = 85.0              # ≥85%
PARTIALLY_VERIFIED_THRESHOLD = 60.0    # 60-84%
                                       # <60%: NOT_VERIFIED
```

### Fuzzy Matching Weights
```python
# In services/intelligent_verification.py
WEIGHTS = {
    "person_name": 0.40,           # 40%
    "organization": 0.30,          # 30%
    "certificate_title": 0.20,     # 20%
    "issue_date": 0.10             # 10%
}
```

---

## 🐛 Troubleshooting Quick Guide

### Port Already In Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9  # Linux/Mac

# Or use different port in .env
PORT=8001
```

### Database Connection Error
```bash
# Check PostgreSQL is running
psql -U postgres -l

# Check connection string
echo $DATABASE_URL

# Verify user exists
psql -U postgres -c "SELECT * FROM pg_user WHERE usename = 'certuser';"
```

### Tesseract Not Found
```bash
# Linux
sudo apt-get install tesseract-ocr

# Mac
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki

# Update .env with correct path
```

### spaCy Model Not Found
```bash
python -m spacy download en_core_web_sm
```

### Low Confidence Scores
- Normal! v2 is stricter than v1
- Scores <60% indicate actual mismatches
- Check uploaded document quality
- Try adjusting weights in `intelligent_verification.py`

### Rate Limiting Blocking Requests
```env
# Increase in .env
REQUESTS_PER_MINUTE=500
```

### Docker Container Won't Start
```bash
# Check logs
docker-compose logs api

# Rebuild
docker-compose build --no-cache

# Restart
docker-compose restart api
```

---

## 📊 Performance Tuning

### Database Query Optimization
```python
# Create indexes (automatically done in v2)
CREATE INDEX idx_cert_id ON certificate(certificate_id);
CREATE INDEX idx_verify_status ON verification_result(verification_status);
```

### OCR Preprocessing Optimization
```python
# In ocr/preprocessor.py - adjust parameters:
cv2.bilateralFilter(image, 9, 75, 75)      # Increase kernel for more blur
cv2.adaptiveThreshold(..., blockSize=11)   # Adjust block size
clahe = cv2.createCLAHE(clipLimit=2.0)     # Increase for more contrast
```

### Rate Limiting Adjustment
```env
# Increase for high traffic
REQUESTS_PER_MINUTE=1000

# Or implement in routes_v2.py:
rate_limiter.is_allowed(client_ip)
```

---

## 📚 Key File Locations

| File | Purpose | Edit For |
|------|---------|----------|
| main.py | Application entry point | Server config |
| .env | Environment variables | Credentials, paths |
| api/routes_v2.py | REST endpoints | API behavior |
| services/intelligent_verification.py | Fuzzy matching | Weights, thresholds |
| ocr/preprocessor.py | Image processing | OCR quality |
| services/security_validator.py | File validation | Security rules |
| core/rate_limiting.py | Rate limiting | Limits |
| frontend/index.html | Web UI | UI design |
| database/models_orm.py | Database schema | Table structure |
| docker-compose.yml | Services config | Infrastructure |

---

## 🔄 Common Workflows

### Upload and Verify Certificate
```bash
# 1. Upload
CERT_ID=$(curl -X POST -F "file=@cert.pdf" http://localhost:8000/api/upload | jq -r '.certificate_id')

# 2. Verify
curl -X POST http://localhost:8000/api/verify/$CERT_ID \
  -H "Content-Type: application/json" \
  -d '{"expected_person_name": "John Doe", ...}'
```

### Search and Get Report
```bash
# 1. Search
curl "http://localhost:8000/api/search?status=VERIFIED" | jq '.results[0].certificate_id'

# 2. Get Report
CERT_ID="CERT-001"
curl http://localhost:8000/api/certificate/$CERT_ID/report | jq '.'
```

### Database Backup
```bash
# Backup PostgreSQL
pg_dump -U certuser certificate_verification > backup.sql

# Restore from backup
psql -U certuser certificate_verification < backup.sql
```

---

## 💡 Pro Tips

1. **Use API Documentation**: Visit http://localhost:8000/docs for interactive testing
2. **Check Logs**: `tail -f logs/app.log` for real-time debugging
3. **Monitor Database**: Use `docker-compose logs postgres` to monitor DB
4. **Test Rate Limits**: `ab -n 150 http://localhost:8000/api/health` (test with 150 requests)
5. **Batch Operations**: Use search endpoint for bulk certificate operations
6. **Leverage Caching**: Redis automatically caches frequently accessed certificates
7. **Monitor Performance**: Check average response times in logs

---

## 📞 Support Resources

- **Setup Issues**: Run `python setup_v2.py` with verbose output
- **API Issues**: Check `http://localhost:8000/docs`
- **Database Issues**: Review `logs/app.log`
- **Docker Issues**: Run `docker-compose logs`
- **Upgrade Issues**: See `MIGRATION_GUIDE.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **Checklist**: See `CHECKLIST.md`

---

## ✨ Quick Commands Cheat Sheet

```bash
# Setup & Start
python setup_v2.py && python main.py
docker-compose up -d

# Testing
curl http://localhost:8000/api/health
curl -X POST -F "file=@cert.pdf" http://localhost:8000/api/upload
curl http://localhost:8000/api/stats

# Database
psql -U certuser -d certificate_verification
docker-compose exec postgres psql -U certuser -d certificate_verification

# Docker
docker-compose ps
docker-compose logs -f api
docker-compose down

# Logs
tail -f logs/app.log
grep "VERIFIED" logs/app.log

# Configuration
cat .env
cat requirements.txt
```

---

**Certificate Verification System v2** | Quick Reference v1.0 | 2024
