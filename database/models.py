"""
Database models for certificate verification
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class Certificate(BaseModel):
    """Certificate model"""
    certificate_id: str
    filename: str
    file_path: str
    file_type: str
    upload_timestamp: datetime
    extracted_text: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    verification_status: Optional[str] = None
    verified_timestamp: Optional[datetime] = None


class ExtractedEntities(BaseModel):
    """Model for extracted entities from NER"""
    person_name: Optional[str] = None
    organization: Optional[str] = None
    certificate_name: Optional[str] = None
    date_of_issue: Optional[str] = None
    registration_number: Optional[str] = None
