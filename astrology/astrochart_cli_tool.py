# # import argparse
# # import json
# # import yaml
# # import os
# # import astrochart_cli_engine as chart_engine
# # from astrochart_cli_engine import run_geometry_audit  # ensure this exists at module level in the engine

# # from astrochart_cli_engine import run_geometry_audit

# # def load_input_data(file_path=None, args=None):
# #     if file_path:
# #         with open(file_path, 'r') as f:
# #             if file_path.endswith('.json'):
# #                 return json.load(f)
# #             elif file_path.endswith(('.yaml', '.yml')):
# #                 return yaml.safe_load(f)
# #             else:
# #                 raise ValueError("Input file must be .json, .yaml, or .yml")
# #     else:
# #         # CLI path (not used when -f is provided)
# #         return {
# #             'date': args.date,
# #             'time': args.time,
# #             'city': args.city,
# #             'state': args.state,
# #             'lat': args.lat,
# #             'lon': args.lon
# #         }

# # def save_output(data, filename_prefix):
# #     # Create sub-folder named after prefix
# #     folder = filename_prefix
# #     os.makedirs(folder, exist_ok=True)

# #     # Write each chart component into its own file
# #     for key, value in data.items():
# #         file_name = os.path.join(folder, f"{key}.json")
# #         with open(file_name, 'w') as f:
# #             json.dump(value, f, indent=2)

# #     print(f"✅ Chart saved to folder: {folder}")


# # def main():
# #     parser = argparse.ArgumentParser(description='Generate a natal astrology chart from birth info.')
# #     parser.add_argument('-f', '--file', help='Path to input JSON or YAML file with birth info')
# #     parser.add_argument('-d', '--date', help='Birth date (YYYY-MM-DD)')
# #     parser.add_argument('-t', '--time', help='Birth time (HH:MM)')
# #     parser.add_argument('-c', '--city', help='City of birth')
# #     parser.add_argument('-s', '--state', help='State of birth')
# #     parser.add_argument('--lat', type=float, help='Latitude')
# #     parser.add_argument('--lon', type=float, help='Longitude')
# #     parser.add_argument('--ephe', default='/home/adge/dev/astrology/swisseph', help='Path to Swiss Ephemeris data files')  # currently unused
# #     parser.add_argument('--prefix', default='natal_chart', help='Prefix (folder) for output files')

# #     args = parser.parse_args()
# #     input_data = load_input_data(args.file, args)

# #     # Generate astrology data
# #     chart_data = chart_engine.generate_natal_chart(
# #         name=input_data.get("name", "Unknown"),
# #         dob=input_data["birth"]["date"],
# #         tob=input_data["birth"]["time"],
# #         city=input_data["birth"]["city"],
# #         region=input_data["birth"].get("region", ""),
# #         country=input_data["birth"]["country"],
# #         latitude=input_data["birth"].get("latitude"),
# #         longitude=input_data["birth"].get("longitude"),
# #     )

# #     from astrochart_cli_engine import run_geometry_audit
# #     with open("aspects.json") as f:
# #         aspect_defs = json.load(f)

# #     # enable angles + nodes so audit matches detector policy
# #     run_geometry_audit(chart_data, aspect_defs, include_axes=True, include_nodes=True)

# #     # test audit
# #     from collections import Counter

# #     counts = Counter(a["Aspect"] for a in chart_data["chart_aspects"])
# #     print("\nAspect counts:", dict(sorted(counts.items())))

# #     print("\nTrines present (top 15):")
# #     for a in [x for x in chart_data["chart_aspects"] if x["Aspect"] == "Trine"][:15]:
# #         print(f"  {a['Object 1']}–{a['Object 2']}: orb={a['Orb']}")

# #     # end test audit

# #     # Run geometry audit to verify pattern detection; include in final report
# #     # with open("aspects.json") as f:
# #     #     aspect_defs = json.load(f)


# #     from astrochart_cli_engine import run_geometry_audit

# #     # ...

# #     with open("aspects.json") as f:
# #         aspect_defs = json.load(f)
# #     audit = run_geometry_audit(chart_data, aspect_defs, print_report=True)

# #     save_output(chart_data, args.prefix)
# #     chart_engine.generate_natal_report(
# #         chart_data,
# #         filename=f"{args.prefix}/natal_report.json",
# #         geometry_audit=audit,
# #     )


# # if __name__ == '__main__':
# #     main()


