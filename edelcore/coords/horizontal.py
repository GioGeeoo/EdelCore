"""
Horizontal Coordinate System & Atmospheric Refraction.
Converts Topocentric Equatorial Coordinates (RA, Dec) to Horizontal Coordinates (Azimuth, Altitude),
and applies high-accuracy atmospheric refraction corrections (Saemundsson / Bennett standard formulas).
"""
import math
from typing import Tuple, NamedTuple

class HorizontalCoords(NamedTuple):
    azimuth: float          # Azimuth in degrees [0, 360) measured from North towards East
    true_altitude: float    # Geometric / True altitude in degrees [-90, +90]
    apparent_altitude: float # Refracted / Apparent altitude in degrees [-90, +90]
    refraction: float       # Refraction angle in arcminutes

def apply_refraction(
    true_alt_deg: float,
    pressure_mbar: float = 1013.25,
    temp_celsius: float = 10.0
) -> Tuple[float, float]:
    """
    Compute atmospheric refraction R (in degrees) and apparent altitude h_app = h_true + R.
    Uses Bennett (1982) formula for true altitude (Meeus Astronomical Algorithms Ch. 16, eq 16.3):
    R_0 = 1.0 / tan(h_true + 7.31 / (h_true + 4.4)) in arcminutes where h is in degrees.
    Returns: (apparent_altitude_deg, refraction_arcmin)
    """
    h = true_alt_deg
    if h < -5.0:
        return h, 0.0

    # Bennett formula: argument of tan is in degrees
    arg_deg = h + 7.31 / (h + 4.4)
    r_arcmin = 1.0 / math.tan(math.radians(arg_deg))

    # Pressure and temperature correction factor: (P / 1010) * (283 / (273 + T))
    pt_factor = (pressure_mbar / 1010.0) * (283.0 / (273.15 + temp_celsius))
    r_corrected_arcmin = max(0.0, r_arcmin * pt_factor)

    r_deg = r_corrected_arcmin / 60.0
    h_app = h + r_deg
    return h_app, r_corrected_arcmin

def remove_refraction(
    apparent_alt_deg: float,
    pressure_mbar: float = 1013.25,
    temp_celsius: float = 10.0
) -> Tuple[float, float]:
    """
    Inverse refraction: Compute true altitude from apparent altitude using Bennett's formula.
    Returns: (true_altitude_deg, refraction_arcmin)
    """
    h_app = apparent_alt_deg
    if h_app < -5.0:
        return h_app, 0.0

    # Bennett (1982) formula for apparent altitude
    arg_deg = h_app + 7.31 / (h_app + 4.4)
    r_arcmin = 1.0 / math.tan(math.radians(arg_deg))

    pt_factor = (pressure_mbar / 1010.0) * (283.0 / (273.15 + temp_celsius))
    r_corrected_arcmin = max(0.0, r_arcmin * pt_factor)

    r_deg = r_corrected_arcmin / 60.0
    h_true = h_app - r_deg
    return h_true, r_corrected_arcmin

def equatorial_to_horizontal(
    ra_deg: float,
    dec_deg: float,
    lmst_deg: float,
    lat_deg: float,
    pressure_mbar: float = 1013.25,
    temp_celsius: float = 10.0
) -> HorizontalCoords:
    """
    Convert Topocentric Equatorial (RA, Dec) to Horizontal (Azimuth, True Altitude, Apparent Altitude).
    Azimuth is measured from True North Eastward (North = 0, East = 90, South = 180, West = 270).
    Local Hour Angle H = LMST - RA.
    """
    # Local Hour Angle in radians
    h_angle_rad = math.radians((lmst_deg - ra_deg + 360.0) % 360.0)
    dec_rad = math.radians(dec_deg)
    lat_rad = math.radians(lat_deg)

    sin_dec = math.sin(dec_rad)
    cos_dec = math.cos(dec_rad)
    sin_lat = math.sin(lat_rad)
    cos_lat = math.cos(lat_rad)
    cos_h = math.cos(h_angle_rad)
    sin_h = math.sin(h_angle_rad)

    # 1. Altitude h_true: sin(h) = sin(phi)*sin(delta) + cos(phi)*cos(delta)*cos(H)
    sin_alt = sin_lat * sin_dec + cos_lat * cos_dec * cos_h
    sin_alt = max(-1.0, min(1.0, sin_alt))
    alt_rad = math.asin(sin_alt)
    true_alt_deg = math.degrees(alt_rad)

    # 2. Azimuth A (from North):
    # tan(A) = -sin(H) / (tan(delta)*cos(phi) - sin(phi)*cos(H))
    # Or in 3D:
    # y = -cos(delta) * sin(H)
    # x = cos(phi) * sin(delta) - sin(phi) * cos(delta) * cos(H)
    y = -cos_dec * sin_h
    x = cos_lat * sin_dec - sin_lat * cos_dec * cos_h
    az_rad = math.atan2(y, x)
    azimuth_deg = (math.degrees(az_rad) + 360.0) % 360.0

    # 3. Refraction & Apparent Altitude
    app_alt_deg, r_arcmin = apply_refraction(true_alt_deg, pressure_mbar, temp_celsius)

    return HorizontalCoords(
        azimuth=azimuth_deg,
        true_altitude=true_alt_deg,
        apparent_altitude=app_alt_deg,
        refraction=r_corrected_arcmin if (r_corrected_arcmin := r_arcmin) else 0.0
    )

def horizontal_to_equatorial(
    azimuth_deg: float,
    alt_deg: float,
    lmst_deg: float,
    lat_deg: float,
    is_apparent_altitude: bool = False,
    pressure_mbar: float = 1013.25,
    temp_celsius: float = 10.0
) -> Tuple[float, float]:
    """
    Inverse conversion: Horizontal (Azimuth, Altitude) to Equatorial (RA, Dec).
    Returns: (ra_deg, dec_deg)
    """
    if is_apparent_altitude:
        true_alt_deg, _ = remove_refraction(alt_deg, pressure_mbar, temp_celsius)
    else:
        true_alt_deg = alt_deg

    az_rad = math.radians(azimuth_deg)
    alt_rad = math.radians(true_alt_deg)
    lat_rad = math.radians(lat_deg)

    sin_alt = math.sin(alt_rad)
    cos_alt = math.cos(alt_rad)
    sin_lat = math.sin(lat_rad)
    cos_lat = math.cos(lat_rad)
    cos_az = math.cos(az_rad)
    sin_az = math.sin(az_rad)

    # Declination: sin(delta) = sin(phi)*sin(h) + cos(phi)*cos(h)*cos(A)
    sin_dec = sin_lat * sin_alt + cos_lat * cos_alt * cos_az
    sin_dec = max(-1.0, min(1.0, sin_dec))
    dec_rad = math.asin(sin_dec)
    dec_deg = math.degrees(dec_rad)

    # Hour Angle H:
    # y = -cos(h)*sin(A)
    # x = cos(phi)*sin(h) - sin(phi)*cos(h)*cos(A)
    y = -cos_alt * sin_az
    x = cos_lat * sin_alt - sin_lat * cos_alt * cos_az
    h_rad = math.atan2(y, x)
    h_deg = (math.degrees(h_rad) + 360.0) % 360.0

    # RA = LMST - H
    ra_deg = (lmst_deg - h_deg + 360.0) % 360.0
    return ra_deg, dec_deg
