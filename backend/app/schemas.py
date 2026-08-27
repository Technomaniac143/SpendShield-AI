from typing import Any

from pydantic import BaseModel, Field


class RegisterEvidenceRequest(BaseModel):
    record_id: str = Field(min_length=1)
    event_type: str = Field(min_length=1)
    timestamp: str = Field(min_length=1)
    source_type: str = "DOCUMENT"
    source_id: str | None = None
    metadata_hash: str | None = Field(default=None, min_length=64, max_length=64)


class VerifyEvidenceRequest(BaseModel):
    pass


class EvidenceResponse(BaseModel):
    status: str
    eventId: str
    data: dict[str, Any] | None = None


class ActorContext(BaseModel):
    tenant_id: str
    actor: str
