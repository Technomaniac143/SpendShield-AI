from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import Principal, get_current_principal, require_permission
from app.core.database import get_db
from app.models import GoodsReceipt, Inventory, Invoice, Payment, Product, PurchaseOrder, Supplier
from app.schemas import (
    ExposureRequest, GoodsReceiptCreateRequest, InventoryCreateRequest, InventoryMovementRequest,
    InvoiceCreateRequest, PaymentCreateRequest, ProductCreateRequest, ProductUpdateRequest,
    PurchaseOrderCreateRequest, SupplierCreateRequest, SupplierUpdateRequest, ThreeWayMatchRequest,
    TrueCostRequest,
)
from app.services import procurement_data
from app.services.procurement import calculate_quantity_exposure, calculate_true_cost, three_way_match

router = APIRouter(tags=["procurement"])


@router.post("/procurement/reconciliation/three-way")
def reconcile(request: ThreeWayMatchRequest, _: Principal = Depends(get_current_principal)):
    return {"data": three_way_match(request), "meta": {}}


@router.post("/procurement/true-cost/calculate")
def true_cost(request: TrueCostRequest, _: Principal = Depends(get_current_principal)):
    return {"data": calculate_true_cost(request), "meta": {}}


@router.post("/procurement/exposure/quantity-mismatch")
def quantity_exposure(request: ExposureRequest, _: Principal = Depends(get_current_principal)):
    return {"data": calculate_quantity_exposure(request), "meta": {}}


def _list(db: Session, model, tenant_id: str, page: int, page_size: int) -> dict:
    page_size = min(page_size, 100)
    records = list(db.scalars(select(model).where(model.tenant_id == tenant_id).order_by(model.created_at.desc()).offset((page - 1) * page_size).limit(page_size)))
    return {"data": records, "meta": {"page": page, "page_size": page_size}}


def _error(exc: Exception) -> HTTPException:
    if isinstance(exc, IntegrityError):
        return HTTPException(status_code=409, detail="resource conflicts with an existing record")
    return HTTPException(status_code=422, detail=str(exc))


@router.get("/suppliers")
def suppliers(page: int = 1, page_size: int = 50, principal: Principal = Depends(require_permission("supplier:read")), db: Session = Depends(get_db)):
    result = _list(db, Supplier, principal.tenant_id, page, page_size)
    return {"data": [procurement_data.supplier_dict(item) for item in result["data"]], "meta": result["meta"]}


@router.post("/suppliers", status_code=status.HTTP_201_CREATED)
def create_supplier(request: SupplierCreateRequest, principal: Principal = Depends(require_permission("supplier:write")), db: Session = Depends(get_db)):
    try:
        return {"data": procurement_data.supplier_dict(procurement_data.create_supplier(db, principal.tenant_id, request)), "meta": {}}
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        raise _error(exc) from exc


@router.get("/suppliers/{supplier_id}")
def get_supplier(supplier_id: str, principal: Principal = Depends(require_permission("supplier:read")), db: Session = Depends(get_db)):
    record = db.scalar(select(Supplier).where(Supplier.id == supplier_id, Supplier.tenant_id == principal.tenant_id))
    if record is None:
        raise HTTPException(status_code=404, detail="supplier not found")
    return {"data": procurement_data.supplier_dict(record), "meta": {}}


@router.patch("/suppliers/{supplier_id}")
def patch_supplier(supplier_id: str, request: SupplierUpdateRequest, principal: Principal = Depends(require_permission("supplier:write")), db: Session = Depends(get_db)):
    try:
        return {"data": procurement_data.supplier_dict(procurement_data.update_supplier(db, principal.tenant_id, supplier_id, request)), "meta": {}}
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        raise _error(exc) from exc


