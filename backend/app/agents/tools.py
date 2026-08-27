import json
from typing import Dict, Any, List
from app.services.reconciliation.match import ReconciliationEngine
from app.services.anomaly.duplicate import DuplicateDetectionEngine
from app.services.anomaly.price_anomaly import PriceAnomalyEngine
from app.services.true_cost.true_cost import TrueCostEngine
from app.services.exposure.exposure import FinancialExposureEngine
from app.services.graph.neo4j_client import neo4j_client

# These are mocked DB retrieval tools for the hackathon MVP.
# In a full implementation, they would use SQLAlchemy AsyncSession to fetch actual data.

async def get_supplier_profile(tenant_id: str, supplier_id: str) -> str:
    """Mock fetching supplier profile."""
    # In reality, this queries the DB
    return json.dumps({
        "id": supplier_id,
        "name": "ABC Industries",
        "risk_score": 87,
        "status": "ACTIVE"
    })

async def run_three_way_match(tenant_id: str, invoice_id: str) -> str:
    """Mock running a 3-way match."""
    # Mocking a discrepancy
    return json.dumps({
        "status": "FAIL",
        "financial_exposure": 40000,
        "reasons": ["Invoice quantity (1000) exceeds received quantity (920) for product P-001."]
    })

async def find_duplicate_invoices(tenant_id: str, invoice_id: str) -> str:
    """Mock checking for duplicates."""
    return json.dumps({
        "duplicates": [
            {"probability": 0.96, "matched_invoice_id": "INV-10091", "signals": ["same supplier", "similar invoice number", "same amount"]}
        ]
    })

async def detect_price_anomaly(tenant_id: str, invoice_id: str) -> str:
    """Mock detecting price anomalies."""
    return json.dumps({
        "is_anomalous": True,
        "variance_percent": 11.6,
        "expected_price": 500,
        "baseline_type": "CONTRACT",
        "score": 58.0
    })

async def traverse_supplier_graph(tenant_id: str, supplier_id: str) -> str:
    """Uses Neo4j client to fetch graph relationships."""
    res = await neo4j_client.get_supplier_relationships(tenant_id, supplier_id)
    # If DB not available, mock it
    if "error" in res:
        return json.dumps({
            "relationships": [
                {"relationship": "SHARES_ADDRESS", "connected_id": "SUP-002", "node_type": ["Supplier"]}
            ],
            "risk_signals": 2,
            "status": "MOCKED_SUCCESS"
        })
    return json.dumps(res)

async def calculate_true_cost(tenant_id: str, supplier_id: str) -> str:
    """Mock true cost calculation."""
    return json.dumps(TrueCostEngine.calculate_true_cost(
        quoted_price=950,
        logistics_cost=30,
        quality_cost=45,
        delay_cost=20,
        discounts=10
    ))

async def calculate_financial_exposure(tenant_id: str, investigation_id: str) -> str:
    """Mock financial exposure calculation based on findings."""
    return json.dumps(FinancialExposureEngine.calculate_exposure(
        quantity_variance=80,
        unit_price=500,
        duplicate_amount=0
    ))

AVAILABLE_TOOLS = {
    "get_supplier_profile": get_supplier_profile,
    "run_three_way_match": run_three_way_match,
    "find_duplicate_invoices": find_duplicate_invoices,
    "detect_price_anomaly": detect_price_anomaly,
    "traverse_supplier_graph": traverse_supplier_graph,
    "calculate_true_cost": calculate_true_cost,
    "calculate_financial_exposure": calculate_financial_exposure
}
