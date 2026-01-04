"""
API endpoints for certificate verification
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any

from services import upload_service, verification_service
from database import db
from utils import get_logger


logger = get_logger("api.routes")
router = APIRouter()


@router.post("/upload")
async def upload_certificate(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload a certificate file
    
    Args:
        file: Certificate file (PDF, JPG, PNG, DOCX)
        
    Returns:
        Certificate details including ID and extracted information
    """
    try:
        logger.info(f"Receiving file upload: {file.filename}")
        
        # Read content to capture file size, then reset pointer for saving
        file_bytes = await file.read()
        file_size = len(file_bytes)
        file.file.seek(0)
        
        # Save file and get certificate ID
        certificate_id, file_path, file_type = await upload_service.save_file(file)
        
        # Process certificate (OCR + NER)
        certificate_data = await verification_service.process_certificate(
            certificate_id=certificate_id,
            file_path=file_path,
            file_type=file_type,
            filename=file.filename,
            file_size=file_size
        )
        
        # Ensure file_size included in response
        if "file_size" not in certificate_data:
            certificate_data["file_size"] = file_size
        
        # Return response
        response = {
            "success": True,
            "message": "Certificate uploaded and processed successfully",
            "certificate_id": certificate_id,
            "filename": file.filename,
            "file_size": certificate_data.get("file_size"),
            "ocr_confidence": certificate_data.get("ocr_confidence", 0.0),
            "extracted_entities": certificate_data.get("entities"),
            "upload_timestamp": certificate_data.get("upload_timestamp").isoformat()
        }
        
        logger.info(f"Upload completed: {certificate_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error uploading certificate: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading certificate: {str(e)}")


@router.get("/certificate/{certificate_id}")
async def get_certificate(certificate_id: str) -> Dict[str, Any]:
    """
    Get certificate details by ID
    
    Args:
        certificate_id: Unique certificate ID
        
    Returns:
        Certificate details
    """
    try:
        logger.info(f"Retrieving certificate: {certificate_id}")
        
        # Get certificate from database
        certificate = db.get_certificate(certificate_id)
        
        if not certificate:
            raise HTTPException(status_code=404, detail=f"Certificate {certificate_id} not found")
        
        # Format response
        response = {
            "success": True,
            "certificate_id": certificate["certificate_id"],
            "filename": certificate["filename"],
            "file_type": certificate["file_type"],
            "upload_timestamp": certificate["upload_timestamp"].isoformat(),
            "extracted_text": certificate.get("extracted_text", ""),
            "entities": certificate.get("entities"),
            "verification_status": certificate.get("verification_status"),
            "verified_timestamp": certificate.get("verified_timestamp").isoformat() if certificate.get("verified_timestamp") else None
        }
        
        logger.info(f"Certificate retrieved: {certificate_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving certificate {certificate_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving certificate: {str(e)}")


@router.post("/verify/{certificate_id}")
async def verify_certificate(certificate_id: str) -> Dict[str, Any]:
    """
    Verify a certificate against dummy database
    
    Args:
        certificate_id: Unique certificate ID
        
    Returns:
        Verification results
    """
    try:
        logger.info(f"Verifying certificate: {certificate_id}")
        
        # Check if certificate exists
        certificate = db.get_certificate(certificate_id)
        if not certificate:
            raise HTTPException(status_code=404, detail=f"Certificate {certificate_id} not found")
        
        # Verify certificate
        verification_result = await verification_service.verify_certificate(certificate_id)
        
        # Format response
        response = {
            "success": True,
            "message": "Certificate verification completed",
            "certificate_id": verification_result["certificate_id"],
            "verification_status": verification_result["verification_status"],
            "entities": verification_result["entities"],
            "verified_timestamp": verification_result["verified_timestamp"].isoformat(),
            "email_sent": verification_result["email_sent"]
        }
        
        logger.info(f"Verification completed: {certificate_id} - {verification_result['verification_status']}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying certificate {certificate_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error verifying certificate: {str(e)}")


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Certificate Verification API"
    }
