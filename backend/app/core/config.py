from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SpendShield AI"
    environment: str = "development"
    database_url: str = "sqlite:///./spendshield.db"
    auth_secret: str = ""
    access_token_ttl_seconds: int = 900
    refresh_token_ttl_days: int = 30
    max_document_bytes: int = 25 * 1024 * 1024
    max_ingestion_bytes: int = 100 * 1024 * 1024
    cors_origins: str = "http://localhost:5173"
    storage_endpoint_url: str = "http://localhost:9000"
    storage_access_key: str = ""
    storage_secret_key: str = ""
    storage_bucket: str = "spendshield-evidence"
    fabric_gateway_url: str = "grpc://localhost:7051"
    fabric_channel: str = "spendchannel"
    fabric_chaincode: str = "spendshield"
    fabric_cert_path: str = ""
    fabric_key_path: str = ""
    fabric_tls_cert_path: str = ""
    fabric_msp_id: str = "Org1MSP"
    fabric_peer_endpoint: str = "localhost:7051"
    fabric_peer_host_alias: str = "peer0.org1.example.com"
    fabric_helper_path: str = "fabric/client/gateway.js"
    evidence_ledger_backend: str = "database"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def model_post_init(self, __context) -> None:
        if self.environment.lower() == "production" and not self.database_url.startswith(("postgresql://", "postgresql+psycopg://")):
            raise ValueError("production requires a PostgreSQL database")
        if self.environment.lower() == "production" and len(self.auth_secret) < 32:
            raise ValueError("production auth_secret must be at least 32 characters")


@lru_cache
def get_settings() -> Settings:
    return Settings()
