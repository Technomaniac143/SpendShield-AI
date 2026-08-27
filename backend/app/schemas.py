from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class RegisterEvidenceRequest(BaseModel):
    record_id: str = Field(min_length=1, max_length=128)
    event_type: str = Field(min_length=1, max_length=64)
    timestamp: str = Field(min_length=1, max_length=64)
    source_type: str = Field(default="DOCUMENT", max_length=64)
    source_id: str | None = Field(default=None, max_length=128)
    metadata_hash: str | None = Field(default=None, min_length=64, max_length=64)


class VerifyEvidenceRequest(BaseModel):
    pass


class EvidenceResponse(BaseModel):
    status: str
    eventId: str
    data: dict[str, Any] | None = None


class ActorContext(BaseModel):
    tenant_id: str
    actor: str


class ThreeWayMatchRequest(BaseModel):
    po_quantity: float = Field(ge=0)
    grn_quantity: float = Field(ge=0)
    invoice_quantity: float = Field(ge=0)
    invoice_unit_price: float = Field(ge=0)
    po_unit_price: float = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3)
    supplier_matches: bool = True


class TrueCostRequest(BaseModel):
    purchase_price: float = Field(ge=0)
    logistics_cost: float = Field(default=0, ge=0)
    quality_cost: float = Field(default=0, ge=0)
    delay_cost: float = Field(default=0, ge=0)
    inventory_cost: float = Field(default=0, ge=0)
    dispute_cost: float = Field(default=0, ge=0)
    expected_failure_cost: float = Field(default=0, ge=0)
    discounts: float = Field(default=0, ge=0)
    rebates: float = Field(default=0, ge=0)


class ExposureRequest(BaseModel):
    quantity_invoiced: float = Field(ge=0)
    quantity_received: float = Field(ge=0)
    unit_price: float = Field(ge=0)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=256)
    tenant_id: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=32, max_length=256)


class LogoutRequest(RefreshRequest):
    pass


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserCreateRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    display_name: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=8, max_length=256)
    roles: list[str] = Field(default_factory=list, max_length=6)


class UserUpdateRequest(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=128)
    active: bool | None = None
    roles: list[str] | None = Field(default=None, max_length=6)


class UserResponse(BaseModel):
    id: str
    tenant_id: str
    email: str
    display_name: str
    active: bool
    roles: list[str]


class SupplierCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=256)
    tax_id: str | None = Field(default=None, max_length=128)
    registration_id: str | None = Field(default=None, max_length=128)
    address: str | None = None
    country: str | None = Field(default=None, min_length=2, max_length=2)
    status: str = Field(default="ACTIVE", max_length=32)


class SupplierUpdateRequest(SupplierCreateRequest):
    pass


class ProductCreateRequest(BaseModel):
    sku: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=256)
    category_id: str | None = None
    unit_of_measure: str = Field(default="UNIT", max_length=32)


class ProductUpdateRequest(ProductCreateRequest):
    pass


class PurchaseOrderItemRequest(BaseModel):
    product_id: str
    description: str = Field(min_length=1, max_length=512)
    quantity: Decimal = Field(ge=0)
    unit_price: Decimal = Field(ge=0)
    tax: Decimal = Field(default=Decimal("0"), ge=0)
    discount: Decimal = Field(default=Decimal("0"), ge=0)


class PurchaseOrderCreateRequest(BaseModel):
    po_number: str = Field(min_length=1, max_length=128)
    supplier_id: str
    order_date: date
    currency: str = Field(min_length=3, max_length=3)
    status: str = Field(default="OPEN", max_length=32)
    items: list[PurchaseOrderItemRequest] = Field(min_length=1, max_length=500)


class GoodsReceiptItemRequest(BaseModel):
    product_id: str
    quantity_received: Decimal = Field(ge=0)
    accepted_quantity: Decimal = Field(ge=0)
    rejected_quantity: Decimal = Field(ge=0)


class GoodsReceiptCreateRequest(BaseModel):
    grn_number: str = Field(min_length=1, max_length=128)
    po_id: str
    supplier_id: str
    receipt_date: date
    status: str = Field(default="RECEIVED", max_length=32)
    items: list[GoodsReceiptItemRequest] = Field(min_length=1, max_length=500)


class InvoiceItemRequest(BaseModel):
    product_id: str | None = None
    description: str = Field(min_length=1, max_length=512)
    quantity: Decimal = Field(ge=0)
    unit_price: Decimal = Field(ge=0)
    tax: Decimal = Field(default=Decimal("0"), ge=0)
    discount: Decimal = Field(default=Decimal("0"), ge=0)


class InvoiceCreateRequest(BaseModel):
    invoice_number: str = Field(min_length=1, max_length=128)
    supplier_id: str
    po_id: str | None = None
    invoice_date: date
    currency: str = Field(min_length=3, max_length=3)
    tax: Decimal = Field(default=Decimal("0"), ge=0)
    discount: Decimal = Field(default=Decimal("0"), ge=0)
    status: str = Field(default="RECEIVED", max_length=32)
    document_id: str | None = Field(default=None, max_length=128)
    document_hash: str | None = Field(default=None, min_length=64, max_length=64)
    items: list[InvoiceItemRequest] = Field(min_length=1, max_length=500)


class PaymentCreateRequest(BaseModel):
    invoice_id: str
    amount: Decimal = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3)
    payment_date: date | None = None
    status: str = Field(default="PENDING", max_length=32)
    payment_reference: str = Field(min_length=1, max_length=128)


class InventoryCreateRequest(BaseModel):
    warehouse: str = Field(min_length=1, max_length=128)
    product_id: str
    quantity: Decimal = Field(ge=0)
    unit_cost: Decimal = Field(ge=0)


class InventoryMovementRequest(BaseModel):
    inventory_id: str
    quantity: Decimal = Field(gt=0)
    movement_type: str = Field(min_length=1, max_length=32)
    movement_date: date
    reference: str | None = Field(default=None, max_length=128)


class IngestionJobResponse(BaseModel):
    job_id: str
    status: str
    total_rows: int = 0
    processed_rows: int = 0
    successful_rows: int = 0
    failed_rows: int = 0
    skipped_rows: int = 0
    progress_percent: float = 0


class IngestionErrorResponse(BaseModel):
    row_number: int
    field: str | None
    error_code: str
    message: str
    raw_value: str | None
