"""
Certificate verification service
Coordinates OCR, NER, and verification processes
"""
from typing import Dict, Any, Optional
from datetime import datetime

from ocr import ocr_service
from ner import ner_service
from database import db
from services.email_service import email_service
from utils import get_logger


logger = get_logger("verification_service")


class VerificationService:
    """Service for certificate verification workflow"""
    
    def __init__(self):
        """Initialize verification service"""
        logger.info("Verification service initialized")
    
    async def process_certificate(
        self,
        certificate_id: str,
        file_path: str,
        file_type: str,
        filename: str
    ) -> Dict[str, Any]:
        """
        Process certificate: extract text, extract entities, store in DB
        
        Args:
            certificate_id: Unique certificate ID
            file_path: Path to uploaded file
            file_type: MIME type of file
            filename: Original filename
            
        Returns:
            Dictionary with certificate data
        """
        try:
            # Step 1: Extract text using OCR
            logger.info(f"Extracting text from {filename}")
            extracted_text = ocr_service.extract_text(file_path, file_type)
            
            # Step 2: Extract entities using NER
            logger.info(f"Extracting entities from {filename}")
            entities = ner_service.extract_entities(extracted_text)
            
            # Step 3: Store in database
            certificate_data = {
                "certificate_id": certificate_id,
                "filename": filename,
                "file_path": file_path,
                "file_type": file_type,
                "upload_timestamp": datetime.now(),
                "extracted_text": extracted_text,
                "entities": entities,
                "verification_status": None,
                "verified_timestamp": None
            }
            
            db.add_certificate(certificate_id, certificate_data)
            logger.info(f"Certificate {certificate_id} processed and stored")
            
            return certificate_data
            
        except Exception as e:
            logger.error(f"Error processing certificate {certificate_id}: {str(e)}")
            raise
    
    async def verify_certificate(self, certificate_id: str) -> Dict[str, Any]:
        """
        Verify certificate against dummy database
        
        Args:
            certificate_id: Certificate ID to verify
            
        Returns:
            Dictionary with verification results
        """
        try:
            # Get certificate from database
            certificate = db.get_certificate(certificate_id)
            if not certificate:
                raise ValueError(f"Certificate {certificate_id} not found")
            
            # Get entities
            entities = certificate.get("entities", {})
            
            # Verify against dummy database
            logger.info(f"Verifying certificate {certificate_id}")
            verification_status = db.verify_certificate(entities)
            
            # Update certificate with verification status
            db.update_certificate_verification(
                certificate_id,
                verification_status,
                entities
            )
            
            # Update timestamp
            certificate["verification_status"] = verification_status
            certificate["verified_timestamp"] = datetime.now()
            
            # Send email alert
            logger.info(f"Sending verification alert for {certificate_id}")
            email_sent = email_service.send_verification_alert(
                certificate_id,
                entities,
                verification_status
            )
            
            result = {
                "certificate_id": certificate_id,
                "verification_status": verification_status,
                "entities": entities,
                "verified_timestamp": certificate["verified_timestamp"],
                "email_sent": email_sent
            }
            
            logger.info(f"Certificate {certificate_id} verified: {verification_status}")
            return result
            
        except Exception as e:
            logger.error(f"Error verifying certificate {certificate_id}: {str(e)}")
            raise


# Global verification service instance
verification_service = VerificationService()
