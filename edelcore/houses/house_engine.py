"""
House Systems Engine for EdelCore.
Exact spherical trigonometry implementations for:
- Placidus (Newton-Raphson semi-arc solver)
- Koch (Birthplace / GOH)
- Regiomontanus (Rational sphere)
- Campanus (Prime vertical division)
- Topocentric / Polich-Page (Time-proportional poles)
- Porphyry (Quadrant trisection)
- Whole Sign (0 deg of sign of ASC)
- Equal (ASC = Cusp 1, each 30 deg)
- Vehlow Equal (ASC at 15 deg of 1st house)
- Morinus (Equator division projected to ecliptic)
- Meridian / Axial (Equal ARMC division)
- Alcabitius (Semi-diurnal arc trisection)
"""
from __future__ import annotations
import math
from enum import Enum
from typing import List, Tuple, Dict
from .angles import calculate_mc, calculate_ascendant, compute_all_angles, ChartAngles

class HouseSystem(str, Enum):
    PLACIDUS = "Placidus"
    KOCH = "Koch"
    REGIOMONTANUS = "Regiomontanus"
    CAMPANUS = "Campanus"
    TOPOCENTRIC = "Topocentric"
    PORPHYRY = "Porphyry"
    WHOLE_SIGN = "Whole Sign"
    EQUAL = "Equal"
    VEHLOW_EQUAL = "Vehlow Equal"
    MORINUS = "Morinus"
    MERIDIAN = "Meridian"
    ALCABITIUS = "Alcabitius"

# -----------------------------------------------------------------------------
# Placidus Solver (Newton-Raphson Semi-Arc Root Finding)
# -----------------------------------------------------------------------------
def _placidus_cusp_root(
    armc_deg: float,
    lat_deg: float,
    eps_deg: float,
    semi_fraction: float, # e.g. 1/3 or 2/3
    is_diurnal: bool,
    initial_guess_deg: float
) -> float:
    """
    Solve Placidus house cusp equation using Newton-Raphson iteration.
    Diurnal semi-arc DSA = 90 + dsa_offset
    Condition: ARMC - RA(lambda) = fraction * Semi-Arc
    """
    eps = math.radians(eps_deg)
    lat = math.radians(lat_deg)
    armc = math.radians(armc_deg)
    tan_lat = math.tan(lat)
    sin_eps = math.sin(eps)
    cos_eps = math.cos(eps)
    tan_eps = math.tan(eps)

    # Lambda search
    lam = math.radians(initial_guess_deg)

    for _ in range(30):
        sin_lam = math.sin(lam)
        cos_lam = math.cos(lam)

        # Declination delta: sin(delta) = sin(eps)*sin(lam)
        sin_delta = sin_eps * sin_lam
        sin_delta = max(-0.999999, min(0.999999, sin_delta))
        delta = math.asin(sin_delta)
        cos_delta = math.cos(delta)
        tan_delta = sin_delta / cos_delta

        # Right Ascension alpha: tan(alpha) = tan(lam)*cos(eps)
        # alpha in [0, 2pi)
        alpha = math.atan2(sin_lam * cos_eps, cos_lam)
        if alpha < 0:
            alpha += 2.0 * math.pi

        # Semi-arc argument: -tan(lat)*tan(delta)
        # Check polar condition (circumpolar)
        pole_arg = -tan_lat * tan_delta
        if abs(pole_arg) >= 1.0:
            # Fallback to Porphyry/Equal if inside polar circle
            return initial_guess_deg

        # Semi-diurnal arc AD = asin(tan(lat)*tan(delta))
        # DSA = pi/2 + AD, NSA = pi/2 - AD
        ad = math.asin(tan_lat * tan_delta)
        if is_diurnal:
            semi_arc = math.pi / 2.0 + ad
        else:
            semi_arc = math.pi / 2.0 - ad

        # Target hour angle H = fraction * semi_arc
        # Placidus condition: F(lam) = (armc - alpha) - semi_fraction * semi_arc = 0
        h_target = semi_fraction * semi_arc
        # Unwind difference
        h_actual = (armc - alpha + math.pi) % (2.0 * math.pi) - math.pi

        f_val = h_actual - h_target

        if abs(f_val) < 1e-9:
            break

        # Numerical derivative
        d_lam = 1e-5
        lam_step = lam + d_lam
        s_lam_s, c_lam_s = math.sin(lam_step), math.cos(lam_step)
        sin_delta_s = max(-0.999999, min(0.999999, sin_eps * s_lam_s))
        tan_delta_s = sin_delta_s / math.sqrt(1.0 - sin_delta_s**2)
        alpha_s = math.atan2(s_lam_s * cos_eps, c_lam_s)
        if alpha_s < 0:
            alpha_s += 2.0 * math.pi
        ad_s = math.asin(max(-0.999999, min(0.999999, tan_lat * tan_delta_s)))
        semi_s = (math.pi / 2.0 + ad_s) if is_diurnal else (math.pi / 2.0 - ad_s)
        h_act_s = (armc - alpha_s + math.pi) % (2.0 * math.pi) - math.pi
        f_val_s = h_act_s - semi_fraction * semi_s

        df_dlam = (f_val_s - f_val) / d_lam
        if abs(df_dlam) < 1e-12:
            break
        lam -= f_val / df_dlam

    return (math.degrees(lam) + 360.0) % 360.0

