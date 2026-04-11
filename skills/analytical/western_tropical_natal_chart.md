---
name: western_tropical_natal_chart
version: "2.0"
category: analytical
risk_tier: T1-autonomous
description: >
  Generate or rectify a Western Tropical natal chart. Use when someone needs
  a standard natal chart, chart rectification (adjusting uncertain birth time),
  or a focused tropical reading without the full Soul Stratigraphy treatment.
  Triggers on: "natal chart", "birth chart", "western tropical", "chart
  rectification", or when birth data is provided with a request for astrological
  analysis. If the request calls for all three systems, use soul_stratigraphy
  instead. Now backed by real Swiss Ephemeris calculations via the ephemeris
  engine.
requires:
  services: []
  tools: [python3, pyswisseph]
  files: [/opt/mythos/skills/analytical/tools/ephemeris.py]
  env_vars: []
inputs:
  required:
    - birth date
    - birth time (or note if unknown)
    - birth location
  optional:
    - name
    - house system preference (default: Placidus)
    - specific questions
    - life events for rectification
outputs:
  files:
    - natal_chart_{name}.md
    - natal_chart_{name}.json
  formats: [.md, .json]
  destinations:
    - conversation or /mnt/user-data/outputs/
---

# Western Tropical Natal Chart

## Purpose

Standard Western Tropical natal chart generation and interpretation. This is
Layer 1 of Soul Stratigraphy as a standalone skill — for when a full tri-field
analysis isn't needed.

## CRITICAL: Use the Ephemeris Engine

**Never fabricate planetary positions.** Always run the computation engine first.

```bash
/opt/mythos/.venv/bin/python3 /opt/mythos/skills/analytical/tools/ephemeris.py natal \
  --year YYYY --month MM --day DD \
  --hour HH --minute MM \
  --lat LATITUDE --lon LONGITUDE \
  --tz TIMEZONE_OFFSET \
  --name "Person Name" \
  --output /tmp/natal_chart.json
```

The engine returns tropical positions, Placidus houses, aspects with orbs,
essential dignities, sect, and element/modality balance. Use the
`western_tropical` section of the output as your data source.

## Pre-Flight Checks

1. Verify birth data: date, time, location all provided.
2. **Run the ephemeris engine** to get real positions.
3. If birth time is uncertain and rectification is requested, gather life
   events (marriage, children, career changes, accidents, moves) with dates.
4. Confirm house system — default Placidus, offer Whole Sign as alternative.

## Process

### Step 1: Calculate Positions

Run the ephemeris engine. It computes:
- Tropical zodiac positions for Sun through Pluto + nodes + South Node
- House cusps (Placidus) and angles (ASC, MC, DSC, IC)
- All major aspects with orbs
- Essential dignities for traditional planets
- Sect (diurnal/nocturnal)
- Element and modality counts

### Step 2: Identify Key Features

From the engine output, identify:
- Chart ruler (lord of Ascendant sign — check `western_tropical.houses.angles.ASC.sign`
  and find which planet rules that sign)
- Stellia (3+ planets in one sign or house — scan planet house assignments)
- T-squares, grand trines, grand crosses, yods (identify from aspect patterns)
- Planets on angles (within 5° of ASC/MC/DSC/IC longitudes)
- Mutual receptions (planet A in planet B's sign and vice versa)

### Step 3: Read Aspects

From `western_tropical.aspects`, prioritize by:
1. Tightest orb first — exact aspects dominate
2. Aspects involving luminaries (Sun, Moon) or angles
3. Aspect patterns (multiple aspects forming geometric shapes)

Note applying vs. separating: if the faster planet's longitude is approaching
the aspect angle, it's applying (strengthening). If past, it's separating (waning).

### Step 4: Interpret

Read the chart in structured layers:
- Core identity: Sun sign, house, aspects
- Emotional nature: Moon sign, house, aspects
- Interface with world: Ascendant, chart ruler
- Mind and communication: Mercury
- Values and relationships: Venus
- Drive and assertion: Mars
- Growth: Jupiter
- Structure and lessons: Saturn
- Generational themes: outer planets
- Karmic axis: nodes
- Dignity assessment: which planets are strong, which are challenged

### Step 5: Rectification (if requested)

If birth time is uncertain and events are provided:
- Run the engine with multiple candidate times
- Check whether major life events align with transits to the angles
- Narrow the time window until ASC and MC align with the known life story
- Present the rectified time with confidence assessment

### Step 6: Format Output

Markdown report with:
- Positions table (planet, sign, degree, house, dignity, retrograde status)
- Aspect list (sorted by orb)
- Key features and patterns
- Interpretation sections

## Validation

- All positions come from ephemeris engine output
- Aspects match the engine's calculated aspects list
- House cusps valid for the given location and time
- Interpretation references actual chart positions, not generic descriptions
- No fabricated degrees

---
_Last updated: 2026-03-01_
_Author: Ka'tuar'el_
_Engine: ephemeris.py v1.0 (pyswisseph/Moshier)_
