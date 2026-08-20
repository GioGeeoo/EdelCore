# Installation & Setup Guide

## Requirements
- Python `>= 3.9` (fully compatible with Python 3.9, 3.10, 3.11, 3.12, 3.13, and 3.14).
- Operating Systems: Linux, macOS, Windows (Architecture: x86_64, ARM64 / Apple Silicon).

---

## 1. Install via pip

Install the latest release from PyPI:

```bash
pip install edelcore
```

To install with optional development/testing tools:

```bash
pip install "edelcore[dev]"
```

---

## 2. Install from Source (Development Mode)

Clone the repository and install in editable mode:

```bash
git clone https://github.com/edelcore/edelcore.git
cd edelcore

# Create virtual environment
python -m venv .venv
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install in editable mode
pip install -e ".[dev]"
```

---

## 3. Running Unit Tests

Verify that your local installation passes all mathematical and precision regression tests:

```bash
pytest -v
```

All tests should pass in $< 0.5$ seconds:

```text
tests/test_accuracy_vs_sweph.py::test_full_chart_engine_run PASSED
tests/test_ephem.py::test_ephemeris_sun_moon PASSED
tests/test_houses.py::test_all_house_systems_produce_12_ordered_cusps PASSED
tests/test_sidereal.py::test_ayanamsha_values PASSED
tests/test_stars.py::test_star_positions_at_j2000 PASSED
tests/test_events.py::test_sun_ingress_equinox PASSED
...
============================= 25 passed in 0.35s ==============================
```

---

## 4. Optional: Using NASA JPL Binary SPICE Kernels

EdelCore contains high-accuracy analytical models (VSOP87D and ELP2000) built-in out of the box with zero external files required.

If you require sub-kilometer millimeter accuracy matching JPL DE440/DE441, download any standard `.bsp` file from the [NASA NAIF Server](https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/):

```bash
# Example: Download DE440
curl -O https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440.bsp
```

Pass the path directly when instantiating `EdelEngine`:

```python
from edelcore import EdelEngine

engine = EdelEngine(bsp_path="path/to/de440.bsp")
```