def _placidus_cusp(armc_offset_deg: float, pole_fraction: float, lat_deg: float, eps_deg: float) -> float:
    """
    Calculate Placidus cusp by iteratively solving pole altitude:
    sin(d) = sin(eps) * sin(lam)
    tan(pole) = tan(lat) * pole_fraction
    lam = calculate_ascendant(ARMC + offset, pole_eff, eps)
    Repeat until convergence.
    """
    tan_lat = math.tan(math.radians(lat_deg))
    pole_init = math.degrees(math.atan(tan_lat * pole_fraction))
    lam = calculate_ascendant(armc_offset_deg, pole_init, eps_deg)

    sin_eps = math.sin(math.radians(eps_deg))
    for _ in range(20):
        sin_delta = sin_eps * math.sin(math.radians(lam))
        sin_delta = max(-0.99999, min(0.99999, sin_delta))
        tan_delta = sin_delta / math.sqrt(1.0 - sin_delta**2)

        # AD = asin(tan_lat * tan_delta)
        ad_arg = tan_lat * tan_delta
        if abs(ad_arg) >= 1.0:
            break
        ad = math.asin(ad_arg)
        # Semi-arc fraction: target AD_sub = pole_fraction * ad
        sin_ad_sub = math.sin(pole_fraction * ad)
        if abs(tan_delta) < 1e-10:
            pole_eff = math.degrees(math.atan(tan_lat * pole_fraction))
        else:
            tan_pole = sin_ad_sub / tan_delta
            pole_eff = math.degrees(math.atan(tan_pole))

        lam_next = calculate_ascendant(armc_offset_deg, pole_eff, eps_deg)
        if abs(lam_next - lam) < 1e-7:
            break
        lam = lam_next

    return lam

def calculate_placidus(armc_deg: float, lat_deg: float, eps_deg: float) -> List[float]:
    """
    Calculate 12 Placidus house cusps [Cusp 1 .. Cusp 12] in degrees [0, 360).
    """
    mc = calculate_mc(armc_deg, eps_deg)
    asc = calculate_ascendant(armc_deg, lat_deg, eps_deg)

    # In extreme polar zones (lat > 66 deg), fallback to Porphyry
    if abs(lat_deg) > 66.0:
        return calculate_porphyry(armc_deg, lat_deg, eps_deg)

    c11 = _placidus_cusp(armc_deg - 60.0, 1.0 / 3.0, lat_deg, eps_deg)
    c12 = _placidus_cusp(armc_deg - 30.0, 2.0 / 3.0, lat_deg, eps_deg)
    c2 = _placidus_cusp(armc_deg + 30.0, 2.0 / 3.0, lat_deg, eps_deg)
    c3 = _placidus_cusp(armc_deg + 60.0, 1.0 / 3.0, lat_deg, eps_deg)

    c1 = asc
    c10 = mc
    c4 = (c10 + 180.0) % 360.0
    c7 = (c1 + 180.0) % 360.0
    c5 = (c11 + 180.0) % 360.0
    c6 = (c12 + 180.0) % 360.0
    c8 = (c2 + 180.0) % 360.0
    c9 = (c3 + 180.0) % 360.0

    return [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12]

