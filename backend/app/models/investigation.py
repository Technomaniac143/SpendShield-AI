from sqlalchemy import String, Float, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import TenantBoundModel
from datetime import datetime
import uuid

class Investigation(TenantBoundModel):
    __tablename__ = "investigations"

    status: Mapped[str] = mapped_column(String(50), default="IN_PROGRESS")
    target_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g., SUPPLIER, INVOICE
    target_id: Mapped[str] = mapped_column(String(100), nullable=False)
    
    risk_score: Mapped[float] = mapped_column(Float, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=True)
    financial_exposure: Mapped[float] = mapped_column(Float, nullable=True)
    
    findings: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    steps = relationship("InvestigationStep", back_populates="investigation")

class InvestigationStep(TenantBoundModel):
    __tablename__ = "investigation_steps"

    investigation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="STARTED")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    input_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    output_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    error_msg: Mapped[str] = mapped_column(String(500), nullable=True)

    investigation = relationship("Investigation", back_populates="steps")
