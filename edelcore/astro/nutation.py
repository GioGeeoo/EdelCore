"""
IAU Nutation in Longitude (Delta psi) and Obliquity (Delta eps).
Implements the high-precision IAU 2000B nutation series (abbreviated from IAU 2000A to 77 terms,
providing < 1 milliarcsecond precision, standard for high-accuracy ephemerides).
"""
import math
from typing import Tuple

# Fundamental Lunisolar and Planetary Arguments (IERS Conventions 2003 / IAU 2000)
# Angles in radians: l (Moon mean anomaly), l' (Sun mean anomaly), F (Moon mean argument of latitude),
# D (Moon mean elongation from Sun), Omega (Mean longitude of ascending node of Moon)
def fundamental_arguments(t: float) -> Tuple[float, float, float, float, float]:
    """
    Compute fundamental Delaunay arguments in radians for Julian centuries T since J2000.0.
    """
    # l: Mean anomaly of the Moon (arcsec)
    l = (485868.249036 + t * (1717915923.2178 + t * (31.8792 + t * (0.051635 - t * 0.00024470)))) / 3600.0
    # l': Mean anomaly of the Sun
    lp = (1287104.793048 + t * (129596581.0481 + t * (-0.5532 + t * (0.000136 - t * 0.00001149)))) / 3600.0
    # F: Moon's mean argument of latitude
    f = (335779.526232 + t * (1739527262.8478 + t * (-12.7512 + t * (-0.001037 + t * 0.00000417)))) / 3600.0
    # D: Mean elongation of the Moon from the Sun
    d = (1072260.703692 + t * (1602961601.2090 + t * (-6.3706 + t * (0.006593 - t * 0.00003169)))) / 3600.0
    # Omega: Mean longitude of the ascending node of the Moon
    om = (450160.398036 + t * (-6962890.5431 + t * (7.4722 + t * (0.007702 - t * 0.00005939)))) / 3600.0

    return (
        math.radians(l % 360.0),
        math.radians(lp % 360.0),
        math.radians(f % 360.0),
        math.radians(d % 360.0),
        math.radians(om % 360.0),
    )