@router.delete("/suppliers/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(supplier_id: str, principal: Principal = Depends(require_permission("supplier:write")), db: Session = Depends(get_db)):
    record = db.scalar(select(Supplier).where(Supplier.id == supplier_id, Supplier.tenant_id == principal.tenant_id))
    if record is None:
        raise HTTPException(status_code=404, detail="supplier not found")
    record.status = "INACTIVE"
    db.commit()


@router.get("/products")
def products(page: int = 1, page_size: int = 50, principal: Principal = Depends(require_permission("supplier:read")), db: Session = Depends(get_db)):
    result = _list(db, Product, principal.tenant_id, page, page_size)
    return {"data": [procurement_data.product_dict(item) for item in result["data"]], "meta": result["meta"]}


@router.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(request: ProductCreateRequest, principal: Principal = Depends(require_permission("supplier:write")), db: Session = Depends(get_db)):
    try:
        return {"data": procurement_data.product_dict(procurement_data.create_product(db, principal.tenant_id, request)), "meta": {}}
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        raise _error(exc) from exc


@router.get("/products/{product_id}")
def get_product(product_id: str, principal: Principal = Depends(require_permission("supplier:read")), db: Session = Depends(get_db)):
    record = db.scalar(select(Product).where(Product.id == product_id, Product.tenant_id == principal.tenant_id))
    if record is None:
        raise HTTPException(status_code=404, detail="product not found")
    return {"data": procurement_data.product_dict(record), "meta": {}}


@router.patch("/products/{product_id}")
def patch_product(product_id: str, request: ProductUpdateRequest, principal: Principal = Depends(require_permission("supplier:write")), db: Session = Depends(get_db)):
    try:
        return {"data": procurement_data.product_dict(procurement_data.update_product(db, principal.tenant_id, product_id, request)), "meta": {}}
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        raise _error(exc) from exc


@router.post("/purchase-orders", status_code=status.HTTP_201_CREATED)
def create_po(request: PurchaseOrderCreateRequest, principal: Principal = Depends(require_permission("invoice:write")), db: Session = Depends(get_db)):
    try:
        record = procurement_data.create_purchase_order(db, principal.tenant_id, request)
        return {"data": {"id": record.id, "po_number": record.po_number, "supplier_id": record.supplier_id, "currency": record.currency, "total_amount": record.total_amount, "status": record.status}, "meta": {}}
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        raise _error(exc) from exc


@router.get("/purchase-orders")
def purchase_orders(page: int = 1, page_size: int = 50, principal: Principal = Depends(require_permission("invoice:read")), db: Session = Depends(get_db)):
    return _list(db, PurchaseOrder, principal.tenant_id, page, page_size)


@router.get("/purchase-orders/{po_id}")
def get_po(po_id: str, principal: Principal = Depends(require_permission("invoice:read")), db: Session = Depends(get_db)):
    record = db.scalar(select(PurchaseOrder).where(PurchaseOrder.id == po_id, PurchaseOrder.tenant_id == principal.tenant_id))
    if record is None:
        raise HTTPException(status_code=404, detail="purchase order not found")
    return {"data": {"id": record.id, "po_number": record.po_number, "supplier_id": record.supplier_id, "currency": record.currency, "total_amount": record.total_amount, "status": record.status}, "meta": {}}


@router.post("/goods-receipts", status_code=status.HTTP_201_CREATED)
def create_grn(request: GoodsReceiptCreateRequest, principal: Principal = Depends(require_permission("invoice:write")), db: Session = Depends(get_db)):
    try:
        record = procurement_data.create_goods_receipt(db, principal.tenant_id, request)
        return {"data": {"id": record.id, "grn_number": record.grn_number, "po_id": record.po_id, "supplier_id": record.supplier_id, "status": record.status}, "meta": {}}
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        raise _error(exc) from exc


@router.get("/goods-receipts")
def goods_receipts(page: int = 1, page_size: int = 50, principal: Principal = Depends(require_permission("invoice:read")), db: Session = Depends(get_db)):
    return _list(db, GoodsReceipt, principal.tenant_id, page, page_size)


@router.get("/goods-receipts/{grn_id}")
def get_grn(grn_id: str, principal: Principal = Depends(require_permission("invoice:read")), db: Session = Depends(get_db)):
    record = db.scalar(select(GoodsReceipt).where(GoodsReceipt.id == grn_id, GoodsReceipt.tenant_id == principal.tenant_id))
    if record is None:
        raise HTTPException(status_code=404, detail="goods receipt not found")
    return {"data": {"id": record.id, "grn_number": record.grn_number, "po_id": record.po_id, "supplier_id": record.supplier_id, "status": record.status}, "meta": {}}


@router.post("/invoices", status_code=status.HTTP_201_CREATED)
def create_invoice(request: InvoiceCreateRequest, principal: Principal = Depends(require_permission("invoice:write")), db: Session = Depends(get_db)):
    try:
        record = procurement_data.create_invoice(db, principal.tenant_id, request)
        return {"data": {"id": record.id, "invoice_number": record.invoice_number, "supplier_id": record.supplier_id, "total_amount": record.total_amount, "currency": record.currency, "status": record.status}, "meta": {}}
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        raise _error(exc) from exc


@router.get("/invoices")
def invoices(page: int = 1, page_size: int = 50, principal: Principal = Depends(require_permission("invoice:read")), db: Session = Depends(get_db)):
    return _list(db, Invoice, principal.tenant_id, page, page_size)


@router.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: str, principal: Principal = Depends(require_permission("invoice:read")), db: Session = Depends(get_db)):
    record = db.scalar(select(Invoice).where(Invoice.id == invoice_id, Invoice.tenant_id == principal.tenant_id))
    if record is None:
        raise HTTPException(status_code=404, detail="invoice not found")
    return {"data": {"id": record.id, "invoice_number": record.invoice_number, "supplier_id": record.supplier_id, "total_amount": record.total_amount, "currency": record.currency, "status": record.status}, "meta": {}}


