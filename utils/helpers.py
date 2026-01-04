"""
Utility functions for the application
"""
import uuid
from datetime import datetime
from pathlib import Path


def generate_certificate_id() -> str:
    """Generate a unique certificate ID"""
    return f"CERT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"


def ensure_directory_exists(directory: str) -> Path:
    """Ensure a directory exists, create if it doesn't"""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return Path(filename).suffix.lower()
