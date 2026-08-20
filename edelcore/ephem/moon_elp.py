"""
Meeus / ELP-2000 Lunar Theory & Lunar Points:
- High-precision Lunar coordinates (Longitude, Latitude, Distance)
- Mean and True Lunar Nodes (Rahu / Ketu)
- Mean and True Lunar Apogee (Lilith / Black Moon)
"""
import math
from typing import Tuple
from ..astro.nutation import fundamental_arguments

def moon_position_meeus(t_centuries: float) -> Tuple[float, float, float]:
    """
    Calculate Moon's geocentric ecliptic longitude (lambda, deg), latitude (beta, deg),
    and distance (Delta, Earth radii / AU) based on Meeus Astronomical Algorithms (Ch. 47),
    which is an abbreviated truncation of ELP-2000/82.
    Accuracy: ~10 arcseconds in longitude and latitude.
    """
    t = t_centuries
    t2 = t * t
    t3 = t2 * t
    t4 = t3 * t

    # Moon's mean longitude L'
    lp_deg = 218.3164477 + 481267.88123421 * t - 0.0015786 * t2 + t3 / 538841.0 - t4 / 65194000.0
    # Mean elongation D
    d_deg = 297.8501921 + 445267.1114034 * t - 0.0018819 * t2 + t3 / 545868.0 - t4 / 113065000.0
    # Sun's mean anomaly M
    m_deg = 357.5291092 + 35999.0502909 * t - 0.0001536 * t2 + t3 / 24490000.0
    # Moon's mean anomaly M'
    mp_deg = 134.9633964 + 477198.8675055 * t + 0.0087414 * t2 + t3 / 69699.0 - t4 / 14712000.0
    # Moon's argument of latitude F
    f_deg = 93.2720950 + 483202.0175233 * t - 0.0036539 * t2 - t3 / 3526000.0 + t4 / 863310000.0

    # Additional arguments for planetary perturbations A1, A2, A3
    a1 = math.radians(119.75 + 131.849 * t)
    a2 = math.radians(53.09 + 479264.290 * t)
    a3 = math.radians(313.45 + 481266.484 * t)

    # Eccentricity of Earth orbit factor E
    e = 1.0 - 0.002516 * t - 0.0000074 * t2

    # Periodic terms for Longitude (Sigma l in 0.000001 deg)
    # [D, M, M', F, coeff, e_power]
    LON_TERMS = (
        (0, 0, 1, 0, 6288774, 0),
        (2, 0, -1, 0, 1274027, 0),
        (2, 0, 0, 0, 658314, 0),
        (0, 0, 2, 0, 213618, 0),
        (0, 1, 0, 0, -185116, 1),
        (0, 0, 0, 2, -114332, 0),
        (2, 0, -2, 0, 58793, 0),
        (2, -1, -1, 0, 57066, 1),
        (2, 0, 1, 0, 53322, 0),
        (2, -1, 0, 0, 45758, 1),
        (0, 1, -1, 0, -40923, 1),
        (1, 0, 0, 0, -34720, 0),
        (0, 1, 1, 0, -30383, 1),
        (2, 0, 0, -2, 15327, 0),
        (0, 0, 1, 2, -12528, 0),
        (0, 0, 1, -2, 10980, 0),
        (4, 0, -1, 0, 10675, 0),
        (0, 0, 3, 0, 10034, 0),
        (4, 0, -2, 0, 8548, 0),
        (2, 1, -1, 0, -7888, 1),
        (2, 1, 0, 0, -6766, 1),
        (1, 0, -1, 0, -5163, 0),
        (1, 1, 0, 0, 4987, 1),
        (2, -1, 1, 0, 4036, 1),
        (2, 0, 2, 0, 3994, 0),
        (4, 0, 0, 0, 3861, 0),
        (2, 0, -3, 0, 3665, 0),
        (0, 1, -2, 0, -2689, 1),
        (2, 0, -1, 2, -2602, 0),
        (2, -1, -2, 0, 2390, 1),
        (1, 0, 1, 0, -2348, 0),
        (2, -2, 0, 0, 2236, 2),
        (0, 1, 2, 0, -2120, 1),
        (0, 2, 0, 0, -2069, 2),
        (2, -2, -1, 0, 2048, 2),
        (2, 0, 1, -2, -1773, 0),
        (2, 0, 0, 2, -1595, 0),
        (4, -1, -1, 0, 1215, 1),
        (0, 0, 2, 2, -1110, 0),
        (3, 0, -1, 0, -892, 0),
        (2, 1, 1, 0, -810, 1),
        (4, -1, -2, 0, 759, 1),
        (0, 2, -1, 0, -713, 2),
        (2, 2, -1, 0, -700, 2),
        (2, 1, -2, 0, 691, 1),
        (2, -1, 0, -2, 596, 1),
        (4, 0, 1, 0, 549, 0),
        (0, 0, 4, 0, 537, 0),
        (4, -1, 0, 0, 520, 1),
        (1, 0, -2, 0, -487, 0),
        (2, 1, 0, -2, -399, 1),
        (0, 0, 2, -2, -381, 0),
        (1, 1, 1, 0, 351, 1),
        (3, 0, -2, 0, -340, 0),
        (4, 0, -3, 0, 330, 0),
        (2, -1, -1, -2, 327, 1),
        (1, 0, 2, 0, -323, 0),
        (0, 0, 1, -4, 299, 0),
        (2, 0, -1, -2, 294, 0),
    )

    # Periodic terms for Latitude (Sigma b in 0.000001 deg)
    LAT_TERMS = (
        (0, 0, 0, 1, 5128122, 0),
        (0, 0, 1, 1, 280602, 0),
        (0, 0, 1, -1, 277693, 0),
        (2, 0, 0, -1, 173237, 0),
        (2, 0, -1, 1, 55413, 0),
        (2, 0, -1, -1, 46271, 0),
        (2, 0, 0, 1, 32573, 0),
        (0, 0, 2, 1, 17198, 0),
        (2, 0, 1, -1, 9266, 0),
        (0, 0, 2, -1, 8822, 0),
        (2, -1, 0, -1, 8216, 1),
        (2, 0, -2, -1, 4324, 0),
        (2, 0, 1, 1, 4200, 0),
        (2, 1, 0, -1, -3359, 1),
        (2, -1, -1, 1, 2463, 1),
        (2, -1, 0, 1, 2211, 1),
        (2, -1, -1, -1, 2065, 1),
        (0, 1, -1, -1, -1870, 1),
        (4, 0, -1, -1, 1828, 0),
        (0, 1, 0, 1, -1794, 1),
        (0, 0, 0, 3, -1749, 0),
        (0, 1, -1, 1, -1565, 1),
        (1, 0, 0, 1, -1491, 0),
        (0, 1, 1, 1, -1475, 1),
        (0, 1, 1, -1, -1410, 1),
        (0, 1, 0, -1, -1344, 1),
        (1, 0, 0, -1, -1335, 0),
        (0, 0, 3, 1, 1107, 0),
        (4, 0, 0, -1, 1021, 0),
        (4, 0, -1, 1, 833, 0),
    )

    # Periodic terms for Distance (Sigma r in 0.001 km)
    DIST_TERMS = (
        (0, 0, 1, 0, -20954251, 0),
        (2, 0, -1, 0, -3699111, 0),
        (2, 0, 0, 0, -2955968, 0),
        (0, 0, 2, 0, -569925, 0),
        (0, 1, 0, 0, 48888, 1),
        (0, 0, 0, 2, -3149, 0),
        (2, 0, -2, 0, 246158, 0),
        (2, -1, -1, 0, -152138, 1),
        (2, 0, 1, 0, -170733, 0),
        (2, -1, 0, 0, -204586, 1),
        (0, 1, -1, 0, -129620, 1),
        (1, 0, 0, 0, 108743, 0),
        (0, 1, 1, 0, 104755, 1),
        (2, 0, 0, -2, 10321, 0),
        (0, 0, 1, 2, 0, 0),
        (0, 0, 1, -2, 79661, 0),
        (4, 0, -1, 0, -34782, 0),
        (0, 0, 3, 0, -23210, 0),
        (4, 0, -2, 0, -21636, 0),
        (2, 1, -1, 0, 24208, 1),
        (2, 1, 0, 0, 30824, 1),
        (1, 0, -1, 0, -8379, 0),
        (1, 1, 0, 0, -16675, 1),
        (2, -1, 1, 0, -12831, 1),
        (2, 0, 2, 0, -10445, 0),
        (4, 0, 0, 0, -11650, 0),
        (2, 0, -3, 0, 14403, 0),
        (0, 1, -2, 0, -7003, 1),
    )

    d_rad = math.radians(d_deg)
    m_rad = math.radians(m_deg)
    mp_rad = math.radians(mp_deg)
    f_rad = math.radians(f_deg)

    sigma_l = 0.0
    for d_c, m_c, mp_c, f_c, coeff, ep in LON_TERMS:
        factor = (e ** ep) if ep > 0 else 1.0
        arg = d_c * d_rad + m_c * m_rad + mp_c * mp_rad + f_c * f_rad
        sigma_l += factor * coeff * math.sin(arg)

    # Venus and Jupiter perturbations on Moon longitude
    sigma_l += 3958.0 * math.sin(a1) + 1962.0 * math.sin(math.radians(lp_deg) - f_rad) + 318.0 * math.sin(a2)

    sigma_b = 0.0
    for d_c, m_c, mp_c, f_c, coeff, ep in LAT_TERMS:
        factor = (e ** ep) if ep > 0 else 1.0
        arg = d_c * d_rad + m_c * m_rad + mp_c * mp_rad + f_c * f_rad
        sigma_b += factor * coeff * math.sin(arg)

    sigma_b += -2235.0 * math.sin(math.radians(lp_deg)) + 382.0 * math.sin(a3) + 175.0 * math.sin(a1 - f_rad) + 175.0 * math.sin(a1 + f_rad)

    sigma_r = 0.0
    for d_c, m_c, mp_c, f_c, coeff, ep in DIST_TERMS:
        factor = (e ** ep) if ep > 0 else 1.0
        arg = d_c * d_rad + m_c * m_rad + mp_c * mp_rad + f_c * f_rad
        sigma_r += factor * coeff * math.cos(arg)

    # Longitude in degrees
    lon_deg = (lp_deg + sigma_l * 1e-6) % 360.0
    # Latitude in degrees
    lat_deg = sigma_b * 1e-6
    # Distance in km -> converted to AU (1 AU = 149597870.7 km)
    dist_km = 385000.56 + sigma_r * 1e-3
    dist_au = dist_km / 149597870.7

    return lon_deg, lat_deg, dist_au

