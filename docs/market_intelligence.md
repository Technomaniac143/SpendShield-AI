# Web Supplier & Market Intelligence Module

Collects publicly available supplier/product/price information from permitted web sources, normalizes it, stores it in the database, and compares it with internal procurement records to benchmark pricing and recommend alternative sources.

## Architecture

```text
Public Sources
      ↓
GenericCatalogCollector / Custom Collectors
      ↓
Parser
      ↓
Normalizer (product, supplier, price)
      ↓
Entity Resolution / Matching (exact SKU, name exact, fuzzy)
      ↓
SQLite Database (market_collection_jobs, market_products, market_suppliers, market_price_observations)
      ↓
Supplier & Price Intelligence API
      ↓
Savings / Benchmark Engine
      ↓
SpendShield Dashboard (Market Intelligence Tab)
```

## Database Schema

### `market_suppliers`
Holds unique resolved market suppliers.
- `id` (String-36, PK)
- `name` (String-256)
- `normalized_name` (String-256, Index, Unique)
- `source` (String-64)
- `website`, `description`, `country`, `location`, `supplier_type`, `source_url`, `status`

### `market_products`
Holds unique resolved market products.
- `id` (String-36, PK)
- `name` (String-256)
- `normalized_name` (String-256, Index, Unique)
- `sku` (String-128, Index)
- `manufacturer`, `model`, `category`, `description`

### `market_price_observations`
Logs price observations over time.
- `id` (String-36, PK)
- `supplier_id` (FK to `market_suppliers.id`)
- `product_id` (FK to `market_products.id`)
- `price` (Numeric)
- `currency` (String-3)
- `unit` (String-32)
- `pack_quantity` (Integer)
- `normalized_unit_price` (Numeric)
- `normalized_unit` (String-32)
- `availability` (String-32)
- `source` (String-64)
- `collected_at` (DateTime, Index)

### `market_collection_jobs`
Audit log of scraping jobs.
- `id` (String-36, PK)
- `source`, `query`, `status`, `records_found`, `records_inserted`, `records_updated`, `records_failed`, `error_message`, `started_at`, `completed_at`

## Normalization & Matching

- **Product & Supplier Normalization**: Trims whitespace, lowercases text, standardizes units (e.g. `GSM`, pack sizes), and strips corporate suffixes (`Private Limited`, `Corp`, etc.).
- **Product Matcher**: Performs progressive matching using exact SKU, exact normalized name match, and fuzzy match ratios (`difflib.SequenceMatcher`).
- **Benchmark Algorithm**: Calculates market stats (median, min, max, average) and variance percentage against internal invoices for the matched product.

## API Endpoints

- `POST /api/v1/market/collect` -> Run collection job asynchronously.
- `GET /api/v1/market/products` -> List all collected products.
- `GET /api/v1/market/suppliers/search` -> Discover alternative suppliers.
- `GET /api/v1/market/prices` -> Retrieve price history.
- `GET /api/v1/market/benchmark/{product_id}` -> Calculate market benchmark stats and compare with internal procurement data.
