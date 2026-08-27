from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Evidence(Base):
    __tablename__ = "evidence"
    __table_args__ = (UniqueConstraint("tenant_id", "fabric_event_id", name="uq_evidence_tenant_event"),)

    evidence_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(128), index=True)
    source_type: Mapped[str] = mapped_column(String(64), default="DOCUMENT")
    source_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    record_id: Mapped[str] = mapped_column(String(128), index=True)
    event_type: Mapped[str] = mapped_column(String(64))
    document_hash: Mapped[str] = mapped_column(String(64))
    metadata_hash: Mapped[str] = mapped_column(String(64))
    calculation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[str] = mapped_column(String(128))
    event_timestamp: Mapped[str] = mapped_column(String(64))
    confidence: Mapped[float | None] = mapped_column(nullable=True)
    verification_status: Mapped[str] = mapped_column(String(64), default="PENDING_BLOCKCHAIN_VERIFICATION")
    fabric_event_id: Mapped[str] = mapped_column(String(128))
    fabric_transaction_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    fabric_channel: Mapped[str] = mapped_column(String(128))
    fabric_chaincode: Mapped[str] = mapped_column(String(128))
    fabric_block_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fabric_block_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
