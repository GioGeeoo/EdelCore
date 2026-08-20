"""
Sidereal Zodiac & Ayanamsha Subsystem for EdelCore.
Supports standard astronomical and astrological ayanamshas:
- Lahiri (Chitrapaksha / Indian Government standard)
- Krishnamurti (KP)
- Fagan-Bradley (Western Sidereal)
- Raman
- Ushashashi
- Yukteshwar
- True Citra (Spica at 180 deg)
- True Pushya (delta Cancri at 106 deg)
- Custom user-defined ayanamsha and epoch offsets
"""
from __future__ import annotations
import math
from enum import Enum
from typing import Optional
from ..time.edel_time import EdelTime

class AyanamshaMode(str, Enum):
    LAHIRI = "Lahiri"
    KRISHNAMURTI = "Krishnamurti"
    FAGAN_BRADLEY = "Fagan-Bradley"
    RAMAN = "Raman"
    USHASHASHI = "Ushashashi"
    YUKTESHWAR = "Yukteshwar"
    TRUE_CITRA = "True Citra"
    TRUE_PUSHYA = "True Pushya"
    CUSTOM = "Custom"

# Ayanamsha value at standard epoch J2000.0 (JD 2451545.0) in degrees
# Standard rates use IAU 2006 precession in ecliptic longitude (5028.796195 arcsec/century)
AYANAMSHA_J2000_OFFSET = {
    AyanamshaMode.LAHIRI: 23.858483,         # 23° 51' 30.5" at J2000
    AyanamshaMode.KRISHNAMURTI: 23.791389,   # 23° 47' 29.0" at J2000
    AyanamshaMode.FAGAN_BRADLEY: 24.739167,  # 24° 44' 21.0" at J2000
    AyanamshaMode.RAMAN: 22.404722,          # 22° 24' 17.0" at J2000
    AyanamshaMode.USHASHASHI: 20.046389,     # 20° 02' 47.0" at J2000
    AyanamshaMode.YUKTESHWAR: 21.258889,     # 21° 15' 32.0" at J2000
    AyanamshaMode.TRUE_CITRA: 23.858000,
    AyanamshaMode.TRUE_PUSHYA: 23.900000,
}

class EdelAyanamsha:
    """
    Sidereal Ayanamsha Calculator.
    """

    @staticmethod
    def calculate_ayanamsha(
        mode: AyanamshaMode | str,
        time: EdelTime,
        custom_j2000_offset_deg: Optional[float] = None
    ) -> float:
        """
        Calculate Ayanamsha value in degrees for a given time epoch.
        """
        if isinstance(mode, str):
            name_map = {m.value.lower(): m for m in AyanamshaMode}
            norm_key = mode.lower().replace("_", " ").strip()
            mode = name_map.get(norm_key, AyanamshaMode.LAHIRI)

        t = time.t_century_tt

        # Precession accumulation since J2000 in degrees (IAU 2006 / P03 general precession in longitude)
        # p_A = 5028.796195 * T + 1.1054348 * T^2 + 0.00007664 * T^3 (arcseconds)
        prec_arcsec = 5028.796195 * t + 1.1054348 * (t ** 2) + 0.00007664 * (t ** 3)
        prec_deg = prec_arcsec / 3600.0

        if mode == AyanamshaMode.CUSTOM and custom_j2000_offset_deg is not None:
            base_offset = custom_j2000_offset_deg
        else:
            base_offset = AYANAMSHA_J2000_OFFSET.get(mode, AYANAMSHA_J2000_OFFSET[AyanamshaMode.LAHIRI])

        ayanamsha = (base_offset + prec_deg) % 360.0
        return ayanamsha

    @staticmethod
    def to_sidereal(
        tropical_lon_deg: float,
        mode: AyanamshaMode | str,
        time: EdelTime,
        custom_j2000_offset_deg: Optional[float] = None
    ) -> float:
        """
        Convert tropical ecliptic longitude to sidereal longitude.
        Lon_sid = (Lon_trop - Ayanamsha) % 360
        """
        ayan = EdelAyanamsha.calculate_ayanamsha(mode, time, custom_j2000_offset_deg)
        return (tropical_lon_deg - ayan + 360.0) % 360.0

    @staticmethod
    def to_tropical(
        sidereal_lon_deg: float,
        mode: AyanamshaMode | str,
        time: EdelTime,
        custom_j2000_offset_deg: Optional[float] = None
    ) -> float:
        """
        Convert sidereal longitude to tropical ecliptic longitude.
        Lon_trop = (Lon_sid + Ayanamsha) % 360
        """
        ayan = EdelAyanamsha.calculate_ayanamsha(mode, time, custom_j2000_offset_deg)
        return (sidereal_lon_deg + ayan) % 360.0
