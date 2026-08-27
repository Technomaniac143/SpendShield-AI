import hashlib
from pathlib import PurePath

from fastapi import APIRouter, BackgroundTasks, Depends, File, Header, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permission
from app.core.config import get_settings
from app.core.database import get_db
from app.integrations.storage import create_storage
from app.models import IngestionError, IngestionJob, IngestionStatus
from app.services.ingestion import IngestionValidationError, create_job, process_ingestion_job

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


def _job_response(job: IngestionJob) -> dict:
    progress = (job.processed_rows / job.total_rows * 100) if job.total_rows else 0
    return {"job_id": job.id, "status": job.status.value, "total_rows": job.total_rows, "processed_rows": job.processed_rows, "successful_rows": job.successful_rows, "failed_rows": job.failed_rows, "skipped_rows": job.skipped_rows, "progress_percent": round(progress, 2)}


async def _read_ingestion_file(upload: UploadFile, job_type: str) -> bytes:
    filename = PurePath(upload.filename or "").name
    expected_extension = ".csv" if job_type == "CSV" else ".xlsx"
    if not filename.lower().endswith(expected_extension):
        raise HTTPException(status_code=422, detail=f"only {expected_extension} files are supported")
    if job_type == "CSV" and upload.content_type not in (None, "text/csv", "application/csv", "application/octet-stream"):
        raise HTTPException(status_code=422, detail="invalid CSV content type")
    if job_type == "XLSX" and upload.content_type not in (None, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/octet-stream"):
        raise HTTPException(status_code=422, detail="invalid XLSX content type")
    chunks: list[bytes] = []
    digest = hashlib.sha256()
    total = 0
    while chunk := await upload.read(1024 * 1024):
        total += len(chunk)
        if total > get_settings().max_ingestion_bytes:
            raise HTTPException(status_code=413, detail="ingestion file is too large")
        digest.update(chunk)
        chunks.append(chunk)
    content = b"".join(chunks)
    if not content:
        raise HTTPException(status_code=422, detail="ingestion file is empty")
    if job_type == "XLSX" and not content.startswith(b"PK"):
        raise HTTPException(status_code=422, detail="invalid XLSX file")
    return content


def _enqueue(job_id: str) -> None:
    storage = create_storage()
    process_ingestion_job(job_id, storage)


async def _create_upload(job_type: str, entity_type: str, upload: UploadFile, background_tasks: BackgroundTasks, principal: Principal, db: Session, idempotency_key: str | None):
    content = await _read_ingestion_file(upload, job_type)
    filename = PurePath(upload.filename or "upload").name
    try:
        job = create_job(db, principal.tenant_id, principal.actor, entity_type, job_type, filename, content, create_storage(), idempotency_key)
    except (ValueError, IngestionValidationError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    background_tasks.add_task(_enqueue, job.id)
    return {"data": {"job_id": job.id, "status": job.status.value}, "meta": {}}


@router.post("/csv", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def upload_csv(background_tasks: BackgroundTasks, entity_type: str = Query(...), document: UploadFile = File(...), idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), principal: Principal = Depends(require_permission("ingestion:write")), db: Session = Depends(get_db)):
    return await _create_upload("CSV", entity_type, document, background_tasks, principal, db, idempotency_key)


@router.post("/excel", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def upload_excel(background_tasks: BackgroundTasks, entity_type: str = Query(...), document: UploadFile = File(...), idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), principal: Principal = Depends(require_permission("ingestion:write")), db: Session = Depends(get_db)):
    return await _create_upload("XLSX", entity_type, document, background_tasks, principal, db, idempotency_key)


@router.get("/jobs", response_model=dict)
def list_jobs(page: int = 1, page_size: int = 50, principal: Principal = Depends(require_permission("ingestion:read")), db: Session = Depends(get_db)):
    page_size = min(max(page_size, 1), 100)
    jobs = list(db.scalars(select(IngestionJob).where(IngestionJob.tenant_id == principal.tenant_id).order_by(IngestionJob.created_at.desc()).offset((max(page, 1) - 1) * page_size).limit(page_size)))
    return {"data": [_job_response(job) for job in jobs], "meta": {"page": page, "page_size": page_size}}


@router.get("/jobs/{job_id}", response_model=dict)
def get_job(job_id: str, principal: Principal = Depends(require_permission("ingestion:read")), db: Session = Depends(get_db)):
    job = db.scalar(select(IngestionJob).where(IngestionJob.id == job_id, IngestionJob.tenant_id == principal.tenant_id))
    if job is None:
        raise HTTPException(status_code=404, detail="ingestion job not found")
    return {"data": _job_response(job), "meta": {}}


@router.get("/jobs/{job_id}/errors", response_model=dict)
def get_errors(job_id: str, page: int = 1, page_size: int = 50, field: str | None = None, error_code: str | None = None, row_number: int | None = None, principal: Principal = Depends(require_permission("ingestion:read")), db: Session = Depends(get_db)):
    if db.scalar(select(IngestionJob.id).where(IngestionJob.id == job_id, IngestionJob.tenant_id == principal.tenant_id)) is None:
        raise HTTPException(status_code=404, detail="ingestion job not found")
    query = select(IngestionError).where(IngestionError.job_id == job_id, IngestionError.tenant_id == principal.tenant_id)
    if field: query = query.where(IngestionError.field == field)
    if error_code: query = query.where(IngestionError.error_code == error_code)
    if row_number is not None: query = query.where(IngestionError.row_number == row_number)
    errors = list(db.scalars(query.order_by(IngestionError.row_number).offset((max(page, 1) - 1) * min(max(page_size, 1), 100)).limit(min(max(page_size, 1), 100))))
    return {"data": [{"row_number": error.row_number, "field": error.field, "error_code": error.error_code, "message": error.message, "raw_value": error.raw_value} for error in errors], "meta": {"page": page, "page_size": min(max(page_size, 1), 100)}}


@router.post("/jobs/{job_id}/cancel", response_model=dict)
def cancel_job(job_id: str, principal: Principal = Depends(require_permission("ingestion:cancel")), db: Session = Depends(get_db)):
    job = db.scalar(select(IngestionJob).where(IngestionJob.id == job_id, IngestionJob.tenant_id == principal.tenant_id))
    if job is None: raise HTTPException(status_code=404, detail="ingestion job not found")
    if job.status not in {IngestionStatus.QUEUED, IngestionStatus.PROCESSING}:
        raise HTTPException(status_code=409, detail="ingestion job cannot be cancelled in its current state")
    job.status = IngestionStatus.CANCELLED
    job.completed_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    db.commit()
    return {"data": _job_response(job), "meta": {}}