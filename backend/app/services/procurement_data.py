from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    GoodsReceipt, GoodsReceiptItem, Inventory, InventoryMovement, Invoice, InvoiceItem,
    Payment, Product, ProductCategory, PurchaseOrder, PurchaseOrderItem, Supplier,
)
from app.schemas import (
    GoodsReceiptCreateRequest, InventoryCreateRequest, InventoryMovementRequest,
    InvoiceCreateRequest, PaymentCreateRequest, ProductCreateRequest, ProductUpdateRequest,
    PurchaseOrderCreateRequest, SupplierCreateRequest, SupplierUpdateRequest,
)


def normalize(value: str) -> str:
    return " ".join(value.casefold().split())


def _owned(db: Session, model, tenant_id: str, object_id: str):
    return db.scalar(select(model).where(model.id == object_id, model.tenant_id == tenant_id))


def _require_owned(db: Session, model, tenant_id: str, object_id: str):
    record = _owned(db, model, tenant_id, object_id)
    if record is None:
        raise ValueError(f"{model.__tablename__} not found")
    return record


def supplier_dict(record: Supplier) -> dict:
    return {"id": record.id, "tenant_id": record.tenant_id, "name": record.name, "normalized_name": record.normalized_name, "tax_id": record.tax_id, "registration_id": record.registration_id, "address": record.address, "country": record.country, "status": record.status}


def product_dict(record: Product) -> dict:
    return {"id": record.id, "tenant_id": record.tenant_id, "sku": record.sku, "name": record.name, "normalized_name": record.normalized_name, "category_id": record.category_id, "unit_of_measure": record.unit_of_measure}


def create_supplier(db: Session, tenant_id: str, request: SupplierCreateRequest) -> Supplier:
    record = Supplier(tenant_id=tenant_id, name=request.name.strip(), normalized_name=normalize(request.name), tax_id=request.tax_id, registration_id=request.registration_id, address=request.address, country=request.country.upper() if request.country else None, status=request.status.upper())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_supplier(db: Session, tenant_id: str, object_id: str, request: SupplierUpdateRequest) -> Supplier:
    record = _require_owned(db, Supplier, tenant_id, object_id)
    record.name = request.name.strip()
    record.normalized_name = normalize(request.name)
    record.tax_id, record.registration_id, record.address = request.tax_id, request.registration_id, request.address
    record.country, record.status = request.country.upper() if request.country else None, request.status.upper()
    db.commit()
    db.refresh(record)
    return record


def create_product(db: Session, tenant_id: str, request: ProductCreateRequest) -> Product:
    if request.category_id:
        _require_owned(db, ProductCategory, tenant_id, request.category_id)
    record = Product(tenant_id=tenant_id, sku=request.sku.strip(), name=request.name.strip(), normalized_name=normalize(request.name), category_id=request.category_id, unit_of_measure=request.unit_of_measure.upper())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_product(db: Session, tenant_id: str, object_id: str, request: ProductUpdateRequest) -> Product:
    record = _require_owned(db, Product, tenant_id, object_id)
    if request.category_id:
        _require_owned(db, ProductCategory, tenant_id, request.category_id)
    record.sku, record.name, record.normalized_name = request.sku.strip(), request.name.strip(), normalize(request.name)
    record.category_id, record.unit_of_measure = request.category_id, request.unit_of_measure.upper()
    db.commit()
    db.refresh(record)
    return record


def create_purchase_order(db: Session, tenant_id: str, request: PurchaseOrderCreateRequest) -> PurchaseOrder:
    _require_owned(db, Supplier, tenant_id, request.supplier_id)
    record = PurchaseOrder(tenant_id=tenant_id, po_number=request.po_number, supplier_id=request.supplier_id, order_date=request.order_date, currency=request.currency.upper(), status=request.status.upper(), total_amount=Decimal("0"))
    db.add(record)
    db.flush()
    total = Decimal("0")
    for item in request.items:
        _require_owned(db, Product, tenant_id, item.product_id)
        line_total = item.quantity * item.unit_price + item.tax - item.discount
        total += line_total
        db.add(PurchaseOrderItem(tenant_id=tenant_id, purchase_order_id=record.id, product_id=item.product_id, description=item.description, quantity=item.quantity, unit_price=item.unit_price, tax=item.tax, discount=item.discount, line_total=line_total))
    record.total_amount = total
    db.commit()
    db.refresh(record)
    return record


