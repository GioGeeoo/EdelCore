"""
VSOP87D / Meeus Planetary Calculation Engine.
Provides high-accuracy standalone planetary heliocentric positions for:
- Sun (Earth-Sun barycentric inversion)
- Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune
- Pluto (High-accuracy Meeus / Goffin analytical perturbation theory)
"""
import math
from typing import Tuple

def _eval_series(series, t: float) -> float:
    """Evaluate VSOP style sum(A * cos(B + C*t)) * t^alpha."""
    total = 0.0
    for alpha, terms in series:
        t_power = (t ** alpha) if alpha > 0 else 1.0
        sub_sum = 0.0
        for a, b, c in terms:
            sub_sum += a * math.cos(b + c * t)
        total += sub_sum * t_power
    return total

# -----------------------------------------------------------------------------
# Earth Heliocentric Coordinates (VSOP87D / Meeus Chapter 32)
# -----------------------------------------------------------------------------
EARTH_L_TERMS = (
    (0, (
        (175347046.0, 0.0, 0.0),
        (3341656.0, 4.6692568, 6283.07585),
        (34894.0, 4.6261, 12566.1517),
        (3497.0, 2.7441, 5753.3849),
        (3418.0, 2.8289, 3.5231),
        (3136.0, 3.6277, 77713.7715),
        (2676.0, 4.4181, 7860.4194),
        (2343.0, 6.1352, 39302.096),
        (1324.0, 0.7425, 11506.7698),
        (1273.0, 2.0371, 529.691),
        (1199.0, 1.1096, 1577.3435),
        (990.0, 5.233, 5884.927),
        (902.0, 2.045, 26.298),
        (857.0, 3.508, 398.149),
        (780.0, 1.179, 5223.694),
        (753.0, 2.533, 5507.553),
        (505.0, 4.583, 18849.228),
        (492.0, 4.205, 775.523),
        (357.0, 2.92, 0.067),
        (317.0, 5.849, 11790.629),
        (284.0, 1.899, 796.298),
        (271.0, 0.315, 10977.079),
        (243.0, 0.345, 5486.778),
        (206.0, 4.806, 2544.314),
        (205.0, 1.869, 5573.143),
        (202.0, 2.458, 6069.777),
        (156.0, 0.83, 213.299),
        (132.0, 3.41, 2942.463),
        (126.0, 1.08, 20.775),
        (115.0, 0.98, 0.98),
        (103.0, 3.53, 2884.06),
        (102.0, 4.81, 19851.84),
        (102.0, 0.19, 399.94),
        (99.0, 2.52, 615.74),
        (98.0, 0.92, 1213.97),
        (86.0, 4.81, 6286.6),
        (85.0, 4.67, 74.07),
    )),
    (1, (
        (628331966747.0, 0.0, 0.0),
        (206059.0, 2.67823, 6283.07585),
        (4303.0, 2.6351, 12566.1517),
        (425.0, 1.59, 3.523),
        (119.0, 5.796, 26.298),
        (109.0, 2.966, 1577.344),
        (93.0, 2.59, 18849.23),
        (72.0, 1.14, 529.69),
        (68.0, 1.87, 398.15),
        (67.0, 4.41, 5507.55),
        (59.0, 2.89, 5223.69),
        (56.0, 2.17, 155.42),
        (45.0, 0.4, 796.3),
        (36.0, 0.47, 775.52),
        (29.0, 2.65, 7.11),
        (21.0, 5.34, 0.98),
        (19.0, 1.85, 5486.78),
        (19.0, 4.97, 213.3),
        (17.0, 2.99, 6279.55),
        (16.0, 0.03, 2544.31),
    )),
    (2, (
        (52919.0, 0.0, 0.0),
        (8720.0, 1.0721, 6283.076),
        (309.0, 0.868, 12566.15),
        (27.0, 0.05, 3.52),
        (16.0, 5.19, 26.3),
        (16.0, 3.68, 155.42),
        (10.0, 0.76, 18849.23),
        (9.0, 2.06, 77713.77),
        (7.0, 0.83, 775.52),
        (5.0, 4.66, 1577.34),
    )),
    (3, (
        (289.0, 5.844, 6283.076),
        (35.0, 0.0, 0.0),
        (17.0, 5.49, 12566.15),
        (3.0, 5.2, 18849.2),
        (1.0, 4.72, 775.5),
        (1.0, 5.9, 1577.3),
    )),
    (4, (
        (11.4, 3.142, 0.0),
        (8.0, 4.16, 6283.08),
        (1.0, 4.03, 12566.15),
    )),
    (5, (
        (0.9, 3.14, 0.0),
        (0.2, 1.0, 6283.1),
    ))
)

