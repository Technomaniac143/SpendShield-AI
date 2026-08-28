"""
LocalObjectStorage — a filesystem-backed storage adapter for development/database mode.

When EVIDENCE_LEDGER_BACKEND=database and no S3 credentials are configured,
this adapter is used so that document bytes are preserved locally without
requiring a running MinIO/S3 instance.
"""
import hashlib
import os
from pathlib import Path

from app.integrations.storage import ObjectStorage


class LocalObjectStorage:
    """Stores evidence documents as files in a local directory."""

    def __init__(self, base_dir: str = "./evidence_store"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        safe = key.replace("..", "__").lstrip("/")
        p = self.base_dir / safe
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def put(self, key: str, content: bytes, content_type: str = "application/pdf") -> str:
        self._path(key).write_bytes(content)
        return key

    def get(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def get_stream(self, key: str):
        import io
        return io.BytesIO(self._path(key).read_bytes())

    def delete(self, key: str) -> None:
        p = self._path(key)
        if p.exists():
            p.unlink()

    def hash(self, key: str) -> str:
        digest = hashlib.sha256()
        with open(self._path(key), "rb") as f:
            while chunk := f.read(1024 * 1024):
                digest.update(chunk)
        return digest.hexdigest()
