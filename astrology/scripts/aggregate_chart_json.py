import json
from pathlib import Path

BASE = Path("/opt/mythos/astrology/charts")

def extract_planets(data):

    planets = {}

    if isinstance(data, dict):

        for name, val in data.items():

            if isinstance(val, dict) and "Longitude" in val:
                planets[name.lower()] = val["Longitude"]

    return planets


def extract_houses(data):

    houses = []

    if isinstance(data, dict):

        for i in range(1, 13):

            key = str(i)

            if key in data and "Cusp" in data[key]:
                houses.append(data[key]["Cusp"])

    return houses


def build_chart(chart_dir):

    obj_file = chart_dir / "chart_objects.json"
    house_file = chart_dir / "house_cusps.json"
    aspect_file = chart_dir / "chart_aspects.json"

    if not obj_file.exists():
        return

    objects = json.loads(obj_file.read_text())
    houses_raw = json.loads(house_file.read_text()) if house_file.exists() else {}
    aspects = json.loads(aspect_file.read_text()) if aspect_file.exists() else []

    natal = extract_planets(objects)
    houses = extract_houses(houses_raw)

    out = {
        "name": chart_dir.name,
        "natal": natal,
        "houses": houses,
        "aspects": aspects
    }

    outfile = chart_dir / "react_chart.json"
    outfile.write_text(json.dumps(out, indent=2))

    print("Generated", outfile)


def main():

    for d in BASE.iterdir():
        if d.is_dir():
            build_chart(d)


if __name__ == "__main__":
    main()

