# API Reference: Core Engine (`EdelEngine`)

`edelcore.EdelEngine` is the top-level unified facade orchestrating all sub-modules.

---

## `class EdelEngine`

```python
from edelcore import EdelEngine

engine = EdelEngine(bsp_path=None)
```

### Parameters:
- `bsp_path` (`Optional[str]`): Optional filepath to a NASA JPL SPICE Binary SPK kernel (e.g. `de440.bsp`, `de421.bsp`). When omitted, EdelCore automatically uses its pure-Python standalone analytical engine (VSOP87D / ELP-2000).

---

## Methods

### `calculate_chart(...)`
```python
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
    apparent: bool = True
) -> ChartData
```

Computes an astrological chart containing all planetary coordinates, daily speeds, house cusps, chart angles, obliquity, nutation, and sidereal offsets.

---

### `calculate_horizontal(...)`
```python
def calculate_horizontal(
    self,
    body: Body,
    time: EdelTime,
    lat_deg: float,
    lon_deg: float,
    alt_meters: float = 0.0,
    pressure_mbar: float = 1013.25,
    temp_celsius: float = 10.0
) -> HorizontalCoords
```

Computes topocentric Azimuth ($0^\circ \to 360^\circ$ from North), True Altitude ($h_{\text{true}}$), and Apparent Altitude ($h_{\text{app}}$ with atmospheric refraction) for any body.

---

### `calculate_star(...)`
```python
def calculate_star(
    self,
    star_name: str,
    dt_or_time: Union[datetime, EdelTime],
    lat_deg: Optional[float] = None,
    lon_deg: Optional[float] = None,
    alt_meters: float = 0.0,
    apparent: bool = True
) -> StarPosition
```

Computes coordinates for a cataloged fixed star (e.g. Sirius, Regulus, Spica, Algol, Vega) with proper motion, precession to date, nutation, and optional horizontal Az/Alt.

---

### `list_stars()`
```python
def list_stars(self) -> List[str]
```
Returns a list of all available named fixed stars in the catalog.

---

### `search_transit(...)`
```python
def search_transit(
    self,
    body: Body,
    target_lon_deg: float,
    start_time: Union[datetime, EdelTime],
    end_time: Union[datetime, EdelTime],
    tol_seconds: float = 0.5
) -> Optional[EdelTime]
```
Finds the exact moment when `body` reaches `target_lon_deg`.

---

### `search_sign_ingresses(...)`
```python
def search_sign_ingresses(
    self,
    body: Body,
    start_time: Union[datetime, EdelTime],
    end_time: Union[datetime, EdelTime],
    tol_seconds: float = 0.5
) -> List[Tuple[EdelTime, int]]
```
Finds all zodiac sign boundary entries ($0^\circ, 30^\circ, \dots$) in time range.

---

### `search_stations(...)`
```python
def search_stations(
    self,
    body: Body,
    start_time: Union[datetime, EdelTime],
    end_time: Union[datetime, EdelTime],
    tol_seconds: float = 5.0
) -> List[Tuple[EdelTime, str]]
```
Finds all stationary turning points ($v_\lambda(t) = 0$) in time range.
