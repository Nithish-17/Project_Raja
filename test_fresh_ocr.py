"""
Fresh test with module reload to detect Tesseract
"""
import sys
import importlib
from pathlib import Path

# Remove cached modules
for module in list(sys.modules.keys()):
    if 'ocr' in module or 'ner' in module:
        del sys.modules[module]

print("=" * 70)
print("FRESH TEST - REAL OCR WITH TESSERACT")
print("=" * 70)

# Now import fresh
from ocr.ocr_service import ocr_service, TESSERACT_AVAILABLE
from ner.ner_service import ner_service

print(f"\n✅ Tesseract Available: {TESSERACT_AVAILABLE}")

if not TESSERACT_AVAILABLE:
    print("\n❌ Tesseract still not detected!")
    print("Please restart your Python terminal/IDE to refresh the environment.")
    sys.exit(1)

print("\n" + "-" * 70)
print("Testing on image-based PDF...")
print("-" * 70)

pdf_file = Path('uploads/CERT-20260103-26CFDE3C.pdf')

if not pdf_file.exists():
    print(f"❌ File not found: {pdf_file}")
    sys.exit(1)

print(f"\nFile: {pdf_file.name}")

# Extract text
text = ocr_service.extract_text(str(pdf_file), 'application/pdf')

if not text:
    print("❌ No text extracted")
    sys.exit(1)

print(f"\n✅ Extracted {len(text)} characters")
print("\nText preview:")
print("-" * 70)
print(text[:400])
print("-" * 70)

# Extract entities  
entities = ner_service.extract_entities(text)

print("\n" + "=" * 70)
print("EXTRACTED ENTITIES:")
print("=" * 70)
print(f"Person Name:        {entities.get('person_name')}")
print(f"Organization:       {entities.get('organization')}")
print(f"Certificate Title:  {entities.get('certificate_title')}")
print(f"Issue Date:         {entities.get('issue_date')}")
print("=" * 70)

print("\n✅ REAL OCR IS NOW WORKING!")
print("You can now upload certificates and get real entity extraction!")
print("=" * 70)
