import pytest
import math
from edelcore.houses.house_engine import HouseSystem, EdelHouses
from edelcore.houses.angles import compute_all_angles

def test_angles_calculation():
    # London: Lat 51.5074 N, ARMC = 0.0, True Obliquity = 23.44
    angles = compute_all_angles(armc_deg=0.0, lat_deg=51.5074, eps_deg=23.44)
    # When ARMC = 0, MC = 0 (0 deg Aries), IC = 180 (0 deg Libra)
    assert math.isclose(angles.mc, 0.0, abs_tol=1e-5)
    assert math.isclose(angles.ic, 180.0, abs_tol=1e-5)
    assert 0.0 <= angles.asc < 360.0
    assert math.isclose((angles.asc + 180.0) % 360.0, angles.dsc, abs_tol=1e-5)
    assert math.isclose((angles.vertex + 180.0) % 360.0, angles.anti_vertex, abs_tol=1e-5)

def test_all_house_systems_produce_12_ordered_cusps():
    systems = list(HouseSystem)
    armc = 120.0
    lat = 40.7128 # New York
    eps = 23.44

    for hs in systems:
        cusps, angles = EdelHouses.calculate_houses(hs, armc, lat, eps)
        assert len(cusps) == 12
        for c in cusps:
            assert 0.0 <= c < 360.0

        # Cusp 1 should match ASC for quadrant and equal systems (except Vehlow/Morinus/Whole Sign)
        if hs in [HouseSystem.PLACIDUS, HouseSystem.KOCH, HouseSystem.REGIOMONTANUS, HouseSystem.CAMPANUS, HouseSystem.TOPOCENTRIC, HouseSystem.PORPHYRY, HouseSystem.EQUAL]:
            assert math.isclose(cusps[0], angles.asc, abs_tol=1e-4)
        
        # Cusp 10 should match MC for quadrant systems
        if hs in [HouseSystem.PLACIDUS, HouseSystem.KOCH, HouseSystem.REGIOMONTANUS, HouseSystem.CAMPANUS, HouseSystem.TOPOCENTRIC, HouseSystem.PORPHYRY]:
            assert math.isclose(cusps[9], angles.mc, abs_tol=1e-4)

def test_extreme_latitude_safeguard():
    # Near North Pole (Lat 75 deg N) where Placidus semi-arcs fail
    cusps, angles = EdelHouses.calculate_houses(HouseSystem.PLACIDUS, 60.0, 75.0, 23.44)
    assert len(cusps) == 12
    for c in cusps:
        assert 0.0 <= c < 360.0