@router.post("/payments", status_code=status.HTTP_201_CREATED)
def create_payment(request: PaymentCreateRequest, principal: Principal = Depends(require_permission("invoice:write")), db: Session = Depends(get_db)):
    try:
        record = procurement_data.create_payment(db, principal.tenant_id, request)
        return {"data": {"id": record.id, "invoice_id": record.invoice_id, "amount": record.amount, "currency": record.currency, "status": record.status, "payment_reference": record.payment_reference}, "meta": {}}
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        raise _error(exc) from exc


@router.get("/payments")
def payments(page: int = 1, page_size: int = 50, principal: Principal = Depends(require_permission("invoice:read")), db: Session = Depends(get_db)):
    return _list(db, Payment, principal.tenant_id, page, page_size)


@router.get("/payments/{payment_id}")
def get_payment(payment_id: str, principal: Principal = Depends(require_permission("invoice:read")), db: Session = Depends(get_db)):
    record = db.scalar(select(Payment).where(Payment.id == payment_id, Payment.tenant_id == principal.tenant_id))
    if record is None:
        raise HTTPException(status_code=404, detail="payment not found")
    return {"data": {"id": record.id, "invoice_id": record.invoice_id, "amount": record.amount, "currency": record.currency, "status": record.status, "payment_reference": record.payment_reference}, "meta": {}}


@router.post("/inventory", status_code=status.HTTP_201_CREATED)
def create_inventory(request: InventoryCreateRequest, principal: Principal = Depends(require_permission("invoice:write")), db: Session = Depends(get_db)):
    try:
        return {"data": procurement_data.inventory_dict(procurement_data.create_inventory(db, principal.tenant_id, request)), "meta": {}}
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        raise _error(exc) from exc


@router.get("/inventory")
def inventory(page: int = 1, page_size: int = 50, principal: Principal = Depends(require_permission("invoice:read")), db: Session = Depends(get_db)):
    result = _list(db, Inventory, principal.tenant_id, page, page_size)
    return {"data": [procurement_data.inventory_dict(item) for item in result["data"]], "meta": result["meta"]}


@router.get("/inventory/{inventory_id}")
def get_inventory(inventory_id: str, principal: Principal = Depends(require_permission("invoice:read")), db: Session = Depends(get_db)):
    record = db.scalar(select(Inventory).where(Inventory.id == inventory_id, Inventory.tenant_id == principal.tenant_id))
    if record is None:
        raise HTTPException(status_code=404, detail="inventory not found")
    return {"data": procurement_data.inventory_dict(record), "meta": {}}


@router.post("/inventory/movements")
def inventory_movement(request: InventoryMovementRequest, principal: Principal = Depends(require_permission("invoice:write")), db: Session = Depends(get_db)):
    try:
        return {"data": procurement_data.inventory_dict(procurement_data.add_inventory_movement(db, principal.tenant_id, request)), "meta": {}}
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        raise _error(exc) from exc