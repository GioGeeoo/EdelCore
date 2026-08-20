"""
Data Models, Formats, and Serialization for EdelCore.
Provides rich string formatting, sign properties,
and comprehensive dictionary/JSON serialization.
"""
from __future__ import annotations
import math
import json
from typing import Dict, List, Optional, Tuple, Any, Union, TYPE_CHECKING
from .ephem.bodies import Body

if TYPE_CHECKING:
    from .houses.house_engine import HouseSystem
    from .sidereal.ayanamsha import AyanamshaMode
    from .time.edel_time import EdelTime

ZODIAC_SIGNS = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
)

def format_dms(deg_val: float, include_sign: bool = False) -> str:
    """
    Format a decimal degree value as DD°MM'SS".
    Example: 22.7903 -> 22°47'25"
    """
    sign_str = ""
    val = deg_val
    if include_sign:
        sign_str = "+" if val >= 0 else "-"
        val = abs(val)

    d = int(val)
    rem = (val - d) * 60.0
    m = int(rem)
    s = int(round((rem - m) * 60.0))

    if s >= 60:
        s = 0
        m += 1
    if m >= 60:
        m = 0
        d += 1

    return f"{sign_str}{d:02d}°{m:02d}'{s:02d}\""

def format_zodiac_deg(deg: float) -> Tuple[str, float, str]:
    """
    Convert absolute ecliptic longitude [0, 360) into zodiac sign, relative sign degree,
    and formatted string representation.
    Example: 352.7903 -> ("Pisces", 22.7903, "22°47'25\" Pisces")
    """
    norm_deg = deg % 360.0
    sign_idx = int(norm_deg // 30)
    sign_name = ZODIAC_SIGNS[sign_idx]
    sign_deg = norm_deg % 30.0
    dms_str = format_dms(sign_deg)
    formatted_str = f"{dms_str} {sign_name}"
    return sign_name, sign_deg, formatted_str


class BodyPosition:
    """
    Calculated celestial body position and kinematic state.
    """

    def __init__(
        self,
        body: Body,
        longitude: float,
        latitude: float,
        distance: float,
        speed_longitude: float,
        speed_latitude: float,
        speed_distance: float,
        ra: float,
        dec: float,
        is_retrograde: bool
    ):
        self.body = body
        self.longitude = float(longitude)
        self.latitude = float(latitude)
        self.distance = float(distance)
        self.speed_longitude = float(speed_longitude)
        self.speed_latitude = float(speed_latitude)
        self.speed_distance = float(speed_distance)
        self.ra = float(ra)
        self.dec = float(dec)
        self.is_retrograde = bool(is_retrograde)

    @property
    def sign(self) -> str:
        """Name of the zodiac sign (e.g. 'Aries', 'Pisces')."""
        return ZODIAC_SIGNS[int((self.longitude % 360.0) // 30)]

    @property
    def sign_degree(self) -> float:
        """Degree within the current zodiac sign [0, 30)."""
        return self.longitude % 30.0

    @property
    def formatted(self) -> str:
        """Human-readable formatted sign degree (e.g. '22°47'25\" Pisces')."""
        _, _, fmt = format_zodiac_deg(self.longitude)
        return fmt

    def to_dict(self) -> Dict[str, Any]:
        """Convert body position to a serializable dictionary."""
        return {
            "name": self.body.value,
            "longitude": round(self.longitude, 6),
            "latitude": round(self.latitude, 6),
            "distance_au": round(self.distance, 8),
            "speed_lon_deg_day": round(self.speed_longitude, 6),
            "speed_lat_deg_day": round(self.speed_latitude, 6),
            "speed_dist_au_day": round(self.speed_distance, 8),
            "ra_deg": round(self.ra, 6),
            "dec_deg": round(self.dec, 6),
            "is_retrograde": self.is_retrograde,
            "sign": self.sign,
            "sign_degree": round(self.sign_degree, 6),
            "formatted": self.formatted,
        }

    def __repr__(self) -> str:
        motion = "Retrograde" if self.is_retrograde else "Direct"
        spd_fmt = format_dms(self.speed_longitude, include_sign=True) + "/day"
        return f"<{self.body.value} ({motion}) {spd_fmt} {self.formatted}>"


class ChartAngles:
    """
    Calculated chart angles and axes.
    """

    def __init__(
        self,
        armc: float,
        mc: float,
        ic: float,
        asc: float,
        dsc: float,
        vertex: float,
        anti_vertex: float,
        east_point: float
    ):
        self.armc = float(armc)
        self.mc = float(mc)
        self.ic = float(ic)
        self.asc = float(asc)
        self.dsc = float(dsc)
        self.vertex = float(vertex)
        self.anti_vertex = float(anti_vertex)
        self.east_point = float(east_point)

    @property
    def asc_formatted(self) -> str:
        return format_zodiac_deg(self.asc)[2]

    @property
    def mc_formatted(self) -> str:
        return format_zodiac_deg(self.mc)[2]

    @property
    def vertex_formatted(self) -> str:
        return format_zodiac_deg(self.vertex)[2]

    @property
    def ic_formatted(self) -> str:
        return format_zodiac_deg(self.ic)[2]

    @property
    def dsc_formatted(self) -> str:
        return format_zodiac_deg(self.dsc)[2]

    @property
    def east_point_formatted(self) -> str:
        return format_zodiac_deg(self.east_point)[2]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "armc": round(self.armc, 6),
            "asc": round(self.asc, 6),
            "asc_formatted": self.asc_formatted,
            "mc": round(self.mc, 6),
            "mc_formatted": self.mc_formatted,
            "ic": round(self.ic, 6),
            "ic_formatted": self.ic_formatted,
            "dsc": round(self.dsc, 6),
            "dsc_formatted": self.dsc_formatted,
            "vertex": round(self.vertex, 6),
            "vertex_formatted": self.vertex_formatted,
            "anti_vertex": round(self.anti_vertex, 6),
            "east_point": round(self.east_point, 6),
            "east_point_formatted": self.east_point_formatted,
        }

    def __repr__(self) -> str:
        return f"<Angles ASC: {self.asc_formatted}, MC: {self.mc_formatted}, Vertex: {self.vertex_formatted}>"


class Aspect:
    """Calculated aspect between two celestial bodies."""

    def __init__(
        self,
        body1: Body,
        body2: Body,
        aspect_type: str,
        angle: float,
        orb: float,
        is_applying: bool
    ):
        self.body1 = body1
        self.body2 = body2
        self.aspect_type = aspect_type
        self.angle = float(angle)
        self.orb = float(orb)
        self.is_applying = bool(is_applying)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "body1": self.body1.value,
            "body2": self.body2.value,
            "aspect": self.aspect_type,
            "angle": self.angle,
            "orb_deg": round(self.orb, 4),
            "is_applying": self.is_applying,
            "formatted": f"{self.body1.value} {self.aspect_type} {self.body2.value} ({self.orb:.2f}° {'Applying' if self.is_applying else 'Separating'})"
        }

    def __repr__(self) -> str:
        direction = "Applying" if self.is_applying else "Separating"
        return f"<Aspect {self.body1.value} {self.aspect_type} {self.body2.value} ({self.orb:.2f}° {direction})>"


class ChartData:
    """
    Complete calculated astrological chart container.
    """

    def __init__(
        self,
        time: EdelTime,
        lat_deg: float,
        lon_deg: float,
        alt_meters: float,
        house_system: HouseSystem,
        bodies: Dict[Body, BodyPosition],
        cusps: List[float],
        angles: ChartAngles,
        true_obliquity_deg: float,
        mean_obliquity_deg: float,
        nutation_lon_deg: float,
        nutation_eps_deg: float,
        ayanamsha_deg: Optional[float] = None,
        is_sidereal: bool = False,
        sidereal_mode: Optional[AyanamshaMode] = None
    ):
        self.time = time
        self.lat_deg = lat_deg
        self.lon_deg = lon_deg
        self.alt_meters = alt_meters
        self.house_system = house_system
        self.bodies = bodies
        self.cusps = cusps
        self.angles = angles
        self.true_obliquity = true_obliquity_deg
        self.mean_obliquity = mean_obliquity_deg
        self.nutation_lon = nutation_lon_deg
        self.nutation_eps = nutation_eps_deg
        self.ayanamsha = ayanamsha_deg
        self.is_sidereal = is_sidereal
        self.sidereal_mode = sidereal_mode

    def get(self, body: Body | str) -> BodyPosition:
        """Access body position by enum or string name."""
        if isinstance(body, str):
            for b in self.bodies.keys():
                if b.value.lower() == body.lower().strip() or b.name.lower() == body.lower().strip():
                    return self.bodies[b]
            raise KeyError(f"Body '{body}' not found in chart.")
        return self.bodies[body]

    def get_house_of_body(self, body: Body | str) -> int:
        """Determine which house (1 to 12) a body falls into."""
        pos = self.get(body)
        lon = pos.longitude
        for i in range(12):
            c_curr = self.cusps[i]
            c_next = self.cusps[(i + 1) % 12]
            if c_curr < c_next:
                if c_curr <= lon < c_next:
                    return i + 1
            else:  # crossing 0 deg Aries
                if lon >= c_curr or lon < c_next:
                    return i + 1
        return 1

    def calculate_aspects(self, max_orb: float = 8.0) -> List[Aspect]:
        """Compute all major Ptolemaic aspects between bodies in the chart."""
        ASPECT_TYPES = [
            ("Conjunction", 0.0, max_orb),
            ("Sextile", 60.0, max_orb * 0.75),
            ("Square", 90.0, max_orb * 0.85),
            ("Trine", 120.0, max_orb * 0.85),
            ("Opposition", 180.0, max_orb),
        ]
        body_list = list(self.bodies.keys())
        aspects = []

        for i in range(len(body_list)):
            for j in range(i + 1, len(body_list)):
                b1 = body_list[i]
                b2 = body_list[j]
                pos1 = self.bodies[b1]
                pos2 = self.bodies[b2]

                diff = abs(pos1.longitude - pos2.longitude)
                if diff > 180.0:
                    diff = 360.0 - diff

                for asp_name, target_angle, orb_limit in ASPECT_TYPES:
                    orb = abs(diff - target_angle)
                    if orb <= orb_limit:
                        # Determine applying vs separating
                        rel_speed = pos1.speed_longitude - pos2.speed_longitude
                        raw_diff = (pos2.longitude - pos1.longitude + 360.0) % 360.0
                        if raw_diff > 180.0:
                            rel_speed = -rel_speed
                        is_applying = (rel_speed > 0 and raw_diff < target_angle) or (rel_speed < 0 and raw_diff > target_angle)

                        aspects.append(
                            Aspect(
                                body1=b1,
                                body2=b2,
                                aspect_type=asp_name,
                                angle=target_angle,
                                orb=orb,
                                is_applying=is_applying
                            )
                        )
        return aspects

    def to_dict(self) -> Dict[str, Any]:
        """Serialize complete chart into a clean nested dictionary."""
        y, m, d, h, mn, s = self.time.calendar
        return {
            "time": {
                "iso": f"{y:04d}-{m:02d}-{d:02d}T{h:02d}:{mn:02d}:{s:06.3f}Z",
                "jd_ut1": round(self.time.jd_ut, 8),
                "jd_tt": round(self.time.jd_tt, 8),
                "delta_t_sec": round(self.time.delta_t, 3),
            },
            "location": {
                "latitude_deg": self.lat_deg,
                "longitude_deg": self.lon_deg,
                "altitude_meters": self.alt_meters,
            },
            "house_system": self.house_system.value,
            "is_sidereal": self.is_sidereal,
            "sidereal_mode": self.sidereal_mode.value if self.sidereal_mode else None,
            "ayanamsha_deg": round(self.ayanamsha, 6) if self.ayanamsha is not None else None,
            "obliquity": {
                "true_obliquity_deg": round(self.true_obliquity, 6),
                "mean_obliquity_deg": round(self.mean_obliquity, 6),
                "nutation_lon_deg": round(self.nutation_lon, 6),
                "nutation_eps_deg": round(self.nutation_eps, 6),
            },
            "angles": self.angles.to_dict(),
            "houses": [
                {
                    "house": i + 1,
                    "cusp_deg": round(self.cusps[i], 6),
                    "formatted": format_zodiac_deg(self.cusps[i])[2],
                }
                for i in range(12)
            ],
            "bodies": {
                b.value: {
                    **pos.to_dict(),
                    "house": self.get_house_of_body(b),
                }
                for b, pos in self.bodies.items()
            },
            "aspects": [asp.to_dict() for asp in self.calculate_aspects()],
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize chart into formatted JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def summary(self) -> str:
        """Format chart into a summary table."""
        lines = []
        mode_str = f"Sidereal ({self.sidereal_mode.value})" if self.is_sidereal and self.sidereal_mode else "Tropical"
        lines.append(f"================== EDELCORE CHART SUMMARY ({mode_str}) ==================")
        lines.append(f"Time: {self.time} | Lat: {self.lat_deg:.4f} | Lon: {self.lon_deg:.4f} | House: {self.house_system.value}")
        lines.append(f"ARMC: {self.angles.armc:.4f} deg | True Obliquity: {self.true_obliquity:.4f} deg")
        lines.append("-" * 75)
        lines.append(f"{'Body':<16} {'Longitude':<18} {'Speed (deg/d)':<14} {'House':<6} {'State'}")
        lines.append("-" * 75)

        for b, pos in self.bodies.items():
            h_num = self.get_house_of_body(b)
            state = "R" if pos.is_retrograde else "D"
            lines.append(f"{b.value:<16} {pos.formatted:<18} {pos.speed_longitude:>+11.4f}   {h_num:<6} {state}")

        lines.append("-" * 75)
        lines.append("ANGLES & HOUSE CUSPS:")
        lines.append(f"  ASC: {self.angles.asc_formatted}   |  MC: {self.angles.mc_formatted}   |  Vertex: {self.angles.vertex_formatted}")
        for i in range(12):
            lines.append(f"  House {i+1:>2}: {format_zodiac_deg(self.cusps[i])[2]}")
        lines.append("===========================================================================")
        return "\n".join(lines)
