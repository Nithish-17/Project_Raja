"""
Main application entry point
FastAPI application for Certificate Verification System v2
Enhanced with PostgreSQL, fuzzy matching, security, and modern UI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path

from api.routes_v2 import router as router_v2
from utils import get_logger, settings
from database.connection import db_manager
from services.reference_seeder import seed_reference_certificates


logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("=" * 60)
    logger.info("Starting Certificate Verification System v2")
    logger.info("=" * 60)
    logger.info(f"Database: {settings.database_url}")
    logger.info(f"Upload directory: {settings.upload_directory}")
    logger.info(f"Server: {settings.app_host}:{settings.app_port}")
    
    # Create required directories
    Path(settings.upload_directory).mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    Path("frontend").mkdir(exist_ok=True)

    # Seed reference certificates once
    seed_reference_certificates(db_manager.get_session)
    
    yield
    
    logger.info("Shutting down Certificate Verification System")
    logger.info("=" * 60)


# Create FastAPI application
app = FastAPI(
    title="Certificate Verification System v2",
    description="Advanced backend API with fuzzy matching, OCR enhancement, and security hardening",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only enhanced API routes (single authoritative flow)
app.include_router(router_v2, prefix="/api", tags=["certificates"])

# Mount frontend static files
frontend_path = Path("frontend")
if frontend_path.exists():
    app.mount("/ui", StaticFiles(directory=str(frontend_path), html=True), name="ui")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Certificate Verification System v2",
        "version": "2.0.0",
        "status": "running",
        "api_docs": "/docs",
        "ui": "/ui",
        "endpoints": {
            "upload": "/api/upload",
            "verify": "/api/verify/{id}",
            "get_certificate": "/api/certificate/{id}",
            "get_report": "/api/certificate/{id}/report",
            "search": "/api/search",
            "stats": "/api/stats",
            "health": "/api/health"
        },
        "features": [
            "Intelligent fuzzy matching verification",
            "Advanced OCR preprocessing",
            "Security hardening with file validation",
            "PostgreSQL persistence",
            "Rate limiting",
            "Comprehensive audit logs",
            "Modern responsive UI",
            "Docker containerization"
        ]
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Certificate Verification System v2",
        "version": "2.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting uvicorn server...")
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug
    )
