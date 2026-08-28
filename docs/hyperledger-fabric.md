# Hyperledger Fabric Provenance Architecture

PostgreSQL remains the application source of truth. PDFs stay in MinIO/S3; only SHA-256 fingerprints and minimal procurement event metadata are sent to Fabric. Fabric runs the immutable provenance ledger on `spendchannel` with the `spendshield` chaincode.

The backend uses `app/integrations/blockchain/fabric_client.py` as a transport adapter. It maintains one JSON-lines Node worker using the official `@hyperledger/fabric-gateway` package and configured Org1 credentials.

## Architecture Flow

```
+------------------+       PDF Upload       +---------------+
|   Upload Client  |----------------------->| SpendShield   |
+------------------+                        | FastAPI Host  |
                                            +---------------+
                                                    |
                                            Save    | Compute SHA-256
                                            PDF     v & Queue Outbox
+------------------+                        +---------------+
|   MinIO/S3       |<-----------------------|  PostgreSQL   |
+------------------+                        +---------------+
                                                    |
                                            Process | Background Worker
                                            Outbox  v
                                            +---------------+
                                            | Gateway Node  |
                                            | gateway.js    |
                                            +---------------+
                                                    |
                                    Submit  | ClientIdentity (CID)
                                    Tx      v Enforces Org1MSP & Roles
                                            +---------------+
                                            | Hyperledger   |
                                            | spendshield   |
                                            | Chaincode     |
                                            +---------------+
```

---

## Hardened Security & Design Features

### 1. Client Identity & Access Control
- **MSP Validation:** The chaincode strictly validates the caller's MSP ID using `fabric-shim`'s `ClientIdentity`. Write actions are rejected if the caller is not from the authorized `Org1MSP`.
- **Role-Based Access Control (RBAC):** Critical write operations (`RegisterEvidence`) require the caller to possess the `writer` role (or `admin`) mapped via certificate attributes (`role` or `spendshield.role`).
- **Least Privilege:** Public read actions (`GetEvidence`, `VerifyEvidence`, `GetEvidenceHistory`) require a valid channel participant certificate but do not require write-level permissions.

### 2. Strict Input & Validation Rules
- **Event ID Validation:** Must match `^[A-Za-z0-9._:-]+$` with a maximum length of 256 characters.
- **Tenant ID Validation:** Multi-tenant isolation is supported by isolating keys and verifying that tenant IDs conform to event ID structure constraints.
- **Event Type Allowlist:** Only approved SpendShield event types are accepted:
  - `INVOICE_REGISTERED`, `GRN_REGISTERED`, `PAYMENT_APPROVED`, `PAYMENT_BLOCKED`
  - `DISPUTE_CREATED`, `DOCUMENT_VERIFIED`, `DOCUMENT_INTEGRITY_FAILED`
  - `RECOMMENDATION_ACCEPTED`, `RECOMMENDATION_REJECTED`, `OUTCOME_RECORDED`
- **Hash Integrity:** Hashes (document and metadata) must be valid 64-character hexadecimal SHA-256 strings.
- **Timestamp Format:** Input dates must strictly conform to ISO-8601 formatting (`YYYY-MM-DDTHH:mm:ssZ` or with offset).
- **Size Guardrails:** All inputs have a maximum character limit of 256 to prevent Denial of Service (DoS) memory attacks.

### 3. Execution Determinism & Stable Serialization
- **Stable JSON Serialization:** Implements a recursive canonical stringify function (`stableStringify`) in the chaincode. This ensures consistent byte representations on all peers regardless of object property ordering, preventing consensus mismatch.
- **No Non-Deterministic Functions:** Banned JavaScript features such as `Date.now()`, `Math.random()`, or network calls are completely absent from smart contract code.

### 4. Safe History Query Guardrails
- **Max History Limit:** A hard limit of `100` historical versions is enforced in `GetEvidenceHistory` to prevent Node OOM memory exhaustion.
- **Safe Iterators:** Iterators are wrapped in `try/finally` blocks ensuring that they are closed cleanly.
- **JSON Error Tolerance:** Malformed or corrupted historical entries are gracefully captured and returned with diagnostic metadata instead of crashing the chaincode execution.

### 5. Safe Transaction Verification (gateway.js)
- **Validation Code Bounds Checking:** Resolves transaction status with exact bounds checking on validation flag bitmasks.
- **Status Mapping:** Provides explicit mapping to `VALID`, `INVALID`, `UNAVAILABLE`, or `NOT_FOUND` statuses, preventing invalid transactions from appearing as successful commitments.

---

## PowerShell Configuration Script

You can use the following PowerShell snippet to prompt for Fabric gateway settings and configure your environment:

```powershell
# Set Default Environment Variables
$env:FABRIC_GATEWAY_URL = Read-Host -Prompt "Enter FABRIC_GATEWAY_URL [grpc://localhost:7051]" -DefaultValue "grpc://localhost:7051"
$env:FABRIC_CHANNEL = Read-Host -Prompt "Enter FABRIC_CHANNEL [spendchannel]" -DefaultValue "spendchannel"
$env:FABRIC_CHAINCODE = Read-Host -Prompt "Enter FABRIC_CHAINCODE [spendshield]" -DefaultValue "spendshield"
$env:FABRIC_CERT_PATH = Read-Host -Prompt "Enter FABRIC_CERT_PATH"
$env:FABRIC_KEY_PATH = Read-Host -Prompt "Enter FABRIC_KEY_PATH"
$env:FABRIC_TLS_CERT_PATH = Read-Host -Prompt "Enter FABRIC_TLS_CERT_PATH"
$env:FABRIC_MSP_ID = Read-Host -Prompt "Enter FABRIC_MSP_ID [Org1MSP]" -DefaultValue "Org1MSP"
$env:FABRIC_PEER_ENDPOINT = Read-Host -Prompt "Enter FABRIC_PEER_ENDPOINT [localhost:7051]" -DefaultValue "localhost:7051"
$env:FABRIC_PEER_HOST_ALIAS = Read-Host -Prompt "Enter FABRIC_PEER_HOST_ALIAS [peer0.org1.example.com]" -DefaultValue "peer0.org1.example.com"
$env:FABRIC_HELPER_PATH = "fabric/client/gateway.js"

# Verify File Paths
foreach ($pathVar in ("FABRIC_CERT_PATH", "FABRIC_KEY_PATH", "FABRIC_TLS_CERT_PATH")) {
    $val = Get-Item -Path (Get-ItemEnv $pathVar) -ErrorAction SilentlyContinue
    if (-not $val) {
        Write-Warning "Warning: Path for $pathVar does not exist locally."
    }
}
```

---

## Local Development & Docker Commands

### 1. Build and Run Infrastructure
From the project root:
```bash
docker compose up -d
```

### 2. Start Hyperledger Fabric Local Network
Within `fabric-samples/test-network`:
```bash
./network.sh down
./network.sh up createChannel -c spendchannel -ca
./network.sh deployCC -ccn spendshield -ccp /path/to/SpendShield-AI/fabric/chaincode/spendshield -ccl javascript -c spendchannel
```

### 3. Deploy Node.js Dependencies
```bash
cd fabric/chaincode/spendshield && npm install
cd ../../client && npm install
```

### 4. Execute Backend Tests
```bash
cd backend
python -m pytest
```
