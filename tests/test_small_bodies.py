import pytest
import math
from edelcore.time.edel_time import EdelTime
from edelcore.ephem.bodies import Body, STANDARD_ASTEROIDS
from edelcore.ephem.ephemeris import EdelEphemeris

def test_asteroids_and_chiron_positions():
    ephem = EdelEphemeris()
    # J2000.0 epoch (2000-01-01 12:00:00 UT)
    t_j2000 = EdelTime.from_ymd_hms(2000, 1, 1, 12, 0, 0.0)

    for ast in STANDARD_ASTEROIDS:
        pos = ephem.calculate_body(ast, t_j2000)
        assert 0.0 <= pos.longitude < 360.0
        assert -90.0 <= pos.latitude <= 90.0
        assert pos.distance > 0.5
        assert isinstance(pos.is_retrograde, bool)

    # Ceres semi-major axis is ~2.77 AU, distance from Earth ~1.7 - 3.8 AU
    ceres = ephem.calculate_body(Body.CERES, t_j2000)
    assert 1.5 < ceres.distance < 4.0

    # Chiron is far out (semi-major axis ~13.6 AU)
    chiron = ephem.calculate_body(Body.CHIRON, t_j2000)
    assert 8.0 < chiron.distance < 20.0

def test_asteroid_speeds():
    ephem = EdelEphemeris()
    t = EdelTime.from_ymd_hms(2026, 8, 20, 12, 0, 0.0)

    for ast in [Body.CHIRON, Body.CERES, Body.PALLAS, Body.JUNO, Body.VESTA]:
        pos = ephem.calculate_body(ast, t)
        # Asteroids typically move between -0.15 and +0.6 deg/day
        assert -0.5 < pos.speed_longitude < 0.8
