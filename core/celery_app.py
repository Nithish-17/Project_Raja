"""Celery application and tasks for async processing."""
from __future__ import annotations

from celery import Celery
from celery.utils.log import get_task_logger

from utils import settings

logger = get_task_logger(__name__)

# Initialize Celery using Redis for broker and backend
celery_app = Celery(
    "certificate_verification",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

# Basic configuration
celery_app.conf.task_routes = {
    "core.celery_app.send_email_task": {"queue": "emails"},
}
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.broker_heartbeat = 10
celery_app.conf.broker_pool_limit = 5
celery_app.conf.worker_prefetch_multiplier = 1


@celery_app.task(name="core.celery_app.send_email_task", bind=True)
def send_email_task(self, certificate_id: str, entities: dict, verification_status: str) -> dict:
    """Background task to send verification email alerts."""
    try:
        from services.email_service import email_service

        success = email_service.send_verification_alert(
            certificate_id=certificate_id,
            entities=entities,
            verification_status=verification_status,
            use_celery=False,
        )
        return {"success": success}
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Celery send_email_task failed: %s", exc)
        raise