def create_goods_receipt(db: Session, tenant_id: str, request: GoodsReceiptCreateRequest) -> GoodsReceipt:
    po = _require_owned(db, PurchaseOrder, tenant_id, request.po_id)
    if po.supplier_id != request.supplier_id:
        raise ValueError("supplier does not match purchase order")
    _require_owned(db, Supplier, tenant_id, request.supplier_id)
    record = GoodsReceipt(tenant_id=tenant_id, grn_number=request.grn_number, po_id=request.po_id, supplier_id=request.supplier_id, receipt_date=request.receipt_date, status=request.status.upper())
    db.add(record)
    db.flush()
    for item in request.items:
        _require_owned(db, Product, tenant_id, item.product_id)
        if item.accepted_quantity + item.rejected_quantity > item.quantity_received:
            raise ValueError("accepted and rejected quantities exceed received quantity")
        db.add(GoodsReceiptItem(tenant_id=tenant_id, goods_receipt_id=record.id, product_id=item.product_id, quantity_received=item.quantity_received, accepted_quantity=item.accepted_quantity, rejected_quantity=item.rejected_quantity))
    db.commit()
    db.refresh(record)
    return record


def create_invoice(db: Session, tenant_id: str, request: InvoiceCreateRequest) -> Invoice:
    _require_owned(db, Supplier, tenant_id, request.supplier_id)
    if request.po_id:
        po = _require_owned(db, PurchaseOrder, tenant_id, request.po_id)
        if po.supplier_id != request.supplier_id or po.currency != request.currency.upper():
            raise ValueError("purchase order does not match invoice supplier or currency")
    record = Invoice(tenant_id=tenant_id, invoice_number=request.invoice_number, supplier_id=request.supplier_id, po_id=request.po_id, invoice_date=request.invoice_date, currency=request.currency.upper(), subtotal=Decimal("0"), tax=request.tax, discount=request.discount, total_amount=Decimal("0"), status=request.status.upper(), document_id=request.document_id, document_hash=request.document_hash.lower() if request.document_hash else None)
    db.add(record)
    db.flush()
    subtotal = Decimal("0")
    for item in request.items:
        if item.product_id:
            _require_owned(db, Product, tenant_id, item.product_id)
        line_total = item.quantity * item.unit_price + item.tax - item.discount
        subtotal += line_total
        db.add(InvoiceItem(tenant_id=tenant_id, invoice_id=record.id, product_id=item.product_id, description=item.description, quantity=item.quantity, unit_price=item.unit_price, tax=item.tax, discount=item.discount, line_total=line_total))
    record.subtotal = subtotal
    record.total_amount = subtotal + request.tax - request.discount
    db.commit()
    db.refresh(record)
    return record


def create_payment(db: Session, tenant_id: str, request: PaymentCreateRequest) -> Payment:
    invoice = _require_owned(db, Invoice, tenant_id, request.invoice_id)
    if invoice.currency != request.currency.upper():
        raise ValueError("payment currency does not match invoice")
    record = Payment(tenant_id=tenant_id, invoice_id=invoice.id, amount=request.amount, currency=request.currency.upper(), payment_date=request.payment_date, status=request.status.upper(), payment_reference=request.payment_reference)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def create_inventory(db: Session, tenant_id: str, request: InventoryCreateRequest) -> Inventory:
    _require_owned(db, Product, tenant_id, request.product_id)
    record = Inventory(tenant_id=tenant_id, warehouse=request.warehouse, product_id=request.product_id, quantity=request.quantity, unit_cost=request.unit_cost, inventory_value=request.quantity * request.unit_cost)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def add_inventory_movement(db: Session, tenant_id: str, request: InventoryMovementRequest) -> Inventory:
    inventory = _require_owned(db, Inventory, tenant_id, request.inventory_id)
    if request.movement_type.upper() in {"OUT", "ISSUE", "CONSUMPTION"}:
        if request.quantity > inventory.quantity:
            raise ValueError("movement exceeds available inventory")
        inventory.quantity -= request.quantity
    else:
        inventory.quantity += request.quantity
    inventory.inventory_value = inventory.quantity * inventory.unit_cost
    inventory.last_movement = request.movement_date
    db.add(InventoryMovement(tenant_id=tenant_id, inventory_id=inventory.id, quantity=request.quantity, movement_type=request.movement_type.upper(), movement_date=request.movement_date, reference=request.reference))
    db.commit()
    db.refresh(inventory)
    return inventory


def inventory_dict(record: Inventory) -> dict:
    age = (date.today() - record.last_movement).days if record.last_movement else None
    return {"id": record.id, "tenant_id": record.tenant_id, "warehouse": record.warehouse, "product_id": record.product_id, "quantity": record.quantity, "unit_cost": record.unit_cost, "inventory_value": record.inventory_value, "last_movement": record.last_movement, "inventory_age_days": age, "days_on_hand": age, "cash_trapped": record.inventory_value}