from celery import Celery
import time
from app.core.config import settings

celery_app = Celery(
    "spendshield_workers",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(name="process_document_ocr")
def process_document_ocr(tenant_id: str, document_path: str):
    """
    Mock background task for processing OCR on an uploaded document.
    """
    time.sleep(2) # simulate processing
    return {"status": "COMPLETED", "document_path": document_path, "tenant_id": tenant_id}

@celery_app.task(name="register_blockchain_event")
def register_blockchain_event_task(tenant_id: str, record_id: str, event_type: str, document_hash: str, actor: str):
    """
    Background task to register an event on the blockchain.
    """
    # In a real app, this would use the async fabric_client
    # Celery tasks are sync by default unless configured for async event loops.
    time.sleep(1)
    return {"status": "REGISTERED", "record_id": record_id}
