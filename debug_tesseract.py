"""
Debug Tesseract detection
"""
import pytesseract
import platform

print("=" * 70)
print("DEBUGGING TESSERACT DETECTION")
print("=" * 70)

print(f"\nPlatform: {platform.system()}")
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
print(f"Tesseract cmd set to: {pytesseract.pytesseract.tesseract_cmd}")

print("\nAttempting to get version...")
try:
    version = pytesseract.get_tesseract_version()
    print(f"✅ SUCCESS! Version: {version}")
    print(f"Type: {type(version)}")
except Exception as e:
    print(f"❌ FAILED!")
    print(f"Error: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
