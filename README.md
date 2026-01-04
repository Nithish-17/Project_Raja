🧱 1. High-Level Architecture (Big Picture)
Client / UI
   ↓
FastAPI Routes
   ↓
Verification Orchestration
   ↓
OCR → NER → Verification
   ↓
Database + Email + Logs


Everything is modular, config-driven, and locally executed.

⚙️ 2. Tech Stack (Organized by Responsibility)
🔹 Backend / API Layer

FastAPI + Uvicorn

Entry point: main.py

Routing:

routes.py → basic APIs

routes_v2.py → advanced & secured APIs

Provides:

Upload

Verify

Reports

Search

Stats

Health check

👉 FastAPI is chosen for speed, async support, and Swagger UI.

🔹 OCR Layer (Local, Offline)

Tesseract OCR via Python wrappers

Files:

ocr_service.py

preprocessor.py

Flow:

File → Text extraction → OCR fallback → Cleaned text


Tools used:

pytesseract → wrapper

Pillow → image handling

pdf2image → scanned PDFs

PyPDF2 → digital PDFs

OpenCV (optional) → denoise, threshold, deskew

👉 No external API, fully offline OCR.

🔹 NER Layer (Hybrid Intelligence)

Rule-Based + spaCy

File:

ner_service.py

Approach:

Rule-based extraction (primary)

Line after “certify that” → Person

ALL CAPS with keywords → Certificate Title

Line after “issued by” → Organization

Lines with Date → Issue Date

spaCy fallback

Used only if rules fail

👉 This avoids generic NLP mistakes on certificates.

🔹 Verification Engine (Intelligent Matching)

Fuzzy Logic + Weighted Scoring

Files:

intelligent_verification.py

verification_service.py

Responsibilities:

Compare extracted entities with known records

Use fuzzy matching (Levenshtein / fuzzywuzzy)

Assign weights:

Name → highest

Organization

Title

Date

Compute:

Confidence score

Mismatch reasons

👉 This is decision logic, not ML training.

🔹 Data Layer (Persistence)

SQLAlchemy + PostgreSQL / SQLite

Files:

models_orm.py

connection.py

database/db.py

config.py

Stores:

Certificates

Extracted entities (JSON)

Verification results

Logs / audit trail

Configured via:

DATABASE_URL=postgresql://...


👉 ORM allows DB portability and clean schema management.

🔹 Security & Rate Limiting

Defensive backend design

Files:

security_validator.py

rate_limiting.py

Features:

File type allowlist

Magic-byte verification

Dangerous extension blocking

Filename sanitization

Per-IP request throttling (slowapi)

👉 Prevents upload abuse & DoS-style attacks.

🔹 Messaging / Async (Optional, Scalable)

Celery + Redis hooks

Files:

celery_app.py

Used for:

Background email sending

Future async processing

👉 Included for scalability, not mandatory for core flow.

🔹 Email Notifications

SMTP-based alerts

File:

email_service.py

Triggers:

After verification

Includes:

Certificate ID

Result

Confidence

Mismatch details

Configured via .env.

🔹 Logging & Utilities

Observability & performance

Files:

logger.py

cache.py

Features:

Structured logging (JSON/structlog)

Caching helpers

Debug & audit visibility

🧩 3. Core Module Responsibilities (Clean Mapping)
Module	Responsibility
routes.py	Basic API endpoints
routes_v2.py	Advanced APIs + security
upload_service.py	File storage + certificate ID
ocr_service.py	Text extraction
preprocessor.py	OCR quality boost
ner_service.py	Hybrid entity extraction
verification_service.py	End-to-end orchestration
intelligent_verification.py	Fuzzy scoring logic
security_validator.py	File safety
rate_limiting.py	Abuse prevention
email_service.py	Alerts
models_orm.py	DB schema
config.py	Environment config
🔄 4. End-to-End Execution Flow (Very Important)
Upload File
   ↓
Security Validation
   ↓
OCR (text → image OCR fallback)
   ↓
Preprocessing (optional)
   ↓
Hybrid NER
   ↓
Database Storage
   ↓
Intelligent Verification
   ↓
Confidence Score + Mismatch
   ↓
Email Alert
   ↓
API Response
