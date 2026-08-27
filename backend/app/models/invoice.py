from sqlalchemy import String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import TenantBoundModel
from datetime import datetime
import uuid

class Invoice(TenantBoundModel):
    __tablename__ = "invoices"

    invoice_number: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    supplier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("suppliers.id"), nullable=False)
    po_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("purchase_orders.id"), nullable=True)
    invoice_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="REGISTERED")
    
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    tax_amount: Mapped[float] = mapped_column(Float, default=0.0)
    discount_amount: Mapped[float] = mapped_column(Float, default=0.0)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR")
    
    document_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    ocr_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)

    supplier = relationship("Supplier")
    po = relationship("PurchaseOrder")
    items = relationship("InvoiceItem", back_populates="invoice")

class InvoiceItem(TenantBoundModel):
    __tablename__ = "invoice_items"

    invoice_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    po_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("purchase_order_items.id"), nullable=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), nullable=True)
    
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    tax: Mapped[float] = mapped_column(Float, default=0.0)
    discount: Mapped[float] = mapped_column(Float, default=0.0)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)

    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product")