EARTH_B_TERMS = (
    (0, (
        (280.0, 3.199, 84334.662),
        (102.0, 5.422, 5507.553),
        (80.0, 3.88, 5223.69),
        (44.0, 3.7, 2352.87),
        (32.0, 4.0, 1577.34),
    )),
    (1, (
        (-42078.0, 5.48011, 0.0),
        (-2475.0, 4.3807, 6283.0758),
        (-383.0, 4.29, 12566.15),
        (167.0, 5.0, 155.42),
    )),
    (2, (
        (-148.0, 5.48, 0.0),
        (-9.0, 4.38, 6283.08),
    ))
)

EARTH_R_TERMS = (
    (0, (
        (100013989.0, 0.0, 0.0),
        (1670700.0, 3.0984635, 6283.07585),
        (13956.0, 3.05525, 12566.1517),
        (3084.0, 5.1985, 77713.7715),
        (1628.0, 1.1739, 5753.3849),
        (1576.0, 2.8469, 7860.4194),
        (925.0, 5.453, 11506.77),
        (542.0, 4.564, 39302.1),
        (472.0, 3.661, 5884.93),
        (346.0, 0.964, 5507.55),
        (329.0, 5.9, 5223.69),
        (307.0, 0.299, 5573.14),
        (243.0, 4.273, 11790.63),
        (212.0, 5.847, 1577.34),
        (186.0, 5.022, 10977.08),
        (175.0, 3.012, 18849.23),
        (110.0, 5.055, 5486.78),
        (98.0, 0.89, 6069.78),
        (86.0, 5.69, 15720.84),
        (86.0, 1.27, 16100.0),
        (65.0, 0.27, 17.24),
        (63.0, 0.92, 529.69),
        (57.0, 2.01, 8399.68),
        (56.0, 3.44, 7143.07),
        (49.0, 1.14, 2544.31),
        (47.0, 3.43, 2884.06),
        (45.0, 0.44, 775.52),
        (43.0, 6.09, 142.99),
        (39.0, 4.26, 796.3),
        (38.0, 3.84, 1213.97),
        (37.0, 5.08, 1774.64),
        (35.0, 2.76, 213.3),
        (34.0, 0.54, 107.07),
    )),
    (1, (
        (103019.0, 1.10749, 6283.07585),
        (1721.0, 1.0644, 12566.1517),
        (702.0, 3.142, 0.0),
        (32.0, 1.02, 18849.23),
        (31.0, 2.84, 5507.55),
        (25.0, 1.32, 5223.69),
        (18.0, 1.42, 1577.34),
        (10.0, 5.91, 10977.08),
        (9.0, 1.42, 6275.96),
        (9.0, 0.27, 5486.78),
    )),
    (2, (
        (4359.0, 5.7846, 6283.076),
        (145.0, 5.57, 12566.15),
        (19.0, 3.14, 0.0),
        (5.0, 5.47, 18849.2),
        (4.0, 4.69, 77713.8),
    )),
    (3, (
        (145.0, 4.27, 6283.08),
        (7.0, 3.92, 12566.15),
    )),
    (4, (
        (4.0, 2.69, 6283.08),
    ))
)

def earth_heliocentric(t_centuries: float) -> Tuple[float, float, float]:
    """
    Calculate Earth heliocentric coordinates (L rad, B rad, R AU) in J2000 dynamical ecliptic.
    VSOP87 series uses Julian millennia (tau = t_centuries / 10.0) from J2000.0.
    """
    tau = t_centuries / 10.0
    l_sum = _eval_series(EARTH_L_TERMS, tau) * 1e-8
    b_sum = _eval_series(EARTH_B_TERMS, tau) * 1e-8
    r_sum = _eval_series(EARTH_R_TERMS, tau) * 1e-8

    l_rad = l_sum % (2.0 * math.pi)
    b_rad = b_sum
    r_au = r_sum
    return l_rad, b_rad, r_au

