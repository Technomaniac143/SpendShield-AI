from sqlalchemy import String, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import TenantBoundModel
import uuid

class Evidence(TenantBoundModel):
    __tablename__ = "evidence"

    source_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., INVOICE, GRN
    source_id: Mapped[str] = mapped_column(String(100), nullable=False)
    record_id: Mapped[str] = mapped_column(String(100), nullable=False)
    
    document_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    calculation_json: Mapped[dict] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=True)
    
    verification_status: Mapped[str] = mapped_column(String(50), default="UNVERIFIED")
    
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=True)

    user = relationship("User")

class EvidenceEvent(TenantBoundModel):
    __tablename__ = "evidence_events"
    
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    actor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    blockchain_tx_id: Mapped[str] = mapped_column(String(255), nullable=True)
    
    evidence = relationship("Evidence")
    actor = relationship("User")
