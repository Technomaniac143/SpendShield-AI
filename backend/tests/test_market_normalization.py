import pytest
from app.services.market_intelligence.normalizers.price import parse_price_string, normalize_pack_and_unit

def test_price_string_parsing():
    p, c = parse_price_string("₹1,250")
    assert p == 1250.0
    assert c == "INR"

    p, c = parse_price_string("INR 1250.50")
    assert p == 1250.50
    assert c == "INR"

    p, c = parse_price_string("$45.00")
    assert p == 45.0
    assert c == "USD"

    p, c = parse_price_string("Rs. 2,500.75")
    assert p == 2500.75
    assert c == "INR"

def test_pack_size_normalization():
    # Pack of 10
    unit_p, pack_qty, unit_type = normalize_pack_and_unit(500.0, "pack of 10")
    assert unit_p == 50.0
    assert pack_qty == 10
    assert unit_type == "piece"

    # Box of 50
    unit_p, pack_qty, unit_type = normalize_pack_and_unit(2500.0, "box of 50")
    assert unit_p == 50.0
    assert pack_qty == 50
    assert unit_type == "piece"

    # 10 pack
    unit_p, pack_qty, unit_type = normalize_pack_and_unit(100.0, "10 pack")
    assert unit_p == 10.0
    assert pack_qty == 10
    assert unit_type == "piece"

    # Each / single
    unit_p, pack_qty, unit_type = normalize_pack_and_unit(25.0, "each")
    assert unit_p == 25.0
    assert pack_qty == 1
    assert unit_type == "piece"
