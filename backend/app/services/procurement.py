from app.schemas import ExposureRequest, ThreeWayMatchRequest, TrueCostRequest


def three_way_match(request: ThreeWayMatchRequest) -> dict:
    quantity_variance = max(request.invoice_quantity - request.grn_quantity, 0)
    price_variance = request.invoice_unit_price - request.po_unit_price
    exposure = quantity_variance * request.invoice_unit_price + max(price_variance, 0) * request.invoice_quantity
    reasons: list[str] = []

    if quantity_variance:
        reasons.append("Invoice quantity exceeds received quantity")
    if price_variance > 0:
        reasons.append("Invoice unit price exceeds purchase-order price")
    if not request.supplier_matches:
        reasons.append("Supplier does not match the purchase order")

    return {
        "status": "FAIL" if reasons else "PASS",
        "quantity_variance": quantity_variance,
        "price_variance": price_variance,
        "financial_exposure": exposure,
        "currency": request.currency.upper(),
        "reasons": reasons,
    }


def calculate_true_cost(request: TrueCostRequest) -> dict:
    total_additions = (
        request.logistics_cost + request.quality_cost + request.delay_cost
        + request.inventory_cost + request.dispute_cost + request.expected_failure_cost
    )
    true_cost = request.purchase_price + total_additions - request.discounts - request.rebates
    return {
        "quoted_price": request.purchase_price,
        "true_cost": true_cost,
        "components": {
            "logistics_cost": {"value": request.logistics_cost, "classification": "known"},
            "quality_cost": {"value": request.quality_cost, "classification": "known"},
            "delay_cost": {"value": request.delay_cost, "classification": "known"},
            "inventory_cost": {"value": request.inventory_cost, "classification": "known"},
            "dispute_cost": {"value": request.dispute_cost, "classification": "known"},
            "expected_failure_cost": {"value": request.expected_failure_cost, "classification": "estimated"},
            "discounts": {"value": request.discounts, "classification": "known"},
            "rebates": {"value": request.rebates, "classification": "known"},
        },
        "calculation": "purchase_price + additions - discounts - rebates",
    }


def calculate_quantity_exposure(request: ExposureRequest) -> dict:
    quantity_variance = max(request.quantity_invoiced - request.quantity_received, 0)
    return {
        "gross_exposure": quantity_variance * request.unit_price,
        "quantity_variance": quantity_variance,
        "calculation": "max(quantity_invoiced - quantity_received, 0) * unit_price",
        "confidence": 1.0,
    }