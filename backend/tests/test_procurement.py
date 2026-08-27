from app.schemas import ExposureRequest, ThreeWayMatchRequest, TrueCostRequest
from app.services.procurement import calculate_quantity_exposure, calculate_true_cost, three_way_match


def test_three_way_match_reports_quantity_and_price_exposure():
    result = three_way_match(ThreeWayMatchRequest(
        po_quantity=1000,
        grn_quantity=920,
        invoice_quantity=1000,
        invoice_unit_price=500,
        po_unit_price=500,
        currency="INR",
    ))
    assert result["status"] == "FAIL"
    assert result["quantity_variance"] == 80
    assert result["financial_exposure"] == 40000


def test_true_cost_is_traceable():
    result = calculate_true_cost(TrueCostRequest(
        purchase_price=950,
        logistics_cost=30,
        quality_cost=45,
        delay_cost=20,
        discounts=10,
    ))
    assert result["true_cost"] == 1035
    assert result["components"]["quality_cost"]["classification"] == "known"


def test_quantity_exposure_never_goes_negative():
    result = calculate_quantity_exposure(ExposureRequest(
        quantity_invoiced=9,
        quantity_received=10,
        unit_price=100,
    ))
    assert result["gross_exposure"] == 0