"""
EdelCore: High-precision, pure-Python ephemeris and astrological computation engine.
Built on IAU 2000/2006 and NASA JPL standards, delivering sub-arcsecond accuracy with zero C dependencies.
"""
from .engine import EdelEngine, ChartData, Aspect
from .time.edel_time import EdelTime
from .time.delta_t_tables import calculate_delta_t
from .ephem.bodies import Body, STANDARD_PLANETS, STANDARD_ASTEROIDS, NAIF_ID
from .ephem.ephemeris import EdelEphemeris, BodyPosition
from .ephem.jpl_reader import JPLSPKReader
from .ephem.small_bodies import small_body_heliocentric, small_body_geocentric
from .houses.house_engine import HouseSystem, EdelHouses
from .houses.angles import ChartAngles
from .sidereal.ayanamsha import AyanamshaMode, EdelAyanamsha
from .astro.obliquity import mean_obliquity_iau2006, true_obliquity
from .astro.nutation import nutation_iau2000b
from .coords.horizontal import (
    HorizontalCoords,
    equatorial_to_horizontal,
    horizontal_to_equatorial,
    apply_refraction,
    remove_refraction,
)
from .events.search import (
    search_transit_time,
    search_sign_ingress,
    search_station,
)
from .ephem.stars import (
    StarData,
    StarPosition,
    STAR_CATALOG,
    list_star_names,
    calculate_star_position,
)

from .models import (
    format_dms,
    format_zodiac_deg,
    ZODIAC_SIGNS,
    BodyPosition,
    ChartAngles,
    Aspect,
    ChartData,
)

__version__ = "0.3.0"
__author__ = "Giorgi Khunzakhishvili"
__license__ = "MIT"

__all__ = [
    "EdelEngine",
    "ChartData",
    "Aspect",
    "EdelTime",
    "calculate_delta_t",
    "Body",
    "STANDARD_PLANETS",
    "STANDARD_ASTEROIDS",
    "NAIF_ID",
    "EdelEphemeris",
    "BodyPosition",
    "JPLSPKReader",
    "small_body_heliocentric",
    "small_body_geocentric",
    "HouseSystem",
    "EdelHouses",
    "ChartAngles",
    "AyanamshaMode",
    "EdelAyanamsha",
    "mean_obliquity_iau2006",
    "true_obliquity",
    "nutation_iau2000b",
    "HorizontalCoords",
    "equatorial_to_horizontal",
    "horizontal_to_equatorial",
    "apply_refraction",
    "remove_refraction",
    "search_transit_time",
    "search_sign_ingress",
    "search_station",
    "StarData",
    "StarPosition",
    "STAR_CATALOG",
    "list_star_names",
    "calculate_star_position",
    "format_dms",
    "format_zodiac_deg",
    "ZODIAC_SIGNS",
]
