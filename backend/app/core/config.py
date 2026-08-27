from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SpendShield AI"
    database_url: str = "sqlite:///./spendshield.db"
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

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
