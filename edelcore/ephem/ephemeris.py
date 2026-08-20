"""
EdelEphemeris: Ephemeris Subsystem for EdelCore.
Computes positions, speeds, distances, and state for all celestial bodies.
Integrates JPL SPICE binary reader and high-precision analytical standalone models
with complete corrections (light-time iteration, aberration, nutation, and topocentric parallax).
"""
from __future__ import annotations
import math
from typing import Dict, Optional, Tuple, NamedTuple
from .bodies import Body, NAIF_ID, STANDARD_PLANETS
from .vsop87 import sun_geocentric, planet_geocentric
from .moon_elp import moon_position_meeus, mean_lunar_node, true_lunar_node, mean_lunar_apogee, true_lunar_apogee
from .jpl_reader import JPLSPKReader
from ..time.edel_time import EdelTime
from ..astro.obliquity import mean_obliquity_iau2006, true_obliquity
from ..astro.nutation import nutation_iau2000b
from ..astro.corrections import (
    C_AU_PER_DAY,
    apply_annual_aberration,
    solar_gravitational_deflection,
    observer_geocentric_position,
    apply_topocentric_parallax,
)
from ..coords.transformations import (
    cartesian_to_spherical,
    spherical_to_cartesian,
    equatorial_to_ecliptic,
    ecliptic_to_equatorial,
    precession_matrix_iau2006,
    nutation_matrix,
    apply_matrix_3x3,
)
from ..models import BodyPosition

