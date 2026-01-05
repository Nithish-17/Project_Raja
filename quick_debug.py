"""
Quick debug of the most recent certificate
"""
from pathlib import Path
from ocr.ocr_service import ocr_service
from ner.ner_service import ner_service

# Test with an older valid certificate
pdf_path = Path('uploads/CERT-20260103-585CF992.pdf')  # This one worked before

print("=" * 70)
print(f"DEBUGGING: {pdf_path.name}")
print("=" * 70)

# Extract text
print("\nExtracting text with OCR...")
text = ocr_service.extract_text(str(pdf_path), 'application/pdf')

print(f"\nExtracted Text ({len(text)} characters):")
print("-" * 70)
print(text[:1000])  # Show first 1000 characters
print("-" * 70)

# Extract entities
print("\nExtracting entities...")
entities = ner_service.extract_entities(text)

print("\nExtracted Entities:")
print("-" * 70)
print(f"Person Name:        {entities.get('person_name') or 'N/A'}")
print(f"Organization:       {entities.get('organization') or 'N/A'}")
print(f"Certificate Title:  {entities.get('certificate_title') or 'N/A'}")
print(f"Issue Date:         {entities.get('issue_date') or 'N/A'}")
print("=" * 70)
