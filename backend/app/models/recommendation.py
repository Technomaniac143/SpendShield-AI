from sqlalchemy import String, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import TenantBoundModel
import uuid

class Recommendation(TenantBoundModel):
    __tablename__ = "recommendations"

    investigation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("investigations.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., HOLD_PAYMENT
    priority: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[str] = mapped_column(String(1000), nullable=False)
    
    exposure: Mapped[float] = mapped_column(Float, nullable=True)
    expected_savings: Mapped[float] = mapped_column(Float, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), default="PENDING_DECISION")
    
    investigation = relationship("Investigation")
    decision = relationship("Decision", uselist=False, back_populates="recommendation")

class Decision(TenantBoundModel):
    __tablename__ = "decisions"

    recommendation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("recommendations.id"), nullable=False, unique=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    decision: Mapped[str] = mapped_column(String(50), nullable=False) # e.g., ACCEPTED, REJECTED, OVERRIDDEN
    reason: Mapped[str] = mapped_column(String(1000), nullable=True)

    recommendation = relationship("Recommendation", back_populates="decision")
    user = relationship("User")
