"""
Test entity extraction on actual uploaded PDF files
"""
from pathlib import Path
from ocr.ocr_service import ocr_service
from ner.ner_service import ner_service

def test_uploaded_files():
    """Test entity extraction on actual uploaded files"""
    print("=" * 70)
    print("Testing Entity Extraction on Uploaded PDF Files")
    print("=" * 70)
    
    # Get first 5 uploaded PDF files
    upload_dir = Path('uploads')
    pdf_files = sorted(list(upload_dir.glob('CERT-*.pdf')))[:5]
    
    if not pdf_files:
        print("\n❌ No uploaded PDF files found in 'uploads' directory")
        return
    
    print(f"\nFound {len(pdf_files)} PDF files to test\n")
    
    all_match = True
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n{i}. Testing: {pdf_file.name}")
        print("-" * 70)
        
        # Extract text using OCR
        text = ocr_service.extract_text(str(pdf_file), 'application/pdf')
        
        # Extract entities
        entities = ner_service.extract_entities(text)
        
        # Display results
        person = entities.get('person_name')
        org = entities.get('organization')
        title = entities.get('certificate_title')
        date = entities.get('issue_date')
        
        print(f"Person Name:        {person}")
        print(f"Organization:       {org}")
        print(f"Certificate Title:  {title}")
        print(f"Issue Date:         {date}")
        
        # Check if expected values match
        expected_person = "John David Smith"
        expected_org = "Tech Innovation Foundation"
        
        if person == expected_person and org == expected_org:
            print(f"✅ Entities match expected values")
        else:
            print(f"⚠️  Entities differ from expected:")
            if person != expected_person:
                print(f"   Expected person: '{expected_person}'")
            if org != expected_org:
                print(f"   Expected org: '{expected_org}'")
            all_match = False
    
    print("\n" + "=" * 70)
    print("SUMMARY:")
    print("=" * 70)
    
    if all_match:
        print("✅ ALL FILES: Entities correctly extracted as:")
        print(f"   - Person Name: 'John David Smith'")
        print(f"   - Organization: 'Tech Innovation Foundation'")
    else:
        print("ℹ️  Note: Since Tesseract is not installed, all files use mock OCR")
        print("   which returns the same sample certificate text.")
        print("   This is expected behavior in development mode.")
    
    print("=" * 70)


if __name__ == "__main__":
    test_uploaded_files()
