"""
Fixed Stars Catalog & Ephemeris Subsystem.
Implements high-precision positioning for prominent fixed stars based on Hipparcos and SIMBAD astrometric datasets.
Includes proper motion (mas/yr), IAU 2006 precession to date, nutation,
equatorial-to-ecliptic transformations, and horizontal Azimuth/Altitude calculations.
"""
from __future__ import annotations
import math
from typing import Dict, List, Optional, Tuple, NamedTuple
from ..time.edel_time import EdelTime
from ..astro.obliquity import mean_obliquity_iau2006, true_obliquity
from ..astro.nutation import nutation_iau2000b
from ..coords.transformations import (
    spherical_to_cartesian,
    cartesian_to_spherical,
    equatorial_to_ecliptic,
    precession_matrix_iau2006,
    nutation_matrix,
    apply_matrix_3x3,
)
from ..coords.horizontal import equatorial_to_horizontal, HorizontalCoords

class StarData(NamedTuple):
    name: str              # Standard identifier (e.g. "Sirius")
    traditional_name: str  # Traditional / Bayer (e.g. "Alpha Canis Majoris")
    constellation: str     # Constellation (e.g. "Canis Major")
    ra_j2000_deg: float    # Right Ascension J2000 in degrees [0, 360)
    dec_j2000_deg: float   # Declination J2000 in degrees [-90, +90]
    pm_ra_mas_yr: float    # Proper motion mu_alpha * cos(delta) in mas/yr
    pm_dec_mas_yr: float   # Proper motion mu_delta in mas/yr
    vmag: float            # Visual magnitude

