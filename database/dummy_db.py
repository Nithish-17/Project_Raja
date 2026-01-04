"""
Dummy database for certificate verification
Contains sample valid certificates for cross-verification
"""
from typing import List, Dict, Any, Optional

# Dummy database containing valid certificates
VALID_CERTIFICATES = [
    {
        "person_name": "John Smith",
        "organization": "Stanford University",
        "certificate_name": "Machine Learning Specialization",
        "date_of_issue": "2023-06-15",
        "registration_number": "ML-2023-001234"
    },
    {
        "person_name": "Jane Doe",
        "organization": "MIT",
        "certificate_name": "Data Science Certificate",
        "date_of_issue": "2023-08-20",
        "registration_number": "DS-2023-005678"
    },
    {
        "person_name": "Alice Johnson",
        "organization": "Harvard University",
        "certificate_name": "Python Programming Certificate",
        "date_of_issue": "2023-09-10",
        "registration_number": "PY-2023-009012"
    },
    {
        "person_name": "Bob Williams",
        "organization": "Google",
        "certificate_name": "Cloud Architecture Certificate",
        "date_of_issue": "2023-07-25",
        "registration_number": "GCP-2023-003456"
    },
    {
        "person_name": "Carol Martinez",
        "organization": "IBM",
        "certificate_name": "AI Engineering Certificate",
        "date_of_issue": "2023-10-05",
        "registration_number": "AI-2023-007890"
    },
]


class DummyDatabase:
    """Dummy database for certificate verification"""
    
    def __init__(self):
        """Initialize the dummy database"""
        self.certificates = VALID_CERTIFICATES
        self.uploaded_certificates: Dict[str, Any] = {}
    
    def add_certificate(self, certificate_id: str, certificate_data: Dict[str, Any]) -> None:
        """Add a certificate to the database"""
        self.uploaded_certificates[certificate_id] = certificate_data
    
    def get_certificate(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        """Get a certificate by ID"""
        return self.uploaded_certificates.get(certificate_id)
    
    def verify_certificate(self, entities: Dict[str, Any]) -> str:
        """
        Verify certificate against valid certificates in the database
        Returns: VERIFIED, PARTIALLY VERIFIED, or NOT VERIFIED
        """
        if not entities:
            return "NOT VERIFIED"
        
        # Count matching fields
        max_matches = 0
        total_fields = 5  # person_name, organization, certificate_name, date_of_issue, registration_number
        
        for valid_cert in self.certificates:
            matches = 0
            
            # Compare each field (case-insensitive)
            for field in ["person_name", "organization", "certificate_name", "date_of_issue", "registration_number"]:
                entity_value = entities.get(field, "").lower().strip()
                valid_value = valid_cert.get(field, "").lower().strip()
                
                if entity_value and valid_value:
                    # Check for exact match or partial match
                    if entity_value == valid_value or entity_value in valid_value or valid_value in entity_value:
                        matches += 1
            
            max_matches = max(max_matches, matches)
        
        # Determine verification status based on matches
        if max_matches >= 4:
            return "VERIFIED"
        elif max_matches >= 2:
            return "PARTIALLY VERIFIED"
        else:
            return "NOT VERIFIED"
    
    def update_certificate_verification(
        self, 
        certificate_id: str, 
        verification_status: str,
        entities: Dict[str, Any]
    ) -> None:
        """Update certificate verification status"""
        if certificate_id in self.uploaded_certificates:
            self.uploaded_certificates[certificate_id]["verification_status"] = verification_status
            self.uploaded_certificates[certificate_id]["entities"] = entities


# Global database instance
db = DummyDatabase()
