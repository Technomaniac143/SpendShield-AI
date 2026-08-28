import pytest
from app.services.market_intelligence.collectors.robots import is_allowed_by_robots
from app.services.market_intelligence.collectors.http_catalog import HttpCatalogCollector

def test_robots_parser_safeguard():
    # Test checking a mock local URL is allowed
    assert is_allowed_by_robots("http://localhost:8000/some-catalog", "SpendShield-MarketIntelligence/1.0") is True

def test_json_ld_parsing():
    html_sample = """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@context": "https://schema.org/",
          "@type": "Product",
          "name": "JK Copier Paper A4 75GSM",
          "sku": "JK-A4-75",
          "brand": {
            "@type": "Brand",
            "name": "JK Paper"
          },
          "offers": {
            "@type": "Offer",
            "price": "350.00",
            "priceCurrency": "INR",
            "availability": "https://schema.org/InStock"
          }
        }
        </script>
      </head>
      <body>
        <h1>Sample Catalog Product</h1>
      </body>
    </html>
    """
    collector = HttpCatalogCollector()
    results = collector.parse_html(html_sample, "https://mocksupplier.com/products/1")
    
    assert len(results) == 1
    record = results[0]
    assert record["product_name"] == "JK Copier Paper A4 75GSM"
    assert record["price"] == 350.00
    assert record["currency"] == "INR"
    assert record["sku"] == "JK-A4-75"
    assert record["manufacturer"] == "JK Paper"
