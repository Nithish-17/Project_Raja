"""
Test script for the Certificate Verification API
This script demonstrates how to use the API endpoints
"""
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_root():
    """Test the root endpoint"""
    print("\n=== Testing Root Endpoint ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_upload(file_path):
    """Test certificate upload"""
    print(f"\n=== Testing Certificate Upload ===")
    print(f"Uploading file: {file_path}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return result.get('certificate_id')
        else:
            print(f"Error: {response.text}")
            return None
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

def test_get_certificate(certificate_id):
    """Test getting certificate details"""
    print(f"\n=== Testing Get Certificate ===")
    print(f"Certificate ID: {certificate_id}")
    
    response = requests.get(f"{BASE_URL}/api/certificate/{certificate_id}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_verify_certificate(certificate_id):
    """Test certificate verification"""
    print(f"\n=== Testing Certificate Verification ===")
    print(f"Certificate ID: {certificate_id}")
    
    response = requests.post(f"{BASE_URL}/api/verify/{certificate_id}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        print(f"\nVerification Status: {result.get('verification_status')}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("Certificate Verification API - Test Suite")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Health check failed!")
        return
    print("✅ Health check passed!")
    
    # Test 2: Root endpoint
    if not test_root():
        print("\n❌ Root endpoint failed!")
        return
    print("✅ Root endpoint passed!")
    
    # Test 3: Upload (you can add a file path here)
    print("\n" + "=" * 60)
    print("Upload Test Instructions:")
    print("To test upload, provide a certificate file path.")
    print("Example: python test_api.py --file certificate.pdf")
    print("=" * 60)
    
    print("\n" + "=" * 60)
    print("API is ready! You can now:")
    print("1. Use the Swagger docs at: http://localhost:8000/docs")
    print("2. Upload certificates via POST /api/upload")
    print("3. Get certificate details via GET /api/certificate/{id}")
    print("4. Verify certificates via POST /api/verify/{id}")
    print("=" * 60)

if __name__ == "__main__":
    import sys
    
    # Check for file argument
    if "--file" in sys.argv and len(sys.argv) > sys.argv.index("--file") + 1:
        file_path = sys.argv[sys.argv.index("--file") + 1]
        
        # Run all tests
        test_health()
        test_root()
        
        # Upload and process
        cert_id = test_upload(file_path)
        if cert_id:
            test_get_certificate(cert_id)
            test_verify_certificate(cert_id)
    else:
        # Run basic tests only
        main()