class StarPosition:
    def __init__(
        self,
        name: str,
        traditional_name: str,
        constellation: str,
        vmag: float,
        longitude: float,
        latitude: float,
        ra: float,
        dec: float,
        azimuth: Optional[float] = None,
        altitude: Optional[float] = None,
        apparent_altitude: Optional[float] = None
    ):
        self.name = name
        self.traditional_name = traditional_name
        self.constellation = constellation
        self.vmag = float(vmag)
        self.longitude = float(longitude)
        self.latitude = float(latitude)
        self.ra = float(ra)
        self.dec = float(dec)
        self.azimuth = float(azimuth) if azimuth is not None else None
        self.altitude = float(altitude) if altitude is not None else None
        self.apparent_altitude = float(apparent_altitude) if apparent_altitude is not None else None

    @property
    def sign(self) -> str:
        from ..models import ZODIAC_SIGNS
        return ZODIAC_SIGNS[int((self.longitude % 360.0) // 30)]

    @property
    def sign_degree(self) -> float:
        return self.longitude % 30.0

    @property
    def formatted(self) -> str:
        from ..models import format_zodiac_deg
        return format_zodiac_deg(self.longitude)[2]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "traditional_name": self.traditional_name,
            "constellation": self.constellation,
            "vmag": self.vmag,
            "longitude": round(self.longitude, 6),
            "latitude": round(self.latitude, 6),
            "sign": self.sign,
            "sign_degree": round(self.sign_degree, 6),
            "formatted": self.formatted,
            "ra_deg": round(self.ra, 6),
            "dec_deg": round(self.dec, 6),
            "azimuth_deg": round(self.azimuth, 4) if self.azimuth is not None else None,
            "altitude_deg": round(self.altitude, 4) if self.altitude is not None else None,
            "apparent_altitude_deg": round(self.apparent_altitude, 4) if self.apparent_altitude is not None else None,
        }

    def __repr__(self) -> str:
        return f"<Star {self.name} ({self.traditional_name}) {self.formatted} Vmag: {self.vmag}>"

# Standard catalog of major astronomical and astrological fixed stars
# Coordinates from Hipparcos / SIMBAD catalog datasets (J2000.0)
STAR_CATALOG: Dict[str, StarData] = {
    "sirius": StarData(
        name="Sirius",
        traditional_name="Alpha Canis Majoris",
        constellation="Canis Major",
        ra_j2000_deg=101.287155,
        dec_j2000_deg=-16.716116,
        pm_ra_mas_yr=-546.01,
        pm_dec_mas_yr=-1223.07,
        vmag=-1.46
    ),
    "canopus": StarData(
        name="Canopus",
        traditional_name="Alpha Carinae",
        constellation="Carina",
        ra_j2000_deg=95.987958,
        dec_j2000_deg=-52.695661,
        pm_ra_mas_yr=19.93,
        pm_dec_mas_yr=23.24,
        vmag=-0.74
    ),
    "arcturus": StarData(
        name="Arcturus",
        traditional_name="Alpha Bootis",
        constellation="Bootes",
        ra_j2000_deg=213.915300,
        dec_j2000_deg=19.182410,
        pm_ra_mas_yr=-1093.45,
        pm_dec_mas_yr=-1999.40,
        vmag=-0.05
    ),
    "vega": StarData(
        name="Vega",
        traditional_name="Alpha Lyrae",
        constellation="Lyra",
        ra_j2000_deg=279.234735,
        dec_j2000_deg=38.783689,
        pm_ra_mas_yr=200.94,
        pm_dec_mas_yr=286.23,
        vmag=0.03
    ),
    "capella": StarData(
        name="Capella",
        traditional_name="Alpha Aurigae",
        constellation="Auriga",
        ra_j2000_deg=79.172328,
        dec_j2000_deg=45.997991,
        pm_ra_mas_yr=75.52,
        pm_dec_mas_yr=-427.13,
        vmag=0.08
    ),
    "rigel": StarData(
        name="Rigel",
        traditional_name="Beta Orionis",
        constellation="Orion",
        ra_j2000_deg=78.634467,
        dec_j2000_deg=-8.201638,
        pm_ra_mas_yr=1.31,
        pm_dec_mas_yr=-0.50,
        vmag=0.18
    ),
    "procyon": StarData(
        name="Procyon",
        traditional_name="Alpha Canis Minoris",
        constellation="Canis Minor",
        ra_j2000_deg=114.825494,
        dec_j2000_deg=5.224993,
        pm_ra_mas_yr=-716.57,
        pm_dec_mas_yr=-1034.57,
        vmag=0.34
    ),
    "betelgeuse": StarData(
        name="Betelgeuse",
        traditional_name="Alpha Orionis",
        constellation="Orion",
        ra_j2000_deg=88.792939,
        dec_j2000_deg=7.407064,
        pm_ra_mas_yr=27.33,
        pm_dec_mas_yr=10.86,
        vmag=0.42
    ),
    "achernar": StarData(
        name="Achernar",
        traditional_name="Alpha Eridani",
        constellation="Eridanus",
        ra_j2000_deg=24.428526,
        dec_j2000_deg=-57.236758,
        pm_ra_mas_yr=88.02,
        pm_dec_mas_yr=-40.08,
        vmag=0.45
    ),
    "hadar": StarData(
        name="Hadar",
        traditional_name="Beta Centauri",
        constellation="Centaurus",
        ra_j2000_deg=210.955896,
        dec_j2000_deg=-60.373065,
        pm_ra_mas_yr=-33.27,
        pm_dec_mas_yr=-25.02,
        vmag=0.61
    ),
    "altair": StarData(
        name="Altair",
        traditional_name="Alpha Aquilae",
        constellation="Aquila",
        ra_j2000_deg=297.695827,
        dec_j2000_deg=8.868321,
        pm_ra_mas_yr=536.23,
        pm_dec_mas_yr=385.29,
        vmag=0.77
    ),
    "aldebaran": StarData(
        name="Aldebaran",
        traditional_name="Alpha Tauri (Watcher of the East)",
        constellation="Taurus",
        ra_j2000_deg=68.980163,
        dec_j2000_deg=16.509302,
        pm_ra_mas_yr=63.45,
        pm_dec_mas_yr=-189.36,
        vmag=0.85
    ),
    "antares": StarData(
        name="Antares",
        traditional_name="Alpha Scorpii (Watcher of the West)",
        constellation="Scorpius",
        ra_j2000_deg=247.351915,
        dec_j2000_deg=-26.432002,
        pm_ra_mas_yr=-10.16,
        pm_dec_mas_yr=-23.21,
        vmag=0.96
    ),
    "spica": StarData(
        name="Spica",
        traditional_name="Alpha Virginis",
        constellation="Virgo",
        ra_j2000_deg=201.298247,
        dec_j2000_deg=-11.161322,
        pm_ra_mas_yr=-42.50,
        pm_dec_mas_yr=-31.73,
        vmag=0.98
    ),
    "pollux": StarData(
        name="Pollux",
        traditional_name="Beta Geminorum",
        constellation="Gemini",
        ra_j2000_deg=116.328958,
        dec_j2000_deg=28.026199,
        pm_ra_mas_yr=-625.69,
        pm_dec_mas_yr=-45.94,
        vmag=1.14
    ),
    "fomalhaut": StarData(
        name="Fomalhaut",
        traditional_name="Alpha Piscis Austrini (Watcher of the South)",
        constellation="Piscis Austrinus",
        ra_j2000_deg=344.412693,
        dec_j2000_deg=-29.622237,
        pm_ra_mas_yr=329.22,
        pm_dec_mas_yr=-164.22,
        vmag=1.16
    ),
    "deneb": StarData(
        name="Deneb",
        traditional_name="Alpha Cygni",
        constellation="Cygnus",
        ra_j2000_deg=310.357980,
        dec_j2000_deg=45.280339,
        pm_ra_mas_yr=1.56,
        pm_dec_mas_yr=1.55,
        vmag=1.25
    ),
    "regulus": StarData(
        name="Regulus",
        traditional_name="Alpha Leonis (Watcher of the North)",
        constellation="Leo",
        ra_j2000_deg=152.092962,
        dec_j2000_deg=11.967209,
        pm_ra_mas_yr=-249.40,
        pm_dec_mas_yr=4.91,
        vmag=1.35
    ),
    "castor": StarData(
        name="Castor",
        traditional_name="Alpha Geminorum",
        constellation="Gemini",
        ra_j2000_deg=113.649430,
        dec_j2000_deg=31.888276,
        pm_ra_mas_yr=-206.31,
        pm_dec_mas_yr=-148.18,
        vmag=1.58
    ),
    "bellatrix": StarData(
        name="Bellatrix",
        traditional_name="Gamma Orionis",
        constellation="Orion",
        ra_j2000_deg=81.282764,
        dec_j2000_deg=6.349703,
        pm_ra_mas_yr=-8.75,
        pm_dec_mas_yr=-13.28,
        vmag=1.64
    ),
    "polaris": StarData(
        name="Polaris",
        traditional_name="Alpha Ursae Minoris (North Star)",
        constellation="Ursa Minor",
        ra_j2000_deg=37.954561,
        dec_j2000_deg=89.264109,
        pm_ra_mas_yr=44.22,
        pm_dec_mas_yr=-11.74,
        vmag=1.98
    ),
    "algol": StarData(
        name="Algol",
        traditional_name="Beta Persei (The Demon Star / Caput Medusae)",
        constellation="Perseus",
        ra_j2000_deg=47.042217,
        dec_j2000_deg=40.955647,
        pm_ra_mas_yr=2.47,
        pm_dec_mas_yr=-1.41,
        vmag=2.12
    ),
    "alcyone": StarData(
        name="Alcyone",
        traditional_name="Eta Tauri (Pleiades Central Star)",
        constellation="Taurus",
        ra_j2000_deg=56.871152,
        dec_j2000_deg=24.105139,
        pm_ra_mas_yr=19.34,
        pm_dec_mas_yr=-43.67,
        vmag=2.87
    )
}

def list_star_names() -> List[str]:
    """Return list of standard names for all available fixed stars."""
    return [s.name for s in STAR_CATALOG.values()]

def calculate_star_position(
    star_name: str,
    time: EdelTime,
    lat_deg: Optional[float] = None,
    lon_deg: Optional[float] = None,
    alt_meters: float = 0.0,
    apparent: bool = True
) -> StarPosition:
    """
    Compute high-precision coordinates for a named fixed star.
    Applies proper motion, IAU 2006 precession to date, nutation, and ecliptic conversion.
    If lat_deg and lon_deg are provided, computes horizontal coordinates (Azimuth, Altitude).
    """
    key = star_name.lower().strip()
    if key not in STAR_CATALOG:
        # Search by matching substring
        matched = None
        for k, data in STAR_CATALOG.items():
            if key in k or key in data.traditional_name.lower():
                matched = data
                break
        if not matched:
            raise KeyError(f"Star '{star_name}' not found in catalog. Available stars: {list_star_names()}")
        star = matched
    else:
        star = STAR_CATALOG[key]

    t = time.t_century_tt
    years_since_j2000 = (time.jd_tt - 2451545.0) / 365.25

    # 1. Apply Proper Motion (mas -> deg: 1 mas = 1 / 3,600,000 deg)
    dec_rad_j2000 = math.radians(star.dec_j2000_deg)
    cos_dec_j2000 = math.cos(dec_rad_j2000)
    cos_dec_j2000 = max(1e-6, cos_dec_j2000) # prevent div by 0 near poles

    d_ra_deg = (star.pm_ra_mas_yr * years_since_j2000) / (3600000.0 * cos_dec_j2000)
    d_dec_deg = (star.pm_dec_mas_yr * years_since_j2000) / 3600000.0

    ra_pm = (star.ra_j2000_deg + d_ra_deg) % 360.0
    dec_pm = max(-90.0, min(90.0, star.dec_j2000_deg + d_dec_deg))

    # Convert to unit vector in J2000 Equatorial
    x0, y0, z0 = spherical_to_cartesian(ra_pm, dec_pm, 1.0)
    r_j2000 = (x0, y0, z0)

    # 2. Precession to Date (IAU 2006)
    p_mat = precession_matrix_iau2006(t)
    r_date = apply_matrix_3x3(p_mat, r_j2000)

    # 3. Nutation to True Equator of Date (IAU 2000B)
    delta_psi, delta_eps = nutation_iau2000b(t)
    eps_0 = mean_obliquity_iau2006(t)
    true_eps = true_obliquity(t, delta_eps)

    if apparent:
        n_mat = nutation_matrix(eps_0, delta_psi, delta_eps)
        r_true = apply_matrix_3x3(n_mat, r_date)
    else:
        r_true = r_date

    # 4. Spherical coordinates in True Equator of Date
    ra_date, dec_date, _ = cartesian_to_spherical(r_true[0], r_true[1], r_true[2])

    # 5. Convert to Ecliptic Longitude and Latitude
    lon_date, lat_date = equatorial_to_ecliptic(ra_date, dec_date, true_eps)

    # 6. Horizontal coordinates (Az/Alt) if observer coordinates given
    azimuth = None
    altitude = None
    app_altitude = None

    if lat_deg is not None and lon_deg is not None:
        lmst = time.last(lon_deg, delta_psi, true_eps)
        hz = equatorial_to_horizontal(
            ra_deg=ra_date,
            dec_deg=dec_date,
            lmst_deg=lmst,
            lat_deg=lat_deg
        )
        azimuth = hz.azimuth
        altitude = hz.true_altitude
        app_altitude = hz.apparent_altitude

    return StarPosition(
        name=star.name,
        traditional_name=star.traditional_name,
        constellation=star.constellation,
        vmag=star.vmag,
        longitude=lon_date,
        latitude=lat_date,
        ra=ra_date,
        dec=dec_date,
        azimuth=azimuth,
        altitude=altitude,
        apparent_altitude=app_altitude
    )
