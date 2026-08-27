# SpendShield AI — Project Context

> **Read this file first.** This is the single source of truth for what SpendShield AI is,
> how it's architected, and how backend/frontend must agree with each other. Full detailed
> specs live in `/docs/backend-prompt.md` and `/docs/frontend-prompt.md` — refer to those for
> exhaustive detail; this file is the fast-context summary an IDE/AI agent should load first.

---

## 1. What This Product Is

**SpendShield AI** — an AI Procurement Investigation & Outcome Intelligence Platform.

It is **not** a generic finance dashboard and **not** a chatbot wrapper. It is an
**evidence-first decision-support system** that turns raw procurement records into
investigated, quantified, human-approved, and outcome-tracked financial decisions.

**Core pipeline (applies to backend logic AND frontend narrative):**

```
RAW DATA → NORMALIZATION → ENTITY RESOLUTION → RECONCILIATION → ANOMALY DETECTION
→ RELATIONSHIP ANALYSIS → INVESTIGATION → TRUE-COST ANALYSIS → FINANCIAL EXPOSURE
→ RISK SCORING → RECOMMENDATION → HUMAN DECISION → EVIDENCE VERIFICATION
→ OUTCOME → LEARNING
```

**Core product workflow (frontend framing):**
`DETECT → CONNECT → INVESTIGATE → QUANTIFY → RECOMMEND → ACT → VERIFY → LEARN`

The most important screen is the **Investigation Workspace**.

### Non-negotiable engineering principles
1. Deterministic business logic beats LLM reasoning for financial calculations.
2. Evidence beats assertions — every AI conclusion must reference evidence.
3. PostgreSQL is the transactional source of truth.
4. Neo4j is for relationships, not financial authority.
5. Blockchain (Hyperledger Fabric) verifies evidence provenance only — never stores
   business documents on-chain, never used for ordinary analytics.
6. AI recommends; humans approve high-impact actions (human-in-the-loop).
7. Every financial number must have a traceable calculation source.
8. Tenant isolation is mandatory everywhere (API, service, DB, graph, storage, cache).
9. Potential savings must never be presented as realized savings.
10. The backend must remain useful even when the LLM is unavailable.

---

## 2. Monorepo Layout (assumed)

```
/
├── backend/     ← FastAPI modular monolith (see §3)
├── frontend/    ← React + TS + Vite (see §4)
└── docs/
    ├── backend-prompt.md   ← full original backend spec (verbatim)
    └── frontend-prompt.md  ← full original frontend spec (verbatim)
```

---

## 3. Backend

### 3.1 Stack
- Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic
- PostgreSQL (system of record) + pgvector (prefer over separate vector DB)
- Redis (cache + task broker)
- Celery (or equivalent) for background tasks
- Neo4j (official Python driver) — relationship graph only
- Hyperledger Fabric — evidence/provenance only
- MinIO (local/demo) → S3-compatible abstraction for prod
- ML: scikit-learn, pandas, NumPy, sentence-transformers, XGBoost/LightGBM where justified
- LLM via a clean provider-abstraction layer (never hard-coded to one vendor)
- Documents: PyMuPDF, python-multipart, OCR abstraction, Pillow
- Auth: JWT/OAuth2-compatible, bcrypt/Argon2, CORS, rate limiting, structured audit logging
- Testing: pytest, pytest-asyncio, httpx, factory-boy

### 3.2 Architecture shape
Modular FastAPI monolith with clear domain boundaries — **not** microservices for the
hackathon build:

```
CLIENT → API GATEWAY/API → FASTAPI
  → PROCUREMENT DOMAIN / INTELLIGENCE DOMAIN / INVESTIGATION DOMAIN
  → PostgreSQL / Redis / (pgvector)
  → Neo4j (graph)
  → Hyperledger Fabric (blockchain evidence)
  → Object storage (MinIO/S3)
```

### 3.3 Project structure
```
backend/
├── app/
│   ├── main.py
│   ├── api/v1/         # auth, dashboard, suppliers, transactions, invoices,
│   │                   # procurement, investigations, graph, inventory,
│   │                   # recommendations, evidence, outcomes, health
│   ├── core/           # config, security, database, logging, exceptions
│   ├── models/         # tenant, user, supplier, product, purchase_order,
│   │                   # goods_receipt, invoice, payment, contract, inventory,
│   │                   # anomaly, investigation, recommendation, evidence, outcome
│   ├── schemas/
│   ├── services/        # ingestion, reconciliation, anomaly, supplier, graph,
│   │                    # investigation, true_cost, exposure, inventory, risk,
│   │                    # recommendation, evidence, blockchain, outcomes
│   ├── ml/              # features, models, training, inference, evaluation
│   ├── agents/          # audit_agent.py, tools.py, prompts.py, policies.py
│   ├── workers/         # tasks.py, scheduler.py
│   ├── integrations/    # erp, storage, llm, blockchain
│   └── utils/
├── tests/ migrations/ scripts/ data/ docker/
├── docker-compose.yml Dockerfile requirements.txt .env.example README.md
```