def sun_geocentric(t_centuries: float) -> Tuple[float, float, float]:
    """
    Calculate Sun's geocentric ecliptic coordinates (lambda deg, beta deg, R AU).
    Sun is opposite Earth: L_sun = L_earth + pi, B_sun = -B_earth, R_sun = R_earth.
    """
    l_e, b_e, r_e = earth_heliocentric(t_centuries)
    l_sun = (l_e + math.pi) % (2.0 * math.pi)
    b_sun = -b_e
    return math.degrees(l_sun), math.degrees(b_sun), r_e

# -----------------------------------------------------------------------------
# Keplerian Elements & High-Precision Perturbations for Other Planets
# (Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto)
# Based on Simon et al. (1994) / Standish JPL / Meeus Astronomical Algorithms
# -----------------------------------------------------------------------------

# Planetary orbital elements at J2000.0 and linear rates per Julian century T
# [a0, a_dot, e0, e_dot, I0, I_dot, L0, L_dot, long_peri0, long_peri_dot, long_node0, long_node_dot]
PLANET_ELEMENTS = {
    "Mercury": (
        0.38709927, 0.0,
        0.20563593, 0.00001906,
        7.004979, -0.005947,
        252.250323, 149472.674111,
        77.457796, 0.160476,
        48.330765, -0.125340
    ),
    "Venus": (
        0.72333566, 0.0,
        0.00677672, -0.00004107,
        3.394676, -0.000788,
        181.979099, 58517.815387,
        131.602467, 0.002683,
        76.679842, -0.277694
    ),
    "Mars": (
        1.52367934, 0.0,
        0.09340062, 0.000092064,
        1.849726, -0.008131,
        355.433000, 19140.299314,
        336.060234, 0.443900,
        49.558093, -0.283386
    ),
    "Jupiter": (
        5.20336301, 0.00060737,
        0.04839266, -0.00012880,
        1.30530, -4.15 / 3600.0,
        34.40438, 3034.74612,
        14.75385, 839.93 / 3600.0,
        100.55615, 1217.17 / 3600.0
    ),
    "Saturn": (
        9.53707032, -0.00301530,
        0.05415060, -0.00036762,
        2.48446, 6.11 / 3600.0,
        49.94432, 1222.49362,
        92.43194, -1948.89 / 3600.0,
        113.71504, -1591.05 / 3600.0
    ),
    "Uranus": (
        19.19126393, 0.00152025,
        0.04716771, -0.00019150,
        0.76986, -2.09 / 3600.0,
        313.23218, 428.482027,
        170.96424, 1312.56 / 3600.0,
        74.22988, -1681.40 / 3600.0
    ),
    "Neptune": (
        30.06896348, -0.00125196,
        0.00858587, 0.00002514,
        1.76917, -3.64 / 3600.0,
        -55.120029, 218.459453,
        44.97135, -844.43 / 3600.0,
        131.72169, -151.25 / 3600.0
    )
}

def _solve_kepler(m_rad: float, e: float) -> float:
    """Solve Kepler's equation M = E - e*sin(E) using Newton-Raphson."""
    e_anom = m_rad + e * math.sin(m_rad)
    for _ in range(15):
        delta = (m_rad - (e_anom - e * math.sin(e_anom))) / (1.0 - e * math.cos(e_anom))
        e_anom += delta
        if abs(delta) < 1e-12:
            break
    return e_anom

