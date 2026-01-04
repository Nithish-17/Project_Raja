"""
File upload service
Handles file uploads and storage
"""
import shutil
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile
from datetime import datetime

from utils import get_logger, generate_certificate_id, ensure_directory_exists, settings


logger = get_logger("upload_service")


class UploadService:
    """Service for handling file uploads"""
    
    def __init__(self, upload_directory: str = None):
        """Initialize the upload service"""
        self.upload_directory = upload_directory or settings.upload_directory
        ensure_directory_exists(self.upload_directory)
        logger.info(f"Upload service initialized with directory: {self.upload_directory}")
    
    async def save_file(self, file: UploadFile) -> Tuple[str, str, str]:
        """
        Save uploaded file to local storage
        
        Args:
            file: Uploaded file from FastAPI
            
        Returns:
            Tuple of (certificate_id, file_path, file_type)
        """
        try:
            # Generate unique certificate ID
            certificate_id = generate_certificate_id()
            
            # Get file extension
            file_extension = Path(file.filename).suffix
            file_type = file.content_type or self._get_content_type_from_extension(file_extension)
            
            # Create filename with certificate ID
            filename = f"{certificate_id}{file_extension}"
            file_path = Path(self.upload_directory) / filename
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"File saved successfully: {filename} (ID: {certificate_id})")
            
            return certificate_id, str(file_path), file_type
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise
    
    def _get_content_type_from_extension(self, extension: str) -> str:
        """Get content type from file extension"""
        extension = extension.lower()
        content_types = {
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".doc": "application/msword",
        }
        return content_types.get(extension, "application/octet-stream")
    
    def get_file_path(self, certificate_id: str, extension: str) -> Path:
        """Get file path for a certificate ID"""
        filename = f"{certificate_id}{extension}"
        return Path(self.upload_directory) / filename


# Global upload service instance
upload_service = UploadService()
