import hashlib
import re

SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def sha256_bytes(document: bytes) -> str:
    return hashlib.sha256(document).hexdigest()


def deterministic_modified_hash(registered_hash: str) -> str:
    return hashlib.sha256(f"SpendShield simulated modification:{registered_hash}".encode()).hexdigest()


def is_sha256(value: str) -> bool:
    return bool(SHA256_RE.fullmatch(value))
