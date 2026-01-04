# Migration Guide: v1 to v2

This guide helps you upgrade from Certificate Verification System v1 to v2.

## What's New in v2

### Architecture Changes
- **v1**: In-memory/SQLite database → **v2**: PostgreSQL ORM
- **v1**: Simple exact matching → **v2**: Fuzzy matching with confidence scoring
- **v1**: Basic OCR → **v2**: Advanced preprocessing and quality assessment
- **v1**: No rate limiting → **v2**: Built-in rate limiting
- **v1**: Simple UI → **v2**: Modern responsive dashboard

### Breaking Changes

#### 1. Environment Variables
```bash
# v1 didn't use database_url
# v2 requires:
DATABASE_URL=postgresql://user:pass@localhost:5432/cert_db
```

#### 2. Verification Response
```python
# v1 Response
{
    "verification_status": "VERIFIED",
    "entities": {...}
}

# v2 Response
{
    "verification_status": "VERIFIED",
    "confidence_score": 92.5,
    "field_scores": {
        "person_name": 95.0,
        "organization": 90.0,
        "certificate_title": 85.0,
        "issue_date": 95.0
    },
    "mismatches": {...}
}
```

#### 3. Database Location
- **v1**: `data/certificates.db` (SQLite) or in-memory
- **v2**: PostgreSQL server

## Migration Steps

### Step 1: Backup v1 Data
```bash
# Backup SQLite database if using it
cp data/certificates.db data/certificates.db.backup
```

### Step 2: Install New Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 3: Setup PostgreSQL
```bash
# Create database
psql -U postgres
CREATE DATABASE certificate_verification;
CREATE USER certuser WITH PASSWORD 'certpassword';
GRANT ALL PRIVILEGES ON DATABASE certificate_verification TO certuser;
\q

# Test connection
psql -U certuser -d certificate_verification -h localhost
```

### Step 4: Update Configuration
```bash
# Copy and edit .env
cp .env.example .env

# Required changes:
# DATABASE_URL=postgresql://certuser:certpassword@localhost:5432/certificate_verification
# REQUESTS_PER_MINUTE=100
# MAX_FILE_SIZE_MB=100
```

### Step 5: Migrate Data (Optional)
```bash
# Create Python script to migrate from v1 to v2
python scripts/migrate_v1_to_v2.py
```

### Step 6: Run v2
```bash
python main.py
```

## API Changes

### Endpoint Modifications

#### Verify Endpoint
```bash
# v1
POST /api/verify/{id}
Response: {verification_status, entities}

# v2
POST /api/verify/{id}
Response: {
    verification_status,
    confidence_score,
    field_scores,
    mismatches,
    matched_record
}
```

#### New Endpoints in v2
```bash
GET /api/certificate/{id}/report           # Comprehensive report
GET /api/search?status=VERIFIED&...        # Advanced search
GET /api/stats                              # System statistics
GET /api/health                             # Health check
```

## File Locations

### v1 Structure
```
uploads/                          # Uploaded files
data/certificates.db             # SQLite database
logs/app.log                      # Logs
```

### v2 Structure
```
uploads/                          # Uploaded files (unchanged)
data/                            # New: Database connection config
logs/                            # Logs (unchanged)
frontend/                        # New: Modern UI
database/                        # New: ORM models
services/intelligent_verification.py  # New: Fuzzy matching
ocr/preprocessor.py              # New: OCR enhancement
```

## Verification Status Changes

The verification status values remain the same but with improved accuracy:

| Status | Meaning |
|--------|---------|
| VERIFIED | ≥85% confidence (was exact match) |
| PARTIALLY_VERIFIED | 60-84% confidence (new) |
| NOT_VERIFIED | <60% confidence (was no match) |

## Database Migration Script

```python
# scripts/migrate_v1_to_v2.py
from sqlalchemy.orm import sessionmaker
from database.models_orm import Certificate, ExtractedEntity
from database.connection import db_manager
import sqlite3
from pathlib import Path

def migrate_from_sqlite():
    """Migrate data from SQLite to PostgreSQL"""
    
    # Connect to old SQLite database
    sqlite_path = Path("data/certificates.db.backup")
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_cursor = sqlite_conn.cursor()
    
    # Get all certificates
    sqlite_cursor.execute("SELECT * FROM certificates")
    certificates = sqlite_cursor.fetchall()
    
    # Create PostgreSQL session
    Session = sessionmaker(bind=db_manager.engine)
    session = Session()
    
    # Migrate data
    for cert in certificates:
        new_cert = Certificate(
            certificate_id=cert[0],
            filename=cert[1],
            file_path=cert[2],
            file_type=cert[3],
            extracted_text=cert[5],
            ocr_confidence=0.0  # Not available in v1
        )
        session.add(new_cert)
    
    session.commit()
    session.close()
    sqlite_conn.close()
    print(f"Migrated {len(certificates)} certificates")

if __name__ == "__main__":
    migrate_from_sqlite()
```

## Rollback Plan

If you need to rollback to v1:

1. **Stop v2 application**
```bash
pkill -f "python main.py"
```

2. **Restore v1 files**
```bash
git checkout v1.0.0  # If using git
```

3. **Restore v1 database**
```bash
cp data/certificates.db.backup data/certificates.db
```

4. **Run v1**
```bash
python main.py  # Will use old main.py
```

## Performance Considerations

### v1 vs v2 Performance

| Metric | v1 | v2 |
|--------|----|----|
| Certificate Upload | ~2-5s | ~3-7s (preprocessing) |
| Verification | ~0.5s | ~2-3s (fuzzy matching) |
| Search | Linear scan | Indexed queries |
| Concurrent Users | Limited | ~100+ (with PostgreSQL) |
| Data Persistence | Local | Enterprise-grade |

## Troubleshooting

### PostgreSQL Connection Error
```bash
# Check if PostgreSQL is running
psql -U postgres -l

# Check connection string
echo $DATABASE_URL

# Test connection
psql -d certificate_verification -U certuser
```

### Verification Confidence Scores are Low
- This is normal! v2 uses stricter fuzzy matching
- Scores <60% indicate actual mismatches
- Fine-tune weights in `services/intelligent_verification.py`

### OCR Quality Issues
- Check image preprocessing in `ocr/preprocessor.py`
- Verify tesseract installation: `tesseract --version`
- Try uploading higher-quality images

### Rate Limiting Errors
- Increase `REQUESTS_PER_MINUTE` in `.env`
- Default is 100 req/min per client

## Feature Parity

### v1 Features (All Still Available)
- ✅ Certificate upload
- ✅ OCR text extraction
- ✅ Entity extraction (NER)
- ✅ Email notifications
- ✅ REST API

### New v2 Features
- ✅ Intelligent fuzzy matching
- ✅ Confidence scoring
- ✅ Advanced OCR preprocessing
- ✅ Security hardening
- ✅ Rate limiting
- ✅ PostgreSQL persistence
- ✅ Audit logging
- ✅ Advanced search
- ✅ Statistics dashboard
- ✅ Modern responsive UI
- ✅ Docker support

## Support

For migration issues:
1. Check README_V2.md
2. Review logs in `logs/app.log`
3. Verify PostgreSQL connection
4. Check .env configuration

## Summary

v2 is a significant upgrade with:
- **Better Accuracy**: Fuzzy matching instead of exact matching
- **Enterprise Ready**: PostgreSQL instead of SQLite
- **More Secure**: File validation and rate limiting
- **Better UX**: Modern responsive dashboard
- **Production Ready**: Docker, logging, audit trails

Upgrade recommended for production use! 🚀
