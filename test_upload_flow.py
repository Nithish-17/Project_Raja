"""
Simulate uploading a certificate and check extraction
"""
import os
from pathlib import Path
from ocr.ocr_service import ocr_service
from ner.ner_service import ner_service

# Test with a valid text-based PDF that has real content
pdf_path = Path('uploads/CERT-20260103-585CF992.pdf')

if not pdf_path.exists():
    print(f"File not found: {pdf_path}")
    exit(1)

file_size = pdf_path.stat().st_size
print(f"File: {pdf_path.name}")
print(f"File Size: {file_size} bytes")

if file_size == 0:
    print("❌ File is empty!")
    exit(1)

print("\n" + "=" * 70)
print("SIMULATING CERTIFICATE UPLOAD AND PROCESSING")
print("=" * 70)

# Step 1: Extract text
print("\n1. Extracting text with OCR...")
extracted_text = ocr_service.extract_text(str(pdf_path), 'application/pdf')

print(f"   ✓ Extracted {len(extracted_text)} characters")

# Step 2: Extract entities
print("\n2. Extracting entities with NER...")
entities = ner_service.extract_entities(extracted_text)

print("\n" + "=" * 70)
print("EXTRACTED ENTITIES")
print("=" * 70)

person_name = entities.get('person_name')
organization = entities.get('organization')
certificate_title = entities.get('certificate_title')
issue_date = entities.get('issue_date')

print(f"Person Name:        {person_name or 'N/A'}")
print(f"Organization:       {organization or 'N/A'}")
print(f"Certificate Title:  {certificate_title or 'N/A'}")
print(f"Issue Date:         {issue_date or 'N/A'}")

print("=" * 70)

# Check extraction
if person_name or organization:
    print("\n✅ Entities extracted successfully!")
    print("Try uploading your certificate through the web interface now.")
else:
    print("\n⚠️  No entities found. The PDF might not contain certificate-like content.")
    print("Try uploading a different certificate file.")

print("=" * 70)
