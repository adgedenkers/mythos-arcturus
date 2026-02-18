# astro_position.py
**Astrological Position Calculator — Mythos System**

```
Location:   /opt/mythos/astrology/astro_position.py
Ephemeris:  /opt/mythos/astrology/ephe/
Engine:     Swiss Ephemeris (pyswisseph 2.10.3.2)
Python:     /opt/mythos/.venv/bin/python3  (Python 3.12)
```

---

## Overview

Calculates precise ecliptic positions (degree, minute, second, sign) for any planet, asteroid, or point using the Swiss Ephemeris. Supports geolocation via city/state for birth chart work, including full house cusp and angle calculation.

- Works for any date — ancient history through far future
- Planet naming matches `INCLUDED_OBJECTS` in `astrochart_cli_engine.py`
- JSON output matches `chart_objects.json` structure for `astro_loader.py`
- Houses tagged per planet when location is provided

---

## Quick Start

```bash
# Current sky
astro-a

# Date only
astro-date "1977-11-22"

# Date + time + timezone
astro-date-tz "1977-11-22 14:30" "America/New_York"

# Full birth chart with city/state (planets + houses + angles)
python3 astro_position.py --date "1977-11-22 14:30" --city "Albany" --state "NY" --chart
```

---

## Arguments

| Argument | Description |
|---|---|
| `--date "DATE"` | Date/time string. Required unless `--now` |
| `--now` | Use current UTC time |
| `--tz "TZ"` | Timezone name e.g. `America/New_York`. Default: UTC |
| `--city "CITY"` | City name for geolocation e.g. `Albany` |
| `--state "ST"` | State abbreviation or name e.g. `NY` |
| `--lat FLOAT` | Latitude (manual override, skips geocoding) |
| `--lon FLOAT` | Longitude (manual override, skips geocoding) |
| `--planet NAME` | Planet key, comma list, or `all`. Default: `all` |
| `--chart` | Full chart mode: all planets + houses + angles (requires location) |
| `--houses CHAR` | House system (see below). Default: `P` |
| `--output FORMAT` | `table` (default), `json`, `csv` |
| `--verbose` | Show latitude and distance columns |

### Accepted Date Formats

```
2026-02-20
2026-02-20 14:30
2026-02-20 14:30:00
11/22/1977
11/22/1977 14:30
```

### House Systems

| Code | System |
|---|---|
| `P` | Placidus (default) |
| `K` | Koch |
| `E` | Equal |
| `W` | Whole Sign |
| `C` | Campanus |
| `R` | Regiomontanus |

---

## Usage Examples

### Planets only — no location needed

```bash
# Current sky, all planets
python3 astro_position.py --now --planet all

# Specific date
python3 astro_position.py --date "1977-11-22" --planet all

# Single planet
python3 astro_position.py --now --planet saturn
python3 astro_position.py --date "2026-02-20" --planet chiron

# Comma-separated subset
python3 astro_position.py --date "2026-02-20" --planet "saturn,neptune,chiron"

# With explicit timezone
python3 astro_position.py --date "1977-11-22 14:30" --tz "America/New_York" --planet all

# Historical date
python3 astro_position.py --date "1244-03-16" --planet all
```

### Full birth chart with city/state

```bash
# Table output
python3 astro_position.py --date "1977-11-22 14:30" --city "Albany" --state "NY" --chart

# JSON output (loader-compatible)
python3 astro_position.py --date "1977-11-22 14:30" --city "Albany" --state "NY" --chart --output json

# Different house system
python3 astro_position.py --date "1977-11-22 14:30" --city "Albany" --state "NY" --chart --houses W

# With explicit coordinates instead of geocoding
python3 astro_position.py --date "1977-11-22 14:30" --lat 42.6526 --lon -73.7562 --tz "America/New_York" --chart
```

### Export / pipeline

```bash
# Save JSON for astro_loader
python3 astro_position.py --date "1977-11-22 14:30" --city "Albany" --state "NY" --chart --output json > birth_chart.json

# CSV export
python3 astro_position.py --date "2026-02-20" --planet all --output csv > sky.csv

# Pipe to clipboard
python3 astro_position.py --now --planet all --output json | clip
```

---

## Bash Aliases `(~/.bash_adge)`

| Command | What it does |
|---|---|
| `astro-a` | Current sky, all planets, table output |
| `astro-date "DATE"` | All planets at a specific date |
| `astro-date-tz "DATE TIME" "TZ"` | All planets at date + time + timezone |

Defined as shell **functions** (not aliases) to support argument passing.

```bash
# Definitions in ~/.bash_adge
alias astro-a='/opt/mythos/.venv/bin/python3 /opt/mythos/astrology/astro_position.py --now --planet all'

astro-date() { /opt/mythos/.venv/bin/python3 /opt/mythos/astrology/astro_position.py --date "$1" --planet all; }
astro-date-tz() { /opt/mythos/.venv/bin/python3 /opt/mythos/astrology/astro_position.py --date "$1" --tz "$2" --planet all; }
```

