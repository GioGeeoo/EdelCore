"""
Coordinate Transformations Subsystem for EdelCore.
Supports:
- Cartesian to Spherical (RA/Dec/R and Longitude/Latitude/R)
- Spherical to Cartesian
- Equatorial <-> Ecliptic frames (J2000 and date)
- Precession matrix (IAU 2006 / P03)
- Nutation matrix
"""
import math
from typing import Tuple

def cartesian_to_spherical(x: float, y: float, z: float) -> Tuple[float, float, float]:
    """
    Convert (x, y, z) to (lon/RA in deg [0, 360), lat/Dec in deg [-90, 90], distance R).
    """
    r_xy = math.hypot(x, y)
    r = math.hypot(r_xy, z)
    if r == 0.0:
        return 0.0, 0.0, 0.0

    lon_rad = math.atan2(y, x)
    lat_rad = math.atan2(z, r_xy)

    lon_deg = (math.degrees(lon_rad) + 360.0) % 360.0
    lat_deg = math.degrees(lat_rad)

    return lon_deg, lat_deg, r

def spherical_to_cartesian(lon_deg: float, lat_deg: float, r: float) -> Tuple[float, float, float]:
    """
    Convert (lon/RA in deg, lat/Dec in deg, distance R) to (x, y, z).
    """
    lon_rad = math.radians(lon_deg)
    lat_rad = math.radians(lat_deg)
    cos_lat = math.cos(lat_rad)

    x = r * cos_lat * math.cos(lon_rad)
    y = r * cos_lat * math.sin(lon_rad)
    z = r * math.sin(lat_rad)
    return x, y, z

def equatorial_to_ecliptic(
    ra_deg: float, dec_deg: float, eps_deg: float
) -> Tuple[float, float]:
    """
    Convert Equatorial (RA, Dec) to Ecliptic Longitude (lambda) and Latitude (beta)
    given Ecliptic Obliquity eps.
    """
    alpha = math.radians(ra_deg)
    delta = math.radians(dec_deg)
    eps = math.radians(eps_deg)

    sin_delta = math.sin(delta)
    cos_delta = math.cos(delta)
    sin_alpha = math.sin(alpha)
    cos_alpha = math.cos(alpha)
    sin_eps = math.sin(eps)
    cos_eps = math.cos(eps)

    # sin(beta) = sin(delta)*cos(eps) - cos(delta)*sin(eps)*sin(alpha)
    sin_beta = sin_delta * cos_eps - cos_delta * sin_eps * sin_alpha
    # clamp to [-1, 1] to avoid float precision issues
    sin_beta = max(-1.0, min(1.0, sin_beta))
    beta_rad = math.asin(sin_beta)

    # y = sin(alpha)*cos(eps) + tan(delta)*sin(eps)
    # x = cos(alpha)
    y = sin_alpha * cos_eps + math.tan(delta) * sin_eps
    x = cos_alpha
    lambda_rad = math.atan2(y, x)

    lambda_deg = (math.degrees(lambda_rad) + 360.0) % 360.0
    beta_deg = math.degrees(beta_rad)
    return lambda_deg, beta_deg

def ecliptic_to_equatorial(
    lambda_deg: float, beta_deg: float, eps_deg: float
) -> Tuple[float, float]:
    """
    Convert Ecliptic Longitude (lambda) and Latitude (beta) to Equatorial (RA, Dec)
    given Ecliptic Obliquity eps.
    """
    lam = math.radians(lambda_deg)
    bet = math.radians(beta_deg)
    eps = math.radians(eps_deg)

    sin_bet = math.sin(bet)
    cos_bet = math.cos(bet)
    sin_lam = math.sin(lam)
    cos_lam = math.cos(lam)
    sin_eps = math.sin(eps)
    cos_eps = math.cos(eps)

    sin_dec = sin_bet * cos_eps + cos_bet * sin_eps * sin_lam
    sin_dec = max(-1.0, min(1.0, sin_dec))
    dec_rad = math.asin(sin_dec)

    y = sin_lam * cos_eps - math.tan(bet) * sin_eps
    x = cos_lam
    ra_rad = math.atan2(y, x)

    ra_deg = (math.degrees(ra_rad) + 360.0) % 360.0
    dec_deg = math.degrees(dec_rad)
    return ra_deg, dec_deg

