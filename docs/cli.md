# Command Line Interface (CLI)

The `edel` CLI tool provides direct terminal access to ephemerides, birth chart generators, time diagnostics, event search, and fixed stars.

---

## 1. Subcommands Overview

```text
edel [-h] {chart,time,ephem,events,stars} ...
```

---

## 2. Command: `edel chart`

Generate a complete astrological birth chart in terminal format.

```bash
edel chart [options]
```

### Options:
- `--date`: ISO 8601 UTC date/time (e.g. `2026-08-20T14:30:00`). Defaults to current UTC time.
- `--lat`: Observer latitude in decimal degrees (e.g. `51.5074` for London, `-33.8688` for Sydney). Default: `51.5074`.
- `--lon`: Observer longitude in decimal degrees (e.g. `-0.1278` for London, `151.2093` for Sydney). Default: `-0.1278`.
- `--alt`: Altitude above sea level in meters. Default: `0.0`.
- `--house`: House system name (`Placidus`, `Koch`, `Regiomontanus`, `Campanus`, `Topocentric`, `Porphyry`, `Whole Sign`, `Equal`, `Vehlow Equal`, `Morinus`, `Meridian`, `Alcabitius`). Default: `Placidus`.
- `--sidereal`: Optional Ayanamsha mode (`Lahiri`, `Krishnamurti`, `Fagan-Bradley`, `Raman`, `Yukteshwar`, `True Citra`). Default: `None` (Tropical).

### Example:
```bash
edel chart --date 1980-05-15T08:30:00 --lat 40.7128 --lon -74.0060 --house Placidus
```

---

## 3. Command: `edel ephem`

Query exact coordinates, speeds, distances, and horizontal Az/Alt for any celestial body.

```bash
edel ephem [options]
```

### Options:
- `--body`: Celestial body name (`Sun`, `Moon`, `Mercury`, `Venus`, `Mars`, `Jupiter`, `Saturn`, `Uranus`, `Neptune`, `Pluto`, `Chiron`, `Ceres`, `Pallas`, `Juno`, `Vesta`, `Mean Node`, `True Node`, `Mean Lilith`, `True Lilith`). Default: `Sun`.
- `--date`: ISO 8601 UTC date/time.
- `--lat`: Optional latitude for topocentric Az/Alt.
- `--lon`: Optional longitude for topocentric Az/Alt.

### Example:
```bash
edel ephem --body Mars --date 2026-08-20T21:04:00 --lat 51.5074 --lon -0.1278
```

---

## 4. Command: `edel events`

Search for exact astronomical events (degree transits, sign ingresses, stationary retrograde turns).

```bash
edel events --type {ingress,station,transit} --body <name> --start <iso_date> --end <iso_date> [--deg <deg>]
```

### Examples:
```bash
# 1. Search for upcoming Sun sign ingresses
edel events --type ingress --body Sun --start 2026-01-01 --end 2026-12-31

# 2. Search for Mercury retrograde stationary points
edel events --type station --body Mercury --start 2026-01-01 --end 2026-12-31

# 3. Find when Moon hits 0° Aries (0.0°)
edel events --type transit --body Moon --start 2026-08-01 --end 2026-08-15 --deg 0.0
```

---

## 5. Command: `edel stars`

Calculate fixed star coordinates or list available catalog stars.

```bash
# Calculate specific star
edel stars --name Sirius --date 2026-08-20T21:04:00 --lat 51.5074 --lon -0.1278

# List all catalog stars
edel stars --list
```

---

## 6. Command: `edel time`

Print high-precision time diagnostics (UT1, TT, $\Delta T$, GMST, LMST).

```bash
edel time --date 2026-08-20T21:04:00
```
