from typing import Any

from pydantic import BaseModel, Field


class RegisterEvidenceRequest(BaseModel):
    tenant_id: str = Field(min_length=1)
    record_id: str = Field(min_length=1)
    event_type: str = Field(min_length=1)
    document_hash: str = Field(min_length=64, max_length=64)
    actor: str = Field(min_length=1)
    timestamp: str = Field(min_length=1)
    metadata_hash: str = Field(min_length=64, max_length=64)
    source_type: str = "DOCUMENT"
    source_id: str | None = None


class VerifyEvidenceRequest(BaseModel):
    tenant_id: str = Field(min_length=1)
    current_document_hash: str = Field(min_length=64, max_length=64)


class EvidenceResponse(BaseModel):
    status: str
    eventId: str
    data: dict[str, Any] | None = None


class ActorContext(BaseModel):
    tenant_id: str
    actor: str
