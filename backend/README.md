# SpendShield AI - Backend

SpendShield AI is an AI Procurement Investigation & Outcome Intelligence Platform. The backend is designed as an evidence-first decision-support platform that normalizes procurement records, reconciles transactions (PO-GRN-Invoice), runs anomaly detection, manages a supplier risk/performance graph, and orchestrates investigations with `AuditAgent`.

---

## Technical Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (System of Record via SQLAlchemy 2.0 Async engine)
- **Graph Database**: Neo4j (Relationship Intelligence Layer)
- **Cache & Jobs**: Redis (Caching & Celery background tasks)
- **Object Storage**: S3-compatible Storage (MinIO or AWS S3)
- **ML / AI**: scikit-learn, pandas, NumPy, sentence-transformers, XGBoost
- **Testing**: pytest & pytest-asyncio

---

## First-Time Setup & Installation

Follow these steps to set up and run the SpendShield AI backend on your local environment.

### 1. Prerequisites
Ensure you have the following installed on your host machine:
- Python 3.11 or higher
- PostgreSQL (running locally or accessible via network)
- Redis (running locally or accessible via network)
- Neo4j (running locally or accessible via network)
- MinIO or an S3 bucket

### 2. Create Virtual Environment
Navigate to the `backend/` directory and set up a virtual environment:

**On Windows:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
Update pip and install all required python libraries:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Environment Variables Setup
Copy the example environment file and update it with your local credentials/paths for PostgreSQL, Redis, Neo4j, and your LLM provider api keys:
```bash
cp .env.example .env
```
Open the `.env` file and modify the database URLs, API Keys, and service configurations as necessary.

### 5. Running Database Migrations
Initialize your database schemas using Alembic:
```bash
# Generate database schema tables
alembic upgrade head
```

---

## Running the Application

### 1. Start the API Server
Start the FastAPI development server with hot-reload enabled:
```bash
uvicorn app.main:app --reload
```
Once started, you can access:
- **API Reference (Swagger Docs)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Docs (Redoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 2. Start Background Workers (Celery)
To execute background tasks (e.g., OCR processing, blockchain events), launch the Celery worker:
```bash
celery -A app.workers.tasks.celery_app worker --loglevel=info
```

---

## Seeding Demo Data
To immediately populate the database with a realistic demo tenant, suppliers (e.g., *ABC Industries*), invoices, POs, and GRNs for the mock presentation flow:
```bash
python scripts/seed_demo.py
```

---

## Testing & ML Training

### Running Automated Tests
We use `pytest` for unit and integration testing. Run the following command from the `backend/` directory:
```bash
# Run all tests
pytest

# Run tests showing stdout details
pytest -s
```

### ML Models & Feature Processing
ML features and models are organized in `app/ml/`.
- **Feature store**: Features are extracted using pipelines under `app/ml/features/`.
- **Training models**: To retrain pricing models or risk models manually, run the respective training script:
```bash
# Example training execution (when training scripts are populated)
python -m app.ml.training.train_risk_model
```
- **Evaluation**: Validate updated models against outcomes before transitioning from `SHADOW` to `ACTIVE`:
```bash
python -m app.ml.evaluation.evaluate_models
```