# -----------------------------------------------------------------------------
# Koch House System (GOH - Geburtsortshäuser)
# -----------------------------------------------------------------------------
def calculate_koch(armc_deg: float, lat_deg: float, eps_deg: float) -> List[float]:
    """
    Calculate Koch house cusps using polar altitude equations.
    """
    mc = calculate_mc(armc_deg, eps_deg)
    asc = calculate_ascendant(armc_deg, lat_deg, eps_deg)

    # Calculate oblique ascension of MC: OA(MC) = RAMC - AD(MC)
    # where sin(d_MC) = sin(eps)*sin(MC), sin(AD_MC) = tan(lat)*tan(d_MC)
    sin_eps = math.sin(math.radians(eps_deg))
    sin_d_mc = sin_eps * math.sin(math.radians(mc))
    if abs(sin_d_mc) >= 1.0:
        return calculate_porphyry(armc_deg, lat_deg, eps_deg)

    tan_d_mc = sin_d_mc / math.sqrt(1.0 - sin_d_mc**2)
    tan_lat = math.tan(math.radians(lat_deg))
    ad_arg = tan_lat * tan_d_mc
    if abs(ad_arg) >= 1.0:
        return calculate_porphyry(armc_deg, lat_deg, eps_deg)

    ad_mc_deg = math.degrees(math.asin(ad_arg))

    # Oblique Ascension increments relative to Ascendant RAMC:
    c11 = calculate_ascendant(armc_deg - 60.0 - (2.0/3.0) * ad_mc_deg, lat_deg, eps_deg)
    c12 = calculate_ascendant(armc_deg - 30.0 - (1.0/3.0) * ad_mc_deg, lat_deg, eps_deg)
    c2 = calculate_ascendant(armc_deg + 30.0 + (1.0/3.0) * ad_mc_deg, lat_deg, eps_deg)
    c3 = calculate_ascendant(armc_deg + 60.0 + (2.0/3.0) * ad_mc_deg, lat_deg, eps_deg)

    c1 = asc
    c10 = mc
    c4 = (c10 + 180.0) % 360.0
    c7 = (c1 + 180.0) % 360.0
    c5 = (c11 + 180.0) % 360.0
    c6 = (c12 + 180.0) % 360.0
    c8 = (c2 + 180.0) % 360.0
    c9 = (c3 + 180.0) % 360.0

    return [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12]

# -----------------------------------------------------------------------------
# Regiomontanus (Rational Sphere Horizon Division)
# -----------------------------------------------------------------------------
def calculate_regiomontanus(armc_deg: float, lat_deg: float, eps_deg: float) -> List[float]:
    """
    Calculate Regiomontanus house cusps (equator divided into 30-degree intervals
    and projected onto horizon circles).
    Pole phi_k: tan(phi_k) = tan(lat) * sin(k * 30 deg).
    """
    mc = calculate_mc(armc_deg, eps_deg)
    asc = calculate_ascendant(armc_deg, lat_deg, eps_deg)

    tan_lat = math.tan(math.radians(lat_deg))

    # Pole 11 & 3: sin(30 deg) = 0.5
    pole_11 = math.degrees(math.atan(tan_lat * math.sin(math.radians(30.0))))
    # Pole 12 & 2: sin(60 deg) = sqrt(3)/2
    pole_12 = math.degrees(math.atan(tan_lat * math.sin(math.radians(60.0))))

    c11 = calculate_ascendant(armc_deg - 60.0, pole_11, eps_deg)
    c12 = calculate_ascendant(armc_deg - 30.0, pole_12, eps_deg)
    c2 = calculate_ascendant(armc_deg + 30.0, pole_12, eps_deg)
    c3 = calculate_ascendant(armc_deg + 60.0, pole_11, eps_deg)

    c1 = asc
    c10 = mc
    c4 = (c10 + 180.0) % 360.0
    c7 = (c1 + 180.0) % 360.0
    c5 = (c11 + 180.0) % 360.0
    c6 = (c12 + 180.0) % 360.0
    c8 = (c2 + 180.0) % 360.0
    c9 = (c3 + 180.0) % 360.0

    return [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12]

