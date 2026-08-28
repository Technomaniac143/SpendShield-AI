import re

def normalize_supplier_name(name: str) -> str:
    if not name:
        return ""
    # Lowercase
    n = name.lower()
    # Remove common suffixes
    suffixes = [
        r'\bprivate\s+limited\b', r'\bpvt\s+ltd\b', r'\bpvt\.?\s*ltd\.?\b',
        r'\bltd\.?\b', r'\bcorp\.?\b', r'\bcorporation\b', r'\binc\.?\b',
        r'\bincorporated\b', r'\bco\.?\b', r'\bcompany\b', r'\bllc\b', r'\bplc\b'
    ]
    for suffix in suffixes:
        n = re.sub(suffix, '', n)
    
    # Clean punctuation and extra spaces
    n = re.sub(r'[^\w\s]', ' ', n)
    n = " ".join(n.split())
    return n
