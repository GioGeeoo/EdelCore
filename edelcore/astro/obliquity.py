"""
IAU Obliquity of the Ecliptic.
Implements IAU 2006 / Laskar (1986) formulas for mean and true obliquity.
"""
import math

def mean_obliquity_iau2006(t_centuries: float) -> float:
    """
    Calculate Mean Obliquity of the Ecliptic (eps_0) in degrees for Julian centuries T since J2000.0.
    Based on IAU 2006 precession-nutation model (Capitaine et al. 2003 / Hilton et al. 2006).
    eps_0 = 84381.406 - 46.836769*T - 0.0001831*T^2 + 0.00200340*T^3 - 0.000000576*T^4 - 0.0000000434*T^5 (arcseconds)
    """
    t = t_centuries
    eps_arcsec = (
        84381.406
        - 46.836769 * t
        - 0.0001831 * (t ** 2)
        + 0.00200340 * (t ** 3)
        - 0.000000576 * (t ** 4)
        - 0.0000000434 * (t ** 5)
    )
    return eps_arcsec / 3600.0

def true_obliquity(t_centuries: float, delta_eps_deg: float) -> float:
    """
    Calculate True Obliquity of the Ecliptic: eps = eps_0 + delta_eps.
    """
    return mean_obliquity_iau2006(t_centuries) + delta_eps_deg
