"""
Delta T (TT - UT1) Calculation Model
Covers -3000 to +3000 CE based on Espenak & Meeus (2006) and Morrison & Stephenson (2004) polynomial models.
Returns Delta T in seconds.
"""
import math

def calculate_delta_t(year: float, month: int = 1) -> float:
    """
    Calculate Delta T (in seconds) for a given decimal year or year and month.
    Delta T = Terrestrial Time (TT) - Universal Time (UT1).
    Based on Fred Espenak and Jean Meeus (2006), "Five Millennium Canon of Solar Eclipses: -1999 to +3000".
    """
    y = year + (month - 0.5) / 12.0

    if y < -500:
        u = (y - 1820.0) / 100.0
        return -20.0 + 32.0 * (u ** 2)
    elif -500 <= y < 500:
        u = y / 100.0
        return (
            10583.6
            - 1014.41 * u
            + 33.78311 * (u ** 2)
            - 5.952053 * (u ** 3)
            - 0.1798452 * (u ** 4)
            + 0.022174192 * (u ** 5)
            + 0.0090316521 * (u ** 6)
        )
    elif 500 <= y < 1600:
        u = (y - 1000.0) / 100.0
        return (
            1574.2
            - 564.40 * u
            - 19.7413 * (u ** 2)
            + 27.06588 * (u ** 3)
            - 2.443276 * (u ** 4)
            - 0.2500470 * (u ** 5)
            + 0.06797772 * (u ** 6)
        )
    elif 1600 <= y < 1700:
        t = y - 1600.0
        return 120.0 - 0.9808 * t - 0.01532 * (t ** 2) + (t ** 3) / 7129.0
    elif 1700 <= y < 1800:
        t = y - 1700.0
        return (
            8.83
            + 0.1603 * t
            - 0.0059285 * (t ** 2)
            + 0.00013336 * (t ** 3)
            - (t ** 4) / 1174000.0
        )
    elif 1800 <= y < 1860:
        t = y - 1800.0
        return (
            13.72
            - 0.332447 * t
            + 0.0068612 * (t ** 2)
            + 0.0041116 * (t ** 3)
            - 0.00037436 * (t ** 4)
            + 0.0000121272 * (t ** 5)
            - 0.0000001699 * (t ** 6)
            + 0.000000000875 * (t ** 7)
        )
    elif 1860 <= y < 1900:
        t = y - 1860.0
        return (
            7.62
            + 0.5737 * t
            - 0.251754 * (t ** 2)
            + 0.01680668 * (t ** 3)
            - 0.0004473624 * (t ** 4)
            + (t ** 5) / 233174.0
        )
    elif 1900 <= y < 1920:
        t = y - 1900.0
        return (
            -2.79
            + 1.494119 * t
            - 0.0598939 * (t ** 2)
            + 0.0061966 * (t ** 3)
            - 0.000197 * (t ** 4)
        )
    elif 1920 <= y < 1941:
        t = y - 1920.0
        return (
            21.20
            + 0.84493 * t
            - 0.076100 * (t ** 2)
            + 0.0020936 * (t ** 3)
        )
    elif 1941 <= y < 1961:
        t = y - 1941.0
        return (
            29.07
            + 0.407 * t
            - (t ** 2) / 233.0
            + (t ** 3) / 2547.0
        )
    elif 1961 <= y < 1986:
        t = y - 1961.0
        return (
            33.59
            + 0.320 * t
            - 0.005138 * (t ** 2)
            + 0.0000676 * (t ** 3)
        )
    elif 1986 <= y < 2005:
        t = y - 1986.0
        return (
            54.34
            + 0.6389 * t
            - 0.005737 * (t ** 2)
            + 0.00000854 * (t ** 3)
        )
    elif 2005 <= y < 2050:
        t = y - 2000.0
        return (
            62.92
            + 0.32217 * t
            + 0.005589 * (t ** 2)
        )
    elif 2050 <= y < 2150:
        return -20.0 + 32.0 * (((y - 1820.0) / 100.0) ** 2) - 0.5628 * (2150.0 - y)
    else:  # y >= 2150 or y < -3000
        u = (y - 1820.0) / 100.0
        return -20.0 + 32.0 * (u ** 2)
