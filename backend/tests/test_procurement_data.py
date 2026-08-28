from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models import GoodsReceipt, Invoice, Inventory, Product, ProductCategory, PurchaseOrder, Supplier, Tenant
from app.schemas import (
    GoodsReceiptCreateRequest, GoodsReceiptItemRequest, InventoryCreateRequest, InventoryMovementRequest,
    InvoiceCreateRequest, InvoiceItemRequest, PaymentCreateRequest, ProductCreateRequest,
    PurchaseOrderCreateRequest, PurchaseOrderItemRequest, SupplierCreateRequest,
)
from app.services import procurement_data


@pytest.fixture
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


def test_procurement_lifecycle_is_persisted_with_decimal_totals(db):
    tenant = Tenant(name="Procurement Tenant")
    db.add(tenant)
    db.commit()

    supplier = procurement_data.create_supplier(db, tenant.id, SupplierCreateRequest(name="ABC Industries"))
    product = procurement_data.create_product(db, tenant.id, ProductCreateRequest(sku="SKU-1", name="Widget"))
    po = procurement_data.create_purchase_order(db, tenant.id, PurchaseOrderCreateRequest(
        po_number="PO-1", supplier_id=supplier.id, order_date=date(2026, 8, 1), currency="INR",
        items=[PurchaseOrderItemRequest(product_id=product.id, description="Widget", quantity=Decimal("100"), unit_price=Decimal("500"), tax=Decimal("50"))],
    ))
    assert po.total_amount == Decimal("50050.00")

    grn = procurement_data.create_goods_receipt(db, tenant.id, GoodsReceiptCreateRequest(
        grn_number="GRN-1", po_id=po.id, supplier_id=supplier.id, receipt_date=date(2026, 8, 5),
        items=[GoodsReceiptItemRequest(product_id=product.id, quantity_received=Decimal("80"), accepted_quantity=Decimal("80"), rejected_quantity=Decimal("0"))],
    ))
    invoice = procurement_data.create_invoice(db, tenant.id, InvoiceCreateRequest(
        invoice_number="INV-1", supplier_id=supplier.id, po_id=po.id, invoice_date=date(2026, 8, 6), currency="INR",
        items=[InvoiceItemRequest(product_id=product.id, description="Widget", quantity=Decimal("100"), unit_price=Decimal("500"))],
    ))
    payment = procurement_data.create_payment(db, tenant.id, PaymentCreateRequest(
        invoice_id=invoice.id, amount=Decimal("50000"), currency="INR", payment_reference="PAY-1",
    ))
    inventory = procurement_data.create_inventory(db, tenant.id, InventoryCreateRequest(
        warehouse="WH-1", product_id=product.id, quantity=Decimal("80"), unit_cost=Decimal("500"),
    ))
    updated = procurement_data.add_inventory_movement(db, tenant.id, InventoryMovementRequest(
        inventory_id=inventory.id, quantity=Decimal("10"), movement_type="OUT", movement_date=date(2026, 8, 7), reference="ISSUE-1",
    ))

    assert db.get(GoodsReceipt, grn.id).supplier_id == supplier.id
    assert db.get(PurchaseOrder, po.id).total_amount == Decimal("50050.00")
    assert db.get(Invoice, invoice.id).total_amount == Decimal("50000.00")
    assert payment.invoice_id == invoice.id
    assert updated.quantity == Decimal("70.000000")


def test_tenant_scope_rejects_foreign_supplier_reference(db):
    tenant_a, tenant_b = Tenant(name="A"), Tenant(name="B")
    db.add_all([tenant_a, tenant_b])
    db.commit()
    category = ProductCategory(tenant_id=tenant_a.id, name="Private Category", normalized_name="private category")
    db.add(category)
    db.commit()
    with pytest.raises(ValueError, match="product_categories not found"):
        procurement_data.create_product(db, tenant_b.id, ProductCreateRequest(sku="SKU-2", name="Widget", category_id=category.id))


def test_duplicate_business_identity_is_rejected_by_database(db):
    tenant = Tenant(name="Unique Tenant")
    db.add(tenant)
    db.commit()
    procurement_data.create_supplier(db, tenant.id, SupplierCreateRequest(name="Same Supplier"))
    with pytest.raises(Exception):
        procurement_data.create_supplier(db, tenant.id, SupplierCreateRequest(name="Same Supplier"))