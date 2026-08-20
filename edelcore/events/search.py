"""
High-Precision Astronomical Event & Crossing Search Engine.
Provides deterministic root-finding algorithms (Brent's method / Newton-Raphson)
for time-critical astronomical events:
- Exact degree crossings (search_transit_time)
- Exact zodiac sign ingresses (search_sign_ingress)
- Exact stationary turns & retrograde transitions (search_station)
"""
from __future__ import annotations
import math
from typing import Optional, List, Tuple, Callable
from ..time.edel_time import EdelTime
from ..ephem.bodies import Body
from ..ephem.ephemeris import EdelEphemeris

def _brent_root(
    f: Callable[[float], float],
    a: float,
    b: float,
    tol: float = 1e-8,
    max_iter: int = 60
) -> float:
    """
    Brent-Dekker root-finding algorithm.
    Guarantees superlinear convergence for continuous monotonic intervals [a, b].
    """
    fa = f(a)
    fb = f(b)
    if fa * fb > 0.0:
        raise ValueError(f"Root is not bracketed: f({a})={fa}, f({b})={fb}")

    if abs(fa) < abs(fb):
        a, b = b, a
        fa, fb = fb, fa

    c = a
    fc = fa
    mflag = True
    d = 0.0

    for _ in range(max_iter):
        if abs(fb) < 1e-14 or abs(b - a) < tol:
            return b

        if fa != fc and fb != fc:
            # Inverse quadratic interpolation
            s = (
                (a * fb * fc) / ((fa - fb) * (fa - fc))
                + (b * fa * fc) / ((fb - fa) * (fb - fc))
                + (c * fa * fb) / ((fc - fa) * (fc - fb))
            )
        else:
            # Secant method
            s = b - fb * (b - a) / (fb - fa)

        # Conditions to fall back to bisection
        cond1 = not ((3.0 * a + b) / 4.0 <= s <= b or b <= s <= (3.0 * a + b) / 4.0)
        cond2 = mflag and (abs(s - b) >= abs(b - c) / 2.0)
        cond3 = (not mflag) and (abs(s - b) >= abs(c - d) / 2.0)
        cond4 = mflag and (abs(b - c) < tol)
        cond5 = (not mflag) and (abs(c - d) < tol)

        if cond1 or cond2 or cond3 or cond4 or cond5:
            s = (a + b) / 2.0
            mflag = True
        else:
            mflag = False

        fs = f(s)
        d = c
        c = b
        fc = fb

        if fa * fs < 0.0:
            b = s
            fb = fs
        else:
            a = s
            fa = fs

        if abs(fa) < abs(fb):
            a, b = b, a
            fa, fb = fb, fa

    return b

def search_transit_time(
    ephem: EdelEphemeris,
    body: Body,
    target_lon_deg: float,
    start_time: EdelTime,
    end_time: EdelTime,
    tol_seconds: float = 0.5,
    sample_step_days: float = 1.0
) -> Optional[EdelTime]:
    """
    Search for the exact moment (EdelTime) when a body reaches target_lon_deg in [start_time, end_time].
    Target longitude is in degrees [0, 360).
    """
    target = target_lon_deg % 360.0
    tol_days = tol_seconds / 86400.0

    def f_offset(jd: float) -> float:
        t = EdelTime.from_jd(jd)
        pos = ephem.calculate_body(body, t)
        # Angular difference wrapped to [-180, +180]
        diff = (pos.longitude - target + 180.0) % 360.0 - 180.0
        return diff

    # Step through interval to bracket zero crossings
    t_curr = start_time.jd_ut
    t_end = end_time.jd_ut
    f_prev = f_offset(t_curr)

    while t_curr < t_end:
        t_next = min(t_curr + sample_step_days, t_end)
        f_next = f_offset(t_next)

        # Check if crossed zero without crossing the 180 discontinuity
        if f_prev * f_next <= 0.0 and abs(f_next - f_prev) < 180.0:
            # Bracket found
            root_jd = _brent_root(f_offset, t_curr, t_next, tol=tol_days)
            return EdelTime.from_jd(root_jd)

        t_curr = t_next
        f_prev = f_next

    return None

def search_sign_ingress(
    ephem: EdelEphemeris,
    body: Body,
    start_time: EdelTime,
    end_time: EdelTime,
    tol_seconds: float = 0.5
) -> List[Tuple[EdelTime, int]]:
    """
    Find all zodiac sign ingresses within the time window.
    Returns list of tuples: (EdelTime_of_ingress, new_sign_index_0_to_11).
    0 = Aries, 1 = Taurus, ..., 11 = Pisces.
    """
    # Sample step based on body type (Moon needs smaller step ~0.25 day, planets ~1.0 day)
    sample_step = 0.1 if body == Body.MOON else 0.5

    ingresses = []
    t_curr = start_time.jd_ut
    t_end = end_time.jd_ut

    pos_start = ephem.calculate_body(body, start_time)
    sign_curr = int(pos_start.longitude // 30)

    while t_curr < t_end:
        t_next = min(t_curr + sample_step, t_end)
        t_next_time = EdelTime.from_jd(t_next)
        pos_next = ephem.calculate_body(body, t_next_time)
        sign_next = int(pos_next.longitude // 30)

        if sign_next != sign_curr:
            # Body changed sign! Target longitude is the boundary:
            # If moving direct: boundary = sign_next * 30
            # If moving retrograde: boundary = (sign_curr * 30) % 360
            if (pos_next.longitude - pos_start.longitude + 360.0) % 360.0 < 180.0:
                target_lon = (sign_next * 30.0) % 360.0
            else:
                target_lon = (sign_curr * 30.0) % 360.0

            ingress_time = search_transit_time(
                ephem=ephem,
                body=body,
                target_lon_deg=target_lon,
                start_time=EdelTime.from_jd(t_curr),
                end_time=t_next_time,
                tol_seconds=tol_seconds,
                sample_step_days=sample_step
            )
            if ingress_time:
                ingresses.append((ingress_time, sign_next))

        sign_curr = sign_next
        t_curr = t_next

    return ingresses

def search_station(
    ephem: EdelEphemeris,
    body: Body,
    start_time: EdelTime,
    end_time: EdelTime,
    tol_seconds: float = 5.0,
    sample_step_days: float = 0.5
) -> List[Tuple[EdelTime, str]]:
    """
    Find all stationary points (retrograde turn or direct turn) where longitudinal velocity v_lon(t) = 0.
    Returns list of tuples: (EdelTime, 'Direct to Retrograde' or 'Retrograde to Direct').
    """
    tol_days = tol_seconds / 86400.0

    def speed_func(jd: float) -> float:
        t = EdelTime.from_jd(jd)
        pos = ephem.calculate_body(body, t)
        return pos.speed_longitude

    stations = []
    t_curr = start_time.jd_ut
    t_end = end_time.jd_ut
    v_prev = speed_func(t_curr)

    while t_curr < t_end:
        t_next = min(t_curr + sample_step_days, t_end)
        v_next = speed_func(t_next)

        # Check if speed changed sign
        if v_prev * v_next <= 0.0:
            root_jd = _brent_root(speed_func, t_curr, t_next, tol=tol_days)
            event_type = "Direct to Retrograde" if v_prev > 0 else "Retrograde to Direct"
            stations.append((EdelTime.from_jd(root_jd), event_type))

        v_prev = v_next
        t_curr = t_next

    return stations