def precession_matrix_iau2006(t_centuries: float) -> Tuple[Tuple[float, ...], ...]:
    """
    IAU 2006 (P03) Precession 3x3 Matrix from J2000.0 to Date T (centuries).
    Transforms equatorial vectors from J2000.0 (ICRF) to Mean Equator/Equinox of date:
    r_date = P * r_J2000.
    """
    t = t_centuries
    # Fukushima-Williams 4 angles (or Lieske / Capitaine zeta, z, theta)
    # Using Capitaine et al. 2003 / IAU 2006 precession angles (arcseconds):
    zeta = (2.5976176 + 2306.0809506 * t + 0.3019015 * t**2 + 0.0179663 * t**3 - 0.0000327 * t**4 - 0.0000002 * t**5) / 3600.0
    z = (-2.5976176 + 2306.0803226 * t + 1.0947790 * t**2 + 0.0182273 * t**3 + 0.0000470 * t**4 - 0.0000003 * t**5) / 3600.0
    theta = (2004.1917476 * t - 0.4269353 * t**2 - 0.0418251 * t**3 - 0.0000601 * t**4 - 0.0000001 * t**5) / 3600.0

    zeta_r = math.radians(zeta)
    z_r = math.radians(z)
    th_r = math.radians(theta)

    sin_zeta = math.sin(zeta_r)
    cos_zeta = math.cos(zeta_r)
    sin_z = math.sin(z_r)
    cos_z = math.cos(z_r)
    sin_th = math.sin(th_r)
    cos_th = math.cos(th_r)

    p11 = cos_zeta * cos_th * cos_z - sin_zeta * sin_z
    p12 = -sin_zeta * cos_th * cos_z - cos_zeta * sin_z
    p13 = -sin_th * cos_z

    p21 = cos_zeta * cos_th * sin_z + sin_zeta * cos_z
    p22 = -sin_zeta * cos_th * sin_z + cos_zeta * cos_z
    p23 = -sin_th * sin_z

    p31 = cos_zeta * sin_th
    p32 = -sin_zeta * sin_th
    p33 = cos_th

    return (
        (p11, p12, p13),
        (p21, p22, p23),
        (p31, p32, p33),
    )

def nutation_matrix(eps_0_deg: float, delta_psi_deg: float, delta_eps_deg: float) -> Tuple[Tuple[float, ...], ...]:
    """
    Nutation 3x3 Matrix: N = R_x(-(eps_0 + delta_eps)) * R_z(-delta_psi) * R_x(eps_0).
    Transforms mean equator/equinox to true equator/equinox.
    """
    eps_0 = math.radians(eps_0_deg)
    eps = math.radians(eps_0_deg + delta_eps_deg)
    dpsi = math.radians(delta_psi_deg)

    c0, s0 = math.cos(eps_0), math.sin(eps_0)
    c1, s1 = math.cos(eps), math.sin(eps)
    cdp, sdp = math.cos(dpsi), math.sin(dpsi)

    n11 = cdp
    n12 = -sdp * c0
    n13 = -sdp * s0

    n21 = sdp * c1
    n22 = c1 * cdp * c0 + s1 * s0
    n23 = c1 * cdp * s0 - s1 * c0

    n31 = sdp * s1
    n32 = s1 * cdp * c0 - c1 * s0
    n33 = s1 * cdp * s0 + c1 * c0

    return (
        (n11, n12, n13),
        (n21, n22, n23),
        (n31, n32, n33),
    )

def apply_matrix_3x3(m: Tuple[Tuple[float, ...], ...], v: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Matrix-vector multiplication for 3x3 matrix and 3D vector."""
    x = m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2]
    y = m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2]
    z = m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2]
    return x, y, z
