import pytest
from fastapi import HTTPException, UploadFile
from starlette.datastructures import Headers

from app.api.evidence import read_pdf


@pytest.mark.anyio
async def test_pdf_signature_is_required():
    upload = UploadFile(file=__import__("io").BytesIO(b"not a pdf"), headers=Headers({"content-type": "application/pdf"}))
    with pytest.raises(HTTPException) as error:
        await read_pdf(upload)
    assert error.value.status_code == 422


@pytest.mark.anyio
async def test_pdf_size_is_bounded(monkeypatch):
    monkeypatch.setattr("app.api.evidence.MAX_DOCUMENT_BYTES", 3)
    upload = UploadFile(file=__import__("io").BytesIO(b"%PDF-1234"), headers=Headers({"content-type": "application/pdf"}))
    with pytest.raises(HTTPException) as error:
        await read_pdf(upload)
    assert error.value.status_code == 413