"""
Certificate verification service
Coordinates OCR, NER, and verification processes
"""
from typing import Dict, Any, Optional
from datetime import datetime

from ocr import ocr_service
from ner import ner_service
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
        filename: str,
        file_size: int = 0
    ) -> Dict[str, Any]:
        """
        Process certificate: extract text, extract entities, store in DB
        
        Args:
            certificate_id: Unique certificate ID
            file_path: Path to uploaded file
            file_type: MIME type of file
            filename: Original filename
            file_size: Size of file in bytes
            
        Returns:
            Dictionary with certificate data
        """
        try:
            # Step 1: Extract text using OCR
            logger.info(f"Extracting text from {filename}")
            ocr_result = ocr_service.extract_text(file_path, file_type)
            
            # Handle both string and dict returns from OCR
            if isinstance(ocr_result, dict):
                extracted_text = ocr_result.get("text", "")
                ocr_confidence = ocr_result.get("confidence", 0.0)
                ocr_warnings = ocr_result.get("warnings", [])
            else:
                extracted_text = ocr_result
                # Use simple heuristic: if we got any text, return mid-level confidence (50%)
                ocr_confidence = 50.0 if extracted_text.strip() else 0.0
                ocr_warnings = []
            
            # Step 2: Extract entities using NER
            logger.info(f"Extracting entities from {filename}")
            entities = ner_service.extract_entities(extracted_text)
            
            # Step 3: Store in database
            certificate_data = {
                "certificate_id": certificate_id,
                "filename": filename,
                "file_path": file_path,
                "file_type": file_type,
                "file_size": file_size,
                "upload_timestamp": datetime.now(),
                "extracted_text": extracted_text,
                "ocr_confidence": ocr_confidence,
                "ocr_warnings": ocr_warnings,
                "entities": entities,
                "verification_status": None,
                "verified_timestamp": None
            }
            
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
        raise NotImplementedError("verify_certificate is handled by routes_v2 using the reference database")


# Global verification service instance
verification_service = VerificationService()
