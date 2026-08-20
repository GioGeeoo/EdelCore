"""
EdelEngine: Unified High-Precision Astrological & Ephemeris Computation Engine.
High-level facade orchestrating EdelTime, EdelEphemeris, EdelHouses, and EdelAyanamsha.
"""
from __future__ import annotations
import math
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, Tuple

from .time.edel_time import EdelTime
from .ephem.bodies import Body, STANDARD_PLANETS
from .ephem.ephemeris import EdelEphemeris
from .houses.house_engine import HouseSystem, EdelHouses
from .sidereal.ayanamsha import AyanamshaMode, EdelAyanamsha
from .astro.obliquity import mean_obliquity_iau2006, true_obliquity
from .astro.nutation import nutation_iau2000b
from .models import BodyPosition, ChartAngles, Aspect, ChartData


class EdelEngine:
    """
    Main EdelCore Engine Facade.
    Provides standard interface for astrological calculations and ephemeris querying.
    """

    def __init__(self, bsp_path: Optional[str] = None):
        import os
        if bsp_path is None:
            # Check default packaged location
            bundled = os.path.join(os.path.dirname(__file__), "data", "de440s.bsp")
            if os.path.exists(bundled):
                bsp_path = bundled
        self.ephemeris = EdelEphemeris(bsp_path=bsp_path)

    def calculate_chart(
        self,
        dt_or_time: Union[datetime, EdelTime],
        lat_deg: float,
        lon_deg: float,
        alt_meters: float = 0.0,
        house_system: Union[HouseSystem, str] = HouseSystem.PLACIDUS,
        sidereal_mode: Optional[Union[AyanamshaMode, str]] = None,
        custom_ayanamsha_j2000_deg: Optional[float] = None,
        bodies: Optional[List[Body]] = None,
        apparent: bool = True,
        topocentric: bool = False
    ) -> ChartData:
        """
        Calculate complete astrological chart.
        """
        # 1. Resolve Time
        if isinstance(dt_or_time, datetime):
            time = EdelTime.from_datetime(dt_or_time)
        else:
            time = dt_or_time

        # 2. Obliquity & Nutation
        t = time.t_century_tt
        delta_psi, delta_eps = nutation_iau2000b(t)
        eps_0 = mean_obliquity_iau2006(t)
        true_eps = true_obliquity(t, delta_eps)

        # 3. Calculate ARMC (Local Apparent Sidereal Time in degrees)
        # ARMC = GAST + Longitude
        armc = time.last(lon_deg, delta_psi, true_eps)

        # 4. House Cusps & Angles
        cusps, angles = EdelHouses.calculate_houses(house_system, armc, lat_deg, true_eps)

        # 5. Planetary Positions
        # Standard natal charts evaluate geocentric apparent positions
        # Topocentric parallax is applied when topocentric is explicitly requested
        target_bodies = bodies or STANDARD_PLANETS
        computed_bodies: Dict[Body, BodyPosition] = {}

        p_lat = lat_deg if topocentric else None
        p_lon = lon_deg if topocentric else None

        for b in target_bodies:
            pos = self.ephemeris.calculate_body(
                body=b,
                time=time,
                lat_deg=p_lat,
                lon_deg=p_lon,
                alt_meters=alt_meters if topocentric else 0.0,
                apparent=apparent
            )
            computed_bodies[b] = pos

        # 6. Apply Sidereal Ayanamsha if requested
        ayanamsha_val = None
        is_sidereal = sidereal_mode is not None
        resolved_sid_mode = None

        if is_sidereal:
            if isinstance(sidereal_mode, str):
                name_map = {m.value.lower(): m for m in AyanamshaMode}
                resolved_sid_mode = name_map.get(sidereal_mode.lower().replace("_", " ").strip(), AyanamshaMode.LAHIRI)
            else:
                resolved_sid_mode = sidereal_mode

            ayanamsha_val = EdelAyanamsha.calculate_ayanamsha(
                resolved_sid_mode, time, custom_ayanamsha_j2000_deg
            )

            # Offset planetary longitudes
            sid_bodies = {}
            for b, pos in computed_bodies.items():
                sid_lon = (pos.longitude - ayanamsha_val + 360.0) % 360.0
                sid_bodies[b] = BodyPosition(
                    body=pos.body,
                    longitude=sid_lon,
                    latitude=pos.latitude,
                    distance=pos.distance,
                    speed_longitude=pos.speed_longitude,
                    speed_latitude=pos.speed_latitude,
                    speed_distance=pos.speed_distance,
                    ra=pos.ra,
                    dec=pos.dec,
                    is_retrograde=pos.is_retrograde
                )
            computed_bodies = sid_bodies

            # Offset cusps and angles
            cusps = [(c - ayanamsha_val + 360.0) % 360.0 for c in cusps]
            angles = ChartAngles(
                armc=angles.armc,
                mc=(angles.mc - ayanamsha_val + 360.0) % 360.0,
                ic=(angles.ic - ayanamsha_val + 360.0) % 360.0,
                asc=(angles.asc - ayanamsha_val + 360.0) % 360.0,
                dsc=(angles.dsc - ayanamsha_val + 360.0) % 360.0,
                vertex=(angles.vertex - ayanamsha_val + 360.0) % 360.0,
                anti_vertex=(angles.anti_vertex - ayanamsha_val + 360.0) % 360.0,
                east_point=(angles.east_point - ayanamsha_val + 360.0) % 360.0
            )

        if isinstance(house_system, str):
            name_map = {s.value.lower(): s for s in HouseSystem}
            norm_key = house_system.lower().replace("_", " ").strip()
            resolved_house_system = name_map.get(norm_key, HouseSystem.PLACIDUS)
        else:
            resolved_house_system = house_system

        return ChartData(
            time=time,
            lat_deg=lat_deg,
            lon_deg=lon_deg,
            alt_meters=alt_meters,
            house_system=resolved_house_system,
            bodies=computed_bodies,
            cusps=cusps,
            angles=angles,
            true_obliquity_deg=true_eps,
            mean_obliquity_deg=eps_0,
            nutation_lon_deg=delta_psi,
            nutation_eps_deg=delta_eps,
            ayanamsha_deg=ayanamsha_val,
            is_sidereal=is_sidereal,
            sidereal_mode=resolved_sid_mode
        )

    def calculate_horizontal(
        self,
        body: Body,
        time: EdelTime,
        lat_deg: float,
        lon_deg: float,
        alt_meters: float = 0.0,
        pressure_mbar: float = 1013.25,
        temp_celsius: float = 10.0
    ) -> HorizontalCoords:
        """
        Calculate topocentric Azimuth, True Altitude, and Refracted Apparent Altitude
        for a celestial body.
        """
        from .coords.horizontal import equatorial_to_horizontal
        delta_psi, delta_eps = nutation_iau2000b(time.t_century_tt)
        true_eps = true_obliquity(time.t_century_tt, delta_eps)
        lmst = time.last(lon_deg, delta_psi, true_eps)

        pos = self.ephemeris.calculate_body(
            body=body,
            time=time,
            lat_deg=lat_deg,
            lon_deg=lon_deg,
            alt_meters=alt_meters
        )
        return equatorial_to_horizontal(
            ra_deg=pos.ra,
            dec_deg=pos.dec,
            lmst_deg=lmst,
            lat_deg=lat_deg,
            pressure_mbar=pressure_mbar,
            temp_celsius=temp_celsius
        )

    def search_transit(
        self,
        body: Body,
        target_lon_deg: float,
        start_time: Union[datetime, EdelTime],
        end_time: Union[datetime, EdelTime],
        tol_seconds: float = 0.5
    ) -> Optional[EdelTime]:
        """Find exact moment when body reaches target longitude."""
        from .events.search import search_transit_time
        t_start = EdelTime.from_datetime(start_time) if isinstance(start_time, datetime) else start_time
        t_end = EdelTime.from_datetime(end_time) if isinstance(end_time, datetime) else end_time
        return search_transit_time(self.ephemeris, body, target_lon_deg, t_start, t_end, tol_seconds=tol_seconds)

    def search_sign_ingresses(
        self,
        body: Body,
        start_time: Union[datetime, EdelTime],
        end_time: Union[datetime, EdelTime],
        tol_seconds: float = 0.5
    ) -> List[Tuple[EdelTime, int]]:
        """Find all zodiac sign ingresses in time range."""
        from .events.search import search_sign_ingress
        t_start = EdelTime.from_datetime(start_time) if isinstance(start_time, datetime) else start_time
        t_end = EdelTime.from_datetime(end_time) if isinstance(end_time, datetime) else end_time
        return search_sign_ingress(self.ephemeris, body, t_start, t_end, tol_seconds=tol_seconds)

    def search_stations(
        self,
        body: Body,
        start_time: Union[datetime, EdelTime],
        end_time: Union[datetime, EdelTime],
        tol_seconds: float = 5.0
    ) -> List[Tuple[EdelTime, str]]:
        """Find all stationary turning points (retrograde / direct) in time range."""
        from .events.search import search_station
        t_start = EdelTime.from_datetime(start_time) if isinstance(start_time, datetime) else start_time
        t_end = EdelTime.from_datetime(end_time) if isinstance(end_time, datetime) else end_time
        return search_station(self.ephemeris, body, t_start, t_end, tol_seconds=tol_seconds)

    def calculate_star(
        self,
        star_name: str,
        dt_or_time: Union[datetime, EdelTime],
        lat_deg: Optional[float] = None,
        lon_deg: Optional[float] = None,
        alt_meters: float = 0.0,
        apparent: bool = True
    ):
        """
        Calculate high-precision coordinates for a named fixed star.
        Returns StarPosition (longitude, latitude, ra, dec, azimuth, altitude, apparent_altitude).
        """
        from .ephem.stars import calculate_star_position
        time = EdelTime.from_datetime(dt_or_time) if isinstance(dt_or_time, datetime) else dt_or_time
        return calculate_star_position(
            star_name=star_name,
            time=time,
            lat_deg=lat_deg,
            lon_deg=lon_deg,
            alt_meters=alt_meters,
            apparent=apparent
        )

    def list_stars(self) -> List[str]:
        """List all available named fixed stars in catalog."""
        from .ephem.stars import list_star_names
        return list_star_names()
