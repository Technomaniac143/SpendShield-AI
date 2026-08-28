from hashlib import sha256
from typing import Protocol

import boto3

from app.core.config import get_settings


class ObjectStorage(Protocol):
    def put(self, key: str, content: bytes, content_type: str = "application/pdf") -> str: ...
    def get(self, key: str) -> bytes: ...
    def delete(self, key: str) -> None: ...
    def hash(self, key: str) -> str: ...
    def get_stream(self, key: str): ...


class S3ObjectStorage:
    """S3-compatible storage adapter; it never sends document bytes to Fabric."""

    def __init__(self, client, bucket: str):
        self.client = client
        self.bucket = bucket

    def put(self, key: str, content: bytes, content_type: str = "application/pdf") -> str:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=content, ContentType=content_type)
        return key

    def get(self, key: str) -> bytes:
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()

    def get_stream(self, key: str):
        return self.client.get_object(Bucket=self.bucket, Key=key)["Body"]

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def hash(self, key: str) -> str:
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        digest = sha256()
        for chunk in iter(lambda: response["Body"].read(1024 * 1024), b""):
            digest.update(chunk)
        return digest.hexdigest()


def document_hash(content: bytes) -> str:
    return sha256(content).hexdigest()


def create_storage() -> "ObjectStorage":
    """
    Return an object storage adapter.

    Resolution order:
    1. If S3 credentials are configured → use S3ObjectStorage.
    2. Otherwise (typically database-ledger mode in dev) → use
       LocalObjectStorage so the server starts without MinIO.
    """
    settings = get_settings()
    if settings.storage_access_key and settings.storage_secret_key:
        client = boto3.client(
            "s3",
            endpoint_url=settings.storage_endpoint_url,
            aws_access_key_id=settings.storage_access_key,
            aws_secret_access_key=settings.storage_secret_key,
        )
        return S3ObjectStorage(client, settings.storage_bucket)

    # Fallback: local filesystem storage (development / database-mode only)
    from app.integrations.storage_local import LocalObjectStorage
    import logging
    logging.getLogger(__name__).warning(
        "No S3 credentials configured – using local filesystem storage. "
        "Set STORAGE_ACCESS_KEY and STORAGE_SECRET_KEY for production."
    )
    return LocalObjectStorage()