# #!/usr/bin/env python3
# import argparse
# import json
# import yaml
# import os
# from collections import Counter

# import astrochart_cli_engine as chart_engine
# from astrochart_cli_engine import run_geometry_audit


# def load_input_data(file_path=None, args=None):
#     """
#     Load input either from a JSON/YAML file (-f) or from CLI flags.
#     Ensures a consistent structure with a 'birth' sub-dict.
#     """
#     if file_path:
#         with open(file_path, 'r') as f:
#             if file_path.endswith('.json'):
#                 return json.load(f)
#             elif file_path.endswith(('.yaml', '.yml')):
#                 return yaml.safe_load(f)
#             else:
#                 raise ValueError("Input file must be .json, .yaml, or .yml")
#     else:
#         # Build a structure compatible with generate_natal_chart
#         return {
#             "name": "Unknown",
#             "birth": {
#                 "date": args.date,
#                 "time": args.time,
#                 "city": args.city,
#                 "region": args.state or "",
#                 "country": "",              # optional via CLI path
#                 "latitude": args.lat,
#                 "longitude": args.lon,
#             }
#         }


# def save_output(data, filename_prefix):
#     """
#     Create a subfolder named after prefix and write each chart component as its own JSON.
#     """
#     folder = filename_prefix
#     os.makedirs(folder, exist_ok=True)

#     for key, value in data.items():
#         file_name = os.path.join(folder, f"{key}.json")
#         with open(file_name, 'w') as f:
#             json.dump(value, f, indent=2)

#     print(f"✅ Chart saved to folder: {folder}")


# def main():
#     parser = argparse.ArgumentParser(description='Generate a natal astrology chart from birth info.')
#     parser.add_argument('-f', '--file', help='Path to input JSON or YAML file with birth info')
#     parser.add_argument('-d', '--date', help='Birth date (YYYY-MM-DD)')
#     parser.add_argument('-t', '--time', help='Birth time (HH:MM)')
#     parser.add_argument('-c', '--city', help='City of birth')
#     parser.add_argument('-s', '--state', help='State/region of birth')
#     parser.add_argument('--lat', type=float, help='Latitude')
#     parser.add_argument('--lon', type=float, help='Longitude')
#     parser.add_argument('--ephe', default='/home/adge/dev/astrology/swisseph',
#                         help='Path to Swiss Ephemeris data files (currently unused)')
#     parser.add_argument('--prefix', default='natal_chart', help='Prefix (folder) for output files')

#     args = parser.parse_args()
#     input_data = load_input_data(args.file, args)

#     # --- Generate core chart data ---
#     chart_data = chart_engine.generate_natal_chart(
#         name=input_data.get("name", "Unknown"),
#         dob=input_data["birth"]["date"],
#         tob=input_data["birth"]["time"],
#         city=input_data["birth"]["city"],
#         region=input_data["birth"].get("region", ""),
#         country=input_data["birth"].get("country", ""),
#         latitude=input_data["birth"].get("latitude"),
#         longitude=input_data["birth"].get("longitude"),
#     )

#     # --- Load aspect definitions if available (optional) ---
#     aspect_defs = None
#     try:
#         with open("aspects.json") as f:
#             aspect_defs = json.load(f)
#     except FileNotFoundError:
#         pass  # audit can run without it

#     # --- Run geometry audit (enable angles + nodes to match policy) ---
#     audit = run_geometry_audit(
#         chart_data,
#         aspect_defs=aspect_defs,
#         print_report=True,
#         include_axes=True,
#         include_nodes=True,
#     )

#     # --- Quick diagnostics: aspect counts + trines preview ---
#     counts = Counter(a["Aspect"] for a in chart_data.get("chart_aspects", []))
#     print("\nAspect counts:", dict(sorted(counts.items())))

#     trines = [x for x in chart_data.get("chart_aspects", []) if x["Aspect"] == "Trine"]
#     # Sort trines by orb ascending (tightest first), then show top 15
#     trines_sorted = sorted(trines, key=lambda a: float(a.get("Orb", 999)))[:15]
#     print("\nTrines present (top 15):")
#     for a in trines_sorted:
#         print(f"  {a['Object 1']}–{a['Object 2']}: orb={a['Orb']}")

#     # --- Persist outputs ---
#     save_output(chart_data, args.prefix)
#     chart_engine.generate_natal_report(
#         chart_data,
#         filename=f"{args.prefix}/natal_report.json",
#         geometry_audit=audit,
#     )