### 3.4 Multi-tenancy & auth
- Core entities: `Tenant`, `User`, `Role`. Every business record carries `tenant_id`.
- Isolation enforced at: API authorization, service layer, DB queries, graph queries,
  object storage paths, cache keys (e.g. `tenant:{tenant_id}:supplier:{supplier_id}`).
- Roles: `ADMIN, CFO, PROCUREMENT_MANAGER, FINANCE, AUDITOR, VIEWER`.
- Never trust role info supplied directly by the client.
- Full: login, logout, access + refresh tokens, password hashing, token expiry,
  session invalidation, RBAC.

### 3.5 Core DB tables (PostgreSQL, UUID PKs, timestamps, FKs, indexes, soft delete)
```
tenants, users, roles, suppliers, supplier_attributes, products, contracts,
purchase_orders, purchase_order_items, goods_receipts, goods_receipt_items,
invoices, invoice_items, payments, inventory, inventory_movements,
quality_events, delivery_events, disputes, anomalies, investigations,
investigation_steps, findings, recommendations, decisions, evidence,
evidence_events, blockchain_records, outcomes, audit_logs
```

### 3.6 Core business capabilities (24)
1. PO–GRN–Invoice 3-way matching
2. Exact duplicate invoice detection
3. Near-duplicate invoice detection
4. Vendor price anomaly detection
5. Vendor performance intelligence
6. Supplier risk scoring
7. Procurement relationship graph
8. AI investigation orchestration (AuditAgent)
9. Evidence-grounded explanations
10. True-cost procurement engine
11. Financial exposure calculation
12. Inventory-to-cash intelligence
13. Savings estimation
14. Action recommendation engine
15. Human-in-the-loop decisions
16. Blockchain evidence verification
17. SHA-256 document integrity verification
18. Multi-party procurement event provenance
19. Outcome tracking
20. Outcome-adjusted learning
21. Audit trail
22. RBAC
23. Multi-tenant architecture
24. Real-time investigation events

### 3.7 Data ingestion pipeline
`UPLOAD → VALIDATE → PARSE → NORMALIZE → RESOLVE ENTITIES → STORE → TRIGGER ANALYTICS`
Supports CSV, Excel, JSON, PDF invoices, structured API data.

### 3.8 API surface (v1) — domains
`auth, dashboard, suppliers, transactions, invoices, procurement, anomalies,
investigations, graph, true-cost, exposure, inventory, recommendations,
evidence, outcomes, health` — see `docs/backend-prompt.md` §41 for exact routes.

### 3.9 AuditAgent (investigation orchestrator)
- AI **orchestrates and explains**; deterministic services **calculate**.
- Tool-calling agent (`agents/audit_agent.py`, `tools.py`, `prompts.py`, `policies.py`)
  that pulls supplier risk, transaction reconciliation, duplicate detection, price
  anomaly, performance, graph signals, true-cost comparison — then produces
  evidence-linked findings and recommendations for human decision.
- Every AI conclusion must cite evidence records; no unsupported fraud claims.

### 3.10 MVP priority (hackathon-scoped, build in this order)
```
1. Auth  2. Ingestion  3. PostgreSQL schema  4. PO-GRN-Invoice matching
5. Duplicate invoice detection  6. Price anomaly detection  7. Supplier risk score
8. Financial exposure  9. True-cost engine  10. Investigation API
11. AuditAgent tool orchestration  12. Procurement graph  13. Recommendation engine
14. Human decision  15. SHA-256 evidence verification  16. Hyperledger evidence registration
17. Outcome tracking  18. Frontend API integration
```

### 3.11 Explicitly out of scope for MVP
Microservices everywhere, Kubernetes, complex deep learning, autonomous payment
execution, on-chain document storage, token systems/crypto, blockchain for ordinary
analytics, unrestricted autonomous agents, unnecessary vector DBs, complex event buses,
real-time processing of every record, fake AI reasoning, unsupported fraud claims.

---

## 4. Frontend

### 4.1 Stack
- React + TypeScript + Vite, Tailwind CSS, React Router, Axios, Recharts, React Flow,
  Lucide React icons
