"""
Verify Tesseract OCR installation and test real extraction
"""
import sys
from pathlib import Path

def verify_tesseract():
    """Verify Tesseract installation"""
    print("=" * 70)
    print("TESSERACT OCR VERIFICATION")
    print("=" * 70)
    
    # Check if Tesseract executable exists
    tesseract_path = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    
    if not tesseract_path.exists():
        print("\n❌ Tesseract NOT found at:", tesseract_path)
        print("\nPlease install Tesseract from:")
        print("https://github.com/UB-Mannheim/tesseract/wiki")
        return False
    
    print(f"\n✅ Tesseract found at: {tesseract_path}")
    
    # Try to get Tesseract version
    try:
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = str(tesseract_path)
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
    except Exception as e:
        print(f"⚠️  Could not verify Tesseract version: {e}")
        return False
    
    # Test OCR service initialization
    try:
        print("\n" + "-" * 70)
        print("Testing OCR Service...")
        print("-" * 70)
        
        from ocr.ocr_service import ocr_service, TESSERACT_AVAILABLE
        
        if TESSERACT_AVAILABLE:
            print("✅ OCR Service initialized with Tesseract support")
            print("✅ REAL OCR is now ACTIVE!")
        else:
            print("❌ OCR Service still using mock mode")
            print("   You may need to restart Python or your IDE")
            return False
        
    except Exception as e:
        print(f"❌ Error initializing OCR service: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("✅ SUCCESS! Tesseract is properly configured")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Upload your certificates through the web interface")
    print("2. Each certificate will now extract its REAL content")
    print("3. No more mock 'John David Smith' data!")
    print("=" * 70)
    
    return True


def test_real_extraction():
    """Test real extraction on uploaded PDFs"""
    print("\n\n" + "=" * 70)
    print("TESTING REAL OCR ON UPLOADED FILES")
    print("=" * 70)
    
    try:
        from ocr.ocr_service import ocr_service
        from ner.ner_service import ner_service
        
        upload_dir = Path('uploads')
        pdf_files = sorted(list(upload_dir.glob('CERT-*.pdf')))[:3]
        
        if not pdf_files:
            print("\n⚠️  No PDF files found in uploads directory")
            print("Upload some certificates to test real OCR extraction")
            return
        
        print(f"\nTesting OCR on {len(pdf_files)} files...\n")
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"{i}. File: {pdf_file.name}")
            print("-" * 70)
            
            # Extract text using REAL OCR
            text = ocr_service.extract_text(str(pdf_file), 'application/pdf')
            
            if text:
                # Show first 200 characters of extracted text
                preview = text[:200].replace('\n', ' ')
                print(f"Extracted text preview: {preview}...")
                
                # Extract entities
                entities = ner_service.extract_entities(text)
                print(f"\nExtracted Entities:")
                print(f"  Person:       {entities.get('person_name')}")
                print(f"  Organization: {entities.get('organization')}")
                print(f"  Title:        {entities.get('certificate_title')}")
                print(f"  Date:         {entities.get('issue_date')}")
            else:
                print("⚠️  No text extracted")
            
            print()
        
        print("=" * 70)
        print("✅ Real OCR test complete!")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if verify_tesseract():
        # Ask if user wants to test real extraction
        print("\n")
        response = input("Would you like to test real OCR on uploaded files? (y/n): ")
        if response.lower() == 'y':
            test_real_extraction()
    else:
        print("\n⚠️  Please install Tesseract and run this script again")
        sys.exit(1)
