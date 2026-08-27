from sqlalchemy import String, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import TenantBoundModel
from datetime import datetime
import uuid

class Contract(TenantBoundModel):
    __tablename__ = "contracts"

    contract_number: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    supplier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    
    agreed_price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR")
    
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    effective_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    supplier = relationship("Supplier")
    product = relationship("Product")
