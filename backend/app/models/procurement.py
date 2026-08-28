from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

Money = Numeric(18, 2)
Quantity = Numeric(18, 6)


def identifier() -> str:
    return str(uuid4())


class TenantEntity(Base):
    __abstract__ = True
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ProductCategory(TenantEntity):
    __tablename__ = "product_categories"
    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_product_categories_tenant_name"),)
    name: Mapped[str] = mapped_column(String(128))
    normalized_name: Mapped[str] = mapped_column(String(128), index=True)


class Supplier(TenantEntity):
    __tablename__ = "suppliers"
    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_suppliers_tenant_name"), Index("ix_suppliers_tenant_status", "tenant_id", "status"))
    name: Mapped[str] = mapped_column(String(256))
    normalized_name: Mapped[str] = mapped_column(String(256), index=True)
    tax_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    registration_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", index=True)


class SupplierMetric(TenantEntity):
    __tablename__ = "supplier_metrics"
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id", ondelete="CASCADE"), index=True)
    on_time_delivery_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    late_delivery_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    defect_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    return_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    dispute_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    price_variance: Mapped[Decimal] = mapped_column(Numeric(7, 2), default=0)
    invoice_anomaly_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    supplier_risk_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    risk_confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)


class Product(TenantEntity):
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("tenant_id", "sku", name="uq_products_tenant_sku"),)
    sku: Mapped[str] = mapped_column(String(128))
    name: Mapped[str] = mapped_column(String(256))
    normalized_name: Mapped[str] = mapped_column(String(256), index=True)
    category_id: Mapped[str | None] = mapped_column(ForeignKey("product_categories.id", ondelete="SET NULL"), nullable=True, index=True)
    unit_of_measure: Mapped[str] = mapped_column(String(32), default="UNIT")


class Contract(TenantEntity):
    __tablename__ = "contracts"
    __table_args__ = (UniqueConstraint("tenant_id", "contract_number", name="uq_contracts_tenant_number"),)
    contract_number: Mapped[str] = mapped_column(String(128))
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), index=True)
    currency: Mapped[str] = mapped_column(String(3))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", index=True)


class PurchaseOrder(TenantEntity):
    __tablename__ = "purchase_orders"
    __table_args__ = (UniqueConstraint("tenant_id", "po_number", name="uq_purchase_orders_tenant_number"), Index("ix_purchase_orders_tenant_date", "tenant_id", "order_date"))
    po_number: Mapped[str] = mapped_column(String(128))
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), index=True)
    order_date: Mapped[date] = mapped_column(Date)
    currency: Mapped[str] = mapped_column(String(3))
    status: Mapped[str] = mapped_column(String(32), default="OPEN", index=True)
    total_amount: Mapped[Decimal] = mapped_column(Money, default=0)


class PurchaseOrderItem(TenantEntity):
    __tablename__ = "purchase_order_items"
    purchase_order_id: Mapped[str] = mapped_column(ForeignKey("purchase_orders.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    description: Mapped[str] = mapped_column(String(512))
    quantity: Mapped[Decimal] = mapped_column(Quantity)
    unit_price: Mapped[Decimal] = mapped_column(Money)
    tax: Mapped[Decimal] = mapped_column(Money, default=0)
    discount: Mapped[Decimal] = mapped_column(Money, default=0)
    line_total: Mapped[Decimal] = mapped_column(Money)


class GoodsReceipt(TenantEntity):
    __tablename__ = "goods_receipts"
    __table_args__ = (UniqueConstraint("tenant_id", "grn_number", name="uq_goods_receipts_tenant_number"),)
    grn_number: Mapped[str] = mapped_column(String(128))
    po_id: Mapped[str] = mapped_column(ForeignKey("purchase_orders.id"), index=True)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), index=True)
    receipt_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(32), default="RECEIVED", index=True)


