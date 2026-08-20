"""
Astrometric and Relativistic Corrections:
- Light-time travel correction (t - tau)
- Annual Aberration
- Relativistic Solar Gravitational Deflection
- Topocentric Parallax for observer coordinates (lat, lon, altitude)
"""
import math
from typing import Tuple

# Speed of light in AU/day
C_AU_PER_DAY = 173.1446326846693
# Earth equatorial radius in meters (WGS84)
WGS84_A = 6378137.0
# Earth flattening (WGS84)
WGS84_F = 1.0 / 298.257223563
# 1 AU in meters
AU_IN_METERS = 149597870700.0

def apply_annual_aberration(
    geo_x: float, geo_y: float, geo_z: float,
    v_earth_x: float, v_earth_y: float, v_earth_z: float
) -> Tuple[float, float, float]:
    """
    Apply annual aberration to geocentric position vector using Earth's orbital velocity vector.
    Position vector in AU, velocity vector in AU/day.
    Formula: u_app = (u + V/c) / (1 + (u . V)/c)
    """
    dist = math.sqrt(geo_x**2 + geo_y**2 + geo_z**2)
    if dist == 0.0:
        return geo_x, geo_y, geo_z

    # Unit direction vector to celestial body
    ux = geo_x / dist
    uy = geo_y / dist
    uz = geo_z / dist

    # Earth velocity / c
    beta_x = v_earth_x / C_AU_PER_DAY
    beta_y = v_earth_y / C_AU_PER_DAY
    beta_z = v_earth_z / C_AU_PER_DAY

    u_dot_beta = ux * beta_x + uy * beta_y + uz * beta_z
    gamma = 1.0 / math.sqrt(1.0 - (beta_x**2 + beta_y**2 + beta_z**2))

    denom = 1.0 + u_dot_beta
    # Relativistic aberration
    app_ux = (ux + beta_x + (gamma / (gamma + 1.0)) * u_dot_beta * beta_x) / denom
    app_uy = (uy + beta_y + (gamma / (gamma + 1.0)) * u_dot_beta * beta_y) / denom
    app_uz = (uz + beta_z + (gamma / (gamma + 1.0)) * u_dot_beta * beta_z) / denom

    # Normalize to original distance
    norm = math.sqrt(app_ux**2 + app_uy**2 + app_uz**2)
    return (app_ux / norm) * dist, (app_uy / norm) * dist, (app_uz / norm) * dist

def solar_gravitational_deflection(
    body_x: float, body_y: float, body_z: float,
    sun_geo_x: float, sun_geo_y: float, sun_geo_z: float
) -> Tuple[float, float, float]:
    """
    Relativistic gravitational light deflection by the Sun.
    body_*: geocentric vector to target body
    sun_geo_*: geocentric vector to Sun
    """
    r_body = math.sqrt(body_x**2 + body_y**2 + body_z**2)
    r_sun = math.sqrt(sun_geo_x**2 + sun_geo_y**2 + sun_geo_z**2)
    if r_body == 0.0 or r_sun == 0.0:
        return body_x, body_y, body_z

    # Unit vectors from Earth
    p_x, p_y, p_z = body_x / r_body, body_y / r_body, body_z / r_body
    e_x, e_y, e_z = sun_geo_x / r_sun, sun_geo_y / r_sun, sun_geo_z / r_sun

    # Unit vector from Sun to Earth
    # Vector from Sun to body
    q_x = body_x - sun_geo_x
    q_y = body_y - sun_geo_y
    q_z = body_z - sun_geo_z
    r_q = math.sqrt(q_x**2 + q_y**2 + q_z**2)
    if r_q == 0.0:
        return body_x, body_y, body_z
    q_x /= r_q
    q_y /= r_q
    q_z /= r_q

    # Cosine angle between body and Sun
    cos_d = p_x * e_x + p_y * e_y + p_z * e_z
    if cos_d <= -0.9999999 or cos_d >= 0.9999999:
        return body_x, body_y, body_z

    # Deflection factor (2 * GM_sun / (c^2 * r_sun)) = approx 4.072e-8 AU
    factor = 4.072e-8 / (1.0 + cos_d)
    
    dp_x = factor * ((p_y * e_z - p_z * e_y) * (e_y * p_z - e_z * p_y)) # transverse component
    # Simple vector formulation: dp = factor * ( (e - cos_d * p) )
    deflect_x = factor * (e_x - cos_d * p_x)
    deflect_y = factor * (e_y - cos_d * p_y)
    deflect_z = factor * (e_z - cos_d * p_z)

    new_p_x = p_x + deflect_x
    new_p_y = p_y + deflect_y
    new_p_z = p_z + deflect_z
    norm = math.sqrt(new_p_x**2 + new_p_y**2 + new_p_z**2)

    return (new_p_x / norm) * r_body, (new_p_y / norm) * r_body, (new_p_z / norm) * r_body

def observer_geocentric_position(
    lat_deg: float,
    lon_deg: float,
    alt_meters: float,
    gast_deg: float
) -> Tuple[float, float, float]:
    """
    Calculate geocentric rectangular coordinates (in AU) of an observer on the WGS84 Earth ellipsoid.
    Equatorial coordinate system (True Equator and Equinox of date).
    """
    phi = math.radians(lat_deg)
    # Geocentric coordinates on ellipsoid
    b_over_a = 1.0 - WGS84_F
    tan_u = b_over_a * math.tan(phi)
    cos_u = 1.0 / math.sqrt(1.0 + tan_u**2)
    sin_u = tan_u * cos_u

    rho_cos_phi = cos_u + (alt_meters / WGS84_A) * math.cos(phi)
    rho_sin_phi = b_over_a * sin_u + (alt_meters / WGS84_A) * math.sin(phi)

    # Local Sidereal Time in radians
    theta = math.radians((gast_deg + lon_deg) % 360.0)

    # Convert from Earth radii to AU
    earth_radius_au = WGS84_A / AU_IN_METERS

    x_obs = rho_cos_phi * math.cos(theta) * earth_radius_au
    y_obs = rho_cos_phi * math.sin(theta) * earth_radius_au
    z_obs = rho_sin_phi * earth_radius_au

    return x_obs, y_obs, z_obs

def apply_topocentric_parallax(
    geo_equatorial_x: float,
    geo_equatorial_y: float,
    geo_equatorial_z: float,
    obs_x: float,
    obs_y: float,
    obs_z: float
) -> Tuple[float, float, float]:
    """
    Subtract observer's geocentric vector to obtain topocentric position vector.
    """
    return (
        geo_equatorial_x - obs_x,
        geo_equatorial_y - obs_y,
        geo_equatorial_z - obs_z,
    )
