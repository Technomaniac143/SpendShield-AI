from app.core.database import SessionLocal
from app.integrations.blockchain import get_fabric_client
from app.workers.fabric_outbox import FabricOutboxWorker


if __name__ == "__main__":
    worker = FabricOutboxWorker(SessionLocal, get_fabric_client())
    while worker.process_once():
        pass
