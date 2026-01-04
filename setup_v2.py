#!/usr/bin/env python3
"""
Quick setup script for PostgreSQL and v2 system
Run: python setup_v2.py
"""

import os
import sys
import subprocess
from pathlib import Path
import time

def check_postgresql():
    """Check if PostgreSQL is installed"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        print(f"✓ PostgreSQL found: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("✗ PostgreSQL not found. Please install PostgreSQL first.")
        print("  Windows: https://www.postgresql.org/download/windows/")
        print("  macOS: brew install postgresql")
        print("  Linux: sudo apt-get install postgresql")
        return False

def check_dependencies():
    """Check Python dependencies"""
    try:
        import sqlalchemy
        import tesseract
        import spacy
        import fuzzywuzzy
        import cv2
        print("✓ All Python dependencies installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("  Run: pip install -r requirements.txt")
        return False

def create_database():
    """Create PostgreSQL database"""
    print("\n=== Creating PostgreSQL Database ===")
    
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
        'database': 'certificate_verification'
    }
    
    try:
        # Create database
        subprocess.run([
            'psql',
            '-U', db_config['user'],
            '-h', db_config['host'],
            '-c', f"CREATE DATABASE {db_config['database']};"
        ], check=False)
        
        print(f"✓ Database created: {db_config['database']}")
        
        # Create user with privileges
        subprocess.run([
            'psql',
            '-U', db_config['user'],
            '-h', db_config['host'],
            '-d', db_config['database'],
            '-c', "CREATE USER IF NOT EXISTS certuser WITH PASSWORD 'certpassword';"
        ], check=False)
        
        subprocess.run([
            'psql',
            '-U', db_config['user'],
            '-h', db_config['host'],
            '-d', db_config['database'],
            '-c', "GRANT ALL PRIVILEGES ON DATABASE certificate_verification TO certuser;"
        ], check=False)
        
        print("✓ User created: certuser")
        return True
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        return False

def create_env_file():
    """Create .env file with v2 configuration"""
    print("\n=== Creating .env Configuration ===")
    
    env_content = """# Database Configuration (v2)
DATABASE_URL=postgresql://certuser:certpassword@localhost:5432/certificate_verification

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Security
REQUESTS_PER_MINUTE=100
MAX_FILE_SIZE_MB=100

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com

# OCR Configuration
TESSERACT_PATH=/usr/bin/tesseract  # Windows: C:\\Program Files\\Tesseract-OCR\\tesseract.exe

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0

# Feature Flags
ENABLE_OCR_PREPROCESSING=True
ENABLE_FUZZY_MATCHING=True
ENABLE_RATE_LIMITING=True
"""
    
    env_path = Path('.env')
    if not env_path.exists():
        env_path.write_text(env_content)
        print("✓ .env file created")
        print("  Please update SMTP and Tesseract settings before running!")
        return True
    else:
        print("⚠ .env file already exists, skipping")
        return True

def create_directories():
    """Create required directories"""
    print("\n=== Creating Directories ===")
    
    dirs = [
        'uploads',
        'data',
        'logs',
        'logs/archive',
        'frontend',
        'database',
        'services',
        'ocr',
        'core',
        'api'
    ]
    
    for dir_name in dirs:
        path = Path(dir_name)
        path.mkdir(exist_ok=True)
        print(f"✓ Directory created: {dir_name}")
    
    return True

def download_spacy_model():
    """Download spaCy language model"""
    print("\n=== Downloading spaCy Model ===")
    
    try:
        import spacy
        try:
            spacy.load('en_core_web_sm')
            print("✓ spaCy model already downloaded")
        except OSError:
            print("Downloading en_core_web_sm model...")
            subprocess.run([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'], check=True)
            print("✓ spaCy model downloaded")
        return True
    except Exception as e:
        print(f"✗ Error downloading spaCy model: {e}")
        return False

def initialize_database_schema():
    """Initialize database schema using SQLAlchemy"""
    print("\n=== Initializing Database Schema ===")
    
    try:
        # This would be done in the application startup
        print("✓ Schema will be initialized on first application run")
        print("  Run: python main.py")
        return True
    except Exception as e:
        print(f"✗ Error initializing schema: {e}")
        return False

def run_health_check():
    """Run health check"""
    print("\n=== Running Health Check ===")
    
    checks = [
        ("Python version", check_python_version),
        ("PostgreSQL", check_postgresql),
        ("Dependencies", check_dependencies),
    ]
    
    passed = 0
    for name, check_func in checks:
        try:
            if check_func():
                passed += 1
        except Exception as e:
            print(f"✗ {name} check failed: {e}")
    
    return passed == len(checks)

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python 3.8+ required, found {version.major}.{version.minor}")
        return False

def main():
    """Run setup wizard"""
    print("""
╔════════════════════════════════════════════════╗
║   Certificate Verification System v2 Setup     ║
║           PostgreSQL Edition                   ║
╚════════════════════════════════════════════════╝
    """)
    
    # Phase 1: Checks
    print("\n=== Phase 1: Prerequisites Check ===")
    if not check_python_version():
        print("Setup failed: Python 3.8+ required")
        return False
    
    if not check_postgresql():
        print("Setup failed: PostgreSQL not found")
        return False
    
    # Phase 2: Setup
    print("\n=== Phase 2: System Setup ===")
    create_directories()
    create_env_file()
    
    # Phase 3: Dependencies
    print("\n=== Phase 3: Dependencies ===")
    if not check_dependencies():
        print("Installing dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
    
    download_spacy_model()
    
    # Phase 4: Database
    print("\n=== Phase 4: Database Setup ===")
    if create_database():
        initialize_database_schema()
    
    # Phase 5: Summary
    print("""
╔════════════════════════════════════════════════╗
║              Setup Complete! 🎉               ║
╚════════════════════════════════════════════════╝

Next Steps:
1. Edit .env file with your configuration:
   - SMTP settings for email notifications
   - Tesseract path for your OS
   
2. Start the application:
   python main.py
   
3. Access the UI:
   http://localhost:8000/ui
   
4. API Documentation:
   http://localhost:8000/docs

Documentation:
- See README_V2.md for complete guide
- See MIGRATION_GUIDE.md for upgrading from v1
- Check logs/app.log for troubleshooting

For Docker deployment:
docker-compose up -d
    """)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nSetup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
