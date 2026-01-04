"""
OCR (Optical Character Recognition) service
Extracts text from images and PDFs
"""
import pytesseract
from pathlib import Path
from typing import Optional
from PIL import Image
from PyPDF2 import PdfReader
from pdf2image import convert_from_path

from utils import get_logger


logger = get_logger("ocr_service")


class OCRService:
    """Service for extracting text from files using OCR"""
    
    def __init__(self):
        """Initialize OCR service"""
        logger.info("OCR service initialized")
    
    def extract_text(self, file_path: str, file_type: str) -> str:
        """
        Extract text from a file based on its type
        
        Args:
            file_path: Path to the file
            file_type: MIME type of the file
            
        Returns:
            Extracted text as string
        """
        try:
            file_path = Path(file_path)
            
            # Determine extraction method based on file type
            if "pdf" in file_type.lower():
                return self._extract_from_pdf(file_path)
            elif "image" in file_type.lower() or file_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                return self._extract_from_image(file_path)
            elif "word" in file_type.lower() or file_path.suffix.lower() in ['.docx', '.doc']:
                # For DOCX, we'll try to convert to image or extract as image
                logger.warning(f"DOCX file detected. This requires additional processing.")
                return self._extract_from_docx(file_path)
            else:
                logger.warning(f"Unsupported file type: {file_type}")
                return ""
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return ""
    
    def _extract_from_pdf(self, file_path: Path) -> str:
        """
        Extract text from PDF file
        First tries direct text extraction, falls back to OCR if needed
        """
        try:
            # Try direct text extraction first
            reader = PdfReader(str(file_path))
            text = ""
            
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            # If no text extracted, use OCR
            if not text.strip():
                logger.info(f"No text found in PDF, using OCR for {file_path.name}")
                text = self._extract_from_pdf_with_ocr(file_path)
            
            logger.info(f"Extracted {len(text)} characters from PDF: {file_path.name}")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting from PDF {file_path}: {str(e)}")
            # Fallback to OCR
            return self._extract_from_pdf_with_ocr(file_path)
    
    def _extract_from_pdf_with_ocr(self, file_path: Path) -> str:
        """Extract text from PDF using OCR"""
        try:
            # Convert PDF pages to images
            images = convert_from_path(str(file_path))
            
            text = ""
            for i, image in enumerate(images):
                logger.info(f"Processing page {i+1}/{len(images)} with OCR")
                page_text = pytesseract.image_to_string(image)
                text += page_text + "\n"
            
            return text
            
        except Exception as e:
            logger.error(f"Error in PDF OCR for {file_path}: {str(e)}")
            return ""
    
    def _extract_from_image(self, file_path: Path) -> str:
        """Extract text from image file using OCR"""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            logger.info(f"Extracted {len(text)} characters from image: {file_path.name}")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting from image {file_path}: {str(e)}")
            return ""
    
    def _extract_from_docx(self, file_path: Path) -> str:
        """
        Extract text from DOCX file
        Note: This is a simplified implementation
        """
        try:
            # For DOCX files, we could use python-docx library
            # For now, return a placeholder message
            logger.warning("DOCX extraction requires additional setup. Please convert to PDF or image.")
            return "DOCX file - text extraction not fully implemented"
            
        except Exception as e:
            logger.error(f"Error extracting from DOCX {file_path}: {str(e)}")
            return ""


# Global OCR service instance
ocr_service = OCRService()
