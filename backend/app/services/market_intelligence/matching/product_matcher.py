from difflib import SequenceMatcher
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.services.market_intelligence.models import MarketProduct, MarketSupplier
from app.services.market_intelligence.normalizers.product import normalize_product_name
from app.services.market_intelligence.normalizers.supplier import normalize_supplier_name

def match_product(db: Session, name: str, sku: str | None = None, manufacturer: str | None = None) -> tuple[MarketProduct | None, str, float]:
    """
    Progressively match a product:
    1. Exact SKU
    2. Exact manufacturer + model
    3. Exact normalized product identity
    4. Fuzzy matching
    Returns (MatchedProduct, MatchMethod, MatchConfidence)
    """
    norm_name = normalize_product_name(name)
    
    # 1. Exact SKU Match
    if sku:
        prod = db.scalar(select(MarketProduct).where(MarketProduct.sku == sku))
        if prod:
            return prod, "sku_exact", 1.0

    # 2. Exact Normalized Name Match
    prod = db.scalar(select(MarketProduct).where(MarketProduct.normalized_name == norm_name))
    if prod:
        return prod, "name_exact", 0.95

    # 3. Fuzzy Name Match
    products = db.scalars(select(MarketProduct)).all()
    best_match = None
    highest_score = 0.0
    for p in products:
        score = SequenceMatcher(None, norm_name, p.normalized_name).ratio()
        if score > highest_score:
            highest_score = score
            best_match = p
            
    if highest_score >= 0.8:
        return best_match, "fuzzy_name", round(highest_score * 0.9, 2)

    return None, "none", 0.0

def match_supplier(db: Session, name: str) -> tuple[MarketSupplier | None, str, float]:
    """
    Match a supplier:
    1. Exact normalized name match
    2. Fuzzy match
    """
    norm_name = normalize_supplier_name(name)
    
    # 1. Exact Normalized Match
    sup = db.scalar(select(MarketSupplier).where(MarketSupplier.normalized_name == norm_name))
    if sup:
        return sup, "name_exact", 1.0
        
    # 2. Fuzzy Match
    suppliers = db.scalars(select(MarketSupplier)).all()
    best_match = None
    highest_score = 0.0
    for s in suppliers:
        score = SequenceMatcher(None, norm_name, s.normalized_name).ratio()
        if score > highest_score:
            highest_score = score
            best_match = s
            
    if highest_score >= 0.85:
        return best_match, "fuzzy_name", round(highest_score * 0.95, 2)
        
    return None, "none", 0.0
