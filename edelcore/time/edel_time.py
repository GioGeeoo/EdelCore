"""
EdelTime: Time Subsystem for Astronomical and Astrological Calculations.
Supports Gregorian and Julian calendars, Julian Day (UT and TT),
Delta T corrections, GMST, GAST, and LMST.
"""
from __future__ import annotations
import math
from datetime import datetime, timezone
from typing import Tuple, Union
from .delta_t_tables import calculate_delta_t

class EdelTime:
    """
    High-precision astronomical time representation.
    Handles JD(UT), JD(TT), Delta T, GMST, GAST, LMST, LAST.
    """

    def __init__(self, jd_ut: float, delta_t_sec: float | None = None):
        self._jd_ut = float(jd_ut)
        if delta_t_sec is not None:
            self._delta_t = float(delta_t_sec)
        else:
            # Estimate year for Delta-T
            y, m, d, _, _, _ = self.jd_to_calendar(self._jd_ut)
            self._delta_t = calculate_delta_t(y, m)
        
        self._jd_tt = self._jd_ut + (self._delta_t / 86400.0)

    @classmethod
    def from_datetime(
        cls,
        dt: datetime,
        delta_t_sec: float | None = None
    ) -> EdelTime:
        """Create EdelTime from Python datetime (assumed UTC if naive)."""
        year = dt.year
        month = dt.month
        day = dt.day
        hour = dt.hour
        minute = dt.minute
        second = dt.second + dt.microsecond / 1_000_000.0
        jd_ut = cls.calendar_to_jd(year, month, day, hour, minute, second)
        return cls(jd_ut, delta_t_sec=delta_t_sec)

    @classmethod
    def from_ymd_hms(
        cls,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: float = 0.0,
        delta_t_sec: float | None = None
    ) -> EdelTime:
        """Create EdelTime from year, month, day, hour, minute, second."""
        jd_ut = cls.calendar_to_jd(year, month, day, hour, minute, second)
        return cls(jd_ut, delta_t_sec=delta_t_sec)

    @classmethod
    def from_jd(cls, jd_ut: float, delta_t_sec: float | None = None) -> EdelTime:
        """Create EdelTime directly from Julian Day (Universal Time)."""
        return cls(jd_ut, delta_t_sec=delta_t_sec)

    @classmethod
    def from_jd_tt(cls, jd_tt: float, delta_t_sec: float | None = None) -> EdelTime:
        """Create EdelTime from Julian Day in Terrestrial Time."""
        if delta_t_sec is None:
            # approximate year
            y, m, _, _, _, _ = cls.jd_to_calendar(jd_tt)
            delta_t_sec = calculate_delta_t(y, m)
        jd_ut = jd_tt - (delta_t_sec / 86400.0)
        return cls(jd_ut, delta_t_sec=delta_t_sec)

    @property
    def jd_ut(self) -> float:
        """Julian Day in Universal Time (UT1 / UTC)."""
        return self._jd_ut

    @property
    def jd_tt(self) -> float:
        """Julian Day in Terrestrial Time (TT / TDT)."""
        return self._jd_tt

    @property
    def delta_t(self) -> float:
        """Delta T = TT - UT1 in seconds."""
        return self._delta_t

    @property
    def t_century_tt(self) -> float:
        """Julian centuries of TT since J2000.0 (JD 2451545.0)."""
        return (self._jd_tt - 2451545.0) / 36525.0

    @property
    def t_century_ut(self) -> float:
        """Julian centuries of UT since J2000.0 (JD 2451545.0)."""
        return (self._jd_ut - 2451545.0) / 36525.0

    @property
    def calendar(self) -> Tuple[int, int, int, int, int, float]:
        """Returns (year, month, day, hour, minute, second) in UT."""
        return self.jd_to_calendar(self._jd_ut)

    # -------------------------------------------------------------------------
    # Calendar <-> Julian Day Algorithms (Meeus Astronomical Algorithms Ch. 7)
    # -------------------------------------------------------------------------

    @staticmethod
    def calendar_to_jd(
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: float = 0.0,
        gregorian_cutover: bool = True
    ) -> float:
        """
        Convert calendar date to Julian Day number.
        Accounts for Gregorian transition (1582-Oct-15 and later).
        """
        y = year
        m = month
        if m <= 2:
            y -= 1
            m += 12

        day_fraction = (day + hour / 24.0 + minute / 1440.0 + second / 86400.0)

        # Check if date is in Gregorian calendar
        is_gregorian = False
        if gregorian_cutover:
            if year > 1582:
                is_gregorian = True
            elif year == 1582:
                if month > 10 or (month == 10 and day >= 15):
                    is_gregorian = True

        if is_gregorian:
            a = math.floor(y / 100)
            b = 2 - a + math.floor(a / 4)
        else:
            b = 0

        jd = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + day_fraction + b - 1524.5
        return jd

    @staticmethod
    def jd_to_calendar(jd: float, gregorian_cutover: bool = True) -> Tuple[int, int, int, int, int, float]:
        """
        Convert Julian Day number to (year, month, day, hour, minute, second).
        """
        z_floor = math.floor(jd + 0.5)
        f = (jd + 0.5) - z_floor

        if gregorian_cutover and z_floor >= 2299161:
            alpha = math.floor((z_floor - 1867216.25) / 36524.25)
            a = z_floor + 1 + alpha - math.floor(alpha / 4)
        else:
            a = z_floor

        b = a + 1524
        c = math.floor((b - 122.1) / 365.25)
        d = math.floor(365.25 * c)
        e = math.floor((b - d) / 30.6001)

        day_fraction = b - d - math.floor(30.6001 * e) + f
        day = int(math.floor(day_fraction))
        fractional_day = day_fraction - day

        if e < 14:
            month = e - 1
        else:
            month = e - 13

        if month > 2:
            year = c - 4716
        else:
            year = c - 4715

        # Convert fractional day to HMS
        total_seconds = fractional_day * 86400.0
        hour = int(total_seconds // 3600)
        remaining = total_seconds - (hour * 3600)
        minute = int(remaining // 60)
        second = remaining - (minute * 60)

        # Micro-rounding correction
        if second >= 59.99999999:
            second = 0.0
            minute += 1
            if minute >= 60:
                minute = 0
                hour += 1
                if hour >= 24:
                    hour = 0
                    day += 1

        return year, month, day, hour, minute, second

    # -------------------------------------------------------------------------
    # Sidereal Time Calculations (IAU Standards)
    # -------------------------------------------------------------------------

    def gmst(self) -> float:
        """
        Greenwich Mean Sidereal Time (GMST) in degrees [0, 360).
        Based on IAU 2006 standard (Capitaine et al. 2006).
        theta_GMST = 280.46061837 + 360.98564736629 * (JD_UT - 2451545.0) + 0.000387933 * T^2 - T^3 / 38710000.
        """
        d = self._jd_ut - 2451545.0
        t = d / 36525.0
        deg = (
            280.46061837
            + 360.98564736629 * d
            + 0.000387933 * (t ** 2)
            - (t ** 3) / 38710000.0
        )
        return (deg % 360.0 + 360.0) % 360.0

    def gast(self, delta_psi_deg: float = 0.0, true_eps_deg: float = 23.4392911) -> float:
        """
        Greenwich Apparent Sidereal Time (GAST) in degrees [0, 360).
        GAST = GMST + Equation of Equinoxes = GMST + delta_psi * cos(eps).
        """
        eq_equinox = delta_psi_deg * math.cos(math.radians(true_eps_deg))
        return (self.gmst() + eq_equinox) % 360.0

    def lmst(self, longitude_deg: float) -> float:
        """
        Local Mean Sidereal Time (LMST) in degrees [0, 360).
        longitude_deg: East positive, West negative.
        """
        return (self.gmst() + longitude_deg) % 360.0

    def last(self, longitude_deg: float, delta_psi_deg: float = 0.0, true_eps_deg: float = 23.4392911) -> float:
        """
        Local Apparent Sidereal Time (LAST) in degrees [0, 360).
        """
        return (self.gast(delta_psi_deg, true_eps_deg) + longitude_deg) % 360.0

    def __repr__(self) -> str:
        y, m, d, h, mn, s = self.calendar
        return f"<EdelTime {y:04d}-{m:02d}-{d:02d} {h:02d}:{mn:02d}:{s:06.3f} UT | JD={self._jd_ut:.6f} | DeltaT={self._delta_t:.2f}s>"
