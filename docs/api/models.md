# API Reference: Data Models & Enums

Comprehensive reference of all public data structures, NamedTuples, and enumerations in EdelCore.

---

## 1. Enumerations

### `enum Body`
```python
from edelcore import Body
```
- `Body.SUN`: Sun
- `Body.MOON`: Moon
- `Body.MERCURY`: Mercury
- `Body.VENUS`: Venus
- `Body.MARS`: Mars
- `Body.JUPITER`: Jupiter
- `Body.SATURN`: Saturn
- `Body.URANUS`: Uranus
- `Body.NEPTUNE`: Neptune
- `Body.PLUTO`: Pluto
- `Body.CHIRON`: Centaur 2060 Chiron
- `Body.CERES`: Dwarf Planet 1 Ceres
- `Body.PALLAS`: Asteroid 2 Pallas
- `Body.JUNO`: Asteroid 3 Juno
- `Body.VESTA`: Asteroid 4 Vesta
- `Body.MEAN_NODE`: Mean North Lunar Node (Rahu)
- `Body.TRUE_NODE`: Osculating True North Lunar Node
- `Body.MEAN_SOUTH_NODE`: Mean South Lunar Node (Ketu)
- `Body.TRUE_SOUTH_NODE`: True South Lunar Node
- `Body.MEAN_LILITH`: Mean Black Moon (Lunar Apogee)
- `Body.TRUE_LILITH`: True Osculating Lilith

---

### `enum HouseSystem`
```python
from edelcore import HouseSystem
```
- `HouseSystem.PLACIDUS = "Placidus"`
- `HouseSystem.KOCH = "Koch"`
- `HouseSystem.REGIOMONTANUS = "Regiomontanus"`
- `HouseSystem.CAMPANUS = "Campanus"`
- `HouseSystem.TOPOCENTRIC = "Topocentric"`
- `HouseSystem.PORPHYRY = "Porphyry"`
- `HouseSystem.WHOLE_SIGN = "Whole Sign"`
- `HouseSystem.EQUAL = "Equal"`
- `HouseSystem.VEHLOW_EQUAL = "Vehlow Equal"`
- `HouseSystem.MORINUS = "Morinus"`
- `HouseSystem.MERIDIAN = "Meridian"`
- `HouseSystem.ALCABITIUS = "Alcabitius"`

---

### `enum AyanamshaMode`
```python
from edelcore import AyanamshaMode
```
- `AyanamshaMode.LAHIRI = "Lahiri"`
- `AyanamshaMode.KRISHNAMURTI = "Krishnamurti"`
- `AyanamshaMode.FAGAN_BRADLEY = "Fagan-Bradley"`
- `AyanamshaMode.RAMAN = "Raman"`
- `AyanamshaMode.USHASHASHI = "Ushashashi"`
- `AyanamshaMode.YUKTESHWAR = "Yukteshwar"`
- `AyanamshaMode.TRUE_CITRA = "True Citra"`
- `AyanamshaMode.TRUE_PUSHYA = "True Pushya"`
- `AyanamshaMode.CUSTOM = "Custom"`

---

## 2. Models & Data Classes

### `class BodyPosition`
```python
class BodyPosition(NamedTuple):
    body: Body
    longitude: float       # Ecliptic Longitude [0, 360) deg
    latitude: float        # Ecliptic Latitude [-90, +90] deg
    distance: float        # Distance in AU
    speed_longitude: float # Daily rate of change in longitude (deg/day)
    speed_latitude: float  # Daily rate of change in latitude (deg/day)
    speed_distance: float  # Daily rate of change in distance (AU/day)
    ra: float              # Right Ascension [0, 360) deg
    dec: float             # Declination [-90, +90] deg
    is_retrograde: bool    # True if speed_longitude < 0
```

---

### `class ChartAngles`
```python
class ChartAngles(NamedTuple):
    armc: float        # Right Ascension of Midheaven (degrees)
    mc: float          # Midheaven longitude (degrees)
    ic: float          # Imum Coeli longitude (degrees)
    asc: float         # Ascendant longitude (degrees)
    dsc: float         # Descendant longitude (degrees)
    vertex: float      # Vertex longitude (degrees)
    anti_vertex: float # Anti-Vertex longitude (degrees)
    east_point: float  # East Point / Equatorial Ascendant (degrees)
```

---

### `class Aspect`
```python
class Aspect(NamedTuple):
    body1: Body
    body2: Body
    aspect_type: str      # 'Conjunction', 'Sextile', 'Square', 'Trine', 'Opposition'
    angle: float          # Standard angle (0, 60, 90, 120, 180)
    orb: float            # Deviation from exact aspect (degrees)
    is_applying: bool     # True if moving towards exact aspect
```

---

### `class StarPosition`
```python
class StarPosition(NamedTuple):
    name: str
    traditional_name: str
    constellation: str
    vmag: float
    longitude: float
    latitude: float
    ra: float
    dec: float
    azimuth: Optional[float] = None
    altitude: Optional[float] = None
    apparent_altitude: Optional[float] = None
```

---

### `class ChartData`
Container for computed astrological charts.
- `chart.bodies`: `Dict[Body, BodyPosition]`
- `chart.cusps`: `List[float]` (12 house cusps in degrees)
- `chart.angles`: `ChartAngles`
- `chart.get_house_of_body(body: Body) -> int`: Returns house number $1 \dots 12$.
- `chart.calculate_aspects(max_orb=8.0) -> List[Aspect]`
- `chart.summary() -> str`: Formatted text chart table.
