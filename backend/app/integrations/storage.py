from hashlib import sha256
from typing import Protocol

import boto3

from app.core.config import get_settings


class ObjectStorage(Protocol):
    def put(self, key: str, content: bytes, content_type: str = "application/pdf") -> str: ...
    def get(self, key: str) -> bytes: ...


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


def document_hash(content: bytes) -> str:
    return sha256(content).hexdigest()


def create_storage() -> S3ObjectStorage:
    settings = get_settings()
    if not settings.storage_access_key or not settings.storage_secret_key:
        raise RuntimeError("object storage credentials are required")
    client = boto3.client("s3", endpoint_url=settings.storage_endpoint_url,
                          aws_access_key_id=settings.storage_access_key,
                          aws_secret_access_key=settings.storage_secret_key)
    return S3ObjectStorage(client, settings.storage_bucket)
