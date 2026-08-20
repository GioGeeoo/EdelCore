import pytest
import math
from edelcore.coords.horizontal import (
    equatorial_to_horizontal,
    horizontal_to_equatorial,
    apply_refraction,
    remove_refraction,
)

def test_zenith_and_meridian_horizontal_coords():
    # Observer at 50 deg N, LMST = 100 deg
    lat = 50.0
    lmst = 100.0

    # Object at Zenith: Dec = Lat = 50, RA = LMST = 100
    hz_zenith = equatorial_to_horizontal(ra_deg=100.0, dec_deg=50.0, lmst_deg=lmst, lat_deg=lat)
    assert math.isclose(hz_zenith.true_altitude, 90.0, abs_tol=1e-4)

    # Object at Upper Culmination due South: RA = LMST = 100, Dec = 0
    # True Alt = 90 - Lat = 40 deg, Azimuth = 180 deg (South)
    hz_south = equatorial_to_horizontal(ra_deg=100.0, dec_deg=0.0, lmst_deg=lmst, lat_deg=lat)
    assert math.isclose(hz_south.true_altitude, 40.0, abs_tol=1e-4)
    assert math.isclose(hz_south.azimuth, 180.0, abs_tol=1e-4)

def test_refraction_consistency():
    # At 0 deg altitude (horizon), standard refraction is ~ 34 arcminutes (~ 0.57 deg)
    h_app, r_arcmin = apply_refraction(0.0)
    assert 30.0 < r_arcmin < 38.0
    assert 0.50 < h_app < 0.65

    # Round trip: True Alt -> Apparent Alt -> True Alt
    true_alt = 15.0
    app_alt, _ = apply_refraction(true_alt)
    recovered_alt, _ = remove_refraction(app_alt)
    assert math.isclose(recovered_alt, true_alt, abs_tol=0.01)

def test_equatorial_horizontal_roundtrip():
    lat = 35.6762 # Tokyo
    lmst = 45.0
    ra_orig = 123.45
    dec_orig = 22.15

    hz = equatorial_to_horizontal(ra_orig, dec_orig, lmst, lat)
    ra_back, dec_back = horizontal_to_equatorial(hz.azimuth, hz.true_altitude, lmst, lat, is_apparent_altitude=False)

    assert math.isclose(ra_back, ra_orig, abs_tol=1e-4)
    assert math.isclose(dec_back, dec_orig, abs_tol=1e-4)
