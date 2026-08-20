import pytest
import math
from edelcore.time.edel_time import EdelTime
from edelcore.ephem.bodies import Body, STANDARD_PLANETS
from edelcore.ephem.ephemeris import EdelEphemeris

def test_ephemeris_sun_moon():
    ephem = EdelEphemeris()
    # 2026-08-20 12:00:00 UT
    t = EdelTime.from_ymd_hms(2026, 8, 20, 12, 0, 0.0)

    # Sun position
    sun = ephem.calculate_body(Body.SUN, t)
    # Late August: Sun is in Leo (approx 145 - 150 deg)
    assert 140.0 < sun.longitude < 155.0
    assert 0.98 < sun.distance < 1.02
    assert 0.95 < sun.speed_longitude < 1.02
    assert not sun.is_retrograde

    # Moon position
    moon = ephem.calculate_body(Body.MOON, t)
    assert 0.0 <= moon.longitude < 360.0
    assert 11.0 < moon.speed_longitude < 15.5
    assert not moon.is_retrograde

def test_ephemeris_all_standard_planets():
    ephem = EdelEphemeris()
    t = EdelTime.from_ymd_hms(2000, 1, 1, 12, 0, 0.0)

    for b in STANDARD_PLANETS:
        pos = ephem.calculate_body(b, t)
        assert 0.0 <= pos.longitude < 360.0
        assert -90.0 <= pos.latitude <= 90.0
        assert pos.distance > 0.0
        assert isinstance(pos.is_retrograde, bool)

def test_lunar_nodes_and_lilith():
    ephem = EdelEphemeris()
    t = EdelTime.from_ymd_hms(2000, 1, 1, 12, 0, 0.0)

    mean_node = ephem.calculate_body(Body.MEAN_NODE, t)
    true_node = ephem.calculate_body(Body.TRUE_NODE, t)
    mean_lilith = ephem.calculate_body(Body.MEAN_LILITH, t)
    true_lilith = ephem.calculate_body(Body.TRUE_LILITH, t)

    # Mean node at J2000 is ~ 125.04 deg (opposite Ketu is ~ 305.04 deg)
    assert math.isclose(mean_node.longitude, 125.04, abs_tol=0.2)
    # True node oscillates around mean node within ~1.5 deg
    assert abs((true_node.longitude - mean_node.longitude + 180.0) % 360.0 - 180.0) < 2.0
    # Mean node always moves retrograde (speed < 0)
    assert mean_node.is_retrograde
