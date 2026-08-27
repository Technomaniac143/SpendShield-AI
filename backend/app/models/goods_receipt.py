from sqlalchemy import String, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import TenantBoundModel
from datetime import datetime
import uuid

class GoodsReceipt(TenantBoundModel):
    __tablename__ = "goods_receipts"

    grn_number: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    po_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("purchase_orders.id"), nullable=True)
    supplier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("suppliers.id"), nullable=False)
    receipt_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="RECEIVED")

    po = relationship("PurchaseOrder")
    supplier = relationship("Supplier")
    items = relationship("GoodsReceiptItem", back_populates="grn")

class GoodsReceiptItem(TenantBoundModel):
    __tablename__ = "goods_receipt_items"

    grn_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("goods_receipts.id", ondelete="CASCADE"), nullable=False)
    po_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("purchase_order_items.id"), nullable=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), nullable=True)
    received_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    accepted_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    rejected_quantity: Mapped[float] = mapped_column(Float, default=0.0)

    grn = relationship("GoodsReceipt", back_populates="items")
    product = relationship("Product")