---

## Output Formats

### `--output table` (default)
Human-readable terminal display with Unicode symbols, retrograde markers, house numbers, and formatted positions.

### `--output json`
Structured output compatible with `astro_loader.py`. Full chart JSON includes:
- `planets` — matches `chart_objects.json` (Longitude, Sign, DegMin, Full, Retrograde, Speed, Latitude, Distance, House)
- `house_cusps` — matches `house_cusps.json`
- `chart_points` — matches `chart_points.json` (Ascendant, MC, Descendant, IC, Vertex, ARMC)
- `chart_points_detail` — full position objects for each angle

### `--output csv`
One row per planet with header. Columns: datetime, planet, sign, degree, minute, second, longitude, retrograde, speed, latitude, house.

---

## Supported Planets & Points

| CLI name | Displays as | Symbol |
|---|---|---|
| `sun` | Sun | ☉ |
| `moon` | Moon | ☽ |
| `mercury` | Mercury | ☿ |
| `venus` | Venus | ♀ |
| `mars` | Mars | ♂ |
| `jupiter` | Jupiter | ♃ |
| `saturn` | Saturn | ♄ |
| `uranus` | Uranus | ♅ |
| `neptune` | Neptune | ♆ |
| `pluto` | Pluto | ♇ |
| `chiron` | Chiron | ⚷ |
| `ceres` | Ceres | ⚳ |
| `pallas` | Pallas | ⚴ |
| `juno` | Juno | ⚵ |
| `vesta` | Vesta | ⚶ |
| `eris` | Eris | ⯝ |
| `sedna` | Sedna | ⊕ |
| `lilith` | Lilith | ⚸ |
| `meannode` | Mean Node | ☊ |
| `truenode` / `northnode` | True Node | ☊ |
| `southnode` | South Node | ☋ |
| `all` | All of the above | — |

---

## Ephemeris Files

Stored in `/opt/mythos/astrology/ephe/`. Auto-detected via `_EPHE_CANDIDATES` (same list as `astrochart_cli_engine.py`). Falls back to Moshier built-in if files are missing — Moshier covers Sun through Pluto but **cannot** compute Chiron, Ceres, Pallas, Juno, Vesta, or Eris.

| File | Coverage | Bodies |
|---|---|---|
| `sepl_18.se1` | 1800–2400 | Sun, planets |
| `semo_18.se1` | 1800–2400 | Moon (high precision) |
| `seas_18.se1` | 1800–2400 | Chiron, Ceres, Pallas, Juno, Vesta |
| `ast136/s136199s.se1` | 600yr | Eris |

### Re-downloading ephemeris files

```bash
cd /opt/mythos/astrology/ephe
wget https://github.com/aloistr/swisseph/raw/master/ephe/seas_18.se1
wget https://github.com/aloistr/swisseph/raw/master/ephe/sepl_18.se1
wget https://github.com/aloistr/swisseph/raw/master/ephe/semo_18.se1

mkdir -p ast136 && cd ast136
wget "https://www.dropbox.com/scl/fo/y3naz62gy6f6qfrhquu7u/h/all_ast/ast136/s136199s.se1?rlkey=ejltdhb262zglm7eo6yfj2940&dl=1" -O s136199s.se1
```

---

## Dependencies

All installed in `/opt/mythos/.venv/`.

```bash
# Already installed
pip install pyswisseph pytz

# Required for --city/--state geolocation
pip install geopy timezonefinder
```

To check:
```bash
/opt/mythos/.venv/bin/pip list | grep -E "pyswisseph|geopy|timezonefinder"
```

---

## Mythos Integration

### JSON → `astro_loader.py`
`--output json` with `--chart` produces a superset of what the loader expects. The `planets` block maps directly to `insert_objects()`. The `house_cusps` block maps to `insert_house_cusps()`. The `chart_points` block maps to `insert_points()`.

### Relation to `astrochart_cli_engine.py`
- Planet names and display labels match `INCLUDED_OBJECTS` in the engine
- Mean Node / True Node / South Node naming matches engine and DB schema
- Ephemeris path candidates are identical — both scripts find the same files
- `astro_position.py` is a standalone quick-lookup and data-extract tool; the engine generates full natal charts with aspects, dignities, patterns, etc.

---

## Related Files

```
/opt/mythos/astrology/
├── astro_position.py          ← this script
├── astrochart_cli_engine.py   ← full natal chart engine
├── astro_loader.py            ← loads chart JSON into PostgreSQL
├── astro_report.py            ← family comparison CSV generator
├── astrochart_cli_tool.py     ← CLI wrapper for the engine
├── ephe/                      ← Swiss Ephemeris data files
├── charts/                    ← generated chart output
└── reports/                   ← generated report output
```

---

*Mythos System · Arcturus · Ka'tuar'el*
