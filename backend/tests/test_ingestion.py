import io
from datetime import date

import pytest
from fastapi import HTTPException, UploadFile
from openpyxl import Workbook
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models import IngestionError, IngestionJob, IngestionStatus, Product, Supplier, Tenant
from app.services import ingestion
from app.api.ingestion import _read_ingestion_file
from starlette.datastructures import Headers


class MemoryStorage:
    def __init__(self):
        self.objects = {}
        self.deleted = []

    def put(self, key, content, content_type=""):
        self.objects[key] = content
        return key

    def get(self, key):
        return self.objects[key]

    def delete(self, key):
        self.deleted.append(key)
        self.objects.pop(key, None)


@pytest.fixture
def db(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = Session(engine)
    monkeypatch.setattr(ingestion, "SessionLocal", lambda: Session(engine))
    yield session
    session.close()
    engine.dispose()


def tenant(db, name="Tenant A"):
    record = Tenant(name=name)
    db.add(record)
    db.commit()
    return record


def test_csv_partial_success_persists_valid_rows_and_errors(db):
    owner = tenant(db)
    storage = MemoryStorage()
    content = b"name,tax_id\n  ABC Industries Ltd. ,TAX-1\n,missing-name\nABC Industries Ltd.,TAX-1\n"
    job = ingestion.create_job(db, owner.id, "admin", "suppliers", "CSV", "suppliers.csv", content, storage, "import-1")
    ingestion.process_ingestion_job(job.id, storage)

    db.expire_all()
    job = db.get(IngestionJob, job.id)
    assert job.status == IngestionStatus.PARTIAL
    assert (job.processed_rows, job.successful_rows, job.failed_rows) == (3, 2, 1)
    assert db.scalar(select(Supplier).where(Supplier.tenant_id == owner.id)).name == "ABC Industries Ltd."
    error = db.scalar(select(IngestionError).where(IngestionError.job_id == job.id))
    assert error.error_code == "MISSING_COLUMN"


def test_xlsx_read_only_processing(db):
    owner = tenant(db)
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["sku", "name"])
    sheet.append(["SKU-1", "Widget"])
    output = io.BytesIO()
    workbook.save(output)
    storage = MemoryStorage()
    job = ingestion.create_job(db, owner.id, "admin", "products", "XLSX", "products.xlsx", output.getvalue(), storage, None)
    ingestion.process_ingestion_job(job.id, storage)

    db.expire_all()
    job = db.get(IngestionJob, job.id)
    assert job.status == IngestionStatus.COMPLETED
    assert db.scalar(select(Product).where(Product.tenant_id == owner.id)).sku == "SKU-1"


def test_idempotency_key_and_file_hash_return_existing_job(db):
    owner = tenant(db)
    storage = MemoryStorage()
    content = b"name\nSupplier A\n"
    first = ingestion.create_job(db, owner.id, "admin", "suppliers", "CSV", "a.csv", content, storage, "same-key")
    second = ingestion.create_job(db, owner.id, "admin", "suppliers", "CSV", "b.csv", content, storage, "same-key")
    assert first.id == second.id
    assert db.scalar(select(IngestionJob.id).where(IngestionJob.tenant_id == owner.id, IngestionJob.file_hash == first.file_hash)) == first.id


def test_unknown_supplier_is_tenant_scoped(db):
    owner_a, owner_b = tenant(db, "A"), tenant(db, "B")
    storage = MemoryStorage()
    job = ingestion.create_job(db, owner_b.id, "admin", "purchase_orders", "CSV", "po.csv", b"po_number,supplier,order_date,currency\nPO-1,Private Supplier,2026-08-28,INR\n", storage, None)
    ingestion.process_ingestion_job(job.id, storage)
    error = db.scalar(select(IngestionError).where(IngestionError.job_id == job.id))
    assert owner_a.id != owner_b.id
    assert error.error_code == "UNKNOWN_SUPPLIER"


@pytest.mark.anyio
async def test_upload_rejects_wrong_extension_and_empty_file():
    wrong_extension = UploadFile(file=io.BytesIO(b"name\nSupplier\n"), filename="data.txt", headers=Headers({"content-type": "text/plain"}))
    with pytest.raises(HTTPException) as extension_error:
        await _read_ingestion_file(wrong_extension, "CSV")
    assert extension_error.value.status_code == 422

    empty = UploadFile(file=io.BytesIO(b""), filename="data.csv", headers=Headers({"content-type": "text/csv"}))
    with pytest.raises(HTTPException) as empty_error:
        await _read_ingestion_file(empty, "CSV")
    assert empty_error.value.status_code == 422


@pytest.mark.anyio
async def test_upload_rejects_oversized_file(monkeypatch):
    monkeypatch.setattr("app.api.ingestion.get_settings", lambda: type("Settings", (), {"max_ingestion_bytes": 3})())
    upload = UploadFile(file=io.BytesIO(b"name"), filename="data.csv", headers=Headers({"content-type": "text/csv"}))
    with pytest.raises(HTTPException) as error:
        await _read_ingestion_file(upload, "CSV")
    assert error.value.status_code == 413


def test_cancelled_job_is_not_processed(db):
    owner = tenant(db, "Cancel Tenant")
    storage = MemoryStorage()
    job = ingestion.create_job(db, owner.id, "admin", "suppliers", "CSV", "suppliers.csv", b"name\nSupplier\n", storage, None)
    job.status = IngestionStatus.CANCELLED
    db.commit()
    ingestion.process_ingestion_job(job.id, storage)
    assert db.scalar(select(Supplier).where(Supplier.tenant_id == owner.id)) is None