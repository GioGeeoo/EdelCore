# EdelCore

[![PyPI version](https://img.shields.io/badge/pypi-v0.4.1-blue.svg)](https://pypi.org/project/edelcore/)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](https://pypi.org/project/edelcore/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-29%20passed-brightgreen.svg)]()

**High-precision, pure-Python ephemeris and astrological computation engine built on IAU 2000/2006 and NASA JPL standards, delivering sub-arcsecond accuracy with zero C dependencies.**

---

## Core Features

- **Time Subsystem (`edelcore.time`)**: Gregorian/Julian calendars, native timezone handling (`ZoneInfo`/`timezone`), high-precision $\Delta T$ (-3000 to +3000 CE), GMST, GAST, LMST, LAST.
- **Celestial Mechanics & Ephemerides (`edelcore.ephem`)**:
  - Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto.
  - Asteroids & Centaurs: **Chiron**, **Ceres**, **Pallas**, **Juno**, **Vesta**.
  - Lunar Nodes (Mean & True Rahu/Ketu) and Lunar Apogee (Mean & True Lilith).
  - Fixed Stars catalog (Regulus, Aldebaran, Antares, Fomalhaut, Sirius, Spica, Algol, Vega, etc.) with proper motion and precession to date.
  - NASA SPICE JPL binary DE kernels (`.bsp`) + Standalone analytical VSOP87D / ELP2000.
- **Astrometric Corrections (`edelcore.astro`)**: Light-time iteration, annual aberration, relativistic solar deflection, IAU 2000B nutation, IAU 2006 obliquity, topocentric parallax.
- **Coordinate Systems & Refraction (`edelcore.coords`)**:
  - Equatorial $\leftrightarrow$ Ecliptic $\leftrightarrow$ Cartesian.
  - Horizontal Coordinates (Azimuth & True/Apparent Altitude) with Bennett & Saemundsson atmospheric refraction.
- **House Systems (`edelcore.houses`)**: Placidus, Koch, Regiomontanus, Campanus, Topocentric, Porphyry, Whole Sign, Equal, Vehlow, Morinus, Meridian, Alcabitius (with extreme polar safeguards).
- **Sidereal Modes (`edelcore.sidereal`)**: Lahiri (Chitrapaksha), Krishnamurti (KP), Fagan-Bradley, Raman, Ushashashi, Yukteshwar, True Citra, True Pushya, Custom.
- **Event Search Engine (`edelcore.events`)**: Brent-Dekker root-finding for degree transits, zodiac sign ingresses, and stationary retrograde turns.
- **Data Models & Formats (`edelcore.models`)**: Rich object formatting, `.sign`, `.sign_degree`, `.formatted`, `.to_dict()`, `.to_json()`.

---

## Installation

```bash
pip install edelcore
```

---

## Quick Usage and Recipes

### 1. Full Natal Chart Calculation (Supports Local Timezones & UTC)
```python
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from edelcore import EdelEngine, Body, HouseSystem

engine = EdelEngine()

# Pass local timezone or UTC datetime
dt = datetime(1980, 5, 15, 9, 30, 0, tzinfo=timezone(timedelta(hours=1)))

chart = engine.calculate_chart(
    dt_or_time=dt,
    lat_deg=51.5074,
    lon_deg=-0.1278,
    house_system=HouseSystem.PLACIDUS
)

sun = chart.get("Sun")
print(f"Sun: {sun.formatted} | House: {chart.get_house_of_body(Body.SUN)}")
# Output: Sun: 24°33'12" Taurus | House: 11
print(sun) # Rich object repr: <Sun (Direct) +00°57'48"/day 24°33'12" Taurus>

# Print summary table or export to JSON
print(chart.summary())
json_data = chart.to_json(indent=2)
```

### 2. Sidereal Vedic Ayanamsha Conversion
```python
from edelcore import AyanamshaMode

sid_chart = engine.calculate_chart(
    dt_or_time=datetime(1995, 10, 24, 14, 30, 0),
    lat_deg=28.6139,
    lon_deg=77.2090,
    house_system=HouseSystem.WHOLE_SIGN,
    sidereal_mode=AyanamshaMode.LAHIRI
)

print(f"Lahiri Ayanamsha: {sid_chart.ayanamsha:.4f}°")
print(f"Moon Sidereal: {sid_chart.get('Moon').formatted}")
```

### 3. Fixed Star Positions & Observation Angles
```python
# Calculate Regulus position and topocentric Azimuth & Altitude for London
star = engine.calculate_star("Regulus", datetime.now(), lat_deg=51.5074, lon_deg=-0.1278)

print(f"Star: {star.name} ({star.traditional_name})")
print(f"Ecliptic Longitude: {star.formatted}")
print(f"Azimuth: {star.azimuth:.2f}° | Apparent Altitude: {star.apparent_altitude:.2f}°")
```

### 4. Astronomical Event & Retrograde Search
```python
from edelcore import EdelTime

# Search for all Mercury retrograde turning points in 2026
t_start = EdelTime.from_ymd_hms(2026, 1, 1)
t_end = EdelTime.from_ymd_hms(2026, 12, 31)

stations = engine.search_stations(Body.MERCURY, t_start, t_end)
for t_st, st_type in stations:
    y, m, d, h, mn, s = t_st.calendar
    print(f"Mercury {st_type:<10} at {y:04d}-{m:02d}-{d:02d} {h:02d}:{mn:02d}:{s:04.1f} UT")
```

---

## Command Line Interface (CLI)

```bash
# Generate full astrological chart
edel chart --date 2026-08-20T12:00:00 --lat 51.5074 --lon -0.1278 --house Placidus

# Query body position with topocentric Az/Alt
edel ephem --body Chiron --date 2026-08-20T12:00:00 --lat 51.5074 --lon -0.1278

# Calculate fixed star coordinates
edel stars --name Sirius --date 2026-08-20T21:04:00 --lat 51.5074 --lon -0.1278

# Search for upcoming sign ingresses (Equinoxes & Solstices)
edel events --type ingress --body Sun --start 2026-08-01 --end 2026-10-01

# Search for stationary retrograde turning points
edel events --type station --body Mercury --start 2026-01-01 --end 2026-12-31
```

---

## Documentation and Cookbook

For in-depth mathematical documentation, theoretical celestial mechanics guides, and the complete 9-scenario cookbook, visit the [EdelCore Documentation](https://github.com/GioGeeoo/EdelCore#readme).

---

## License

MIT License &copy; 2026 Giorgi Khunzakhishvili
