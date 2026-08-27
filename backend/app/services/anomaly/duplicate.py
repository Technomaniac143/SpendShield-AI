import hashlib
from typing import List, Dict, Any, Optional
from datetime import timedelta

class DuplicateDetectionEngine:
    
    @staticmethod
    def calculate_invoice_hash(supplier_id: str, invoice_number: str, invoice_date: str, total_amount: float) -> str:
        """Calculate a deterministic hash for exact duplicate detection."""
        raw_str = f"{supplier_id}|{invoice_number}|{invoice_date}|{total_amount}".lower()
        return hashlib.sha256(raw_str.encode()).hexdigest()

    @staticmethod
    def check_exact_duplicate(new_invoice: Dict[str, Any], existing_invoices: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Check for an exact match based on the core hash.
        """
        new_hash = DuplicateDetectionEngine.calculate_invoice_hash(
            new_invoice['supplier_id'],
            new_invoice['invoice_number'],
            str(new_invoice['invoice_date'].date()),
            new_invoice['total_amount']
        )
        
        for inv in existing_invoices:
            if inv.get('document_hash') == new_hash:
                return {
                    "probability": 1.0,
                    "matched_invoice_id": inv['id'],
                    "signals": ["Exact hash match"]
                }
        return None

    @staticmethod
    def check_near_duplicate(new_invoice: Dict[str, Any], existing_invoices: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Check for near duplicates based on similarity rules.
        """
        highest_prob = 0.0
        best_match = None
        best_signals = []

        for inv in existing_invoices:
            if str(inv['id']) == str(new_invoice.get('id')):
                continue

            signals = []
            score = 0.0
            
            # Same supplier is a prerequisite for most invoice duplicates
            if str(inv['supplier_id']) == str(new_invoice['supplier_id']):
                score += 0.3
                signals.append("same supplier")
                
                # Same amount
                if abs(inv['total_amount'] - new_invoice['total_amount']) < 0.01:
                    score += 0.4
                    signals.append("same amount")
                    
                # Similar date
                date_diff = abs((inv['invoice_date'] - new_invoice['invoice_date']).days)
                if date_diff <= 7:
                    score += 0.2
                    signals.append(f"date within {date_diff} days")
                    
                # Invoice number similarity (simple exact check for demo, can be improved with Levenshtein)
                if new_invoice['invoice_number'] in inv['invoice_number'] or inv['invoice_number'] in new_invoice['invoice_number']:
                    score += 0.1
                    signals.append("similar invoice number")
            
            if score > highest_prob:
                highest_prob = score
                best_match = inv
                best_signals = signals
                
        if highest_prob >= 0.7:
            return {
                "probability": round(highest_prob, 2),
                "matched_invoice_id": best_match['id'],
                "signals": best_signals
            }
            
        return None
