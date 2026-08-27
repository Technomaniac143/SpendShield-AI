from sqlalchemy import String, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import TenantBoundModel
from datetime import datetime
import uuid

class PurchaseOrder(TenantBoundModel):
    __tablename__ = "purchase_orders"

    po_number: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    supplier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("suppliers.id"), nullable=False)
    order_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ISSUED")
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR")

    supplier = relationship("Supplier")
    items = relationship("PurchaseOrderItem", back_populates="po")

class PurchaseOrderItem(TenantBoundModel):
    __tablename__ = "purchase_order_items"

    po_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)

    po = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")
