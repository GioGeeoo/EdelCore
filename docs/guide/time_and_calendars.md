# Time Subsystem & Calendar Systems

The `edelcore.time` module is the foundation of all astronomical and astrological calculations in EdelCore. Precision in ephemerides depends directly on consistent time scale transformations.

---

## 1. Julian Day (JD) Algorithms

The Julian Day number is the continuous count of days elapsed since Greenwich mean noon on January 1, 4713 BCE (Julian proleptic calendar).

### Calendar Conversion Mathematical Model
EdelCore implements the rigorous algorithm from Jean Meeus (*Astronomical Algorithms*, Chapter 7) supporting both Gregorian and Julian historical calendars with the cutover at October 15, 1582:

Let $Y$ be the year and $M$ the month ($1 \le M \le 12$).
If $M \le 2$:
$$Y' = Y - 1, \quad M' = M + 12$$
Otherwise:
$$Y' = Y, \quad M' = M$$

For dates in the Gregorian calendar ($Y > 1582$ or $(Y = 1582 \land M > 10)$ or $(Y = 1582 \land M = 10 \land D \ge 15)$):
$$A = \lfloor Y' / 100 \rfloor$$
$$B = 2 - A + \lfloor A / 4 \rfloor$$
For dates in the Julian calendar ($Y < 1582$, etc.):
$$B = 0$$

The Julian Day at $0^\text{h}$ UT is:
$$\text{JD} = \lfloor 365.25 (Y' + 4716) \rfloor + \lfloor 30.6001 (M' + 1) \rfloor + D + B - 1524.5$$

Where $D$ includes fractional day hours, minutes, and seconds:
$$D = \text{day} + \frac{\text{hour}}{24} + \frac{\text{minute}}{1440} + \frac{\text{second}}{86400}$$

---

## 2. $\Delta T$ (Delta T = TT - UT1) Polynomial Models

Earth's rotational velocity is slowing non-linearly due to tidal friction and core-mantle coupling. 
- **Universal Time (UT1):** Based on Earth's actual variable rotation.
- **Terrestrial Time (TT / TDT):** Uniform atomic dynamical time used for planetary ephemerides.

$$\Delta T = \text{TT} - \text{UT1}$$

EdelCore implements the comprehensive **Espenak & Meeus (2006)** and **Morrison & Stephenson (2004)** polynomial fits spanning **-3000 BCE to +3000 CE**.

### Piecewise Polynomial Formulation:
For $y$ (decimal year $y = \text{year} + \frac{\text{month} - 0.5}{12}$):

- **For $-500 \le y < +500$:**
  $$u = y / 100$$
  $$\Delta T = 10583.6 - 1014.41 u + 33.78311 u^2 - 5.952053 u^3 - 0.1798452 u^4 + 0.022174192 u^5 + 0.0090316521 u^6 \quad (\text{seconds})$$

- **For $+2005 \le y < +2050$:**
  $$t = y - 2000$$
  $$\Delta T = 62.92 + 0.32217 t + 0.005589 t^2 \quad (\text{seconds})$$

---

## 3. Sidereal Time Subsystem (GMST, GAST, LMST, LAST)

### Greenwich Mean Sidereal Time (GMST)
Based on the **IAU 2006** standard (Capitaine et al. 2006):
Let $d = \text{JD}_{\text{UT1}} - 2451545.0$ and $T = d / 36525$:

$$\theta_{\text{GMST}} = 280.46061837^\circ + 360.98564736629^\circ \cdot d + 0.000387933^\circ \cdot T^2 - \frac{T^3}{38710000}^\circ \pmod{360^\circ}$$

### Greenwich Apparent Sidereal Time (GAST)
Incorporates the **Equation of the Equinoxes**:
$$\text{GAST} = \text{GMST} + \Delta\psi \cos(\epsilon)$$
Where:
- $\Delta\psi$ is the IAU 2000B Nutation in Longitude.
- $\epsilon$ is the True Obliquity of the Ecliptic.

### Local Sidereal Time (LMST / LAST)
For an observer at geographic longitude $\lambda_{\text{geo}}$ (East positive, West negative):
$$\text{LMST} = (\text{GMST} + \lambda_{\text{geo}}) \pmod{360^\circ}$$
$$\text{LAST} = (\text{GAST} + \lambda_{\text{geo}}) \pmod{360^\circ}$$

---

## 4. Code Examples

```python
from edelcore import EdelTime

# Construct from datetime
t = EdelTime.from_ymd_hms(2026, 8, 20, 21, 4, 0)

print("Julian Day UT1:", t.jd_ut)
print("Julian Day TT: ", t.jd_tt)
print("Delta T:        ", t.delta_t, "seconds")
print("GMST:           ", t.gmst(), "degrees")
print("LMST (London):  ", t.lmst(-0.1278), "degrees")
```
