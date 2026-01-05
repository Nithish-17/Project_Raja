"""
Test the exact code from ocr_service.py
"""
import pytesseract
import platform

print("Starting Tesseract check...")

# Check if Tesseract is available
TESSERACT_AVAILABLE = False
if platform.system() == "Windows":
    print("Windows detected")
    # Configure pytesseract to use system tesseract executable on Windows
    # Update this path if tesseract is installed in a different location
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    print(f"Set tesseract_cmd to: {pytesseract.pytesseract.tesseract_cmd}")
    try:
        print("Calling get_tesseract_version()...")
        version = pytesseract.get_tesseract_version()
        print(f"Got version: {version}")
        TESSERACT_AVAILABLE = True
        print(f"Set TESSERACT_AVAILABLE = {TESSERACT_AVAILABLE}")
    except Exception as e:
        print(f"Exception caught: {e}")
        TESSERACT_AVAILABLE = False
        print(f"Set TESSERACT_AVAILABLE = {TESSERACT_AVAILABLE}")
else:
    print("Not Windows")

print(f"\nFinal result: TESSERACT_AVAILABLE = {TESSERACT_AVAILABLE}")
