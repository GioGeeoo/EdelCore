"""
Celestial Body Enumerations and Constants for EdelCore.
"""
from enum import Enum

class Body(Enum):
    SUN = "Sun"
    MOON = "Moon"
    MERCURY = "Mercury"
    VENUS = "Venus"
    MARS = "Mars"
    JUPITER = "Jupiter"
    SATURN = "Saturn"
    URANUS = "Uranus"
    NEPTUNE = "Neptune"
    PLUTO = "Pluto"
    # Small Bodies / Asteroids / Centaurs
    CHIRON = "Chiron"
    CERES = "Ceres"
    PALLAS = "Pallas"
    JUNO = "Juno"
    VESTA = "Vesta"
    # Lunar Points
    MEAN_NODE = "Mean Node"              # Rahu (North Node)
    TRUE_NODE = "True Node"              # Osculating True North Node
    MEAN_SOUTH_NODE = "Mean South Node"  # Ketu
    TRUE_SOUTH_NODE = "True South Node"  # True Ketu
    MEAN_LILITH = "Mean Lilith"          # Mean Black Moon / Lunar Apogee
    TRUE_LILITH = "True Lilith"          # Osculating True Lilith

# SPICE / NAIF ID mappings for JPL Ephemeris kernels
NAIF_ID = {
    Body.SUN: 10,
    Body.MOON: 301,
    Body.MERCURY: 199,
    Body.VENUS: 299,
    Body.MARS: 499,
    Body.JUPITER: 5,     # Jupiter Barycenter
    Body.SATURN: 6,      # Saturn Barycenter
    Body.URANUS: 7,      # Uranus Barycenter
    Body.NEPTUNE: 8,     # Neptune Barycenter
    Body.PLUTO: 9,       # Pluto Barycenter
    Body.CHIRON: 2002060, # Minor Planet 2060 Chiron
    Body.CERES: 2000001,  # 1 Ceres
    Body.PALLAS: 2000002, # 2 Pallas
    Body.JUNO: 2000003,   # 3 Juno
    Body.VESTA: 2000004,  # 4 Vesta
}

# Standard astrological planet order
STANDARD_PLANETS = [
    Body.SUN,
    Body.MOON,
    Body.MERCURY,
    Body.VENUS,
    Body.MARS,
    Body.JUPITER,
    Body.SATURN,
    Body.URANUS,
    Body.NEPTUNE,
    Body.PLUTO,
    Body.CHIRON,
    Body.CERES,
    Body.PALLAS,
    Body.JUNO,
    Body.VESTA,
    Body.MEAN_NODE,
    Body.TRUE_NODE,
    Body.MEAN_LILITH,
    Body.TRUE_LILITH,
]

STANDARD_ASTEROIDS = [
    Body.CHIRON,
    Body.CERES,
    Body.PALLAS,
    Body.JUNO,
    Body.VESTA,
]
