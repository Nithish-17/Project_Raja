"""
Security Hardening Module
File validation, filename sanitization, and abuse prevention
"""
import os
import re
from typing import Tuple, Optional
from pathlib import Path
import mimetypes

from utils import get_logger

logger = get_logger("security.validation")


class SecurityValidator:
    """Security validation for file uploads and requests"""
    
    # Allowed MIME types
    ALLOWED_MIME_TYPES = {
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/jpg",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    }
    
    # Dangerous file extensions
    DANGEROUS_EXTENSIONS = {
        ".exe", ".bat", ".cmd", ".scr", ".vbs", ".js", ".jar", ".zip",
        ".rar", ".7z", ".sh", ".bash", ".py", ".php", ".jsp", ".asp",
        ".cgi", ".pl", ".c", ".cpp", ".h", ".dll", ".so", ".app",
    }
    
    # Maximum file size (100MB)
    MAX_FILE_SIZE = 100 * 1024 * 1024
    
    def __init__(self):
        """Initialize security validator"""
        logger.info("Security Validator initialized")
    
    def validate_file(
        self,
        filename: str,
        file_size: int,
        mime_type: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file
        
        Args:
            filename: Original filename
            file_size: File size in bytes
            mime_type: MIME type
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        if file_size > self.MAX_FILE_SIZE:
            error = f"File size exceeds maximum ({file_size / 1024 / 1024:.1f}MB > 100MB)"
            logger.warning(f"File validation failed: {error}")
            return False, error
        
        # Check MIME type
        if mime_type not in self.ALLOWED_MIME_TYPES:
            error = f"Unsupported file type: {mime_type}"
            logger.warning(f"File validation failed: {error}")
            return False, error
        
        # Check extension
        extension = Path(filename).suffix.lower()
        if extension in self.DANGEROUS_EXTENSIONS:
            error = f"Dangerous file type: {extension}"
            logger.warning(f"File validation failed: {error}")
            return False, error
        
        # Sanitize filename
        sanitized, is_safe = self.sanitize_filename(filename)
        if not is_safe:
            error = "Filename contains invalid characters"
            logger.warning(f"File validation failed: {error}")
            return False, error
        
        logger.info(f"File validation passed: {sanitized}")
        return True, None
    
    def sanitize_filename(self, filename: str) -> Tuple[str, bool]:
        """
        Sanitize filename to prevent path traversal
        
        Args:
            filename: Original filename
            
        Returns:
            Tuple of (sanitized_filename, is_safe)
        """
        # Remove path components
        filename = os.path.basename(filename)
        
        # Check for path traversal attempts
        if ".." in filename or "/" in filename or "\\" in filename:
            logger.warning(f"Path traversal attempt detected: {filename}")
            return filename, False
        
        # Remove special characters but keep alphanumeric, dots, and hyphens
        sanitized = re.sub(r'[^\w\s.-]', '', filename)
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:240] + ext
        
        return sanitized, True
    
    def detect_malicious_patterns(self, filename: str) -> bool:
        """
        Detect potentially malicious patterns in filename
        
        Args:
            filename: Filename to check
            
        Returns:
            True if malicious patterns detected, False otherwise
        """
        suspicious_patterns = [
            r'\.exe',
            r'\.scr',
            r'\.bat',
            r'\.cmd',
            r'\.com',
            r'\.pif',
            r'\.sh',
            r'<script',
            r'javascript:',
            r'onerror=',
            r'onload=',
        ]
        
        filename_lower = filename.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, filename_lower):
                logger.warning(f"Malicious pattern detected: {pattern} in {filename}")
                return True
        
        return False
    
    def verify_magic_bytes(self, file_path: str, expected_type: str) -> bool:
        """
        Verify file magic bytes match expected type
        
        Args:
            file_path: Path to file
            expected_type: Expected file type (pdf, image, doc)
            
        Returns:
            True if magic bytes match, False otherwise
        """
        try:
            with open(file_path, 'rb') as f:
                magic_bytes = f.read(4)
            
            # PDF magic bytes
            if expected_type == "pdf":
                if magic_bytes.startswith(b'%PDF'):
                    return True
            
            # PNG magic bytes
            elif expected_type == "png":
                if magic_bytes.startswith(b'\x89PNG'):
                    return True
            
            # JPEG magic bytes
            elif expected_type in ["jpg", "jpeg"]:
                if magic_bytes.startswith(b'\xFF\xD8\xFF'):
                    return True
            
            # DOCX magic bytes (ZIP archive)
            elif expected_type == "docx":
                if magic_bytes.startswith(b'PK\x03\x04'):
                    return True
            
            logger.warning(f"Magic bytes mismatch for {file_path}")
            return False
            
        except Exception as e:
            logger.error(f"Error verifying magic bytes: {str(e)}")
            return False


# Global security validator instance
security_validator = SecurityValidator()
