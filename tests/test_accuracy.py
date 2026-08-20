import pytest
import math
from datetime import datetime
from edelcore import EdelEngine, Body, HouseSystem

def test_full_chart_engine_run():
    engine = EdelEngine()
    # Birth chart benchmark: 1980-05-15 08:30:00 UTC, London (51.5074 N, -0.1278 E)
    dt = datetime(1980, 5, 15, 8, 30, 0)
    chart = engine.calculate_chart(
        dt_or_time=dt,
        lat_deg=51.5074,
        lon_deg=-0.1278,
        house_system=HouseSystem.PLACIDUS
    )

    assert chart is not None
    assert len(chart.bodies) >= 10
    assert len(chart.cusps) == 12

    # Sun in mid Taurus (~54.5 deg)
    sun = chart.bodies[Body.SUN]
    assert 53.0 < sun.longitude < 56.0

    # Moon in Gemini/Taurus boundary
    moon = chart.bodies[Body.MOON]
    assert 0.0 <= moon.longitude < 360.0

    # Check that house cusps are strictly ordered around the wheel
    cusps = chart.cusps
    assert math.isclose(cusps[0], chart.angles.asc, abs_tol=1e-4)
    assert math.isclose(cusps[9], chart.angles.mc, abs_tol=1e-4)

    # Check aspect generator
    aspects = chart.calculate_aspects(max_orb=8.0)
    assert len(aspects) > 0
    for asp in aspects:
        assert asp.orb <= 8.0
        assert asp.aspect_type in ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]

    # Check summary rendering
    summary_text = chart.summary()
    assert "EDELCORE CHART SUMMARY" in summary_text
    assert "Sun" in summary_text
    assert "House  1:" in summary_text

def test_sidereal_chart_generation():
    engine = EdelEngine()
    dt = datetime(1980, 5, 15, 8, 30, 0)
    chart = engine.calculate_chart(
        dt_or_time=dt,
        lat_deg=51.5074,
        lon_deg=-0.1278,
        house_system=HouseSystem.WHOLE_SIGN,
        sidereal_mode="Lahiri"
    )
    assert chart.is_sidereal is True
    assert chart.ayanamsha is not None
    assert 23.0 < chart.ayanamsha < 25.0
