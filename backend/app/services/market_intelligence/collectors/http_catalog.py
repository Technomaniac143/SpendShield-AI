import json
import re
import urllib.request
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List
from app.services.market_intelligence.collectors.base import BaseCollector
from app.services.market_intelligence.collectors.robots import is_allowed_by_robots
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class HttpCatalogCollector(BaseCollector):
    def __init__(self):
        settings = get_settings()
        self.user_agent = settings.market_user_agent
        self.timeout = settings.market_collection_timeout
        self.max_results = settings.market_collection_max_results

    def search(self, query: str) -> List[Dict[str, Any]]:
        # Implement fallback search query logic if query is a URL
        if query.startswith("http://") or query.startswith("https://"):
            return self.fetch_and_parse_html(query)
            
        # If query is normal text, we can search a default permitted mock repository index
        # to fetch and return real/realistic structure
        return []

    def fetch_and_parse_html(self, url: str) -> List[Dict[str, Any]]:
        if not is_allowed_by_robots(url, self.user_agent):
            logger.warning(f"Crawling forbidden by robots.txt for: {url}")
            return []

        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': self.user_agent}
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                html_content = response.read().decode('utf-8', errors='ignore')
            
            return self.parse_html(html_content, url)
        except Exception as e:
            logger.error(f"Failed to fetch/parse HTML catalog at {url}: {e}")
            return []

    def parse_html(self, html: str, url: str) -> List[Dict[str, Any]]:
        results = []
        collected_at = datetime.now(timezone.utc).isoformat()
        
        # 1. Parse JSON-LD scripts
        json_ld_pattern = re.compile(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)
        for match in json_ld_pattern.finditer(html):
            try:
                data = json.loads(match.group(1).strip())
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if item.get("@type") == "Product" or "name" in item:
                        offers = item.get("offers", {})
                        price = None
                        currency = "INR"
                        availability = "IN_STOCK"
                        
                        if isinstance(offers, dict):
                            price = offers.get("price")
                            currency = offers.get("priceCurrency", "INR")
                            availability = "IN_STOCK" if "InStock" in offers.get("availability", "") else "LIMITED"
                        elif isinstance(offers, list) and len(offers) > 0:
                            price = offers[0].get("price")
                            currency = offers[0].get("priceCurrency", "INR")
                        
                        if price:
                            results.append({
                                "source": "http_catalog",
                                "supplier_name": item.get("brand", {}).get("name", "Public Supplier") if isinstance(item.get("brand"), dict) else (item.get("brand") or "Public Supplier"),
                                "product_name": item.get("name", ""),
                                "sku": item.get("sku"),
                                "manufacturer": item.get("brand", {}).get("name", "") if isinstance(item.get("brand"), dict) else (item.get("brand") or ""),
                                "model": item.get("model"),
                                "price": float(price) if isinstance(price, (int, float)) else float(str(price).replace(',', '')),
                                "currency": currency,
                                "unit": "piece",
                                "pack_quantity": 1,
                                "availability": availability,
                                "product_url": url,
                                "collected_at": collected_at
                            })
            except Exception as e:
                logger.debug(f"JSON-LD parse error: {e}")

        # 2. OG / Meta tags fallback
        if not results:
            title_match = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
            price_match = re.search(r'<meta[^>]*property=["\']product:price:amount["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
            curr_match = re.search(r'<meta[^>]*property=["\']product:price:currency["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
            
            if title_match and price_match:
                try:
                    price_val = float(price_match.group(1).strip().replace(',', ''))
                    curr_val = curr_match.group(1).strip() if curr_match else "INR"
                    results.append({
                        "source": "http_catalog",
                        "supplier_name": "Public Catalog Merchant",
                        "product_name": title_match.group(1).strip(),
                        "sku": None,
                        "manufacturer": None,
                        "model": None,
                        "price": price_val,
                        "currency": curr_val,
                        "unit": "piece",
                        "pack_quantity": 1,
                        "availability": "IN_STOCK",
                        "product_url": url,
                        "collected_at": collected_at
                    })
                except Exception:
                    pass

        return results
