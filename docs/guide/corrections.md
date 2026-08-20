# Astrometric Corrections & Optics

EdelCore converts raw geometric barycentric positions into **apparent topocentric coordinates** via a sequence of relativistic, geometrical, and atmospheric corrections.

---

## 1. Light-Time Travel Correction ($t - \tau$)

Light from a celestial body takes a finite time $\tau$ to reach the observer. The body was actually at position $\mathbf{r}(t - \tau)$ when the photon was emitted.

EdelCore solves the light-time equation via fixed-point iteration:
$$\tau_{k+1} = \frac{\|\mathbf{r}_{\text{body}}(t - \tau_k) - \mathbf{r}_{\text{Earth}}(t)\|}{c}$$
Where:
- $c = 173.1446326846693$ AU/day (speed of light).
- Convergence occurs in 2–3 iterations ($|\tau_{k+1} - \tau_k| < 10^{-11}$ day).

---

## 2. Precession & Nutation Matrices

### IAU 2006 Precession Matrix ($P$)
Transforms coordinates from the standard J2000.0 International Celestial Reference Frame (ICRF) to the Mean Equator and Equinox of Date using Fukushima-Williams / Capitaine angles ($\zeta, z, \theta$):
$$\mathbf{r}_{\text{mean\_date}} = P(T) \cdot \mathbf{r}_{\text{J2000}}$$

### IAU 2000B Nutation Matrix ($N$)
Accounts for short-period oscillations of Earth's axis driven by lunar and solar gravitational torques:
$$N = R_x(-(\epsilon_0 + \Delta\epsilon)) \cdot R_z(-\Delta\psi) \cdot R_x(\epsilon_0)$$
$$\mathbf{r}_{\text{true\_date}} = N \cdot \mathbf{r}_{\text{mean\_date}}$$
Where:
- $\Delta\psi$: Nutation in Longitude (77 terms in IAU 2000B).
- $\Delta\epsilon$: Nutation in Obliquity.
- $\epsilon_0$: IAU 2006 Mean Obliquity of the Ecliptic.

---

## 3. Annual Aberration (Special Relativity)

Due to Earth's orbital velocity $\mathbf{V}_\oplus \approx 29.8\text{ km/s}$ relative to the barycenter, the apparent direction $\mathbf{u}_{\text{app}}$ shifts towards Earth's velocity vector $\boldsymbol{\beta} = \mathbf{V}_\oplus / c$:

$$\mathbf{u}_{\text{app}} = \frac{\mathbf{u} + \boldsymbol{\beta} + \left(\frac{\gamma}{\gamma + 1}\right) (\mathbf{u} \cdot \boldsymbol{\beta}) \boldsymbol{\beta}}{1 + \mathbf{u} \cdot \boldsymbol{\beta}}$$
Where $\gamma = 1 / \sqrt{1 - \|\boldsymbol{\beta}\|^2}$.

---

## 4. Topocentric Parallax Correction

Planetary positions seen from the surface of Earth differ from geocentric centers (most prominently for the Moon, whose parallax reaches up to $\approx 1^\circ$).

EdelCore computes the observer's position vector on the **WGS84 Earth Ellipsoid**:
Let $\phi$ be the geographic latitude, $h_{\text{alt}}$ the altitude above sea level, and $\theta = \text{LAST}$ the Local Apparent Sidereal Time:

$$\rho \cos\phi' = \frac{a}{\sqrt{1 + (1-f)^2 \tan^2\phi}} \cos\phi + h_{\text{alt}} \cos\phi$$
$$\rho \sin\phi' = \frac{a(1-f)^2}{\sqrt{1 + (1-f)^2 \tan^2\phi}} \sin\phi + h_{\text{alt}} \sin\phi$$

The observer's rectangular coordinate vector $\mathbf{R}_{\text{obs}}$ in AU is:
$$\mathbf{R}_{\text{obs}} = \begin{pmatrix} \rho \cos\phi' \cos\theta \\ \rho \cos\phi' \sin\theta \\ \rho \sin\phi' \end{pmatrix}$$

Topocentric coordinates are:
$$\mathbf{r}_{\text{topo}} = \mathbf{r}_{\text{geo}} - \mathbf{R}_{\text{obs}}$$

---

## 5. Atmospheric Refraction (Bennett / Saemundsson)

When observing celestial bodies through Earth's atmosphere, rays bend towards the zenith, making objects appear higher than their geometric altitude $h_{\text{true}}$.

EdelCore uses the standard **Bennett (1982)** formula corrected for ambient pressure $P$ (mbar) and temperature $T$ ($^\circ\text{C}$):

$$R_0 = \frac{1.0'}{\tan\left(h_{\text{true}} + \frac{7.31^\circ}{h_{\text{true}} + 4.4^\circ}\right)}$$
$$R = R_0 \cdot \left(\frac{P}{1010}\right) \cdot \left(\frac{283.15}{273.15 + T}\right)$$
$$h_{\text{apparent}} = h_{\text{true}} + \frac{R}{60^\circ}$$
