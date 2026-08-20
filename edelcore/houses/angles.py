"""
Fundamental Astrological Angles and Coordinate Reference Frameworks:
- ARMC / RAMC (Right Ascension of the Midheaven)
- MC (Midheaven / Medium Coeli)
- IC (Imum Coeli)
- ASC (Ascendant / Horoscopus)
- DSC (Descendant)
- Vertex and Anti-Vertex
- East Point (Equatorial Ascendant) and West Point
"""
import math
from typing import Tuple
from ..models import ChartAngles

def calculate_mc(armc_deg: float, eps_deg: float) -> float:
    """
    Calculate Midheaven (MC) ecliptic longitude from ARMC and Ecliptic Obliquity.
    tan(MC) = tan(ARMC) / cos(eps)
    """
    armc_rad = math.radians(armc_deg)
    eps_rad = math.radians(eps_deg)

    y = math.sin(armc_rad)
    x = math.cos(armc_rad) * math.cos(eps_rad)
    mc_rad = math.atan2(y, x)
    return (math.degrees(mc_rad) + 360.0) % 360.0

def calculate_ascendant(armc_deg: float, lat_deg: float, eps_deg: float) -> float:
    """
    Calculate Ascendant (ASC) ecliptic longitude.
    Formula:
    y = cos(RAMC)
    x = - (sin(RAMC) * cos(eps) + tan(lat) * sin(eps))
    ASC = atan2(y, x)
    """
    ramc_rad = math.radians(armc_deg)
    lat_rad = math.radians(lat_deg)
    eps_rad = math.radians(eps_deg)

    # Standard spherical trigonometry for Ascendant
    y = math.cos(ramc_rad)
    x = - (math.sin(ramc_rad) * math.cos(eps_rad) + math.tan(lat_rad) * math.sin(eps_rad))
    asc_rad = math.atan2(y, x)
    return (math.degrees(asc_rad) + 360.0) % 360.0

def calculate_vertex(armc_deg: float, lat_deg: float, eps_deg: float) -> float:
    """
    Calculate Vertex ecliptic longitude.
    The Vertex is the western intersection of the prime vertical with the ecliptic,
    mathematically equivalent to the Ascendant for co-latitude (90 - lat) with RAMC + 180 deg.
    """
    # Co-latitude = 90 - abs(lat)
    co_lat = 90.0 - abs(lat_deg)
    if lat_deg < 0:
        co_lat = -co_lat

    ramc_vert = (armc_deg + 180.0) % 360.0
    return calculate_ascendant(ramc_vert, co_lat, eps_deg)

def calculate_east_point(armc_deg: float, eps_deg: float) -> float:
    """
    Calculate East Point (Equatorial Ascendant).
    The intersection of the eastern horizon with the celestial equator projected onto the ecliptic.
    Formula: Ascendant evaluated at lat = 0.
    """
    return calculate_ascendant(armc_deg, 0.0, eps_deg)

def compute_all_angles(
    armc_deg: float,
    lat_deg: float,
    eps_deg: float
) -> ChartAngles:
    """
    Compute all primary astrological angles given ARMC, geographic latitude, and true obliquity.
    """
    mc = calculate_mc(armc_deg, eps_deg)
    ic = (mc + 180.0) % 360.0

    asc = calculate_ascendant(armc_deg, lat_deg, eps_deg)
    dsc = (asc + 180.0) % 360.0

    vertex = calculate_vertex(armc_deg, lat_deg, eps_deg)
    anti_vertex = (vertex + 180.0) % 360.0

    east_point = calculate_east_point(armc_deg, eps_deg)

    return ChartAngles(
        armc=(armc_deg % 360.0 + 360.0) % 360.0,
        mc=mc,
        ic=ic,
        asc=asc,
        dsc=dsc,
        vertex=vertex,
        anti_vertex=anti_vertex,
        east_point=east_point
    )