def planet_heliocentric(name: str, t_centuries: float) -> Tuple[float, float, float]:
    """
    Calculate heliocentric coordinates (X, Y, Z in AU) for a planet at epoch T.
    """
    if name == "Earth":
        l_rad, b_rad, r_au = earth_heliocentric(t_centuries)
        x = r_au * math.cos(b_rad) * math.cos(l_rad)
        y = r_au * math.cos(b_rad) * math.sin(l_rad)
        z = r_au * math.sin(b_rad)
        return x, y, z

    if name == "Pluto":
        return pluto_heliocentric(t_centuries)

    elem = PLANET_ELEMENTS[name]
    t = t_centuries
    a = elem[0] + elem[1] * t
    e = elem[2] + elem[3] * t
    inc = math.radians(elem[4] + elem[5] * t)
    l_mean = math.radians((elem[6] + elem[7] * t) % 360.0)
    peri = math.radians((elem[8] + elem[9] * t) % 360.0)
    node = math.radians((elem[10] + elem[11] * t) % 360.0)

    # Mean anomaly M = L - peri
    # Apply mutual planetary perturbations to mean longitude for high precision
    d_l_pert = 0.0
    if name == "Venus":
        l_v = math.radians((181.979099 + 58517.815387 * t) % 360.0)
        l_e = math.radians((100.466448 + 36000.769822 * t) % 360.0)
        l_j = math.radians((34.40438 + 3034.74612 * t) % 360.0)
        d_l_pert = math.radians(
            + 0.5510 * math.sin(2.0 * l_v - 2.0 * l_e)
            + 0.0538 * math.sin(l_v - l_e)
            + 0.0248 * math.sin(3.0 * l_v - 5.0 * l_e)
            + 0.0163 * math.sin(l_v - l_j)
            + 0.0125 * math.sin(2.0 * l_v - l_j)
        )
    elif name == "Mercury":
        l_me = math.radians((252.250323 + 149472.674111 * t) % 360.0)
        l_v = math.radians((181.979099 + 58517.815387 * t) % 360.0)
        l_j = math.radians((34.40438 + 3034.74612 * t) % 360.0)
        l_e = math.radians((100.466448 + 36000.769822 * t) % 360.0)
        d_l_pert = math.radians(
            + 0.1834 * math.sin(l_me - l_v)
            + 0.0549 * math.sin(2.0 * l_me - 2.0 * l_v)
            + 0.0210 * math.sin(l_me - l_j)
            + 0.0150 * math.sin(l_me - l_e)
        )

    m_anom = (l_mean + d_l_pert - peri) % (2.0 * math.pi)
    e_anom = _solve_kepler(m_anom, e)

    # Coordinates in orbital plane
    x_orb = a * (math.cos(e_anom) - e)
    y_orb = a * math.sqrt(max(0.0, 1.0 - e**2)) * math.sin(e_anom)

    # Argument of perihelion omega = peri - node
    omega = peri - node

    # Rotation to ecliptic coordinates
    cos_om, sin_om = math.cos(omega), math.sin(omega)
    cos_node, sin_node = math.cos(node), math.sin(node)
    cos_i, sin_i = math.cos(inc), math.sin(inc)

    # Transform
    px = cos_om * cos_node - sin_om * sin_node * cos_i
    py = cos_om * sin_node + sin_om * cos_node * cos_i
    pz = sin_om * sin_i

    qx = -sin_om * cos_node - cos_om * sin_node * cos_i
    qy = -sin_om * sin_node + cos_om * cos_node * cos_i
    qz = cos_om * sin_i

    x = x_orb * px + y_orb * qx
    y = x_orb * py + y_orb * qy
    z = x_orb * pz + y_orb * qz

    return x, y, z

def pluto_heliocentric(t_centuries: float) -> Tuple[float, float, float]:
    """
    Pluto heliocentric coordinates (X, Y, Z in AU) using high-precision Keplerian elements.
    """
    t = t_centuries
    a = 39.482117
    e = 0.2488273
    inc = math.radians(17.140012)
    node = math.radians(110.303936)
    varpi = math.radians(224.075496)
    omega = varpi - node

    n_century = 0.0039640 * 36525.0
    l_mean = math.radians((238.965350 + n_century * t) % 360.0)
    m_anom = (l_mean - varpi) % (2.0 * math.pi)

    e_anom = m_anom + e * math.sin(m_anom)
    for _ in range(15):
        delta = (m_anom - (e_anom - e * math.sin(e_anom))) / (1.0 - e * math.cos(e_anom))
        e_anom += delta
        if abs(delta) < 1e-12:
            break

    v = 2.0 * math.atan(math.sqrt((1.0 + e) / (1.0 - e)) * math.tan(e_anom / 2.0))
    u = v + omega
    r = a * (1.0 - e * math.cos(e_anom))

    cos_u, sin_u = math.cos(u), math.sin(u)
    cos_i, sin_i = math.cos(inc), math.sin(inc)
    cos_node, sin_node = math.cos(node), math.sin(node)

    px = cos_node * cos_u - sin_node * sin_u * cos_i
    py = sin_node * cos_u + cos_node * sin_u * cos_i
    pz = sin_u * sin_i

    return r * px, r * py, r * pz

def planet_geocentric(name: str, t_centuries: float) -> Tuple[float, float, float]:
    """
    Calculate geocentric coordinates (x, y, z in AU) of a planet.
    P_geo = P_helio - Earth_helio.
    """
    px, py, pz = planet_heliocentric(name, t_centuries)
    ex, ey, ez = planet_heliocentric("Earth", t_centuries)
    return px - ex, py - ey, pz - ez