# -----------------------------------------------------------------------------
# Campanus (Prime Vertical Division)
# -----------------------------------------------------------------------------
def calculate_campanus(armc_deg: float, lat_deg: float, eps_deg: float) -> List[float]:
    """
    Calculate Campanus house cusps (Prime vertical divided into equal 30-degree arcs).
    """
    mc = calculate_mc(armc_deg, eps_deg)
    asc = calculate_ascendant(armc_deg, lat_deg, eps_deg)

    cos_lat = math.cos(math.radians(lat_deg))

    # For Campanus, pole phi_k is: sin(phi_k) = sin(lat) * sin(k * 30)
    sin_lat = math.sin(math.radians(lat_deg))
    pole_11 = math.degrees(math.asin(sin_lat * math.sin(math.radians(30.0))))
    pole_12 = math.degrees(math.asin(sin_lat * math.sin(math.radians(60.0))))

    # RAMC offset is: tan(d_RAMC) = tan(k * 30) / cos(lat)
    r30 = math.degrees(math.atan2(math.tan(math.radians(30.0)), cos_lat))
    r60 = math.degrees(math.atan2(math.tan(math.radians(60.0)), cos_lat))

    c11 = calculate_ascendant(armc_deg - 90.0 + r30, pole_11, eps_deg)
    c12 = calculate_ascendant(armc_deg - 90.0 + r60, pole_12, eps_deg)
    c2 = calculate_ascendant(armc_deg + 90.0 - r60, pole_12, eps_deg)
    c3 = calculate_ascendant(armc_deg + 90.0 - r30, pole_11, eps_deg)

    c1 = asc
    c10 = mc
    c4 = (c10 + 180.0) % 360.0
    c7 = (c1 + 180.0) % 360.0
    c5 = (c11 + 180.0) % 360.0
    c6 = (c12 + 180.0) % 360.0
    c8 = (c2 + 180.0) % 360.0
    c9 = (c3 + 180.0) % 360.0

    return [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12]

# -----------------------------------------------------------------------------
# Topocentric (Polich-Page)
# -----------------------------------------------------------------------------
def calculate_topocentric(armc_deg: float, lat_deg: float, eps_deg: float) -> List[float]:
    """
    Calculate Topocentric (Polich-Page) house cusps.
    tan(phi_11) = tan(lat) / 3
    tan(phi_12) = 2 * tan(lat) / 3
    """
    mc = calculate_mc(armc_deg, eps_deg)
    asc = calculate_ascendant(armc_deg, lat_deg, eps_deg)

    tan_lat = math.tan(math.radians(lat_deg))
    pole_11 = math.degrees(math.atan(tan_lat / 3.0))
    pole_12 = math.degrees(math.atan(2.0 * tan_lat / 3.0))

    c11 = calculate_ascendant(armc_deg - 60.0, pole_11, eps_deg)
    c12 = calculate_ascendant(armc_deg - 30.0, pole_12, eps_deg)
    c2 = calculate_ascendant(armc_deg + 30.0, pole_12, eps_deg)
    c3 = calculate_ascendant(armc_deg + 60.0, pole_11, eps_deg)

    c1 = asc
    c10 = mc
    c4 = (c10 + 180.0) % 360.0
    c7 = (c1 + 180.0) % 360.0
    c5 = (c11 + 180.0) % 360.0
    c6 = (c12 + 180.0) % 360.0
    c8 = (c2 + 180.0) % 360.0
    c9 = (c3 + 180.0) % 360.0

    return [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12]

    c1 = asc
    c10 = mc
    c4 = (c10 + 180.0) % 360.0
    c7 = (c1 + 180.0) % 360.0
    c5 = (c11 + 180.0) % 360.0
    c6 = (c12 + 180.0) % 360.0
    c8 = (c2 + 180.0) % 360.0
    c9 = (c3 + 180.0) % 360.0

    return [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12]

