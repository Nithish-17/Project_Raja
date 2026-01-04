"""
Test script for the new hybrid NER service
Validates rule-based extraction and spaCy fallback
"""
import sys
from ner.ner_service import NERService, CertificateTextPreprocessor, RuleBasedEntityExtractor


def test_preprocessor():
    """Test text preprocessing"""
    print("=" * 60)
    print("Testing CertificateTextPreprocessor")
    print("=" * 60)
    
    raw_text = """
    
    This is to certify that   John    Doe
    
    has successfully completed the course
    
    Machine Learning Specialization
    
    
    offered by   Coursera
    
    Issued on: January 15, 2024
    """
    
    cleaned = CertificateTextPreprocessor.preprocess(raw_text)
    lines = CertificateTextPreprocessor.get_lines(raw_text)
    
    print(f"Original text lines: {len(raw_text.split(chr(10)))}")
    print(f"Cleaned text lines: {len(cleaned.split(chr(10)))}")
    print(f"Extracted lines: {len(lines)}")
    print(f"\nCleaned lines:")
    for i, line in enumerate(lines, 1):
        print(f"  {i}. {line}")
    print()


def test_rule_based_extraction():
    """Test rule-based entity extraction"""
    print("=" * 60)
    print("Testing RuleBasedEntityExtractor")
    print("=" * 60)
    
    sample_cert = """
    CERTIFICATE OF ACHIEVEMENT
    
    This is to certify that Sarah Johnson
    
    has successfully completed
    
    Advanced Python Programming
    
    offered by Coursera
    
    Issued on: June 20, 2023
    
    Certificate Number: CERT-2023-001
    """
    
    lines = CertificateTextPreprocessor.get_lines(sample_cert)
    
    # Test person name extraction
    person, person_method = RuleBasedEntityExtractor.extract_person_name(sample_cert, lines)
    print(f"Person Name: {person} (method: {person_method})")
    
    # Test organization extraction
    org, org_method = RuleBasedEntityExtractor.extract_organization(sample_cert, lines)
    print(f"Organization: {org} (method: {org_method})")
    
    # Test certificate title extraction
    title, title_method = RuleBasedEntityExtractor.extract_certificate_title(sample_cert, lines)
    print(f"Certificate Title: {title} (method: {title_method})")
    
    # Test date extraction
    date, date_method = RuleBasedEntityExtractor.extract_issue_date(sample_cert)
    print(f"Issue Date: {date} (method: {date_method})")
    print()


def test_full_ner_service():
    """Test full NER service with hybrid approach"""
    print("=" * 60)
    print("Testing Full NER Service (Hybrid Approach)")
    print("=" * 60)
    
    ner_service = NERService()
    
    test_cases = [
        {
            "name": "Standard Certificate",
            "text": """
            CERTIFICATE OF COMPLETION
            
            This is to certify that Michael Chen
            
            has successfully completed
            
            Data Science Specialization
            
            awarded by edX
            
            Issued on: September 10, 2023
            
            Registration Number: EDX-2023-12345
            """
        },
        {
            "name": "Minimal Information",
            "text": """
            To: Jane Smith
            
            Completion Certificate
            
            From: Udemy
            
            Date: 2024-01-15
            """
        },
        {
            "name": "Complex Layout",
            "text": """
            CERTIFICATE OF ACHIEVEMENT
            
            This certifies that Dr. Robert Williams
            
            has completed the program in
            
            Cloud Architecture Fundamentals
            
            by Amazon Web Services
            
            dated 15th December 2023
            """
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        print("-" * 40)
        
        entities = ner_service.extract_entities(test_case['text'])
        
        for key, value in entities.items():
            status = "✓" if value else "✗"
            print(f"  {status} {key}: {value}")
    
    print()


if __name__ == "__main__":
    try:
        test_preprocessor()
        test_rule_based_extraction()
        test_full_ner_service()
        print("=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error during testing: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
