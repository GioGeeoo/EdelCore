"""
EdelCore CLI Interface (`edel`).
Allows command-line chart generation, ephemeris querying, time conversions, and event searching.
"""
import argparse
import sys
from datetime import datetime, timezone
from edelcore import EdelEngine, EdelTime, Body, HouseSystem, AyanamshaMode

def parse_args():
    parser = argparse.ArgumentParser(
        prog="edel",
        description="EdelCore: High-precision astronomical and astrological computation engine."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: chart
    chart_parser = subparsers.add_parser("chart", help="Calculate an astrological chart")
    chart_parser.add_argument("--date", type=str, required=False, help="ISO format datetime (e.g. 2026-08-20T12:00:00). Defaults to UTC now.")
    chart_parser.add_argument("--lat", type=float, default=51.5074, help="Observer latitude in decimal degrees (default: 51.5074 London)")
    chart_parser.add_argument("--lon", type=float, default=-0.1278, help="Observer longitude in decimal degrees (default: -0.1278 London)")
    chart_parser.add_argument("--alt", type=float, default=0.0, help="Observer altitude in meters (default: 0.0)")
    chart_parser.add_argument("--house", type=str, default="Placidus", choices=[h.value for h in HouseSystem], help="House system")
    chart_parser.add_argument("--sidereal", type=str, default=None, choices=[m.value for m in AyanamshaMode], help="Sidereal ayanamsha mode")

    # Command: time
    time_parser = subparsers.add_parser("time", help="Time subsystem diagnostics (JD, Delta T, GMST)")
    time_parser.add_argument("--date", type=str, required=False, help="ISO format datetime")

    # Command: ephem
    ephem_parser = subparsers.add_parser("ephem", help="Query position and horizontal Az/Alt of celestial bodies")
    ephem_parser.add_argument("--date", type=str, required=False, help="ISO format datetime")
    ephem_parser.add_argument("--body", type=str, default="Sun", help="Celestial body name")
    ephem_parser.add_argument("--lat", type=float, default=None, help="Observer latitude for Az/Alt")
    ephem_parser.add_argument("--lon", type=float, default=None, help="Observer longitude for Az/Alt")

    # Command: events
    events_parser = subparsers.add_parser("events", help="Search astronomical events (ingress, station, degree crossings)")
    events_parser.add_argument("--type", type=str, required=True, choices=["ingress", "station", "transit"], help="Event search type")
    events_parser.add_argument("--body", type=str, default="Sun", help="Celestial body name")
    events_parser.add_argument("--start", type=str, required=True, help="Start ISO datetime")
    events_parser.add_argument("--end", type=str, required=True, help="End ISO datetime")
    events_parser.add_argument("--deg", type=float, default=0.0, help="Target degree for transit search")

    # Command: stars
    stars_parser = subparsers.add_parser("stars", help="Calculate fixed star coordinates or list star catalog")
    stars_parser.add_argument("--name", type=str, default=None, help="Star name (e.g. Sirius, Regulus, Spica, Algol)")
    stars_parser.add_argument("--list", action="store_true", help="List all cataloged fixed stars")
    stars_parser.add_argument("--date", type=str, required=False, help="ISO format datetime")
    stars_parser.add_argument("--lat", type=float, default=None, help="Observer latitude for Az/Alt")
    stars_parser.add_argument("--lon", type=float, default=None, help="Observer longitude for Az/Alt")

    return parser.parse_args()

def main():
    args = parse_args()
    if not args.command:
        # Default chart for current moment
        args.command = "chart"
        args.date = None
        args.lat = 51.5074
        args.lon = -0.1278
        args.alt = 0.0
        args.house = "Placidus"
        args.sidereal = None

    if getattr(args, "date", None):
        try:
            dt = datetime.fromisoformat(args.date)
        except Exception:
            print(f"Error parsing date string: {args.date}", file=sys.stderr)
            sys.exit(1)
    else:
        dt = datetime.now(timezone.utc).replace(tzinfo=None)

    engine = EdelEngine()

    if args.command == "chart":
        chart = engine.calculate_chart(
            dt_or_time=dt,
            lat_deg=args.lat,
            lon_deg=args.lon,
            alt_meters=args.alt,
            house_system=args.house,
            sidereal_mode=args.sidereal
        )
        print(chart.summary())

    elif args.command == "time":
        t = EdelTime.from_datetime(dt)
        print(f"UTC Date/Time: {dt.isoformat()}")
        print(f"Julian Day (UT1): {t.jd_ut:.8f}")
        print(f"Julian Day (TT):  {t.jd_tt:.8f}")
        print(f"Delta T (TT-UT1): {t.delta_t:.3f} seconds")
        print(f"GMST:             {t.gmst():.6f} deg ({t.gmst()/15.0:.4f} hours)")

    elif args.command == "ephem":
        body_name = args.body.title()
        try:
            body = Body(body_name)
        except ValueError:
            print(f"Unknown body: {body_name}. Available bodies: {[b.value for b in Body]}")
            sys.exit(1)

        t = EdelTime.from_datetime(dt)
        pos = engine.ephemeris.calculate_body(body, t, lat_deg=args.lat, lon_deg=args.lon)
        print(f"=== {pos.body.value} Position at {dt.isoformat()} UT ===")
        print(f"Ecliptic Longitude: {pos.longitude:.6f} deg")
        print(f"Ecliptic Latitude:  {pos.latitude:.6f} deg")
        print(f"Distance:           {pos.distance:.8f} AU")
        print(f"Longitude Speed:    {pos.speed_longitude:+.6f} deg / day {'(Retrograde)' if pos.is_retrograde else '(Direct)'}")
        print(f"Right Ascension:    {pos.ra:.6f} deg")
        print(f"Declination:        {pos.dec:.6f} deg")

        if args.lat is not None and args.lon is not None:
            hz = engine.calculate_horizontal(body, t, lat_deg=args.lat, lon_deg=args.lon)
            print(f"--- Topocentric Horizontal Coordinates ---")
            print(f"Azimuth (from North): {hz.azimuth:.4f} deg")
            print(f"True Altitude:        {hz.true_altitude:.4f} deg")
            print(f"Apparent Altitude:    {hz.apparent_altitude:.4f} deg (Refraction: {hz.refraction:.2f}')")

    elif args.command == "events":
        body_name = args.body.title()
        try:
            body = Body(body_name)
        except ValueError:
            print(f"Unknown body: {body_name}. Available bodies: {[b.value for b in Body]}")
            sys.exit(1)

        dt_start = datetime.fromisoformat(args.start)
        dt_end = datetime.fromisoformat(args.end)
        t_start = EdelTime.from_datetime(dt_start)
        t_end = EdelTime.from_datetime(dt_end)

        zodiac_names = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

        if args.type == "ingress":
            ingresses = engine.search_sign_ingresses(body, t_start, t_end)
            print(f"=== Zodiac Ingresses for {body.value} between {args.start} and {args.end} ===")
            if not ingresses:
                print("No sign ingresses found in this range.")
            for t_ing, sign_idx in ingresses:
                y, m, d, h, mn, s = t_ing.calendar
                print(f"-> Enters {zodiac_names[sign_idx]} at {y:04d}-{m:02d}-{d:02d} {h:02d}:{mn:02d}:{s:04.1f} UT (JD {t_ing.jd_ut:.6f})")

        elif args.type == "station":
            stations = engine.search_stations(body, t_start, t_end)
            print(f"=== Stationary Turning Points for {body.value} between {args.start} and {args.end} ===")
            if not stations:
                print("No stationary points found in this range.")
            for t_st, st_type in stations:
                y, m, d, h, mn, s = t_st.calendar
                pos = engine.ephemeris.calculate_body(body, t_st)
                print(f"-> Station ({st_type}) at {y:04d}-{m:02d}-{d:02d} {h:02d}:{mn:02d}:{s:04.1f} UT (Lon: {pos.longitude:.4f} deg)")

        elif args.type == "transit":
            t_cross = engine.search_transit(body, args.deg, t_start, t_end)
            print(f"=== Longitude {args.deg} deg Transit for {body.value} ===")
            if t_cross:
                y, m, d, h, mn, s = t_cross.calendar
                print(f"-> Reaches {args.deg} deg at {y:04d}-{m:02d}-{d:02d} {h:02d}:{mn:02d}:{s:04.1f} UT (JD {t_cross.jd_ut:.6f})")
            else:
                print(f"Did not reach {args.deg} deg in this range.")

    elif args.command == "stars":
        if args.list or not args.name:
            print("=== Cataloged Fixed Stars in EdelCore ===")
            from edelcore.ephem.stars import STAR_CATALOG
            print(f"{'Star Name':<14} {'Traditional Designation':<35} {'Constellation':<16} {'Vmag'}")
            print("-" * 72)
            for k, data in STAR_CATALOG.items():
                print(f"{data.name:<14} {data.traditional_name:<35} {data.constellation:<16} {data.vmag:>+5.2f}")
        else:
            try:
                star = engine.calculate_star(args.name, dt, lat_deg=args.lat, lon_deg=args.lon)
                print(f"=== Fixed Star: {star.name} ({star.traditional_name}) at {dt.isoformat()} UT ===")
                print(f"Constellation:     {star.constellation} (Visual Mag: {star.vmag})")
                print(f"Ecliptic Longitude: {star.longitude:.6f} deg")
                print(f"Ecliptic Latitude:  {star.latitude:.6f} deg")
                print(f"Right Ascension:    {star.ra:.6f} deg")
                print(f"Declination:        {star.dec:.6f} deg")
                if star.azimuth is not None and star.altitude is not None:
                    print(f"--- Topocentric Horizontal Coordinates ---")
                    print(f"Azimuth (from North): {star.azimuth:.4f} deg")
                    print(f"True Altitude:        {star.altitude:.4f} deg")
                    print(f"Apparent Altitude:    {star.apparent_altitude:.4f} deg")
            except KeyError as e:
                print(e, file=sys.stderr)
                sys.exit(1)

if __name__ == "__main__":
    main()
