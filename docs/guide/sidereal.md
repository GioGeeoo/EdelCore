# Sidereal Zodiac & Ayanamshas

The `edelcore.sidereal` subsystem allows converting any tropical chart and ephemeris coordinate into sidereal reference frameworks (Vedic / Jyotish, Western Sidereal, and Babylonian).

---

## 1. What is an Ayanamsha?

The **Tropical Zodiac** is anchored to the Moving Vernal Equinox ($0^\circ$ Aries = Sun's position at Spring Equinox). Due to precession of the equinoxes ($\approx 50.29''$ per year), the tropical zodiac drifts westward relative to the fixed constellations:

$$\lambda_{\text{sidereal}} = (\lambda_{\text{tropical}} - \text{Ayanamsha}) \pmod{360^\circ}$$
$$\lambda_{\text{tropical}} = (\lambda_{\text{sidereal}} + \text{Ayanamsha}) \pmod{360^\circ}$$

---

## 2. Precession Accumulation Algorithm

EdelCore computes the exact accumulated general precession in longitude $p_A(t)$ from standard epoch J2000.0 using the **IAU 2006 (P03)** polynomial model:

$$p_A(T) = \frac{5028.796195'' \cdot T + 1.1054348'' \cdot T^2 + 0.00007664'' \cdot T^3}{3600} \quad (\text{degrees})$$
Where $T$ is the time in Julian centuries since J2000.0 (JD 2451545.0).

$$\text{Ayanamsha}(T) = \text{Offset}_{\text{J2000}} + p_A(T)$$

---

## 3. Supported Ayanamsha Modes

| Ayanamsha Mode | Enum Key | Standard J2000 Offset | Description |
| :--- | :--- | :--- | :--- |
| **Lahiri** | `AyanamshaMode.LAHIRI` | $23^\circ 51' 30.5''$ ($23.858483^\circ$) | Official Indian Calendar Reform Committee standard (Chitrapaksha) |
| **Krishnamurti (KP)** | `AyanamshaMode.KRISHNAMURTI` | $23^\circ 47' 29.0''$ ($23.791389^\circ$) | K.S. Krishnamurti KP Astrology system |
| **Fagan-Bradley** | `AyanamshaMode.FAGAN_BRADLEY` | $24^\circ 44' 21.0''$ ($24.739167^\circ$) | Western Sidereal Astrology standard (Aldebaran at $15^\circ$ Taurus) |
| **Raman** | `AyanamshaMode.RAMAN` | $22^\circ 24' 17.0''$ ($22.404722^\circ$) | B.V. Raman system |
| **Ushashashi** | `AyanamshaMode.USHASHASHI` | $20^\circ 02' 47.0''$ ($20.046389^\circ$) | Ushashashi system |
| **Yukteshwar** | `AyanamshaMode.YUKTESHWAR` | $21^\circ 15' 32.0''$ ($21.258889^\circ$) | Sri Yukteshwar Giri system |
| **True Citra** | `AyanamshaMode.TRUE_CITRA` | $23^\circ 51' 28.8''$ | Anchored to Spica ($\alpha$ Virginis) fixed at exactly $180^\circ 00' 00''$ |
| **True Pushya** | `AyanamshaMode.TRUE_PUSHYA` | $23^\circ 54' 00.0''$ | Anchored to $\delta$ Cancri at $106^\circ 00' 00''$ |
| **Custom** | `AyanamshaMode.CUSTOM` | User-defined | Custom base offset at J2000 |

---

## 4. Usage Example

```python
from datetime import datetime
from edelcore import EdelEngine, AyanamshaMode, HouseSystem

engine = EdelEngine()

# Compute Lahiri Sidereal Chart
chart = engine.calculate_chart(
    dt_or_time=datetime(2026, 8, 20, 12, 0, 0),
    lat_deg=28.6139,
    lon_deg=77.2090,
    house_system=HouseSystem.WHOLE_SIGN,
    sidereal_mode=AyanamshaMode.LAHIRI
)

print(f"Computed Lahiri Ayanamsha for Date: {chart.ayanamsha:.6f}°")
print(chart.summary())
```
