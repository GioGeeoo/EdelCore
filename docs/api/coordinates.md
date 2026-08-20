# API Reference: Coordinate Transformations

The `edelcore.coords` package provides spherical, equatorial, ecliptic, Cartesian, and horizontal conversions.

---

## 1. Spherical & Cartesian Conversions

### `cartesian_to_spherical(x, y, z)`
```python
def cartesian_to_spherical(x: float, y: float, z: float) -> Tuple[float, float, float]
```
Converts Cartesian rectangular coordinates $(x, y, z)$ into spherical coordinates:
- `longitude_or_ra`: $[0^\circ, 360^\circ)$
- `latitude_or_dec`: $[-90^\circ, +90^\circ]$
- `distance`: $\sqrt{x^2 + y^2 + z^2}$

---

### `spherical_to_cartesian(lon_or_ra_deg, lat_or_dec_deg, r)`
```python
def spherical_to_cartesian(lon_deg: float, lat_deg: float, r: float) -> Tuple[float, float, float]
```
Converts spherical coordinates back into Cartesian $(x, y, z)$.

---

## 2. Equatorial $\leftrightarrow$ Ecliptic Conversions

### `equatorial_to_ecliptic(ra_deg, dec_deg, eps_deg)`
```python
def equatorial_to_ecliptic(ra_deg: float, dec_deg: float, eps_deg: float) -> Tuple[float, float]
```
Converts Right Ascension ($\alpha$) and Declination ($\delta$) to Ecliptic Longitude ($\lambda$) and Latitude ($\beta$) given True Obliquity of the Ecliptic $\epsilon$:
$$\sin\beta = \sin\delta \cos\epsilon - \cos\delta \sin\epsilon \sin\alpha$$
$$\tan\lambda = \frac{\sin\alpha \cos\epsilon + \tan\delta \sin\epsilon}{\cos\alpha}$$

---

### `ecliptic_to_equatorial(lambda_deg, beta_deg, eps_deg)`
```python
def ecliptic_to_equatorial(lambda_deg: float, beta_deg: float, eps_deg: float) -> Tuple[float, float]
```
Converts Ecliptic Longitude ($\lambda$) and Latitude ($\beta$) back to Equatorial coordinates ($\alpha, \delta$).

---

## 3. Horizontal Coordinate System & Refraction

### `equatorial_to_horizontal(ra_deg, dec_deg, lmst_deg, lat_deg, pressure_mbar=1013.25, temp_celsius=10.0)`
```python
def equatorial_to_horizontal(...) -> HorizontalCoords
```
Converts topocentric $(\alpha, \delta)$ to:
- `azimuth`: $[0^\circ, 360^\circ)$ measured from North Eastward.
- `true_altitude`: Geometric altitude $[-90^\circ, +90^\circ]$.
- `apparent_altitude`: Refracted altitude.
- `refraction`: Refraction angle in arcminutes.

---

### `apply_refraction(true_alt_deg, pressure_mbar=1013.25, temp_celsius=10.0)`
```python
def apply_refraction(...) -> Tuple[float, float]
```
Computes apparent altitude $h_{\text{apparent}}$ and refraction angle in arcminutes using Bennett's formula.

---

### `remove_refraction(apparent_alt_deg, pressure_mbar=1013.25, temp_celsius=10.0)`
```python
def remove_refraction(...) -> Tuple[float, float]
```
Computes true geometric altitude from observed apparent altitude.
