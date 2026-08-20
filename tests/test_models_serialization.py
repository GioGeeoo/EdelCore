import pytest
import json
from datetime import datetime
from edelcore import (
    EdelEngine,
    Body,
    HouseSystem,
    format_zodiac_deg,
    format_dms,
)

def test_format_helpers():
    # 352.7903 deg -> Pisces 22°47'25"
    sign, deg, fmt = format_zodiac_deg(352.7903)
    assert sign == "Pisces"
    assert round(deg, 4) == 22.7903
    assert fmt == "22°47'25\" Pisces"

    # 4.2050 deg -> Aries 04°12'18"
    sign, deg, fmt = format_zodiac_deg(4.2050)
    assert sign == "Aries"
    assert round(deg, 4) == 4.2050
    assert fmt == "04°12'18\" Aries"

    # Format DMS with sign
    assert format_dms(0.9856, include_sign=True) == "+00°59'08\""
    assert format_dms(-0.0123, include_sign=True) == "-00°00'44\""

def test_body_properties_and_repr():
    engine = EdelEngine()
    dt = datetime(2026, 8, 20, 21, 4, 0)
    chart = engine.calculate_chart(dt, 51.5074, -0.1278)

    sun = chart.get(Body.SUN)
    assert sun.sign in ["Leo", "Virgo"]
    assert 0.0 <= sun.sign_degree < 30.0
    assert "Leo" in sun.formatted or "Virgo" in sun.formatted
    assert "Sun" in repr(sun)
    assert "Direct" in repr(sun) or "Retrograde" in repr(sun)

    sun_dict = sun.to_dict()
    assert sun_dict["name"] == "Sun"
    assert "longitude" in sun_dict
    assert "formatted" in sun_dict
    assert "sign" in sun_dict

def test_chart_json_and_dict_serialization():
    engine = EdelEngine()
    dt = datetime(2026, 8, 20, 21, 4, 0)
    chart = engine.calculate_chart(dt, 51.5074, -0.1278)

    data = chart.to_dict()
    assert "time" in data
    assert "location" in data
    assert "houses" in data
    assert len(data["houses"]) == 12
    assert "bodies" in data
    assert "Sun" in data["bodies"]
    assert data["bodies"]["Sun"]["house"] >= 1
    assert "angles" in data
    assert "aspects" in data

    # Test JSON serialization
    json_str = chart.to_json(indent=2)
    assert isinstance(json_str, str)
    parsed = json.loads(json_str)
    assert parsed["house_system"] == "Placidus"
    assert "Sun" in parsed["bodies"]
