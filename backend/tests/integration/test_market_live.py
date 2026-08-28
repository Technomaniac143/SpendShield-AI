import os
import pytest
from app.services.market_intelligence.collectors.http_catalog import HttpCatalogCollector
from app.core.config import get_settings

@pytest.mark.skipif(
    os.getenv("RUN_MARKET_LIVE", "0") != "1",
    reason="RUN_MARKET_LIVE env variable not set to 1"
)
def test_live_market_smoke_check():
    settings = get_settings()
    collector = HttpCatalogCollector()
    # Try fetching a public search engine page or known public catalog safely
    url = "https://schema.org/Product"
    results = collector.fetch_and_parse_html(url)
    # Schema.org product page won't have standard price offers but we verify it parses or handles gracefully
    assert isinstance(results, list)
