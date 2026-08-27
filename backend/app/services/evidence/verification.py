import hashlib
from typing import Dict, Any

class EvidenceVerificationEngine:
    
    @staticmethod
    def calculate_file_hash(file_bytes: bytes) -> str:
        """Calculates SHA-256 hash of a file."""
        return hashlib.sha256(file_bytes).hexdigest()

    @staticmethod
    def verify_document_integrity(current_file_bytes: bytes, registered_hash: str) -> Dict[str, Any]:
        """
        Verifies if the current file matches the registered blockchain/database hash.
        """
        current_hash = EvidenceVerificationEngine.calculate_file_hash(current_file_bytes)
        
        if current_hash == registered_hash:
            return {
                "status": "VERIFIED",
                "current_hash": current_hash,
                "registered_hash": registered_hash,
                "message": "Document integrity verified."
            }
        else:
            return {
                "status": "INTEGRITY_FAILURE",
                "current_hash": current_hash,
                "registered_hash": registered_hash,
                "message": "Document hash does not match registered evidence."
            }
