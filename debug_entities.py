"""
Debug script to check OCR extraction and entity detection
"""
from pathlib import Path
from ocr.ocr_service import ocr_service
from ner.ner_service import ner_service

def debug_certificate(pdf_path):
    """Debug a specific certificate"""
    print("=" * 70)
    print(f"DEBUGGING: {pdf_path.name}")
    print("=" * 70)
    
    # Extract text
    print("\n1. Extracting text with OCR...")
    text = ocr_service.extract_text(str(pdf_path), 'application/pdf')
    
    print(f"\n2. Extracted Text ({len(text)} characters):")
    print("-" * 70)
    print(text)
    print("-" * 70)
    
    # Extract entities
    print("\n3. Extracting entities...")
    entities = ner_service.extract_entities(text)
    
    print("\n4. Extracted Entities:")
    print("-" * 70)
    print(f"Person Name:        {entities.get('person_name') or 'N/A'}")
    print(f"Organization:       {entities.get('organization') or 'N/A'}")
    print(f"Certificate Title:  {entities.get('certificate_title') or 'N/A'}")
    print(f"Issue Date:         {entities.get('issue_date') or 'N/A'}")
    print("-" * 70)
    
    # Debug text lines
    print("\n5. Text Lines for Analysis:")
    print("-" * 70)
    lines = text.split('\n')
    for i, line in enumerate(lines[:20], 1):  # Show first 20 lines
        if line.strip():
            print(f"{i:2d}. {line.strip()}")
    print("-" * 70)


if __name__ == "__main__":
    # Test on recent uploaded files
    upload_dir = Path('uploads')
    pdf_files = sorted(list(upload_dir.glob('CERT-*.pdf')))
    
    if not pdf_files:
        print("No PDF files found")
    else:
        # Test on 3 most recent files
        print(f"Found {len(pdf_files)} files. Testing 3 most recent:\n")
        for pdf in pdf_files[-3:]:
            debug_certificate(pdf)
            print("\n\n")
