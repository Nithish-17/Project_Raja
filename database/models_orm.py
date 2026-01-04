"""
SQLAlchemy ORM models for PostgreSQL database
"""
from sqlalchemy import create_engine, Column, String, Text, Float, DateTime, Integer, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum

from utils import get_logger

logger = get_logger("database.models_orm")

Base = declarative_base()


class VerificationStatusEnum(str, enum.Enum):
    """Verification status enumeration"""
    VERIFIED = "VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    NOT_VERIFIED = "NOT_VERIFIED"
    PENDING = "PENDING"


class Certificate(Base):
    """Certificate model"""
    __tablename__ = "certificates"
    
    certificate_id = Column(String(100), primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer)
    
    upload_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # OCR results
    extracted_text = Column(Text)
    ocr_confidence = Column(Float, default=0.0)
    ocr_warnings = Column(JSON)
    
    # NER results
    entities = relationship("ExtractedEntity", back_populates="certificate", cascade="all, delete-orphan")
    
    # Verification results
    verification_results = relationship("VerificationResult", back_populates="certificate", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Certificate(id={self.certificate_id}, filename={self.filename})>"


class ReferenceCertificate(Base):
    """Trusted/reference certificate records used for verification"""
    __tablename__ = "reference_certificates"

    id = Column(Integer, primary_key=True)
    person_name = Column(String(255), nullable=False)
    organization = Column(String(255), nullable=False)
    certificate_title = Column(String(255), nullable=False)
    issue_date = Column(String(50), nullable=True)
    registration_number = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "person_name": self.person_name,
            "organization": self.organization,
            "certificate_title": self.certificate_title,
            "issue_date": self.issue_date,
            "registration_number": self.registration_number,
        }


class ExtractedEntity(Base):
    """Extracted entity model"""
    __tablename__ = "extracted_entities"
    
    id = Column(Integer, primary_key=True)
    certificate_id = Column(String(100), ForeignKey("certificates.certificate_id"), nullable=False, index=True)
    
    person_name = Column(String(255))
    person_name_confidence = Column(Float, default=0.0)
    
    organization = Column(String(255))
    organization_confidence = Column(Float, default=0.0)
    
    certificate_title = Column(String(255))
    certificate_title_confidence = Column(Float, default=0.0)
    
    issue_date = Column(String(50))
    issue_date_confidence = Column(Float, default=0.0)
    
    registration_number = Column(String(100))
    registration_number_confidence = Column(Float, default=0.0)
    
    extracted_at = Column(DateTime, default=datetime.utcnow)
    
    certificate = relationship("Certificate", back_populates="entities")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "person_name": self.person_name,
            "organization": self.organization,
            "certificate_title": self.certificate_title,
            "issue_date": self.issue_date,
            "registration_number": self.registration_number,
        }


class VerificationResult(Base):
    """Verification result model"""
    __tablename__ = "verification_results"
    
    id = Column(Integer, primary_key=True)
    certificate_id = Column(String(100), ForeignKey("certificates.certificate_id"), nullable=False, index=True)
    
    status = Column(Enum(VerificationStatusEnum), default=VerificationStatusEnum.PENDING, index=True)
    confidence_score = Column(Float, default=0.0)
    
    # Weighted scores
    name_score = Column(Float, default=0.0)
    organization_score = Column(Float, default=0.0)
    title_score = Column(Float, default=0.0)
    date_score = Column(Float, default=0.0)
    
    # Mismatch details
    mismatches = Column(JSON)
    matched_database_record = Column(JSON)
    
    verification_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    certificate = relationship("Certificate", back_populates="verification_results")
    
    def __repr__(self):
        return f"<VerificationResult(cert_id={self.certificate_id}, status={self.status}, score={self.confidence_score})>"


class VerificationLog(Base):
    """Audit log for verification attempts"""
    __tablename__ = "verification_logs"
    
    id = Column(Integer, primary_key=True)
    certificate_id = Column(String(100), index=True)
    action = Column(String(50), nullable=False)  # UPLOADED, OCR_PROCESSED, NER_PROCESSED, VERIFIED, EMAILED
    status = Column(String(20))
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    ip_address = Column(String(50))
