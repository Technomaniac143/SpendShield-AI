import pytest
from sqlalchemy import select
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.services.market_intelligence.normalizers.product import normalize_product_name
from app.services.market_intelligence.normalizers.supplier import normalize_supplier_name
from app.services.market_intelligence.normalizers.price import normalize_currency
from app.services.market_intelligence.matching.product_matcher import match_product, match_supplier
from app.services.market_intelligence.pipeline import run_collection_pipeline
from app.services.market_intelligence.models import MarketSupplier, MarketProduct, MarketPriceObservation, MarketCollectionJob

client = TestClient(app)

def test_product_normalization():
    assert normalize_product_name("A4 Copier Paper 75GSM") == "a4 copier paper 75 gsm"
    assert normalize_product_name("HP LaserJet Pro M404dn - Printer") == "hp laserjet pro m404dn printer"

def test_supplier_normalization():
    assert normalize_supplier_name("JK Paper Private Limited") == "jk paper"
    assert normalize_supplier_name("HP India Corp.") == "hp india"

def test_currency_normalization():
    assert normalize_currency("₹") == "INR"
    assert normalize_currency("rs") == "INR"
    assert normalize_currency("USD") == "USD"

def test_product_and_supplier_matching():
    db = SessionLocal()
    try:
        # Create mock market supplier & product
        sup = MarketSupplier(
            name="Test Supplier Ltd",
            normalized_name="test supplier",
            source="test"
        )
        prod = MarketProduct(
            name="Test Product Premium 75gsm",
            normalized_name="test product premium 75 gsm",
            sku="TP-75"
        )
        db.add(sup)
        db.add(prod)
        db.commit()

        # Match exact SKU
        matched_p, method, conf = match_product(db, "Test", sku="TP-75")
        assert matched_p is not None
        assert method == "sku_exact"
        assert conf == 1.0

        # Match exact name
        matched_p, method, conf = match_product(db, "Test Product Premium 75gsm")
        assert matched_p is not None
        assert method == "name_exact"
        assert conf == 0.95

        # Match fuzzy name
        matched_p, method, conf = match_product(db, "Test Product Premium 75 gsm Extra")
        assert matched_p is not None
        assert method == "fuzzy_name"
        assert conf > 0.7

        # Match supplier
        matched_s, method, conf = match_supplier(db, "Test Supplier Ltd")
        assert matched_s is not None
        assert method == "name_exact"

        # Cleanup
        db.delete(sup)
        db.delete(prod)
        db.commit()
    finally:
        db.close()

def test_collection_pipeline():
    db = SessionLocal()
    from sqlalchemy import delete
    try:
        db.execute(delete(MarketPriceObservation))
        db.commit()
        result = run_collection_pipeline(db, "A4 Copier Paper")
        assert result["status"] == "COMPLETED"
        assert result["records_found"] > 0
        assert result["records_inserted"] > 0
        
        # Verify job is saved in DB
        job = db.get(MarketCollectionJob, result["job_id"])
        assert job is not None
        assert job.status == "COMPLETED"
    finally:
        db.close()
