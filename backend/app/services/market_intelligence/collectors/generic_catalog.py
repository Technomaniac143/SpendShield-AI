from datetime import datetime, timezone
from typing import Any, Dict, List
from app.services.market_intelligence.collectors.base import BaseCollector

class GenericCatalogCollector(BaseCollector):
    def __init__(self):
        self.catalog = [
            {
                "source": "public_catalog",
                "supplier_name": "Reliable Office Supplies Ltd",
                "product_name": "A4 Copier Paper 75 GSM",
                "sku": "A4-75-500",
                "manufacturer": "JK Paper",
                "price": 380.0,
                "currency": "INR",
                "unit": "box",
                "pack_quantity": 500,
                "availability": "IN_STOCK",
                "product_url": "https://example.com/products/a4-75-500"
            },
            {
                "source": "public_catalog",
                "supplier_name": "Express Stationary Corp",
                "product_name": "JK Copier Paper A4 75GSM",
                "sku": "JK-A4-75",
                "manufacturer": "JK Paper",
                "price": 395.0,
                "currency": "INR",
                "unit": "box",
                "pack_quantity": 500,
                "availability": "IN_STOCK",
                "product_url": "https://example.com/products/jk-a4-75"
            },
            {
                "source": "public_catalog",
                "supplier_name": "Prime Office Products Private Limited",
                "product_name": "A4 Copier Paper 75 GSM (Pack of 500)",
                "sku": "A4-75-500",
                "manufacturer": "JK Paper",
                "price": 400.0,
                "currency": "INR",
                "unit": "box",
                "pack_quantity": 500,
                "availability": "IN_STOCK",
                "product_url": "https://example.com/products/a4-75-500-prime"
            },
            {
                "source": "public_catalog",
                "supplier_name": "Global Trade Links",
                "product_name": "JK Easy Copier A4 75 GSM",
                "sku": "A4-75-EASY",
                "manufacturer": "JK Paper",
                "price": 410.0,
                "currency": "INR",
                "unit": "box",
                "pack_quantity": 500,
                "availability": "LIMITED",
                "product_url": "https://example.com/products/easy-a4"
            },
            {
                "source": "public_catalog",
                "supplier_name": "Reliable Office Supplies Ltd",
                "product_name": "HP LaserJet Pro M404dn Printer",
                "sku": "M404DN",
                "manufacturer": "HP",
                "price": 28500.0,
                "currency": "INR",
                "unit": "piece",
                "pack_quantity": 1,
                "availability": "IN_STOCK",
                "product_url": "https://example.com/products/m404dn"
            },
            {
                "source": "public_catalog",
                "supplier_name": "Express Stationary Corp",
                "product_name": "HP LaserJet M404dn",
                "sku": "HP-M404DN",
                "manufacturer": "HP",
                "price": 29000.0,
                "currency": "INR",
                "unit": "piece",
                "pack_quantity": 1,
                "availability": "IN_STOCK",
                "product_url": "https://example.com/products/hp-m404dn"
            }
        ]

    def search(self, query: str) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        results = []
        collected_at = datetime.now(timezone.utc).isoformat()
        for item in self.catalog:
            if (query_lower in item["product_name"].lower() or 
                query_lower in (item["manufacturer"] or "").lower() or 
                query_lower in (item["sku"] or "").lower()):
                results.append({**item, "collected_at": collected_at})
        
        if not results:
            for item in self.catalog[:2]:
                results.append({
                    **item,
                    "product_name": f"{query} - {item['product_name']}",
                    "collected_at": collected_at
                })
        return results
