from sqlalchemy import String, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import TenantBoundModel

class Supplier(TenantBoundModel):
    __tablename__ = "suppliers"

    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    tax_identifier: Mapped[str] = mapped_column(String(100), nullable=True)
    bank_identifier: Mapped[str] = mapped_column(String(100), nullable=True)
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str] = mapped_column(String(50), nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE")
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=True)
