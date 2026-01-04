"""
Rate Limiting and Async Task Management
Prevents abuse and handles background processing
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
from functools import wraps
import time

from utils import get_logger

logger = get_logger("core.rate_limiting")


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter
        
        Args:
            requests_per_minute: Maximum requests allowed per minute
        """
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed
        
        Args:
            identifier: Client identifier (IP address, user ID, etc.)
            
        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        now = datetime.utcnow()
        one_minute_ago = now - timedelta(minutes=1)
        
        # Initialize if not exists
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Remove old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > one_minute_ago
        ]
        
        # Check limit
        if len(self.requests[identifier]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {identifier}")
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        return True
    
    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests for identifier"""
        now = datetime.utcnow()
        one_minute_ago = now - timedelta(minutes=1)
        
        if identifier not in self.requests:
            return self.requests_per_minute
        
        recent = [
            req_time for req_time in self.requests[identifier]
            if req_time > one_minute_ago
        ]
        
        return max(0, self.requests_per_minute - len(recent))


class AsyncTaskManager:
    """Manages asynchronous background tasks"""
    
    def __init__(self):
        """Initialize task manager"""
        self.tasks: Dict[str, Dict[str, Any]] = {}
        logger.info("AsyncTaskManager initialized")
    
    async def send_email_async(
        self,
        certificate_id: str,
        email_service,
        entities: Dict[str, Any],
        verification_status: str
    ) -> bool:
        """
        Send email asynchronously
        
        Args:
            certificate_id: Certificate ID
            email_service: Email service instance
            entities: Extracted entities
            verification_status: Verification status
            
        Returns:
            True if successful
        """
        try:
            # Skip email if VERIFIED
            if verification_status == "VERIFIED":
                logger.info(f"Skipping email for VERIFIED certificate {certificate_id}")
                return True
            
            # Schedule email sending
            task = asyncio.create_task(
                self._send_email_task(
                    certificate_id,
                    email_service,
                    entities,
                    verification_status
                )
            )
            
            self.tasks[certificate_id] = {
                "type": "email",
                "task": task,
                "created_at": datetime.utcnow(),
                "status": "pending"
            }
            
            logger.info(f"Email task scheduled for {certificate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling email: {str(e)}")
            return False
    
    async def _send_email_task(
        self,
        certificate_id: str,
        email_service,
        entities: Dict[str, Any],
        verification_status: str
    ):
        """Background email sending task"""
        try:
            # Simulate async operation
            await asyncio.sleep(1)
            
            result = email_service.send_verification_alert(
                certificate_id,
                entities,
                verification_status
            )
            
            if self.tasks.get(certificate_id):
                self.tasks[certificate_id]["status"] = "completed" if result else "failed"
            
            logger.info(f"Email sent for {certificate_id}: {result}")
            
        except Exception as e:
            logger.error(f"Email task failed for {certificate_id}: {str(e)}")
            if self.tasks.get(certificate_id):
                self.tasks[certificate_id]["status"] = "failed"
    
    def get_task_status(self, certificate_id: str) -> Optional[str]:
        """Get task status"""
        task = self.tasks.get(certificate_id)
        return task.get("status") if task else None


# Global instances
rate_limiter = RateLimiter(requests_per_minute=100)
task_manager = AsyncTaskManager()
