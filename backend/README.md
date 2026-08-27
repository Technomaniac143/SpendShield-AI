# SpendShield backend

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Configure real Fabric credential paths in `.env` before registration. Without a running Fabric network, registration is explicitly returned as `PENDING_BLOCKCHAIN_VERIFICATION`.
