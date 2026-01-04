"""Seed trusted/reference certificates into the database."""
from typing import List, Dict
from sqlalchemy.orm import Session

from database.models_orm import ReferenceCertificate
from utils import get_logger

logger = get_logger("reference_seeder")

# Default trusted certificates (used only to bootstrap the reference table)
DEFAULT_REFERENCE_CERTIFICATES: List[Dict[str, str]] = [
    {
        "person_name": "John Smith",
        "organization": "Stanford University",
        "certificate_title": "Machine Learning Specialization",
        "issue_date": "2023-06-15",
        "registration_number": "ML-2023-001234",
    },
    {
        "person_name": "Jane Doe",
        "organization": "MIT",
        "certificate_title": "Data Science Certificate",
        "issue_date": "2023-08-20",
        "registration_number": "DS-2023-005678",
    },
    {
        "person_name": "Alice Johnson",
        "organization": "Harvard University",
        "certificate_title": "Python Programming Certificate",
        "issue_date": "2023-09-10",
        "registration_number": "PY-2023-009012",
    },
    {
        "person_name": "Bob Williams",
        "organization": "Google",
        "certificate_title": "Cloud Architecture Certificate",
        "issue_date": "2023-07-25",
        "registration_number": "GCP-2023-003456",
    },
    {
        "person_name": "Carol Martinez",
        "organization": "IBM",
        "certificate_title": "AI Engineering Certificate",
        "issue_date": "2023-10-05",
        "registration_number": "AI-2023-007890",
    },
]


def seed_reference_certificates(db_session_factory) -> None:
    """Ensure reference certificates exist in the database.

    Args:
        db_session_factory: callable that returns a SQLAlchemy Session (e.g., db_manager.get_session)
    """
    session: Session = db_session_factory()
    try:
        existing = session.query(ReferenceCertificate).count()
        if existing > 0:
            logger.info("Reference certificates already present; skipping seed")
            return

        for record in DEFAULT_REFERENCE_CERTIFICATES:
            session.add(ReferenceCertificate(**record))
        session.commit()
        logger.info(f"Seeded {len(DEFAULT_REFERENCE_CERTIFICATES)} reference certificates")
    except Exception as exc:  # pragma: no cover - startup only
        session.rollback()
        logger.error(f"Failed to seed reference certificates: {exc}")
        raise
    finally:
        session.close()
