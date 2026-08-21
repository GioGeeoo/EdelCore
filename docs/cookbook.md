# EdelCore Cookbook: Real-World Recipes and Scenarios

This cookbook provides 9 copy-pasteable, production-ready scenarios covering common and advanced astrological and astronomical workflows with `edelcore`.

---

## Scenario 1: Full Natal Chart and Body Access

Calculate a complete natal chart, access planetary objects using string or enum keys, and display zodiac sign formatting, retrogradation, and speeds.

```python
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from edelcore import EdelEngine, Body, HouseSystem

# 1. Initialize calculation engine
engine = EdelEngine()

# 2. Compute natal chart for London using local timezone (BST is UTC+1)
dt = datetime(1980, 5, 15, 9, 30, 0, tzinfo=timezone(timedelta(hours=1)))
chart = engine.calculate_chart(
    dt_or_time=dt,
    lat_deg=51.5074,
    lon_deg=-0.1278,
    house_system=HouseSystem.PLACIDUS
)

# 3. Access bodies (both chart.get("Sun") or chart.bodies[Body.SUN] are supported)
sun = chart.get("Sun")
moon = chart.get("Moon")
mercury = chart.get(Body.MERCURY)

print(f"Sun:     {sun.formatted} (Sign: {sun.sign}, Deg: {sun.sign_degree:.2f}°)")
print(f"Moon:    {moon.formatted} (Daily Motion: {moon.speed_longitude:+.4f}°/day)")
print(f"Mercury: {mercury}") # Formatted object repr
# Output: <Mercury (Direct) +01°22'45"/day 12°34'56" Gemini>

# 4. Display complete chart table
print(chart.summary())
```

---

## Scenario 2: House Cusps and Angles

Iterate through all 12 astrological house cusps and retrieve principal angles (ASC, MC, IC, DSC, Vertex, East Point).

```python
from datetime import datetime
from edelcore import EdelEngine, format_zodiac_deg

engine = EdelEngine()
chart = engine.calculate_chart(datetime.now(), lat_deg=40.7128, lon_deg=-74.0060)

# 1. Access Angles
angles = chart.angles
print(f"Ascendant (ASC):   {angles.asc_formatted} ({angles.asc:.4f}°)")
print(f"Midheaven (MC):    {angles.mc_formatted} ({angles.mc:.4f}°)")
print(f"Vertex:            {angles.vertex_formatted}")
print(f"East Point (EP):   {angles.east_point_formatted}")

# 2. Iterate through 12 House Cusps
print("\n--- 12 House Cusps ---")
for i, cusp_deg in enumerate(chart.cusps, 1):
    sign, sign_deg, fmt = format_zodiac_deg(cusp_deg)
    print(f"House {i:>2}: {fmt}")
```

---

## Scenario 3: Comparing Multiple House Systems

Compare house cusps side-by-side across Placidus, Koch, Regiomontanus, and Whole Sign systems for the exact same moment.

```python
from datetime import datetime
from edelcore import EdelEngine, HouseSystem, format_zodiac_deg

engine = EdelEngine()
dt = datetime(2026, 8, 20, 21, 4, 0)
lat, lon = 51.5074, -0.1278

systems = [
    HouseSystem.PLACIDUS,
    HouseSystem.KOCH,
    HouseSystem.REGIOMONTANUS,
    HouseSystem.CAMPANUS,
    HouseSystem.WHOLE_SIGN
]

charts = {hs.value: engine.calculate_chart(dt, lat, lon, house_system=hs) for hs in systems}

print(f"{'House':<8} " + " ".join([f"{hs.value:<18}" for hs in systems]))
print("-" * 98)

for i in range(12):
    row = [f"House {i+1:<2}"]
    for hs in systems:
        cusp_val = charts[hs.value].cusps[i]
        _, _, fmt = format_zodiac_deg(cusp_val)
        row.append(f"{fmt:<18}")
    print(" ".join(row))
```

---

## Scenario 4: Centaurs, Asteroids, and Lunar Points

Calculate exact positions for Chiron, Ceres, Pallas, Juno, Vesta, the Lunar Nodes (Rahu/Ketu), and Black Moon Lilith.

```python
from datetime import datetime
from edelcore import EdelEngine, Body

engine = EdelEngine()
dt = datetime.now()
chart = engine.calculate_chart(dt, lat_deg=51.5074, lon_deg=-0.1278)

special_bodies = [
    Body.CHIRON,
    Body.CERES,
    Body.PALLAS,
    Body.JUNO,
    Body.VESTA,
    Body.TRUE_NODE,
    Body.TRUE_LILITH
]

for b in special_bodies:
    pos = chart.get(b)
    h_num = chart.get_house_of_body(b)
    motion = "Rx" if pos.is_retrograde else "Dir"
    print(f"{b.value:<14} | {pos.formatted:<20} | House {h_num:>2} | {motion} ({pos.speed_longitude:>+7.4f}°/d)")
```

---

## Scenario 5: Fixed Stars with Proper Motion and Precession

Calculate high-precision positions and visual magnitudes for the 4 Royal Stars (Regulus, Aldebaran, Antares, Fomalhaut) and key astrological fixed stars (Algol, Sirius, Spica).