# -----------------------------------------------------------------------------
# Porphyry (Quadrant Trisection)
# -----------------------------------------------------------------------------
def calculate_porphyry(armc_deg: float, lat_deg: float, eps_deg: float) -> List[float]:
    """
    Porphyry house system: trisects the ecliptic arc between ASC and MC.
    """
    mc = calculate_mc(armc_deg, eps_deg)
    asc = calculate_ascendant(armc_deg, lat_deg, eps_deg)

    # Arc from MC to ASC
    arc_10_1 = (asc - mc + 360.0) % 360.0
    step_10_1 = arc_10_1 / 3.0

    c10 = mc
    c11 = (mc + step_10_1) % 360.0
    c12 = (mc + 2.0 * step_10_1) % 360.0
    c1 = asc

    # Arc from ASC to IC (IC = MC + 180)
    ic = (mc + 180.0) % 360.0
    arc_1_4 = (ic - asc + 360.0) % 360.0
    step_1_4 = arc_1_4 / 3.0

    c2 = (asc + step_1_4) % 360.0
    c3 = (asc + 2.0 * step_1_4) % 360.0
    c4 = ic

    c5 = (c11 + 180.0) % 360.0
    c6 = (c12 + 180.0) % 360.0
    c7 = (c1 + 180.0) % 360.0
    c8 = (c2 + 180.0) % 360.0
    c9 = (c3 + 180.0) % 360.0

    return [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12]

# -----------------------------------------------------------------------------
# Equal, Whole Sign, Vehlow, Morinus, Meridian, Alcabitius
# -----------------------------------------------------------------------------
def calculate_equal(armc_deg: float, lat_deg: float, eps_deg: float) -> List[float]:
    """Equal houses: Cusp 1 = ASC, each subsequent cusp is + 30 degrees."""
    asc = calculate_ascendant(armc_deg, lat_deg, eps_deg)
    return [(asc + i * 30.0) % 360.0 for i in range(12)]

