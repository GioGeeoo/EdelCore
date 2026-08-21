import pytest
import math
from edelcore.time.edel_time import EdelTime
from edelcore.time.delta_t_tables import calculate_delta_t

def test_julian_day_known_dates():
    # Meeus Chapter 7 Standard Examples:
    # 2000 January 1.5 -> JD 2451545.0
    jd = EdelTime.calendar_to_jd(2000, 1, 1, 12, 0, 0.0)
    assert math.isclose(jd, 2451545.0, abs_tol=1e-7)

    # 1999 January 1.0 -> JD 2451179.5
    jd = EdelTime.calendar_to_jd(1999, 1, 1, 0, 0, 0.0)
    assert math.isclose(jd, 2451179.5, abs_tol=1e-7)

    # 1987 January 27.0 -> JD 2446822.5
    jd = EdelTime.calendar_to_jd(1987, 1, 27, 0, 0, 0.0)
    assert math.isclose(jd, 2446822.5, abs_tol=1e-7)

    # Historical Julian Calendar: -1001 August 17.5 -> JD 1355671.0
    jd = EdelTime.calendar_to_jd(-1001, 8, 17, 12, 0, 0.0)
    assert math.isclose(jd, 1355671.0, abs_tol=1e-7)

    # Historical Julian Calendar: 333 January 27.5 -> JD 1842713.0
    jd = EdelTime.calendar_to_jd(333, 1, 27, 12, 0, 0.0)
    assert math.isclose(jd, 1842713.0, abs_tol=1e-7)

    # Round trip calendar <-> JD
    y, m, d, h, mn, s = EdelTime.jd_to_calendar(2451545.0)
    assert (y, m, d, h, mn) == (2000, 1, 1, 12, 0)
    assert math.isclose(s, 0.0, abs_tol=1e-4)

def test_delta_t():
    # J2000.0 (2000 CE) -> ~63.8 seconds
    dt_2000 = calculate_delta_t(2000, 1)
    assert 60.0 < dt_2000 < 70.0

    # 1800 CE -> ~13.7 seconds
    dt_1800 = calculate_delta_t(1800, 1)
    assert 10.0 < dt_1800 < 20.0

    # Year 0 CE -> ~10583 seconds
    dt_0 = calculate_delta_t(0, 1)
    assert 10000.0 < dt_0 < 11000.0

def test_sidereal_time():
    # J2000.0 (2000-01-01 12:00 UT) GMST = ~280.4606 degrees
    t = EdelTime.from_ymd_hms(2000, 1, 1, 12, 0, 0.0)
    gmst = t.gmst()
    assert math.isclose(gmst, 280.4606, abs_tol=0.01)

    # Local sidereal time at London (0 deg lon) vs New York (-74 deg lon)
    lmst_london = t.lmst(0.0)
    lmst_ny = t.lmst(-74.0)
    assert math.isclose((lmst_london - 74.0) % 360.0, lmst_ny, abs_tol=1e-5)

def test_timezone_aware_datetime_conversion():
    from datetime import datetime, timezone, timedelta
    
    # 12:00 UTC
    dt_utc = datetime(2026, 8, 21, 12, 0, 0, tzinfo=timezone.utc)
    # 16:00 UTC+4 (Tbilisi time) is identical instant to 12:00 UTC
    tz_tbilisi = timezone(timedelta(hours=4))
    dt_tbilisi = datetime(2026, 8, 21, 16, 0, 0, tzinfo=tz_tbilisi)
    # 08:00 UTC-4 (New York EDT) is identical instant to 12:00 UTC
    tz_ny = timezone(timedelta(hours=-4))
    dt_ny = datetime(2026, 8, 21, 8, 0, 0, tzinfo=tz_ny)

    t_utc = EdelTime.from_datetime(dt_utc)
    t_tbilisi = EdelTime.from_datetime(dt_tbilisi)
    t_ny = EdelTime.from_datetime(dt_ny)

    assert math.isclose(t_utc.jd_ut, t_tbilisi.jd_ut, abs_tol=1e-9)
    assert math.isclose(t_utc.jd_ut, t_ny.jd_ut, abs_tol=1e-9)

