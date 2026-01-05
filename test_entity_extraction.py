"""
Test script to verify entity extraction for "John David Smith" and "Tech Innovation Foundation"
"""
from ocr.ocr_service import ocr_service
from ner.ner_service import ner_service

def test_mock_extraction():
    """Test entity extraction using mock OCR"""
    print("=" * 70)
    print("Testing Entity Extraction with Mock OCR")
    print("=" * 70)
    
    # Get mock OCR text (what all files currently return without Tesseract)
    text = ocr_service._mock_ocr_image(None, 'test.pdf')
    
    print("\nOCR Extracted Text:")
    print("-" * 70)
    print(text)
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
    
    # Verify expected values
    print("\n" + "=" * 70)
    print("VERIFICATION RESULTS:")
    print("=" * 70)
    
    expected_person = "John David Smith"
    expected_org = "Tech Innovation Foundation"
    
    person_match = entities.get('person_name') == expected_person
    org_match = entities.get('organization') == expected_org
    
    print(f"✓ Person Name matches '{expected_person}': {person_match}")
    print(f"✓ Organization matches '{expected_org}': {org_match}")
    
    if person_match and org_match:
        print("\n✅ SUCCESS: All entities extracted correctly!")
    else:
        print("\n❌ FAILED: Some entities don't match expected values")
        if not person_match:
            print(f"   Expected person: '{expected_person}'")
            print(f"   Got: '{entities.get('person_name')}'")
        if not org_match:
            print(f"   Expected org: '{expected_org}'")
            print(f"   Got: '{entities.get('organization')}'")
    
    print("=" * 70)
    
    return person_match and org_match


if __name__ == "__main__":
    test_mock_extraction()
