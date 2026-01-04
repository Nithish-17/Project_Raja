"""
Enhanced API endpoints with advanced features
Includes verification reports, search, and admin endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, Optional
import os

from services import upload_service, verification_service
from services.email_service import email_service
from services.security_validator import security_validator
from services.intelligent_verification import verification_engine
from database.connection import get_db
from database.models_orm import Certificate, ExtractedEntity, VerificationResult, VerificationLog
from core.rate_limiting import rate_limiter
from core.celery_app import celery_app
from utils import get_logger, cache


logger = get_logger("api.routes_v2")
router = APIRouter()


def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    return request.client.host if request.client else "unknown"


@router.post("/upload")
async def upload_certificate(
    file: UploadFile = File(...),
    request: Request = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Upload and process a certificate file
    Enhanced with security validation and intelligent verification
    """
    client_ip = get_client_ip(request)
    
    # Rate limiting
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Maximum 100 requests per minute."
        )
    
    try:
        # Validate file
        file_content = await file.read()
        is_valid, error_msg = security_validator.validate_file(
            file.filename,
            len(file_content),
            file.content_type or "application/octet-stream"
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Save file
        certificate_id, file_path, file_type = await upload_service.save_file(file)
        
        # Verify magic bytes
        file_extension = os.path.splitext(file.filename)[1].lower()
        expected_type = file_extension[1:] if file_extension else ""
        
        if not security_validator.verify_magic_bytes(file_path, expected_type):
            logger.warning(f"Magic bytes mismatch for {file.filename}")
        
        # Process certificate
        certificate_data = await verification_service.process_certificate(
            certificate_id=certificate_id,
            file_path=file_path,
            file_type=file_type,
            filename=file.filename
        )
        
        # Store in database
        cert_db = Certificate(
            certificate_id=certificate_id,
            filename=file.filename,
            file_path=file_path,
            file_type=file_type,
            file_size=len(file_content),
            extracted_text=certificate_data.get("extracted_text"),
            ocr_confidence=certificate_data.get("ocr_confidence", 0.0),
            ocr_warnings=certificate_data.get("ocr_warnings")
        )
        db.add(cert_db)
        db.commit()
        
        # Store extracted entities
        entities_data = certificate_data.get("entities", {})
        entity_db = ExtractedEntity(
            certificate_id=certificate_id,
            person_name=entities_data.get("person_name"),
            organization=entities_data.get("organization"),
            certificate_title=entities_data.get("certificate_title"),
            issue_date=entities_data.get("issue_date"),
            registration_number=entities_data.get("registration_number")
        )
        db.add(entity_db)
        db.commit()
        
        # Log verification attempt
        log_entry = VerificationLog(
            certificate_id=certificate_id,
            action="UPLOADED",
            status="SUCCESS",
            ip_address=client_ip
        )
        db.add(log_entry)
        db.commit()
        
        # Invalidate caches affected by new data
        cache.delete_prefix("stats:")
        cache.delete_prefix("search:")
        cache.delete_prefix(f"report:{certificate_id}")

        return {
            "success": True,
            "message": "Certificate uploaded and processed successfully",
            "certificate_id": certificate_id,
            "filename": file.filename,
            "file_size": len(file_content),
            "extracted_entities": entities_data,
            "ocr_confidence": certificate_data.get("ocr_confidence", 0.0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading certificate: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading certificate: {str(e)}")


@router.post("/verify/{certificate_id}")
async def verify_certificate(
    certificate_id: str,
    request: Request = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Verify a certificate with intelligent fuzzy matching
    Returns confidence score and detailed mismatch information
    """
    client_ip = get_client_ip(request)
    
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    try:
        # Get certificate from database
        cert_db = db.query(Certificate).filter(
            Certificate.certificate_id == certificate_id
        ).first()
        
        if not cert_db:
            raise HTTPException(status_code=404, detail="Certificate not found")
        
        # Get extracted entities
        entity_db = db.query(ExtractedEntity).filter(
            ExtractedEntity.certificate_id == certificate_id
        ).first()
        
        if not entity_db:
            raise HTTPException(status_code=404, detail="Entities not found")
        
        # Perform intelligent verification
        entity_dict = entity_db.to_dict()
        verification_result = verification_engine.verify(entity_dict)
        
        # Store verification result
        result_db = VerificationResult(
            certificate_id=certificate_id,
            status=verification_result["verification_status"],
            confidence_score=verification_result["confidence_score"],
            name_score=verification_result.get("field_scores", {}).get("person_name", 0.0),
            organization_score=verification_result.get("field_scores", {}).get("organization", 0.0),
            title_score=verification_result.get("field_scores", {}).get("certificate_title", 0.0),
            date_score=verification_result.get("field_scores", {}).get("issue_date", 0.0),
            mismatches=verification_result.get("mismatches"),
            matched_database_record=verification_result.get("matched_record")
        )
        
        db.add(result_db)
        cert_db.verification_results.append(result_db)
        db.commit()

        # Dispatch email notification asynchronously when possible
        try:
            email_service.send_verification_alert(
                certificate_id=certificate_id,
                entities=entity_dict,
                verification_status=verification_result["verification_status"],
            )
        except Exception as email_exc:  # pragma: no cover - non-critical path
            logger.warning(f"Failed to enqueue email for {certificate_id}: {email_exc}")
        
        # Log verification
        log_entry = VerificationLog(
            certificate_id=certificate_id,
            action="VERIFIED",
            status=verification_result["verification_status"],
            details={"confidence_score": verification_result["confidence_score"]},
            ip_address=client_ip
        )
        db.add(log_entry)
        db.commit()
        
        # Invalidate caches after verification
        cache.delete_prefix("stats:")
        cache.delete_prefix("search:")
        cache.delete_prefix(f"report:{certificate_id}")

        return {
            "success": True,
            "certificate_id": certificate_id,
            "verification_status": verification_result["verification_status"],
            "confidence_score": verification_result["confidence_score"],
            "field_scores": verification_result.get("field_scores"),
            "mismatches": verification_result.get("mismatches"),
            "matched_record": verification_result.get("matched_record"),
            "timestamp": verification_result.get("timestamp"),
            "email_enqueued": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying certificate: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error verifying certificate: {str(e)}")


@router.get("/certificate/{certificate_id}/report")
async def get_certificate_report(
    certificate_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive verification report for a certificate
    Includes all extracted data, verification results, and history
    """
    try:
        cache_key = f"report:{certificate_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Get certificate
        cert_db = db.query(Certificate).filter(
            Certificate.certificate_id == certificate_id
        ).first()
        
        if not cert_db:
            raise HTTPException(status_code=404, detail="Certificate not found")
        
        # Get entities
        entity_db = db.query(ExtractedEntity).filter(
            ExtractedEntity.certificate_id == certificate_id
        ).first()
        
        # Get verification results
        results = db.query(VerificationResult).filter(
            VerificationResult.certificate_id == certificate_id
        ).all()
        
        # Get verification logs
        logs = db.query(VerificationLog).filter(
            VerificationLog.certificate_id == certificate_id
        ).order_by(VerificationLog.timestamp.desc()).all()
        
        # Build comprehensive report
        report = {
            "certificate_id": certificate_id,
            "file_info": {
                "filename": cert_db.filename,
                "file_type": cert_db.file_type,
                "file_size": cert_db.file_size,
                "upload_timestamp": cert_db.upload_timestamp.isoformat() if cert_db.upload_timestamp else None
            },
            "ocr_results": {
                "extracted_text_preview": (cert_db.extracted_text[:500] + "...") if cert_db.extracted_text else None,
                "confidence": cert_db.ocr_confidence,
                "warnings": cert_db.ocr_warnings
            },
            "extracted_entities": entity_db.to_dict() if entity_db else None,
            "verification_history": [
                {
                    "verification_number": i + 1,
                    "status": result.status,
                    "confidence_score": result.confidence_score,
                    "field_scores": {
                        "name": result.name_score,
                        "organization": result.organization_score,
                        "title": result.title_score,
                        "date": result.date_score
                    },
                    "timestamp": result.verification_timestamp.isoformat() if result.verification_timestamp else None
                }
                for i, result in enumerate(results)
            ],
            "audit_log": [
                {
                    "action": log.action,
                    "status": log.status,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                    "details": log.details
                }
                for log in logs
            ]
        }
        
        response = {"success": True, "report": report}
        cache.set(cache_key, response, ttl_seconds=300)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@router.get("/search")
async def search_certificates(
    status: Optional[str] = Query(None),
    filename: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Search and filter certificates"""
    try:
        cache_key = f"search:{status}:{filename}:{date_from}:{date_to}:{limit}:{offset}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        query = db.query(Certificate)
        
        if status:
            query = query.filter(Certificate.verification_results.any(
                VerificationResult.status == status
            ))
        
        if filename:
            query = query.filter(Certificate.filename.ilike(f"%{filename}%"))
        
        if date_from:
            query = query.filter(Certificate.upload_timestamp >= date_from)
        
        if date_to:
            query = query.filter(Certificate.upload_timestamp <= date_to)
        
        total = query.count()
        results = query.order_by(Certificate.upload_timestamp.desc()).limit(limit).offset(offset).all()
        
        response = {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": [
                {
                    "certificate_id": cert.certificate_id,
                    "filename": cert.filename,
                    "upload_timestamp": cert.upload_timestamp.isoformat() if cert.upload_timestamp else None,
                    "file_type": cert.file_type
                }
                for cert in results
            ]
        }
        cache.set(cache_key, response, ttl_seconds=120)
        return response
        
    except Exception as e:
        logger.error(f"Error searching certificates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/stats")
async def get_statistics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get system statistics"""
    try:
        cached = cache.get("stats:summary")
        if cached:
            return cached

        total_certs = db.query(Certificate).count()
        verified = db.query(VerificationResult).filter(
            VerificationResult.status == "VERIFIED"
        ).count()
        partially = db.query(VerificationResult).filter(
            VerificationResult.status == "PARTIALLY_VERIFIED"
        ).count()
        not_verified = db.query(VerificationResult).filter(
            VerificationResult.status == "NOT_VERIFIED"
        ).count()
        
        response = {
            "success": True,
            "stats": {
                "total_certificates": total_certs,
                "verified": verified,
                "partially_verified": partially,
                "not_verified": not_verified,
                "pending": total_certs - (verified + partially + not_verified)
            }
        }
        cache.set("stats:summary", response, ttl_seconds=60)
        return response
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")


@router.get("/health")
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Health check endpoint with dependency diagnostics"""
    checks = {
        "database": "unknown",
        "redis": "unknown",
        "celery": "unknown",
    }

    # Database check
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:  # pragma: no cover
        logger.warning(f"Database health check failed: {exc}")
        checks["database"] = "error"

    # Redis check
    checks["redis"] = "ok" if cache.is_healthy() else "error"

    # Celery check
    try:
        pong = celery_app.control.ping(timeout=1) if celery_app else []
        checks["celery"] = "ok" if pong else "error"
    except Exception as exc:  # pragma: no cover
        logger.warning(f"Celery health check failed: {exc}")
        checks["celery"] = "error"

    status = "healthy" if all(value == "ok" for value in checks.values()) else "degraded"
    return {"status": status, "service": "Certificate Verification API v2", "checks": checks}
