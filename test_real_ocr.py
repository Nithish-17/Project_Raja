"""
Test REAL OCR extraction on image-based PDFs
"""
from pathlib import Path
from ocr.ocr_service import ocr_service
from ner.ner_service import ner_service

def test_image_pdf():
    """Test real OCR on an image-based PDF"""
    print("=" * 70)
    print("TESTING REAL OCR ON IMAGE-BASED PDF")
    print("=" * 70)
    
    # Test on the image-based PDF
    pdf_file = Path('uploads/CERT-20260103-26CFDE3C.pdf')
    
    if not pdf_file.exists():
        print(f"\n❌ File not found: {pdf_file}")
        return
    
    print(f"\nFile: {pdf_file.name}")
    print("-" * 70)
    
    # Extract text using REAL OCR
    print("Extracting text with Tesseract OCR...")
    text = ocr_service.extract_text(str(pdf_file), 'application/pdf')
    
    if not text:
        print("❌ No text extracted")
        return
    
    print(f"\n✅ Extracted {len(text)} characters from PDF")
    print("\nText preview (first 500 characters):")
    print("-" * 70)
    print(text[:500])
    print("-" * 70)
    
    # Extract entities
    print("\nExtracting entities...")
    entities = ner_service.extract_entities(text)
    
    print("\n" + "=" * 70)
    print("EXTRACTED ENTITIES:")
    print("=" * 70)
    print(f"Person Name:        {entities.get('person_name')}")
    print(f"Organization:       {entities.get('organization')}")
    print(f"Certificate Title:  {entities.get('certificate_title')}")
    print(f"Issue Date:         {entities.get('issue_date')}")
    print("=" * 70)
    
    # Check if it's different from mock data
    if entities.get('person_name') != "John David Smith":
        print("\n✅ SUCCESS! Extracting REAL data (not mock data)")
    elif "John David Smith" in text:
        print("\n✅ This PDF actually contains 'John David Smith'")
    else:
        print("\n⚠️  Still showing mock data - check OCR extraction")
    
    print("=" * 70)


if __name__ == "__main__":
    test_image_pdf()
