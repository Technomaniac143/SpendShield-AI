from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SpendShield AI"
    VERSION: str = "1.0.0"

    DATABASE_URL: str
    REDIS_URL: str
    
    NEO4J_URI: str
    NEO4J_USERNAME: str
    NEO4J_PASSWORD: str

    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET: str

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    LLM_PROVIDER: str = "openai"
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4o"

    FABRIC_GATEWAY_URL: Optional[str] = None
    FABRIC_CHANNEL: Optional[str] = None
    FABRIC_CHAINCODE: Optional[str] = None
    FABRIC_CERT_PATH: Optional[str] = None
    FABRIC_KEY_PATH: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