def calculate_whole_sign(armc_deg: float, lat_deg: float, eps_deg: float) -> List[float]:
    """Whole sign houses: Cusp 1 = 0 deg of the zodiac sign containing the Ascendant."""
    asc = calculate_ascendant(armc_deg, lat_deg, eps_deg)
    sign_idx = int(asc // 30)
    base_lon = sign_idx * 30.0
    return [(base_lon + i * 30.0) % 360.0 for i in range(12)]

def calculate_vehlow_equal(armc_deg: float, lat_deg: float, eps_deg: float) -> List[float]:
    """Vehlow Equal: Ascendant is located at the center (15 degrees) of House 1."""
    asc = calculate_ascendant(armc_deg, lat_deg, eps_deg)
    base_cusp1 = (asc - 15.0 + 360.0) % 360.0
    return [(base_cusp1 + i * 30.0) % 360.0 for i in range(12)]

def calculate_morinus(armc_deg: float, eps_deg: float) -> List[float]:
    """Morinus: Divides celestial equator into equal 30-degree arcs from ARMC, projected to ecliptic."""
    from ..coords.transformations import equatorial_to_ecliptic
    cusps = []
    # C10 = ARMC projected to ecliptic (MC)
    # Morinus starts from East point (RAMC + 90) = Cusp 1
    for i in range(12):
        ra = (armc_deg + 90.0 + i * 30.0) % 360.0
        lam, _ = equatorial_to_ecliptic(ra, 0.0, eps_deg)
        cusps.append(lam)
    return cusps

def calculate_meridian(armc_deg: float, eps_deg: float) -> List[float]:
    """Meridian (Axial): Divides equator into equal 30-degree arcs from ARMC, Cusp 10 = MC."""
    from ..coords.transformations import equatorial_to_ecliptic
    cusps = []
    for i in range(12):
        # i=0 corresponds to House 1 -> RA = ARMC - 90? No, Cusp 10 = ARMC, Cusp 1 = ARMC + 90
        ra = (armc_deg - 90.0 + i * 30.0) % 360.0
        lam, _ = equatorial_to_ecliptic(ra, 0.0, eps_deg)
        cusps.append(lam)
    # Rotate so that cusps[0] is Cusp 1
    # with i=0 (ARMC-90) -> Cusp 4 is ARMC -> reorder
    c10 = calculate_mc(armc_deg, eps_deg)
    # Generate directly: Cusp k has RA = ARMC - 90 + (k-1)*30
    return [calculate_mc(armc_deg - 90.0 + i * 30.0, eps_deg) for i in range(12)]

def calculate_alcabitius(armc_deg: float, lat_deg: float, eps_deg: float) -> List[float]:
    """Alcabitius: Trisects the semi-diurnal arc of the Ascendant on the equator."""
    mc = calculate_mc(armc_deg, eps_deg)
    asc = calculate_ascendant(armc_deg, lat_deg, eps_deg)

    # RA of ASC
    sin_eps = math.sin(math.radians(eps_deg))
    cos_eps = math.cos(math.radians(eps_deg))
    sin_asc = math.sin(math.radians(asc))
    cos_asc = math.cos(math.radians(asc))
    ra_asc = math.degrees(math.atan2(sin_asc * cos_eps, cos_asc)) % 360.0

    # Semi-diurnal arc on equator SDA = (RA_ASC - RAMC)
    sda = (ra_asc - armc_deg + 360.0) % 360.0
    step_d = sda / 3.0

    # Semi-nocturnal arc SNA = (RAMC + 180 - RA_ASC)
    sna = (armc_deg + 180.0 - ra_asc + 360.0) % 360.0
    step_n = sna / 3.0

    from ..coords.transformations import equatorial_to_ecliptic
    c11, _ = equatorial_to_ecliptic((armc_deg + step_d) % 360.0, 0.0, eps_deg)
    c12, _ = equatorial_to_ecliptic((armc_deg + 2.0 * step_d) % 360.0, 0.0, eps_deg)
    c2, _ = equatorial_to_ecliptic((ra_asc + step_n) % 360.0, 0.0, eps_deg)
    c3, _ = equatorial_to_ecliptic((ra_asc + 2.0 * step_n) % 360.0, 0.0, eps_deg)

    c1 = asc
    c10 = mc
    c4 = (c10 + 180.0) % 360.0
    c7 = (c1 + 180.0) % 360.0
    c5 = (c11 + 180.0) % 360.0
    c6 = (c12 + 180.0) % 360.0
    c8 = (c2 + 180.0) % 360.0
    c9 = (c3 + 180.0) % 360.0

    return [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12]

    return [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12]

# -----------------------------------------------------------------------------
# Unified EdelHouses Interface
# -----------------------------------------------------------------------------
class EdelHouses:
    """Unified House Calculation Engine."""

    @staticmethod
    def calculate_houses(
        system: HouseSystem | str,
        armc_deg: float,
        lat_deg: float,
        eps_deg: float
    ) -> Tuple[List[float], ChartAngles]:
        """
        Calculate 12 house cusps [C1 .. C12] and primary chart angles.
        """
        if isinstance(system, str):
            # Normalize system name
            name_map = {s.value.lower(): s for s in HouseSystem}
            norm_key = system.lower().replace("_", " ").strip()
            system = name_map.get(norm_key, HouseSystem.PLACIDUS)

        angles = compute_all_angles(armc_deg, lat_deg, eps_deg)

        if system == HouseSystem.PLACIDUS:
            cusps = calculate_placidus(armc_deg, lat_deg, eps_deg)
        elif system == HouseSystem.KOCH:
            cusps = calculate_koch(armc_deg, lat_deg, eps_deg)
        elif system == HouseSystem.REGIOMONTANUS:
            cusps = calculate_regiomontanus(armc_deg, lat_deg, eps_deg)
        elif system == HouseSystem.CAMPANUS:
            cusps = calculate_campanus(armc_deg, lat_deg, eps_deg)
        elif system == HouseSystem.TOPOCENTRIC:
            cusps = calculate_topocentric(armc_deg, lat_deg, eps_deg)
        elif system == HouseSystem.PORPHYRY:
            cusps = calculate_porphyry(armc_deg, lat_deg, eps_deg)
        elif system == HouseSystem.WHOLE_SIGN:
            cusps = calculate_whole_sign(armc_deg, lat_deg, eps_deg)
        elif system == HouseSystem.EQUAL:
            cusps = calculate_equal(armc_deg, lat_deg, eps_deg)
        elif system == HouseSystem.VEHLOW_EQUAL:
            cusps = calculate_vehlow_equal(armc_deg, lat_deg, eps_deg)
        elif system == HouseSystem.MORINUS:
            cusps = calculate_morinus(armc_deg, eps_deg)
        elif system == HouseSystem.MERIDIAN:
            cusps = calculate_meridian(armc_deg, eps_deg)
        elif system == HouseSystem.ALCABITIUS:
            cusps = calculate_alcabitius(armc_deg, lat_deg, eps_deg)
        else:
            cusps = calculate_placidus(armc_deg, lat_deg, eps_deg)

        return cusps, angles