```python
from datetime import datetime
from edelcore import EdelEngine

engine = EdelEngine()
dt = datetime(2026, 8, 20, 22, 0, 0)
lat, lon = 51.5074, -0.1278

key_stars = ["Regulus", "Aldebaran", "Antares", "Fomalhaut", "Algol", "Sirius", "Spica"]

print(f"{'Star Name':<12} {'Constellation':<14} {'Ecliptic Longitude':<22} {'Azimuth / Altitude'}")
print("-" * 75)

for star_name in key_stars:
    star = engine.calculate_star(star_name, dt, lat_deg=lat, lon_deg=lon)
    az_alt = f"{star.azimuth:>6.2f}° / {star.apparent_altitude:>+6.2f}°" if star.azimuth is not None else "N/A"
    print(f"{star.name:<12} {star.constellation:<14} {star.formatted:<22} {az_alt}")
```

---

## Scenario 6: Topocentric Horizontal Coordinates

Compute exact local horizon coordinates (Azimuth $0^\circ \to 360^\circ$ from North Eastward, True Altitude, and Refracted Apparent Altitude) for telescope pointing or planetary visibility.

```python
from datetime import datetime
from edelcore import EdelEngine, Body, EdelTime

engine = EdelEngine()
t = EdelTime.from_datetime(datetime(2026, 8, 20, 22, 30, 0)) # Night sky
lat, lon = 37.7749, -122.4194 # San Francisco

for body in [Body.MOON, Body.JUPITER, Body.SATURN, Body.MARS]:
    hz = engine.calculate_horizontal(body, t, lat_deg=lat, lon_deg=lon)
    visibility = "Visible (Above Horizon)" if hz.true_altitude > 0 else "Below Horizon"
    print(f"{body.value:<10}: Azimuth = {hz.azimuth:>6.2f}°, Apparent Alt = {hz.apparent_altitude:>+6.2f}° ({visibility})")
```

---

## Scenario 7: Sidereal Astrometry and Vedic Ayanamshas

Calculate and compare Western Tropical charts against Vedic Sidereal systems (Lahiri, Krishnamurti KP, Raman, and Fagan-Bradley).

```python
from datetime import datetime
from edelcore import EdelEngine, AyanamshaMode, HouseSystem, Body

engine = EdelEngine()
dt = datetime(1995, 10, 24, 14, 30, 0)
lat, lon = 28.6139, 77.2090 # New Delhi

# 1. Western Tropical Chart
tropical_chart = engine.calculate_chart(dt, lat, lon, house_system=HouseSystem.PLACIDUS)

# 2. Vedic Lahiri Whole Sign Chart
lahiri_chart = engine.calculate_chart(
    dt, lat, lon,
    house_system=HouseSystem.WHOLE_SIGN,
    sidereal_mode=AyanamshaMode.LAHIRI
)

print(f"Lahiri Ayanamsha Value: {lahiri_chart.ayanamsha:.4f}°\n")
print(f"{'Body':<10} {'Tropical Longitude':<22} {'Lahiri Sidereal Longitude'}")
print("-" * 55)

for b in [Body.SUN, Body.MOON, Body.MARS, Body.JUPITER, Body.SATURN]:
    trop_pos = tropical_chart.get(b)
    sid_pos = lahiri_chart.get(b)
    print(f"{b.value:<10} {trop_pos.formatted:<22} {sid_pos.formatted}")
```

---

## Scenario 8: Searching Ingresses and Retrograde Stations

Locate the exact second of astrological ingresses (Equinoxes / Sign changes) and planetary stationary turning points using root-finding algorithms.

```python
from datetime import datetime
from edelcore import EdelEngine, Body, EdelTime

engine = EdelEngine()

# 1. Search for all 2026 Mercury Retrograde Stations
t_start = EdelTime.from_datetime(datetime(2026, 1, 1))
t_end = EdelTime.from_datetime(datetime(2026, 12, 31))

print("=== Mercury Stationary Points (2026) ===")
stations = engine.search_stations(Body.MERCURY, t_start, t_end)
for t_st, st_type in stations:
    y, m, d, h, mn, s = t_st.calendar
    pos = engine.ephemeris.calculate_body(Body.MERCURY, t_st)
    print(f"Station {st_type:<10} at {y:04d}-{m:02d}-{d:02d} {h:02d}:{mn:02d}:{s:04.1f} UT ({pos.formatted})")

# 2. Search for exact Equinoxes and Solstices (Sun Ingresses)
print("\n=== Cardinal Sun Ingresses (2026) ===")
ingresses = engine.search_sign_ingresses(Body.SUN, t_start, t_end)
cardinal_signs = {0: "Aries (Spring Equinox)", 3: "Cancer (Summer Solstice)", 6: "Libra (Autumn Equinox)", 9: "Capricorn (Winter Solstice)"}

for t_ing, sign_idx in ingresses:
    if sign_idx in cardinal_signs:
        y, m, d, h, mn, s = t_ing.calendar
        print(f"{cardinal_signs[sign_idx]:<28} -> {y:04d}-{m:02d}-{d:02d} {h:02d}:{mn:02d}:{s:04.1f} UT")
```

---

## Scenario 9: JSON Export for REST API and Web Services

Serialize full chart calculations into clean dictionaries or JSON strings for web APIs (FastAPI, Flask, Django).

```python
from datetime import datetime
from edelcore import EdelEngine, HouseSystem

engine = EdelEngine()
chart = engine.calculate_chart(
    dt_or_time=datetime(2026, 8, 20, 21, 4, 0),
    lat_deg=51.5074,
    lon_deg=-0.1278,
    house_system=HouseSystem.PLACIDUS
)

# 1. Direct JSON serialization
json_output = chart.to_json(indent=2)
print(json_output[:400] + "\n  ...\n}")

# 2. Python dictionary for FastAPI JSONResponse
data_dict = chart.to_dict()
print("\nTop-level keys in chart dict:", list(data_dict.keys()))
```
