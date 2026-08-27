from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import TenantBoundModel
import uuid

class Outcome(TenantBoundModel):
    __tablename__ = "outcomes"

    decision_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("decisions.id"), nullable=False, unique=True)
    
    predicted_exposure: Mapped[float] = mapped_column(Float, nullable=True)
    predicted_savings: Mapped[float] = mapped_column(Float, nullable=True)
    
    realized_savings: Mapped[float] = mapped_column(Float, nullable=True)
    cash_released: Mapped[float] = mapped_column(Float, nullable=True)
    actual_cost: Mapped[float] = mapped_column(Float, nullable=True)
    prediction_error: Mapped[float] = mapped_column(Float, nullable=True)

    decision = relationship("Decision")
