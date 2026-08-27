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
