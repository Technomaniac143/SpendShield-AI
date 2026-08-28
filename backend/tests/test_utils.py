from app.utils import deterministic_modified_hash, is_sha256, sha256_bytes


def test_sha256_and_deterministic_modification():
    original = sha256_bytes(b"invoice.pdf")
    assert is_sha256(original)
    assert deterministic_modified_hash(original) != original
    assert deterministic_modified_hash(original) == deterministic_modified_hash(original)
