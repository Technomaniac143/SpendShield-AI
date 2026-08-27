# Hyperledger Fabric provenance

## Architecture
PostgreSQL remains the application source of truth. PDFs stay in MinIO/S3; only SHA-256 fingerprints and minimal procurement event metadata are sent to Fabric. Fabric runs the immutable provenance ledger on `spendchannel` with the `spendshield` chaincode.

The backend uses `app/integrations/blockchain/fabric_client.py` as a transport adapter. It maintains one JSON-lines Node worker using the official `@hyperledger/fabric-gateway` package and configured Org1 credentials. There is no in-memory or simulated ledger.

## Network setup on Windows
Use WSL2 or Git Bash with Docker Desktop running. From the `fabric-samples/test-network` directory:

```bash
./network.sh down
./network.sh up createChannel -c spendchannel -ca
./network.sh deployCC -ccn spendshield -ccp /mnt/d/Hackfusion/SpendShield-AI/fabric/chaincode/spendshield -ccl javascript -c spendchannel
```

Install dependencies once:

```bash
cd /mnt/d/Hackfusion/SpendShield-AI/fabric/chaincode/spendshield && npm install
cd /mnt/d/Hackfusion/SpendShield-AI/fabric/client && npm install
cd /mnt/d/Hackfusion/SpendShield-AI/backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
alembic upgrade head
```

Set the paths in `backend/.env` to the Org1 certificate, private key, and TLS CA certificate from `fabric-samples/test-network/organizations`. Never commit those files.

## Ledger schema and operations
Each `eventId` is a unique world-state key. `RegisterEvidence` validates required fields, supported event types, SHA-256 formats, duplicate keys, and writes deterministic JSON containing the supplied timestamp plus the actual `ctx.stub.getTxID()`. It emits `EvidenceRegistered`. `GetEvidence`, `GetEvent`, `VerifyEvidence`, `EvidenceExists`, and `GetEvidenceHistory` are chaincode operations. Corrections are new event IDs; no update function exists.

## Application flow
For a document upload, the server stores the PDF in S3/MinIO and calculates SHA-256. PostgreSQL atomically stores the evidence row and a `fabric_outbox` command. `python scripts/run_fabric_worker.py` submits the command through the persistent Gateway worker and stores the actual Fabric transaction ID. A failed submission remains pending with durable retry state. Block metadata is resolved with `getBlockByTransactionId` and a SHA-256 hash of the real Fabric block header; it is never invented.

## API
- `POST /api/v1/evidence/{event_id}/register` (multipart PDF upload)
- `GET /api/v1/evidence/{event_id}` (tenant derived from bearer principal)
- `POST /api/v1/evidence/{event_id}/verify`
- `GET /api/v1/evidence/{event_id}/history`
- `POST /api/v1/evidence/{event_id}/simulate-modification`
- `GET /api/v1/evidence/{event_id}/blockchain`

All routes require `Authorization: Bearer <signed principal token>`. Tenant and actor values are derived server-side. The client never supplies the authoritative document hash; verification reads the stored PDF and compares its server-side hash to the hash returned by Fabric.

## Demo
Start Fabric, configure `.env`, run the migration, then start the backend and worker from `backend`:

```bash
uvicorn app.main:app --reload --port 8000
python scripts/run_fabric_worker.py
```

Register a SHA-256 evidence event, query it, verify the same hash, submit the simulated modification endpoint, and query history. The history contains the original Fabric transaction and the original state remains unchanged. Use Fabric CLI queries against `spendchannel` to inspect committed blocks and transaction validation.

Reset the network with `./network.sh down`; recreate it with the setup commands above. Common failures are missing Docker Desktop, incorrect WSL path conversion, expired Fabric certificates, wrong `FABRIC_PEER_HOST_ALIAS`, and a chaincode package path that is not visible inside the Docker environment.
