from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional

from app.core.auth import Principal, get_current_principal, require_permission
from app.core.database import get_db
from app.models import Product, Invoice, InvoiceItem
from app.services.market_intelligence.models import MarketCollectionJob, MarketSupplier, MarketProduct, MarketPriceObservation
from app.services.market_intelligence.pipeline import run_collection_pipeline

router = APIRouter(prefix="/market", tags=["market_intelligence"])

class CollectionRequest(BaseModel):
    query: str = Field(min_length=1, max_length=256)
    category: Optional[str] = Field(default=None, max_length=128)

@router.post("/collect", status_code=status.HTTP_202_ACCEPTED)
def collect(
    request: CollectionRequest, 
    background_tasks: BackgroundTasks,
    principal: Principal = Depends(require_permission("supplier:write")), 
    db: Session = Depends(get_db)
):
    # Run pipeline in background so it does not block the client request
    background_tasks.add_task(run_collection_pipeline, db, request.query, request.category)
    return {"message": "Collection job scheduled successfully"}

@router.get("/products")
def get_products(
    principal: Principal = Depends(require_permission("supplier:read")),
    db: Session = Depends(get_db)
):
    products = db.scalars(select(MarketProduct).order_by(MarketProduct.name.asc())).all()
    return {
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "manufacturer": p.manufacturer,
                "category": p.category
            }
            for p in products
        ]
    }

@router.get("/suppliers/search")
def search_suppliers(
    product: Optional[str] = None,
    category: Optional[str] = None,
    principal: Principal = Depends(require_permission("supplier:read")),
    db: Session = Depends(get_db)
):
    query = select(MarketSupplier)
    if product:
        # Find products matching query, then find their suppliers
        product_query = product.lower()
        subquery = select(MarketPriceObservation.supplier_id).join(MarketProduct).where(
            MarketProduct.name.ilike(f"%{product_query}%")
        )
        query = query.where(MarketSupplier.id.in_(subquery))
    if category:
        subquery_cat = select(MarketPriceObservation.supplier_id).join(MarketProduct).where(
            MarketProduct.category.ilike(f"%{category}%")
        )
        query = query.where(MarketSupplier.id.in_(subquery_cat))
        
    suppliers = db.scalars(query).all()
    
    results = []
    for sup in suppliers:
        # Find the prices/products offered by this supplier
        obs_query = select(MarketPriceObservation).where(MarketPriceObservation.supplier_id == sup.id)
        if product:
            obs_query = obs_query.join(MarketProduct).where(MarketProduct.name.ilike(f"%{product}%"))
        obs = db.scalars(obs_query).all()
        
        for o in obs:
            prod = db.get(MarketProduct, o.product_id)
            results.append({
                "id": sup.id,
                "name": sup.name,
                "product_name": prod.name if prod else "Unknown Product",
                "product_id": prod.id if prod else None,
                "price": float(o.price),
                "currency": o.currency,
                "availability": o.availability,
                "source": o.source,
                "confidence": 0.95 # Generic default high confidence for catalog sources
            })
            
    return {"suppliers": results}

@router.get("/prices")
def get_prices(
    product_id: Optional[str] = None,
    supplier_id: Optional[str] = None,
    principal: Principal = Depends(require_permission("supplier:read")),
    db: Session = Depends(get_db)
):
    query = select(MarketPriceObservation)
    if product_id:
        query = query.where(MarketPriceObservation.product_id == product_id)
    if supplier_id:
        query = query.where(MarketPriceObservation.supplier_id == supplier_id)
    
    observations = db.scalars(query.order_by(MarketPriceObservation.collected_at.desc())).all()
    
    return {
        "observations": [
            {
                "id": o.id,
                "product_id": o.product_id,
                "supplier_id": o.supplier_id,
                "price": float(o.price),
                "currency": o.currency,
                "unit": o.unit,
                "pack_quantity": o.pack_quantity,
                "normalized_unit_price": float(o.normalized_unit_price),
                "collected_at": o.collected_at.isoformat()
            }
            for o in observations
        ]
    }

@router.get("/benchmark/{market_product_id}")
def get_benchmark(
    market_product_id: str,
    principal: Principal = Depends(require_permission("supplier:read")),
    db: Session = Depends(get_db)
):
    market_product = db.get(MarketProduct, market_product_id)
    if not market_product:
        raise HTTPException(status_code=404, detail="Market product not found")
        
    observations = db.scalars(
        select(MarketPriceObservation)
        .where(MarketPriceObservation.product_id == market_product_id)
        .order_by(MarketPriceObservation.collected_at.desc())
    ).all()
    
    if not observations:
        return {
            "product_name": market_product.name,
            "market_median": 0.0,
            "lowest_price": 0.0,
            "highest_price": 0.0,
            "sample_count": 0,
            "internal_price": 0.0,
            "price_variance_percentage": 0.0,
            "potential_savings": 0.0,
            "internal_quantity": 0.0
        }
        
    prices = [float(obs.normalized_unit_price) for obs in observations]
    prices.sort()
    lowest = prices[0]
    highest = prices[-1]
    
    n = len(prices)
    if n % 2 == 1:
        median = prices[n // 2]
    else:
        median = (prices[n // 2 - 1] + prices[n // 2]) / 2.0
        
    avg = sum(prices) / n
    
    # Match internal product to compare
    internal_product = None
    if market_product.sku:
        internal_product = db.scalar(
            select(Product).where(Product.tenant_id == principal.tenant_id, Product.sku == market_product.sku)
        )
    if not internal_product:
        internal_product = db.scalar(
            select(Product).where(Product.tenant_id == principal.tenant_id, Product.normalized_name == market_product.normalized_name)
        )
        
    internal_price = 0.0
    variance_pct = 0.0
    potential_savings = 0.0
    total_qty = 0.0
    
    if internal_product:
        invoice_items = db.scalars(
            select(InvoiceItem)
            .join(Invoice)
            .where(Invoice.tenant_id == principal.tenant_id, InvoiceItem.product_id == internal_product.id)
        ).all()
        
        if invoice_items:
            internal_prices = [float(item.unit_price) for item in invoice_items]
            total_qty = sum(float(item.quantity) for item in invoice_items)
            internal_prices.sort()
            
            m_n = len(internal_prices)
            if m_n % 2 == 1:
                internal_price = internal_prices[m_n // 2]
            else:
                internal_price = (internal_prices[m_n // 2 - 1] + internal_prices[m_n // 2]) / 2.0
            
            if median > 0:
                variance_pct = ((internal_price - median) / median) * 100.0
                if internal_price > median:
                    potential_savings = (internal_price - median) * total_qty
                    
    return {
        "product_name": market_product.name,
        "market_median": round(median, 2),
        "lowest_price": round(lowest, 2),
        "highest_price": round(highest, 2),
        "average_price": round(avg, 2),
        "sample_count": len(prices),
        "internal_price": round(internal_price, 2),
        "price_variance_percentage": round(variance_pct, 2),
        "potential_savings": round(potential_savings, 2),
        "internal_quantity": total_qty
    }