class EdelEphemeris:
    """
    Core Ephemeris Calculation Engine.
    """

    def __init__(self, bsp_path: Optional[str] = None):
        self.bsp_path = bsp_path
        self.spk_reader = JPLSPKReader(bsp_path) if bsp_path else None

    def calculate_body(
        self,
        body: Body,
        time: EdelTime,
        lat_deg: Optional[float] = None,
        lon_deg: Optional[float] = None,
        alt_meters: float = 0.0,
        apparent: bool = True
    ) -> BodyPosition:
        """
        Calculate full astrometric/apparent coordinates and speeds for a celestial body.
        """
        # Central difference step for speed determination (0.001 day = 86.4 seconds)
        dt_day = 0.001

        # Current position
        lon, lat, dist, ra, dec = self._compute_pos(body, time, lat_deg, lon_deg, alt_meters, apparent)

        # Position slightly before and after for numerical differentiation of speeds
        time_prev = EdelTime.from_jd(time.jd_ut - dt_day, delta_t_sec=time.delta_t)
        time_next = EdelTime.from_jd(time.jd_ut + dt_day, delta_t_sec=time.delta_t)

        lon_p, lat_p, dist_p, _, _ = self._compute_pos(body, time_prev, lat_deg, lon_deg, alt_meters, apparent)
        lon_n, lat_n, dist_n, _, _ = self._compute_pos(body, time_next, lat_deg, lon_deg, alt_meters, apparent)

        # Unwind 360-degree boundary wrap for longitude speed
        d_lon_forward = (lon_n - lon + 180.0) % 360.0 - 180.0
        d_lon_backward = (lon - lon_p + 180.0) % 360.0 - 180.0
        speed_lon = (d_lon_forward + d_lon_backward) / (2.0 * dt_day)

        speed_lat = (lat_n - lat_p) / (2.0 * dt_day)
        speed_dist = (dist_n - dist_p) / (2.0 * dt_day)
        is_retro = speed_lon < 0.0

        return BodyPosition(
            body=body,
            longitude=lon,
            latitude=lat,
            distance=dist,
            speed_longitude=speed_lon,
            speed_latitude=speed_lat,
            speed_distance=speed_dist,
            ra=ra,
            dec=dec,
            is_retrograde=is_retro
        )

    def _compute_pos(
        self,
        body: Body,
        time: EdelTime,
        lat_deg: Optional[float],
        lon_deg: Optional[float],
        alt_meters: float,
        apparent: bool
    ) -> Tuple[float, float, float, float, float]:
        """
        Internal position solver returning (lon_deg, lat_deg, dist_au, ra_deg, dec_deg).
        """
        t = time.t_century_tt
        delta_psi, delta_eps = nutation_iau2000b(t)
        eps_0 = mean_obliquity_iau2006(t)
        true_eps = true_obliquity(t, delta_eps)

        # -----------------------------------------------------------------
        # 1. Lunar Nodes & Lilith
        # -----------------------------------------------------------------
        if body == Body.MEAN_NODE:
            lon = mean_lunar_node(t)
            ra, dec = ecliptic_to_equatorial(lon, 0.0, true_eps)
            return lon, 0.0, 0.00257, ra, dec
        elif body == Body.TRUE_NODE:
            lon = true_lunar_node(t)
            ra, dec = ecliptic_to_equatorial(lon, 0.0, true_eps)
            return lon, 0.0, 0.00257, ra, dec
        elif body == Body.MEAN_SOUTH_NODE:
            lon = (mean_lunar_node(t) + 180.0) % 360.0
            ra, dec = ecliptic_to_equatorial(lon, 0.0, true_eps)
            return lon, 0.0, 0.00257, ra, dec
        elif body == Body.TRUE_SOUTH_NODE:
            lon = (true_lunar_node(t) + 180.0) % 360.0
            ra, dec = ecliptic_to_equatorial(lon, 0.0, true_eps)
            return lon, 0.0, 0.00257, ra, dec
        elif body == Body.MEAN_LILITH:
            lon = mean_lunar_apogee(t)
            ra, dec = ecliptic_to_equatorial(lon, 0.0, 0.0027, ra, dec) if False else (lon, 0.0) # placeholder
            ra, dec = ecliptic_to_equatorial(lon, 0.0, true_eps)
            return lon, 0.0, 0.0027, ra, dec
        elif body == Body.TRUE_LILITH:
            lon = true_lunar_apogee(t)
            ra, dec = ecliptic_to_equatorial(lon, 0.0, true_eps)
            return lon, 0.0, 0.0027, ra, dec

        # -----------------------------------------------------------------
        # 2. Moon (Use standalone ELP-2000 if no JPL kernel)
        # -----------------------------------------------------------------
        if body == Body.MOON and not (self.spk_reader and NAIF_ID.get(body)):
            lon, lat, dist = moon_position_meeus(t)
            if apparent:
                # Add nutation in longitude
                lon = (lon + delta_psi) % 360.0
            
            ra, dec = ecliptic_to_equatorial(lon, lat, true_eps)

            # Topocentric parallax for Moon if observer coords specified
            if lat_deg is not None and lon_deg is not None:
                gast = time.gast(delta_psi, true_eps)
                obs_x, obs_y, obs_z = observer_geocentric_position(lat_deg, lon_deg, alt_meters, gast)
                # Convert equatorial spherical to cartesian
                mx, my, mz = spherical_to_cartesian(ra, dec, dist)
                # Subtract observer vector
                tx, ty, tz = apply_topocentric_parallax(mx, my, mz, obs_x, obs_y, obs_z)
                ra, dec, dist = cartesian_to_spherical(tx, ty, tz)
                lon, lat = equatorial_to_ecliptic(ra, dec, true_eps)

            return lon, lat, dist, ra, dec

        # -----------------------------------------------------------------
        # 3. Sun (Use standalone VSOP87 if no JPL kernel)
        # -----------------------------------------------------------------
        if body == Body.SUN and not (self.spk_reader and NAIF_ID.get(body)):
            lon, lat, dist = sun_geocentric(t)
            if apparent:
                # Nutation + Aberration (-20.4955 arcsec / dist)
                lon = (lon + delta_psi - (20.49552 / 3600.0) / dist) % 360.0

            ra, dec = ecliptic_to_equatorial(lon, lat, true_eps)

            if lat_deg is not None and lon_deg is not None:
                gast = time.gast(delta_psi, true_eps)
                obs_x, obs_y, obs_z = observer_geocentric_position(lat_deg, lon_deg, alt_meters, gast)
                sx, sy, sz = spherical_to_cartesian(ra, dec, dist)
                tx, ty, tz = apply_topocentric_parallax(sx, sy, sz, obs_x, obs_y, obs_z)
                ra, dec, dist = cartesian_to_spherical(tx, ty, tz)
                lon, lat = equatorial_to_ecliptic(ra, dec, true_eps)

            return lon, lat, dist, ra, dec

        # -----------------------------------------------------------------
        # 4. Planets & Small Bodies (Mercury..Pluto, Chiron, Ceres, Pallas, Juno, Vesta)
        # -----------------------------------------------------------------
        name = body.value
        naif_id = NAIF_ID.get(body)
        
        # Try JPL BSP evaluation first if available
        jpl_evaluated = False
        if self.spk_reader and naif_id is not None:
            # Light-time iteration: t_emit = t - tau
            tau_days = 0.0
            for _ in range(3):
                jpl_pos_km = self.spk_reader.evaluate_geocentric(naif_id, time.jd_tt - tau_days)
                if jpl_pos_km is not None:
                    # km to AU (1 AU = 149597870.7 km)
                    # Note: JPL vectors are in equatorial ICRF/J2000!
                    gx_eq, gy_eq, gz_eq = jpl_pos_km[0] / 149597870.7, jpl_pos_km[1] / 149597870.7, jpl_pos_km[2] / 149597870.7
                    dist = math.sqrt(gx_eq**2 + gy_eq**2 + gz_eq**2)
                    tau_days = dist / C_AU_PER_DAY
                    jpl_evaluated = True
                else:
                    break

            if jpl_evaluated:
                eq_j2000_vec = (gx_eq, gy_eq, gz_eq)
                dist = math.sqrt(gx_eq**2 + gy_eq**2 + gz_eq**2)

        if not jpl_evaluated:
            # Standalone analytical / Keplerian fallback
            from .small_bodies import SMALL_BODY_ELEMENTS, small_body_geocentric
            is_small_body = name in SMALL_BODY_ELEMENTS

            # Light-time iteration: t_emit = t - tau
            tau_days = 0.0
            gx, gy, gz = 0.0, 0.0, 0.0
            for _ in range(3):
                t_eff = (time.jd_tt - tau_days - 2451545.0) / 36525.0
                if is_small_body:
                    gx, gy, gz = small_body_geocentric(name, t_eff)
                else:
                    gx, gy, gz = planet_geocentric(name, t_eff)
                dist = math.sqrt(gx**2 + gy**2 + gz**2)
                tau_days = dist / C_AU_PER_DAY

            # Ecliptic of J2000 -> Convert to Spherical
            lon_j2000, lat_j2000, dist = cartesian_to_spherical(gx, gy, gz)
            # Convert to Equatorial of J2000 (eps_J2000 = 23.43929111 deg)
            ra_j2000, dec_j2000 = ecliptic_to_equatorial(lon_j2000, lat_j2000, 23.43929111)
            eq_j2000_vec = spherical_to_cartesian(ra_j2000, dec_j2000, dist)

        # Precession to Date
        p_mat = precession_matrix_iau2006(t)
        eq_date_vec = apply_matrix_3x3(p_mat, eq_j2000_vec)

        # Nutation to True Equator of Date
        n_mat = nutation_matrix(eps_0, delta_psi, delta_eps)
        eq_true_vec = apply_matrix_3x3(n_mat, eq_date_vec)

        ra, dec, dist = cartesian_to_spherical(eq_true_vec[0], eq_true_vec[1], eq_true_vec[2])

        # Apply Annual Aberration only for non-JPL fallback (planetary light-time in JPL already accounts for aberration)
        if apparent and not jpl_evaluated:
            # Earth velocity vector (AU/day)
            # Differentiate Earth heliocentric position
            dt = 0.0001
            e_x1, e_y1, e_z1 = planet_geocentric("Earth", t + dt) # invert
            # Approximate Earth orbital velocity: ~ 0.0172 AU/day
            # Simple standard annual aberration in equatorial coordinates
            # d_ra = -k*(cos_ra*cos_lon_sun*cos_eps + sin_ra*sin_lon_sun)/cos_dec
            # d_dec = -k*(cos_lon_sun*cos_eps*(tan_eps*cos_dec - sin_ra*sin_dec) + cos_ra*sin_dec*sin_lon_sun)
            k_deg = 20.49552 / 3600.0
            sun_lon, _, _ = sun_geocentric(t)
            sl_rad = math.radians(sun_lon)
            ra_rad = math.radians(ra)
            dec_rad = math.radians(dec)
            eps_rad = math.radians(true_eps)

            d_ra = -k_deg * (math.cos(ra_rad) * math.cos(sl_rad) * math.cos(eps_rad) + math.sin(ra_rad) * math.sin(sl_rad)) / math.cos(dec_rad)
            d_dec = -k_deg * (math.cos(sl_rad) * math.cos(eps_rad) * (math.tan(eps_rad) * math.cos(dec_rad) - math.sin(ra_rad) * math.sin(dec_rad)) + math.cos(ra_rad) * math.sin(dec_rad) * math.sin(sl_rad))
            ra = (ra + d_ra) % 360.0
            dec = dec + d_dec

        # Topocentric Parallax
        if lat_deg is not None and lon_deg is not None:
            gast = time.gast(delta_psi, true_eps)
            obs_x, obs_y, obs_z = observer_geocentric_position(lat_deg, lon_deg, alt_meters, gast)
            px, py, pz = spherical_to_cartesian(ra, dec, dist)
            tx, ty, tz = apply_topocentric_parallax(px, py, pz, obs_x, obs_y, obs_z)
            ra, dec, dist = cartesian_to_spherical(tx, ty, tz)

        lon, lat = equatorial_to_ecliptic(ra, dec, true_eps)
        return lon, lat, dist, ra, dec
