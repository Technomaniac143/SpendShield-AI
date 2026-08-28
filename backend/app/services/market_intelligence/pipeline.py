from datetime import datetime, timezone
from typing import Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.services.market_intelligence.models import MarketCollectionJob, MarketSupplier, MarketProduct, MarketPriceObservation
from app.services.market_intelligence.collectors.generic_catalog import GenericCatalogCollector
from app.services.market_intelligence.normalizers.product import normalize_product_name
from app.services.market_intelligence.normalizers.supplier import normalize_supplier_name
from app.services.market_intelligence.normalizers.price import normalize_currency
from app.services.market_intelligence.matching.product_matcher import match_product, match_supplier

from datetime import datetime, timezone, timedelta
from typing import Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.services.market_intelligence.models import MarketCollectionJob, MarketSupplier, MarketProduct, MarketPriceObservation
from app.services.market_intelligence.collectors.generic_catalog import GenericCatalogCollector
from app.services.market_intelligence.collectors.http_catalog import HttpCatalogCollector
from app.services.market_intelligence.collectors.search_provider import SearchProviderCollector
from app.services.market_intelligence.normalizers.product import normalize_product_name
from app.services.market_intelligence.normalizers.supplier import normalize_supplier_name
from app.services.market_intelligence.normalizers.price import normalize_currency, parse_price_string, normalize_pack_and_unit
from app.services.market_intelligence.matching.product_matcher import match_product, match_supplier
from app.core.config import get_settings

def run_collection_pipeline(db: Session, query: str, category: str | None = None) -> Dict[str, Any]:
    settings = get_settings()
    mode = settings.market_intelligence_mode
    
    # Create the Collection Job
    job = MarketCollectionJob(
        source=f"pipeline_{mode}",
        query=query,
        status="RUNNING",
        started_at=datetime.now(timezone.utc)
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    try:
        # Load collectors based on configuration mode
        collectors = []
        if mode == "web":
            # Web mode utilizes HTTP HTML scrapers and search providers
            collectors.append(HttpCatalogCollector())
            collectors.append(SearchProviderCollector())
        else:
            # Default to mock/sandbox mode
            collectors.append(GenericCatalogCollector())
            
        raw_records = []
        for collector in collectors:
            try:
                records = collector.search(query)
                if records:
                    raw_records.extend(records)
            except Exception as ce:
                # Log collector specific error and continue
                print(f"Collector search failure: {ce}")
                
        records_found = len(raw_records)
        records_inserted = 0
        records_updated = 0
        records_failed = 0
        
        for raw in raw_records:
            price_val = raw.get("price")
            supplier_name = raw.get("supplier_name")
            product_name = raw.get("product_name")
            currency = raw.get("currency")
            
            if not supplier_name or not product_name or price_val is None:
                records_failed += 1
                continue
                
            # If price is a string, parse it
            if isinstance(price_val, str):
                price_val, extracted_curr = parse_price_string(price_val)
                if not currency:
                    currency = extracted_curr
                    
            if not currency:
                currency = "INR"
                
            # Normalize
            norm_product = normalize_product_name(product_name)
            norm_supplier = normalize_supplier_name(supplier_name)
            norm_curr = normalize_currency(currency)
            
            # Resolve Supplier
            matched_sup, _, _ = match_supplier(db, supplier_name)
            if not matched_sup:
                matched_sup = MarketSupplier(
                    name=supplier_name,
                    normalized_name=norm_supplier,
                    source=raw.get("source", "public_catalog"),
                    source_url=raw.get("product_url"),
                    status="ACTIVE"
                )
                db.add(matched_sup)
                db.commit()
                db.refresh(matched_sup)
                
            # Resolve Product
            matched_prod, _, _ = match_product(db, product_name, sku=raw.get("sku"), manufacturer=raw.get("manufacturer"))
            if not matched_prod:
                matched_prod = MarketProduct(
                    name=product_name,
                    normalized_name=norm_product,
                    sku=raw.get("sku"),
                    manufacturer=raw.get("manufacturer"),
                    category=category
                )
                db.add(matched_prod)
                db.commit()
                db.refresh(matched_prod)
                
            collected_at_str = raw.get("collected_at")
            collected_at = datetime.fromisoformat(collected_at_str) if collected_at_str else datetime.now(timezone.utc)
            
            # Calculate freshness
            now = datetime.now(timezone.utc)
            diff = now - collected_at
            if diff < timedelta(days=1):
                freshness = "Fresh"
            elif diff < timedelta(days=7):
                freshness = "Recent"
            elif diff < timedelta(days=30):
                freshness = "Stale"
            else:
                freshness = "Expired"
                
            # Compute Unit Price
            pack_qty = raw.get("pack_quantity", 1) or 1
            unit_str = raw.get("unit", "piece") or "piece"
            norm_unit_price, norm_pack_qty, norm_unit = normalize_pack_and_unit(price_val, unit_str)
            if norm_pack_qty != pack_qty:
                pack_qty = norm_pack_qty
            
            # Prevent Duplicate Observations on the same calendar day for same supplier/product/price
            start_of_day = collected_at.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            existing_obs = db.scalar(
                select(MarketPriceObservation).where(
                    MarketPriceObservation.supplier_id == matched_sup.id,
                    MarketPriceObservation.product_id == matched_prod.id,
                    MarketPriceObservation.price == price_val,
                    MarketPriceObservation.collected_at >= start_of_day,
                    MarketPriceObservation.collected_at < end_of_day
                )
            )
            
            if existing_obs:
                records_updated += 1
                continue
                
            # Quality Scoring calculation
            q_score = 0.50
            if raw.get("sku"): q_score += 0.15
            if raw.get("manufacturer"): q_score += 0.15
            if raw.get("availability") == "IN_STOCK": q_score += 0.10
            if raw.get("product_url"): q_score += 0.10
            q_score = min(q_score, 1.00)
            
            obs = MarketPriceObservation(
                supplier_id=matched_sup.id,
                product_id=matched_prod.id,
                price=price_val,
                currency=norm_curr,
                unit=unit_str,
                pack_quantity=pack_qty,
                normalized_unit_price=norm_unit_price,
                normalized_unit=norm_unit,
                availability=raw.get("availability", "IN_STOCK"),
                source=raw.get("source", "public_catalog"),
                source_url=raw.get("product_url"),
                raw_product_name=product_name,
                raw_supplier_name=supplier_name,
                quality_score=q_score,
                freshness=freshness,
                collected_at=collected_at
            )
            db.add(obs)
            records_inserted += 1
            
        db.commit()
        
        job.records_found = records_found
        job.records_inserted = records_inserted
        job.records_updated = records_updated
        job.records_failed = records_failed
        job.status = "COMPLETED"
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
        
    except Exception as e:
        db.rollback()
        job.status = "FAILED"
        job.error_message = str(e)
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
        
    return {
        "job_id": job.id,
        "status": job.status,
        "records_found": job.records_found,
        "records_inserted": job.records_inserted,
        "records_updated": job.records_updated,
        "records_failed": job.records_failed,
        "error_message": job.error_message
    }
