"""
SQLite database for persistent storage of certificates
Replaces in-memory storage with persistent database
"""
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from utils import get_logger


logger = get_logger("database.sqlite")

# Database path
DB_PATH = Path("data/certificates.db")


class SQLiteDatabase:
    """SQLite database for certificate storage"""
    
    def __init__(self, db_path: str = None):
        """Initialize SQLite database"""
        self.db_path = Path(db_path) if db_path else DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info(f"SQLite database initialized at {self.db_path}")
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Certificates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS certificates (
                certificate_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL,
                upload_timestamp DATETIME NOT NULL,
                extracted_text TEXT,
                entities_json TEXT,
                verification_status TEXT,
                verified_timestamp DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Certificate history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS certificate_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                certificate_id TEXT NOT NULL,
                action TEXT NOT NULL,
                details_json TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (certificate_id) REFERENCES certificates(certificate_id)
            )
        """)
        
        # Create indexes
        cursor.execute("""CREATE INDEX IF NOT EXISTS idx_cert_id ON certificates(certificate_id)""")
        cursor.execute("""CREATE INDEX IF NOT EXISTS idx_cert_status ON certificates(verification_status)""")
        cursor.execute("""CREATE INDEX IF NOT EXISTS idx_upload_date ON certificates(upload_timestamp)""")
        cursor.execute("""CREATE INDEX IF NOT EXISTS idx_history_cert ON certificate_history(certificate_id)""")
        
        conn.commit()
        conn.close()
    
    def add_certificate(self, certificate_data: Dict[str, Any]) -> None:
        """Add a new certificate"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            entities_json = json.dumps(certificate_data.get("entities", {}))
            
            cursor.execute("""
                INSERT INTO certificates 
                (certificate_id, filename, file_path, file_type, upload_timestamp, extracted_text, entities_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                certificate_data["certificate_id"],
                certificate_data["filename"],
                certificate_data["file_path"],
                certificate_data["file_type"],
                certificate_data["upload_timestamp"].isoformat(),
                certificate_data.get("extracted_text", ""),
                entities_json
            ))
            
            # Add history entry
            self._add_history(certificate_id=certificate_data["certificate_id"], action="UPLOADED")
            
            conn.commit()
            conn.close()
            logger.info(f"Certificate {certificate_data['certificate_id']} added to database")
            
        except Exception as e:
            logger.error(f"Error adding certificate: {str(e)}")
            raise
    
    def get_certificate(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        """Get certificate by ID"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM certificates WHERE certificate_id = ?", (certificate_id,))
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            return self._row_to_dict(row)
            
        except Exception as e:
            logger.error(f"Error retrieving certificate: {str(e)}")
            return None
    
    def search_certificates(
        self,
        status: Optional[str] = None,
        filename: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Search certificates with filters"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM certificates WHERE 1=1"
            params = []
            
            if status:
                query += " AND verification_status = ?"
                params.append(status)
            
            if filename:
                query += " AND filename LIKE ?"
                params.append(f"%{filename}%")
            
            if date_from:
                query += " AND upload_timestamp >= ?"
                params.append(date_from)
            
            if date_to:
                query += " AND upload_timestamp <= ?"
                params.append(date_to)
            
            query += " ORDER BY upload_timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error searching certificates: {str(e)}")
            return []
    
    def update_verification_status(
        self,
        certificate_id: str,
        verification_status: str,
        entities: Dict[str, Any] = None
    ) -> None:
        """Update certificate verification status"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            entities_json = json.dumps(entities) if entities else None
            
            cursor.execute("""
                UPDATE certificates
                SET verification_status = ?, verified_timestamp = ?, entities_json = ?
                WHERE certificate_id = ?
            """, (
                verification_status,
                datetime.now().isoformat(),
                entities_json,
                certificate_id
            ))
            
            # Add history entry
            self._add_history(
                certificate_id=certificate_id,
                action="VERIFIED",
                details={"status": verification_status}
            )
            
            conn.commit()
            conn.close()
            logger.info(f"Certificate {certificate_id} verification status updated to {verification_status}")
            
        except Exception as e:
            logger.error(f"Error updating verification status: {str(e)}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Total certificates
            cursor.execute("SELECT COUNT(*) FROM certificates")
            total = cursor.fetchone()[0]
            
            # By status
            cursor.execute("""
                SELECT verification_status, COUNT(*) 
                FROM certificates 
                WHERE verification_status IS NOT NULL
                GROUP BY verification_status
            """)
            status_counts = dict(cursor.fetchall())
            
            # By file type
            cursor.execute("""
                SELECT file_type, COUNT(*) 
                FROM certificates 
                GROUP BY file_type
            """)
            file_type_counts = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                "total_certificates": total,
                "verified": status_counts.get("VERIFIED", 0),
                "partially_verified": status_counts.get("PARTIALLY VERIFIED", 0),
                "not_verified": status_counts.get("NOT VERIFIED", 0),
                "unverified": total - sum(status_counts.values()),
                "by_file_type": file_type_counts
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {}
    
    def get_history(self, certificate_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get certificate history"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM certificate_history
                WHERE certificate_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (certificate_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error retrieving history: {str(e)}")
            return []
    
    def _add_history(
        self,
        certificate_id: str,
        action: str,
        details: Dict[str, Any] = None
    ) -> None:
        """Add entry to certificate history"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            details_json = json.dumps(details) if details else None
            
            cursor.execute("""
                INSERT INTO certificate_history (certificate_id, action, details_json)
                VALUES (?, ?, ?)
            """, (certificate_id, action, details_json))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error adding history: {str(e)}")
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert SQLite row to dictionary"""
        data = dict(row)
        
        # Parse JSON fields
        if "entities_json" in data and data["entities_json"]:
            data["entities"] = json.loads(data["entities_json"])
            del data["entities_json"]
        
        if "details_json" in data and data["details_json"]:
            data["details"] = json.loads(data["details_json"])
            del data["details_json"]
        
        return data
    
    def delete_certificate(self, certificate_id: str) -> bool:
        """Delete a certificate"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM certificate_history WHERE certificate_id = ?", (certificate_id,))
            cursor.execute("DELETE FROM certificates WHERE certificate_id = ?", (certificate_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Certificate {certificate_id} deleted")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting certificate: {str(e)}")
            return False


# Global database instance
sqlite_db = SQLiteDatabase()
