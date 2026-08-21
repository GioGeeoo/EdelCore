# Quickstart: 5-Minute Practical Guide

Get started with EdelCore in 5 minutes with common astronomical and astrological workflows.

---

## 1. Computing a Natal Astrological Chart

EdelCore natively supports both **UTC** and **local timezones** (`zoneinfo`, `pytz`, or `timedelta`):

```python
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from edelcore import EdelEngine, HouseSystem, Body

# 1. Instantiate the unified engine
engine = EdelEngine()

# 2. Compute chart using local timezone (e.g., New York EDT / Tbilisi / Tokyo)
# Example A: Using standard ZoneInfo
dt_ny = datetime(1995, 10, 24, 10, 30, 0, tzinfo=ZoneInfo("America/New_York"))

# Example B: Using UTC offset directly (e.g. UTC+4)
dt_tbilisi = datetime(1995, 10, 24, 18, 30, 0, tzinfo=timezone(timedelta(hours=4)))

# Example C: Naive datetime (treated as UTC)
dt_utc = datetime(1995, 10, 24, 14, 30, 0)

# Calculate chart - timezone is automatically converted to UTC internally
chart = engine.calculate_chart(
    dt_or_time=dt_ny,
    lat_deg=40.7128,
    lon_deg=-74.0060,
    house_system=HouseSystem.PLACIDUS
)

# 3. Print complete chart table
print(chart.summary())
```

---

## 2. Inspecting Planetary Positions, Houses & Speeds

```python
# Access specific bodies
sun = chart.bodies[Body.SUN]
moon = chart.bodies[Body.MOON]
mars = chart.bodies[Body.MARS]

print(f"Sun: {sun.longitude:.4f}° | House: {chart.get_house_of_body(Body.SUN)}")
print(f"Moon: {moon.longitude:.4f}° | Daily Speed: {moon.speed_longitude:+.4f}°/day")
print(f"Mars Retrograde State: {mars.is_retrograde} (Speed: {mars.speed_longitude:+.4f}°/day)")
```

---

## 3. Calculating Ptolemaic Aspects

```python
# Compute aspects with an 8-degree orb limit
aspects = chart.calculate_aspects(max_orb=8.0)

for asp in aspects:
    direction = "Applying" if asp.is_applying else "Separating"
    print(f"{asp.body1.value} {asp.aspect_type} {asp.body2.value} (Orb: {asp.orb:.2f}°, {direction})")
```

---

## 4. Sidereal Chart Calculation (Vedic / Jyotish)

Convert any chart seamlessly to Lahiri, Krishnamurti (KP), or Fagan-Bradley sidereal zodiacs:

```python
from edelcore import AyanamshaMode

# Calculate Sidereal Lahiri Chart
sid_chart = engine.calculate_chart(
    dt_or_time=dt,
    lat_deg=28.6139, # New Delhi
    lon_deg=77.2090,
    house_system=HouseSystem.WHOLE_SIGN,
    sidereal_mode=AyanamshaMode.LAHIRI
)

print(f"Lahiri Ayanamsha: {sid_chart.ayanamsha:.4f}°")
print(sid_chart.summary())
```

---

## 5. Fixed Star Coordinates & Observation Angles

```python
# Calculate Regulus (Alpha Leonis) position and topocentric Az/Alt
regulus = engine.calculate_star(
    star_name="Regulus",
    dt_or_time=datetime.now(),
    lat_deg=51.5074,
    lon_deg=-0.1278
)

print(f"Star: {regulus.name} ({regulus.traditional_name})")
print(f"Ecliptic Longitude: {regulus.longitude:.4f}° | Latitude: {regulus.latitude:.4f}°")
print(f"Azimuth: {regulus.azimuth:.2f}° | Apparent Altitude: {regulus.apparent_altitude:.2f}°")
```

---

## 6. Astronomical Event Searching

Search for exact solar ingresses (e.g. Equinoxes and Solstices):

```python
from edelcore import EdelTime

# Find when Sun enters Aries (Spring Equinox) in 2026
t_start = EdelTime.from_ymd_hms(2026, 3, 15)
t_end = EdelTime.from_ymd_hms(2026, 3, 25)

ingresses = engine.search_sign_ingresses(Body.SUN, t_start, t_end)
for t_ing, sign_idx in ingresses:
    y, m, d, h, mn, s = t_ing.calendar
    print(f"Sun enters Aries at {y:04d}-{m:02d}-{d:02d} {h:02d}:{mn:02d}:{s:04.1f} UT")
```