class GoodsReceiptItem(TenantEntity):
    __tablename__ = "goods_receipt_items"
    goods_receipt_id: Mapped[str] = mapped_column(ForeignKey("goods_receipts.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    quantity_received: Mapped[Decimal] = mapped_column(Quantity)
    accepted_quantity: Mapped[Decimal] = mapped_column(Quantity)
    rejected_quantity: Mapped[Decimal] = mapped_column(Quantity)


class Invoice(TenantEntity):
    __tablename__ = "invoices"
    __table_args__ = (UniqueConstraint("tenant_id", "invoice_number", "supplier_id", name="uq_invoices_tenant_number_supplier"), Index("ix_invoices_tenant_date", "tenant_id", "invoice_date"))
    invoice_number: Mapped[str] = mapped_column(String(128))
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), index=True)
    po_id: Mapped[str | None] = mapped_column(ForeignKey("purchase_orders.id"), nullable=True, index=True)
    invoice_date: Mapped[date] = mapped_column(Date)
    currency: Mapped[str] = mapped_column(String(3))
    subtotal: Mapped[Decimal] = mapped_column(Money, default=0)
    tax: Mapped[Decimal] = mapped_column(Money, default=0)
    discount: Mapped[Decimal] = mapped_column(Money, default=0)
    total_amount: Mapped[Decimal] = mapped_column(Money, default=0)
    status: Mapped[str] = mapped_column(String(32), default="RECEIVED", index=True)
    document_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    document_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)


class InvoiceItem(TenantEntity):
    __tablename__ = "invoice_items"
    invoice_id: Mapped[str] = mapped_column(ForeignKey("invoices.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[str | None] = mapped_column(ForeignKey("products.id"), nullable=True, index=True)
    description: Mapped[str] = mapped_column(String(512))
    quantity: Mapped[Decimal] = mapped_column(Quantity)
    unit_price: Mapped[Decimal] = mapped_column(Money)
    tax: Mapped[Decimal] = mapped_column(Money, default=0)
    discount: Mapped[Decimal] = mapped_column(Money, default=0)
    line_total: Mapped[Decimal] = mapped_column(Money)


class Payment(TenantEntity):
    __tablename__ = "payments"
    __table_args__ = (UniqueConstraint("tenant_id", "payment_reference", name="uq_payments_tenant_reference"),)
    invoice_id: Mapped[str] = mapped_column(ForeignKey("invoices.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Money)
    currency: Mapped[str] = mapped_column(String(3))
    payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="PENDING", index=True)
    payment_reference: Mapped[str] = mapped_column(String(128))


class Inventory(TenantEntity):
    __tablename__ = "inventory"
    __table_args__ = (UniqueConstraint("tenant_id", "warehouse", "product_id", name="uq_inventory_tenant_warehouse_product"),)
    warehouse: Mapped[str] = mapped_column(String(128), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    quantity: Mapped[Decimal] = mapped_column(Quantity)
    unit_cost: Mapped[Decimal] = mapped_column(Money)
    inventory_value: Mapped[Decimal] = mapped_column(Money)
    last_movement: Mapped[date | None] = mapped_column(Date, nullable=True)


class InventoryMovement(TenantEntity):
    __tablename__ = "inventory_movements"
    inventory_id: Mapped[str] = mapped_column(ForeignKey("inventory.id", ondelete="CASCADE"), index=True)
    quantity: Mapped[Decimal] = mapped_column(Quantity)
    movement_type: Mapped[str] = mapped_column(String(32))
    movement_date: Mapped[date] = mapped_column(Date)
    reference: Mapped[str | None] = mapped_column(String(128), nullable=True)


class QualityEvent(TenantEntity):
    __tablename__ = "quality_events"
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), index=True)
    product_id: Mapped[str | None] = mapped_column(ForeignKey("products.id"), nullable=True)
    event_date: Mapped[date] = mapped_column(Date)
    severity: Mapped[str] = mapped_column(String(32))
    description: Mapped[str] = mapped_column(Text)


class DeliveryEvent(TenantEntity):
    __tablename__ = "delivery_events"
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), index=True)
    purchase_order_id: Mapped[str | None] = mapped_column(ForeignKey("purchase_orders.id"), nullable=True)
    expected_date: Mapped[date] = mapped_column(Date)
    actual_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="PENDING")


class Dispute(TenantEntity):
    __tablename__ = "disputes"
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), index=True)
    invoice_id: Mapped[str | None] = mapped_column(ForeignKey("invoices.id"), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Money, default=0)
    status: Mapped[str] = mapped_column(String(32), default="OPEN", index=True)
    reason: Mapped[str] = mapped_column(Text)