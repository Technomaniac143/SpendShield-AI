from hashlib import sha256
from typing import Protocol


class ObjectStorage(Protocol):
    def put(self, key: str, content: bytes, content_type: str = "application/pdf") -> str: ...


class S3ObjectStorage:
    """S3-compatible storage adapter; it never sends document bytes to Fabric."""

    def __init__(self, client, bucket: str):
        self.client = client
        self.bucket = bucket

    def put(self, key: str, content: bytes, content_type: str = "application/pdf") -> str:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=content, ContentType=content_type)
        return key


def document_hash(content: bytes) -> str:
    return sha256(content).hexdigest()
