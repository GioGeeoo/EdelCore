import pytest
import math
from datetime import datetime
from edelcore import EdelEngine, EdelTime
from edelcore.ephem.stars import STAR_CATALOG, list_star_names, calculate_star_position

def test_star_catalog_inventory():
    stars = list_star_names()
    assert len(stars) >= 20
    assert "Sirius" in stars
    assert "Regulus" in stars
    assert "Spica" in stars
    assert "Algol" in stars
    assert "Aldebaran" in stars
    assert "Antares" in stars
    assert "Fomalhaut" in stars

def test_star_positions_at_j2000():
    t_j2000 = EdelTime.from_ymd_hms(2000, 1, 1, 12, 0, 0.0)

    # 1. Regulus: J2000 ecliptic longitude is ~ 149° 50' (~ 29° 50' Leo)
    regulus = calculate_star_position("Regulus", t_j2000)
    assert math.isclose(regulus.longitude, 149.83, abs_tol=0.2)
    assert 0.4 < regulus.latitude < 0.6  # Near ecliptic (+0.46 deg)

    # 2. Spica: J2000 ecliptic longitude is ~ 203° 50' (~ 23° 50' Libra)
    spica = calculate_star_position("Spica", t_j2000)
    assert math.isclose(spica.longitude, 203.84, abs_tol=0.2)
    assert -2.2 < spica.latitude < -1.8  # ~ -2.05 deg

    # 3. Sirius: J2000 ecliptic longitude is ~ 104° 07' (~ 14° 07' Cancer)
    sirius = calculate_star_position("Sirius", t_j2000)
    assert math.isclose(sirius.longitude, 104.12, abs_tol=0.3)
    assert -40.0 < sirius.latitude < -39.0

    # 4. Aldebaran: J2000 ecliptic longitude is ~ 69° 47' (~ 9° 47' Gemini)
    aldebaran = calculate_star_position("Aldebaran", t_j2000)
    assert math.isclose(aldebaran.longitude, 69.79, abs_tol=0.2)

def test_regulus_sign_ingress_precession():
    # Regulus precessed from Leo (29° 50') into Virgo (0° 00' 00") around end of 2011 / 2012
    t_1900 = EdelTime.from_ymd_hms(1900, 1, 1, 0, 0, 0.0)
    t_2026 = EdelTime.from_ymd_hms(2026, 8, 20, 12, 0, 0.0)

    reg_1900 = calculate_star_position("Regulus", t_1900)
    reg_2026 = calculate_star_position("Regulus", t_2026)

    # In 1900: ~ 148.4 deg (28° 24' Leo)
    assert 148.0 < reg_1900.longitude < 149.0
    # In 2026: > 150.0 deg (in Virgo!)
    assert 150.15 < reg_2026.longitude < 150.35

def test_star_facade_and_horizontal_coords():
    engine = EdelEngine()
    dt = datetime(2026, 8, 20, 22, 0, 0)
    # London coordinates
    star = engine.calculate_star("Vega", dt, lat_deg=51.5074, lon_deg=-0.1278)

    assert star.name == "Vega"
    assert star.constellation == "Lyra"
    assert star.vmag == 0.03
    assert 0.0 <= star.longitude < 360.0
    assert star.azimuth is not None
    assert star.altitude is not None
    assert 0.0 <= star.azimuth < 360.0
    assert -90.0 <= star.altitude <= 90.0