- Optional: Zustand (global state), TanStack Query (server state), Zod (validation)
- No unnecessary frameworks.

### 4.2 Design language
Premium enterprise SaaS — modern, minimal, professional, data-dense but readable.
Feel: **enterprise intelligence / financial risk / security investigation console.**
Explicitly avoid: consumer finance app look, generic CRM, generic AI chatbot UI,
excessive gradients/glassmorphism/cartoon illustration/unnecessary animation.

Semantic color rules:
- **RED** — critical risk, blocked payment, integrity failure
- **AMBER** — warning, investigation required, moderate risk
- **GREEN** — verified, safe, realized savings
- **BLUE** — information, AI activity, system intelligence
Use sparingly, don't overuse.

### 4.3 File organization
```
src/
├── app/
├── components/  # common, dashboard, investigation, supplier, transaction,
│                # graph, inventory, recommendation, evidence
├── pages/
├── services/    # api.ts + per-domain: dashboardApi.ts, supplierApi.ts,
│                # transactionApi.ts, investigationApi.ts, graphApi.ts,
│                # inventoryApi.ts, recommendationApi.ts, evidenceApi.ts, outcomeApi.ts
├── hooks/  store/  types/  mocks/  utils/  styles/
```
Never scatter Axios calls directly in components — always go through `services/`.

### 4.4 Routes
```
/dashboard
/investigations            /investigations/:id
/suppliers                 /suppliers/:id
/transactions               /transactions/:id
/graph
/inventory
/recommendations            /recommendations/:id
/evidence                   /evidence/:id
/outcomes
/settings
```

### 4.5 Key screens (in rough priority order)
Command Center (dashboard) → Priority Actions → Procurement Leakage Overview →
Spend Risk Trend → Supplier Risk Table → Inventory-to-Cash widget →
**Investigation Workspace** (Investigation Input → AuditAgent Execution Trace →
Investigation Summary → Findings → Evidence Panel → PO–GRN–Invoice View →
Reconciliation Table → True-Cost Panel → Supplier Comparison) →
Procurement Intelligence Graph → Supplier Profile (performance charts, risk
breakdown) → Transaction page → Invoice detail → Inventory page/actions →
Recommendations (list + detail) → Blockchain/Evidence page → Document
Verification → Dispute view → Outcomes page → Outcome Learning → Global
Search → Filters → Notifications.

### 4.6 Environment
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 4.7 Frontend–backend contract rules
- Backend returns **structured JSON only** — never natural-language strings the
  frontend has to parse for numbers.
  - Correct: `{ "exposure": 840000, "riskScore": 87, "confidence": 0.93 }`
  - Wrong: `{ "message": "The supplier has ₹8.4L exposure." }`
- Full graph / investigation / blockchain data contracts: see
  `docs/frontend-prompt.md` §66–68.

### 4.8 Mock data mode
Frontend must be able to run standalone against `src/mocks/` (demo data) before the
backend is wired up — used for early UI development and hackathon demo fallback.

---

## 5. Demo Script (both sides must support this end-to-end flow)

1. User: "Investigate ABC Industries." → AuditAgent starts investigation.
2. Supplier analysis → `risk = 87`, `confidence = 93%`.
3. Transaction analysis → 80-unit GRN mismatch, ₹40,000 exposure.
4. Duplicate detection → 3 potential near-duplicate invoices.
5. Price analysis → 11.6% price deviation.
6. Supplier performance → 12% delivery delay, 6.2% defect rate.
7. Graph → 2 relationship risk signals.
8. True cost → ABC Industries ₹1,105 vs Supplier B ₹1,060.
9. Recommendation → Hold affected invoice / Investigate supplier / Shift future volume.
10. Evidence → SHA-256 → Hyperledger Fabric → VERIFIED.
11. Human decision → ACCEPT.
12. Outcome recorded → predicted savings, actual savings, cash released.

---

## 6. Working Agreement for the Coding Agent

- Treat `docs/backend-prompt.md` and `docs/frontend-prompt.md` as the exhaustive specs
  (endpoint lists, exact schemas, component-level UI detail, testing strategy, seed
  data, acceptance criteria). This file is the map — go to the detailed doc for the
  territory.
- When backend and frontend specs imply conflicting details, backend's data contract
  wins (frontend renders what backend defines structurally).
- Keep the MVP priority order (§3.10) — don't gold-plate before the hackathon-critical
  path works end-to-end.
- Every new financial calculation needs a clear, traceable source — no numbers invented
  by an LLM.
- Any AI-agent output (findings, recommendations) must carry evidence references.
