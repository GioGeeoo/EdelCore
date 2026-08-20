"""
Small Bodies, Asteroids, and Centaurs Orbit Evaluation Engine.
Provides Keplerian elements and secular perturbation models for:
- 2060 Chiron (Centaur)
- 1 Ceres (Dwarf planet / Main Belt)
- 2 Pallas (Main Belt)
- 3 Juno (Main Belt)
- 4 Vesta (Main Belt)
"""
import math
from typing import Tuple
from .vsop87 import _solve_kepler, earth_heliocentric

# Orbital elements at J2000.0 (JD 2451545.0) and secular variation rates per Julian century T
# Source: JPL Small-Body Database / Minor Planet Center / Bowell Asteroid Orbital Elements
# Format: [a (AU), a_dot, e, e_dot, inc (deg), inc_dot, M0 (deg), n (deg/century), peri_w (deg), peri_dot, node_Omega (deg), node_dot]
SMALL_BODY_ELEMENTS = {
    "Chiron": (
        13.649666, 0.00018,
        0.379124, -0.000045,
        6.9281, -0.0012,
        27.6828, 713.5786,     # Period ~ 50.45 years -> 713.5 deg/century
        339.6387, 0.038,
        209.2844, -0.025
    ),
    "Ceres": (
        2.767409, 0.000002,
        0.075823, -0.000015,
        10.5932, -0.0035,
        95.9891, 7819.743,     # Period ~ 4.60 years -> 7819.7 deg/century
        73.5976, 0.052,
        80.3055, -0.041
    ),
    "Pallas": (
        2.771783, -0.000001,
        0.231269, 0.000024,
        34.8410, 0.0018,
        108.6814, 7802.852,    # Period ~ 4.61 years -> 7802.8 deg/century
        310.0488, 0.045,
        173.0804, -0.038
    ),
    "Juno": (
        2.668744, 0.000003,
        0.255498, -0.000018,
        12.9821, -0.0022,
        38.2435, 8257.062,     # Period ~ 4.36 years -> 8257.1 deg/century
        248.4099, 0.061,
        169.8517, -0.055
    ),
    "Vesta": (
        2.361793, 0.000001,
        0.088741, 0.000031,
        7.1404, 0.0021,
        20.8637, 9918.025,     # Period ~ 3.63 years -> 9918.0 deg/century
        150.5833, 0.068,
        103.8108, -0.049
    )
}

def small_body_heliocentric(name: str, t_centuries: float) -> Tuple[float, float, float]:
    """
    Calculate heliocentric rectangular coordinates (X, Y, Z in AU) in J2000 ecliptic frame.
    """
    if name not in SMALL_BODY_ELEMENTS:
        raise ValueError(f"Unknown small body: {name}")

    elem = SMALL_BODY_ELEMENTS[name]
    t = t_centuries

    a = elem[0] + elem[1] * t
    e = elem[2] + elem[3] * t
    inc = math.radians(elem[4] + elem[5] * t)
    m_anom = math.radians((elem[6] + elem[7] * t) % 360.0)
    omega = math.radians((elem[8] + elem[9] * t) % 360.0)
    node = math.radians((elem[10] + elem[11] * t) % 360.0)

    # Solve Kepler's equation
    e_anom = _solve_kepler(m_anom, e)

    # Orbital plane coordinates
    x_orb = a * (math.cos(e_anom) - e)
    y_orb = a * math.sqrt(max(0.0, 1.0 - e**2)) * math.sin(e_anom)

    # Transformation to J2000 ecliptic
    cos_om, sin_om = math.cos(omega), math.sin(omega)
    cos_node, sin_node = math.cos(node), math.sin(node)
    cos_i, sin_i = math.cos(inc), math.sin(inc)

    # P and Q vectors
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

def small_body_geocentric(name: str, t_centuries: float) -> Tuple[float, float, float]:
    """
    Calculate geocentric rectangular coordinates (X, Y, Z in AU) for small body.
    """
    px, py, pz = small_body_heliocentric(name, t_centuries)
    # Earth heliocentric
    l_e, b_e, r_e = earth_heliocentric(t_centuries)
    ex = r_e * math.cos(b_e) * math.cos(l_e)
    ey = r_e * math.cos(b_e) * math.sin(l_e)
    ez = r_e * math.sin(b_e)
    return px - ex, py - ey, pz - ez