def mean_lunar_node(t_centuries: float) -> float:
    """
    Mean Longitude of the Ascending Lunar Node (Rahu) in degrees [0, 360).
    Omega = 125.04452 - 1934.136261 * T + 0.0020708 * T^2 + T^3 / 450000
    """
    t = t_centuries
    om = 125.0445222 - 1934.1362608 * t + 0.0020708 * (t ** 2) + (t ** 3) / 450000.0
    return (om % 360.0 + 360.0) % 360.0

def true_lunar_node(t_centuries: float) -> float:
    """
    Osculating / True Longitude of the Ascending Lunar Node (Rahu) in degrees.
    Formula includes periodic solar and lunar perturbations on node.
    """
    t = t_centuries
    mean_node = mean_lunar_node(t)
    l, lp, f, d, om = fundamental_arguments(t)

    # Periodic perturbations on true node
    d_node = (
        -1.4979 * math.sin(2.0 * (d - f))
        - 0.1500 * math.sin(lp)
        - 0.1226 * math.sin(2.0 * d)
        + 0.1176 * math.sin(2.0 * f)
        - 0.0801 * math.sin(2.0 * (l - f))
    )
    return (mean_node + d_node) % 360.0

def mean_lunar_apogee(t_centuries: float) -> float:
    """
    Mean Longitude of Lunar Apogee (Mean Lilith / Black Moon) in degrees [0, 360).
    Gamma' = Mean Longitude L' - Mean Anomaly M'
    """
    t = t_centuries
    # Mean longitude of perigee pi_moon
    pi_moon = 83.35324312 + 4069.0137287 * t - 0.0103238 * (t ** 2) - (t ** 3) / 80053.0
    # Apogee is opposite of perigee (+ 180 deg)
    apogee = pi_moon + 180.0
    return (apogee % 360.0 + 360.0) % 360.0

def true_lunar_apogee(t_centuries: float) -> float:
    """
    True (Osculating) Longitude of Lunar Apogee (True Lilith) in degrees.
    Includes major solar perturbations on lunar eccentricity/perigee.
    """
    t = t_centuries
    mean_apogee = mean_lunar_apogee(t)
    l, lp, f, d, om = fundamental_arguments(t)

    # Major perturbation terms on lunar perigee/apogee (Evection & variation harmonics)
    d_apogee = (
        math.degrees(
            0.245 * math.sin(2.0 * d - 2.0 * l)
            + 0.055 * math.sin(2.0 * d)
            - 0.026 * math.sin(lp)
            + 0.015 * math.sin(2.0 * d - l)
        )
    )
    return (mean_apogee + d_apogee) % 360.0