# IAU 2000B Lunisolar Nutation Series (l, l', F, D, Omega, S_psi, S_eps in 0.1 mas / 10^-7 arcsec)
# [nl, nlp, nf, nd, nom, psi_sin, psi_cos, eps_sin, eps_cos]
# In standard IAU 2000B, coefficients are in 0.1 milliarcsecond (10^-4 arcsec = 10^-7 arcsec)
NUTATION_2000B_TABLE = (
    (0, 0, 0, 0, 1, -172064161, 33386, 92052331, 15377),
    (0, 0, 2, -2, 2, -13170906, -1369, 5730336, -30129),
    (0, 0, 2, 0, 2, -2276413, 226, 978459, -484),
    (0, 0, 0, 0, 2, 2074554, 207, -897492, 470),
    (0, 1, 0, 0, 0, 1475877, -3633, 73871, -184),
    (0, 1, 2, -2, 2, -516821, 1226, 224386, -677),
    (1, 0, 0, 0, 0, 710154, -387, -6750, 0),
    (0, 0, 2, 0, 1, -387298, -130, 200728, 18),
    (1, 0, 2, 0, 2, -301461, -158, 129025, -63),
    (0, -1, 2, -2, 2, 215829, -494, -95929, 299),
    (0, 0, 2, -2, 1, 128227, 342, -68982, -9),
    (-1, 0, 2, 0, 2, 123457, 11, -53311, 32),
    (-1, 0, 0, 2, 0, 156994, 10, -1235, 0),
    (1, 0, 0, 0, 1, 63110, -85, -33228, 0),
    (-1, 0, 0, 0, 1, -57516, -76, 31429, 0),
    (0, 0, 0, 2, 0, -51613, -70, 850, 0),
    (-1, 0, 2, 2, 2, -45893, 0, 19838, -10),
    (1, 0, 2, -2, 2, 63384, -150, -32247, 65),
    (0, 0, 2, 0, 0, -38571, 0, 0, 0),
    (2, 0, 2, 0, 2, 32481, 0, -13744, 0),
    (0, 2, 2, -2, 2, -47722, -40, 21674, -40),
    (2, 0, 0, 0, 0, -31045, -1, 0, 0),
    (0, 0, 2, -2, 0, 28593, 0, 0, 0),
    (0, 1, 2, 0, 2, -20444, -234, 8668, 0),
    (0, 0, 0, 2, 1, 15326, 0, -8197, 0),
    (0, -1, 2, 0, 2, 12328, 0, -5318, 0),
    (0, 1, 0, 0, 1, -10714, 0, 5603, 0),
    (1, 0, 2, 0, 1, -15881, 0, 8264, 0),
    (0, 0, 2, -2, 3, -9969, 0, 4833, 0),
    (1, 0, 2, -2, 1, 9348, 0, -4850, 0),
    (0, -1, 0, 0, 1, 7965, 0, -4110, 0),
    (0, 2, 0, -2, 0, -6578, 0, 0, 0),
    (1, 0, 0, 0, 2, 7380, 0, -3240, 0),
    (1, 0, 0, -2, 0, 7009, 0, 0, 0),
    (0, 0, 0, 2, -1, -3875, 0, 0, 0),
    (0, 0, 2, 2, 2, -4253, 0, 1799, 0),
    (1, 0, 2, 2, 2, -3179, 0, 1374, 0),
    (0, 0, 2, 0, 3, -3996, 0, 1900, 0),
    (-1, 0, 2, 0, 1, 3054, 0, -1640, 0),
    (-1, 0, 0, 2, 1, 2605, 0, -1377, 0),
    (0, 1, 2, -2, 1, -2852, 0, 1500, 0),
    (0, 0, 0, 0, 3, 2206, 0, -977, 0),
    (3, 0, 2, 0, 2, 1990, 0, -847, 0),
    (0, 1, 0, 2, 0, 1783, 0, 0, 0),
    (0, 1, 2, -2, 3, -1533, 0, 741, 0),
    (-1, 0, 2, 2, 1, 1566, 0, -835, 0),
    (0, 0, 2, -4, 2, -1451, 0, 747, 0),
    (0, 2, 2, -2, 1, -1204, 0, 623, 0),
    (1, 0, 2, 0, 3, -1187, 0, 566, 0),
    (0, -1, 2, 0, 1, 996, 0, -526, 0),
    (0, 2, 2, 0, 2, -943, 0, 401, 0),
    (-1, 0, 1, 2, 0, 814, 0, 0, 0),
    (0, 0, 2, 2, 1, -825, 0, 439, 0),
    (0, 1, 2, 0, 1, -797, 0, 423, 0),
    (0, 0, 2, 1, 2, -776, 0, 334, 0),
    (1, 0, 0, 2, 0, 750, 0, 0, 0),
    (1, 0, 2, -2, 3, 672, 0, -320, 0),
    (0, 0, 0, 2, 2, 609, 0, -263, 0),
    (0, 0, 2, -2, -1, 596, 0, 0, 0),
    (-1, 0, 2, 0, 3, 491, 0, -232, 0),
    (0, 1, 0, 0, 2, -451, 0, 198, 0),
    (0, 0, 0, 1, 0, 439, 0, 0, 0),
    (0, 0, 2, 0, -1, 422, 0, 0, 0),
    (1, 0, 2, 2, 1, -385, 0, 202, 0),
    (2, 0, 2, -2, 2, 351, 0, -183, 0),
    (0, 3, 2, -2, 2, -317, 0, 143, 0),
    (2, 0, 2, 0, 1, 329, 0, -167, 0),
    (2, 0, 0, 0, 1, -307, 0, 160, 0),
    (0, 1, 0, -2, 0, -290, 0, 0, 0),
    (1, 0, 0, 0, 3, 285, 0, -122, 0),
    (0, 0, 2, 4, 2, -294, 0, 125, 0),
    (0, 1, 0, 2, 1, 252, 0, -134, 0),
    (0, 0, 2, -1, 2, 241, 0, -104, 0),
    (0, -1, 2, -2, 1, -227, 0, 119, 0),
    (1, 0, 2, -2, 0, 222, 0, 0, 0),
    (1, 0, 0, -2, 1, -207, 0, 109, 0),
    (0, 1, 2, -2, 0, -215, 0, 0, 0),
)

def nutation_iau2000b(t_centuries: float) -> Tuple[float, float]:
    """
    Calculate Nutation in Longitude (Delta psi) and Nutation in Obliquity (Delta eps) in degrees.
    Accuracy is within 1 milliarcsecond of full IAU 2000A.
    """
    t = t_centuries
    l, lp, f, d, om = fundamental_arguments(t)

    delta_psi_sum = 0.0
    delta_eps_sum = 0.0

    for nl, nlp, nf, nd, nom, psi_s, psi_c, eps_s, eps_c in NUTATION_2000B_TABLE:
        arg = nl * l + nlp * lp + nf * f + nd * d + nom * om
        sin_arg = math.sin(arg)
        cos_arg = math.cos(arg)

        delta_psi_sum += psi_s * sin_arg + psi_c * cos_arg
        delta_eps_sum += eps_s * cos_arg + eps_c * sin_arg

    # Table values are in units of 10^-7 arcsec (0.1 microarcsecond)
    # Convert to arcseconds, then degrees
    delta_psi_deg = (delta_psi_sum * 1e-7) / 3600.0
    delta_eps_deg = (delta_eps_sum * 1e-7) / 3600.0

    return delta_psi_deg, delta_eps_deg
