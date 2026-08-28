from app.integrations.storage import document_hash


def test_document_hash_is_sha256():
    digest = document_hash(b"invoice.pdf")
    assert len(digest) == 64
    assert digest == document_hash(b"invoice.pdf")
    assert digest != document_hash(b"modified invoice.pdf")
