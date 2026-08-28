# SpendShield backend

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Configure real Fabric credential paths and S3/MinIO credentials in `.env` before registration. Run the outbox worker in a second terminal:

```bash
python scripts/run_fabric_worker.py
```

Registration is persisted as `PENDING_BLOCKCHAIN_VERIFICATION` until that worker submits it to Fabric.

## Implemented status

| Capability | Status |
|---|---|
| Signed principal authentication | Implemented with expiring tokens |
| Tenant-scoped evidence API | Implemented for application records |
| Bounded PDF upload and SHA-256 verification | Implemented |
| S3/MinIO storage compensation and streaming hash | Implemented |
| Fabric provenance | Implemented; requires a configured Fabric network |
| Recoverable Fabric outbox | Implemented with leases and retry scheduling |
| Procurement entities | Implemented through suppliers, products, POs, GRNs, invoices, payments, inventory, and supporting event tables |
| Tenant-scoped procurement CRUD | Implemented with decimal totals and foreign-key validation |
| Three-way reconciliation | Implemented as deterministic calculation API; database-backed reconciliation persistence is pending |
| True-cost calculation | Implemented as deterministic calculation API |
| Quantity exposure | Implemented as deterministic calculation API |
| CSV/XLSX ingestion | Implemented with bounded uploads, SHA-256, background processing, row errors, and partial success |
| Ingestion idempotency | Implemented by tenant-scoped idempotency key and file hash |
| Deterministic ingestion entity resolution | Implemented by normalized supplier name and product SKU/name |
| Ingestion analytics trigger | Hook implemented; downstream analytics are not yet connected |
| OCR, graph, ML, AuditAgent, recommendations, outcomes | Not implemented |
| Redis, Celery, Neo4j, frontend, Dockerized Fabric | Not implemented in this repository |

## Local stack

From the repository root, run `docker compose up --build`. The API is available at
`http://localhost:8000`, PostgreSQL at `localhost:5432`, and MinIO at
`http://localhost:9001`. Create the `spendshield-evidence` bucket in MinIO before
using evidence registration. Fabric remains an external dependency; follow
`docs/hyperledger-fabric.md` for network setup.

After migrations, create the first administrator with:

```bash
python -m app.seed --tenant-name "Demo Tenant" --email admin@example.com --password "change-this-password"
```

## Ingestion

Authenticated users with the ingestion permissions can upload `.csv` or `.xlsx`
files using an explicit `entity_type` query value. Supported types are
`suppliers`, `products`, `purchase_orders`, `purchase_order_items`,
`goods_receipts`, `goods_receipt_items`, `invoices`, `invoice_items`, `payments`,
`inventory`, and `inventory_movements`.

```bash
curl -X POST "http://localhost:8000/api/v1/ingestion/csv?entity_type=suppliers" \
	-H "Authorization: Bearer ACCESS_TOKEN" \
	-H "Idempotency-Key: suppliers-import-001" \
	-F "document=@suppliers.csv"
```

Uploads are bounded by `MAX_INGESTION_BYTES` (100 MB by default), stored under a
tenant-scoped generated key, and processed by a FastAPI background-task queue seam.
The current queue runs in-process; a durable Redis/Celery worker is a later phase.
`.xls` is intentionally unsupported and returns `422`.