# if __name__ == '__main__':
#     main()

#!/usr/bin/env python3
import argparse
import json
import yaml
import os
from collections import Counter

import astrochart_cli_engine as chart_engine
from astrochart_cli_engine import run_geometry_audit


def load_input_data(file_path=None, args=None):
    """
    Load input either from a JSON/YAML file (-f) or from CLI flags.
    Ensures a consistent structure with a 'birth' sub-dict.
    """
    if file_path:
        with open(file_path, 'r') as f:
            if file_path.endswith('.json'):
                return json.load(f)
            elif file_path.endswith(('.yaml', '.yml')):
                return yaml.safe_load(f)
            else:
                raise ValueError("Input file must be .json, .yaml, or .yml")
    else:
        # Build a structure compatible with generate_natal_chart
        return {
            "name": "Unknown",
            "birth": {
                "date": args.date,
                "time": args.time,
                "city": args.city,
                "region": args.state or "",
                "country": "",              # optional via CLI path
                "latitude": args.lat,
                "longitude": args.lon,
            }
        }


def save_output(data, filename_prefix):
    """
    Create a subfolder named after prefix and write each chart component as its own JSON.
    """
    folder = filename_prefix
    os.makedirs(folder, exist_ok=True)

    for key, value in data.items():
        file_name = os.path.join(folder, f"{key}.json")
        with open(file_name, 'w') as f:
            json.dump(value, f, indent=2)

    print(f"✅ Chart saved to folder: {folder}")


def main():
    parser = argparse.ArgumentParser(description='Generate a natal astrology chart from birth info.')
    parser.add_argument('-f', '--file', help='Path to input JSON or YAML file with birth info')
    parser.add_argument('-d', '--date', help='Birth date (YYYY-MM-DD)')
    parser.add_argument('-t', '--time', help='Birth time (HH:MM)')
    parser.add_argument('-c', '--city', help='City of birth')
    parser.add_argument('-s', '--state', help='State/region of birth')
    parser.add_argument('--lat', type=float, help='Latitude')
    parser.add_argument('--lon', type=float, help='Longitude')
    parser.add_argument('--ephe', default='/home/adge/dev/astrology/swisseph',
                        help='Path to Swiss Ephemeris data files (currently unused)')
    parser.add_argument('--prefix', default='natal_chart', help='Prefix (folder) for output files')

    args = parser.parse_args()
    input_data = load_input_data(args.file, args)

    # --- Generate core chart data ---
    chart_data = chart_engine.generate_natal_chart(
        name=input_data.get("name", "Unknown"),
        dob=input_data["birth"]["date"],
        tob=input_data["birth"]["time"],
        city=input_data["birth"]["city"],
        region=input_data["birth"].get("region", ""),
        country=input_data["birth"].get("country", ""),
        latitude=input_data["birth"].get("latitude"),
        longitude=input_data["birth"].get("longitude"),
    )

    # --- Load aspect definitions if available (optional) ---
    aspect_defs = None
    try:
        with open("aspects.json") as f:
            aspect_defs = json.load(f)
    except FileNotFoundError:
        pass  # audit can run without it

    # --- Run geometry audit (enable angles + nodes to match policy) ---
    audit = run_geometry_audit(
        chart_data,
        aspect_defs=aspect_defs,
        print_report=True,
        include_axes=True,
        include_nodes=True,
    )

    # --- Quick diagnostics: aspect counts + trines preview ---
    counts = Counter(a["Aspect"] for a in chart_data.get("chart_aspects", []))
    print("\nAspect counts:", dict(sorted(counts.items())))

    trines = [x for x in chart_data.get("chart_aspects", []) if x["Aspect"] == "Trine"]
    # Sort trines by orb ascending (tightest first), then show top 15
    trines_sorted = sorted(trines, key=lambda a: float(a.get("Orb", 999)))[:15]
    print("\nTrines present (top 15):")
    for a in trines_sorted:
        print(f"  {a['Object 1']}–{a['Object 2']}: orb={a['Orb']}")

    # --- Persist outputs ---
    save_output(chart_data, args.prefix)
    chart_engine.generate_natal_report( 
        chart_data,
        filename=f"{args.prefix}/natal_report.json",
        geometry_audit=audit,
    )


if __name__ == '__main__':
    main()
