import re

def normalize_product_name(name: str) -> str:
    if not name:
        return ""
    # Lowercase
    normalized = name.lower()
    # Normalize common abbreviations or specifications
    normalized = normalized.replace("75gsm", "75 gsm")
    normalized = normalized.replace("80gsm", "80 gsm")
    # Clean punctuation and extra spaces
    normalized = re.sub(r'[^\w\s]', ' ', normalized)
    normalized = " ".join(normalized.split())
    return normalized
