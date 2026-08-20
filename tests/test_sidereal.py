import pytest
import math
from edelcore.time.edel_time import EdelTime
from edelcore.sidereal.ayanamsha import AyanamshaMode, EdelAyanamsha

def test_ayanamsha_values():
    t_j2000 = EdelTime.from_ymd_hms(2000, 1, 1, 12, 0, 0.0)

    # Lahiri at J2000 is ~23.858 degrees (23° 51' 30")
    lahiri = EdelAyanamsha.calculate_ayanamsha(AyanamshaMode.LAHIRI, t_j2000)
    assert math.isclose(lahiri, 23.858483, abs_tol=0.01)

    # Fagan-Bradley at J2000 is ~24.739 degrees
    fb = EdelAyanamsha.calculate_ayanamsha(AyanamshaMode.FAGAN_BRADLEY, t_j2000)
    assert math.isclose(fb, 24.739167, abs_tol=0.01)

    # In 2026 (~26 years past 2000 -> precession adds ~ 26 * 50.29" = ~ 1307" = 0.363 deg)
    t_2026 = EdelTime.from_ymd_hms(2026, 8, 20, 12, 0, 0.0)
    lahiri_2026 = EdelAyanamsha.calculate_ayanamsha(AyanamshaMode.LAHIRI, t_2026)
    assert 24.15 < lahiri_2026 < 24.30

def test_tropical_to_sidereal_conversion():
    t = EdelTime.from_ymd_hms(2000, 1, 1, 12, 0, 0.0)
    trop_lon = 30.0 # 0 deg Taurus
    sid_lon = EdelAyanamsha.to_sidereal(trop_lon, AyanamshaMode.LAHIRI, t)
    assert math.isclose(sid_lon, 30.0 - 23.858483, abs_tol=0.01)

    # Round trip
    back_to_trop = EdelAyanamsha.to_tropical(sid_lon, AyanamshaMode.LAHIRI, t)
    assert math.isclose(back_to_trop, trop_lon, abs_tol=1e-6)
