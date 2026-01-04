"""
PostgreSQL database connection and session management
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from typing import Generator

from utils import get_logger, settings
from database.models_orm import Base

logger = get_logger("database.connection")


class DatabaseManager:
    """Database connection manager"""
    
    def __init__(self):
        """Initialize database connection"""
        self.database_url = settings.database_url
        
        # Create engine
        self.engine = create_engine(
            self.database_url,
            poolclass=NullPool,
            echo=False,
            connect_args={"check_same_thread": False} if "sqlite" in self.database_url else {}
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        self._create_tables()
        
        logger.info(f"Database connected: {self.database_url}")
    
    def _create_tables(self):
        """Create all tables in the database"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            raise
    
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    def close(self):
        """Close database connection"""
        self.engine.dispose()
        logger.info("Database connection closed")


# Global database manager
db_manager = DatabaseManager()


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session in FastAPI"""
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()
