def normalize_currency(currency: str) -> str:
    c = currency.strip().upper()
    if c in ["₹", "RS", "RS.", "INR"]:
        return "INR"
    if c in ["$", "USD"]:
        return "USD"
    if c in ["€", "EUR"]:
        return "EUR"
    return c

import re
from typing import Tuple

def parse_price_string(price_str: str) -> Tuple[float, str]:
    """
    Extracts price value and currency from strings like '₹1,250', 'INR 1250', 'Rs. 1,250'.
    """
    cleaned = price_str.strip()
    currency = "INR"
    if "₹" in cleaned or "INR" in cleaned or "RS" in cleaned.upper():
        currency = "INR"
    elif "$" in cleaned or "USD" in cleaned.upper():
        currency = "USD"
    elif "€" in cleaned or "EUR" in cleaned.upper():
        currency = "EUR"
        
    nums = re.findall(r'[\d,]+\.?\d*', cleaned)
    if nums:
        price_val = float(nums[0].replace(',', ''))
        return price_val, currency
    return 0.0, currency

def normalize_pack_and_unit(price: float, unit_str: str) -> Tuple[float, int, str]:
    """
    Normalizes commercial units. Returns (unit_price, pack_quantity, unit_type).
    """
    unit_clean = unit_str.strip().lower()
    
    pack_match = re.search(r'(?:pack|box|case|packet|qty)\s+(?:of\s+)?(\d+)', unit_clean)
    if pack_match:
        qty = int(pack_match.group(1))
        if qty > 0:
            return round(price / qty, 6), qty, "piece"
            
    pack_match_alt = re.search(r'(\d+)\s*(?:pack|box|pcs|pieces)', unit_clean)
    if pack_match_alt:
        qty = int(pack_match_alt.group(1))
        if qty > 0:
            return round(price / qty, 6), qty, "piece"
            
    if "each" in unit_clean or "piece" in unit_clean or "pcs" in unit_clean or "unit" in unit_clean:
        return price, 1, "piece"
        
    return price, 1, unit_clean
