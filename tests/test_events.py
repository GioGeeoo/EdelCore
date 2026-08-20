import pytest
import math
from datetime import datetime
from edelcore import EdelEngine, Body, EdelTime

def test_sun_ingress_equinox():
    engine = EdelEngine()
    # Search for Sun entering Aries (0 deg longitude / Spring Equinox) in March 2026
    t_start = EdelTime.from_datetime(datetime(2026, 3, 15, 0, 0, 0))
    t_end = EdelTime.from_datetime(datetime(2026, 3, 25, 0, 0, 0))

    ingresses = engine.search_sign_ingresses(Body.SUN, t_start, t_end)
    assert len(ingresses) == 1
    t_ing, sign_idx = ingresses[0]
    assert sign_idx == 0 # Aries

    # In 2026, Spring Equinox is around March 20
    y, m, d, h, mn, s = t_ing.calendar
    assert (y, m, d) == (2026, 3, 20)

    # Verify Sun longitude at that exact moment is 0.0 deg within 0.001 deg (3.6 arcsec)
    pos = engine.ephemeris.calculate_body(Body.SUN, t_ing)
    assert abs((pos.longitude + 180.0) % 360.0 - 180.0) < 0.001

def test_degree_transit_search():
    engine = EdelEngine()
    # Search for Moon reaching 180 deg (0 Libra) in August 2026
    t_start = EdelTime.from_datetime(datetime(2026, 8, 1, 0, 0, 0))
    t_end = EdelTime.from_datetime(datetime(2026, 8, 10, 0, 0, 0))

    t_cross = engine.search_transit(Body.MOON, 180.0, t_start, t_end)
    if t_cross:
        pos = engine.ephemeris.calculate_body(Body.MOON, t_cross)
        assert math.isclose(pos.longitude, 180.0, abs_tol=0.005)

def test_station_search():
    engine = EdelEngine()
    # Search Mercury station turning points across 2026
    t_start = EdelTime.from_datetime(datetime(2026, 1, 1, 0, 0, 0))
    t_end = EdelTime.from_datetime(datetime(2026, 6, 1, 0, 0, 0))

    stations = engine.search_stations(Body.MERCURY, t_start, t_end)
    assert len(stations) >= 1
    for t_st, st_type in stations:
        pos = engine.ephemeris.calculate_body(Body.MERCURY, t_st)
        assert abs(pos.speed_longitude) < 0.02
