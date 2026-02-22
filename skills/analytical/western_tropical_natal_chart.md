---
name: western_tropical_natal_chart
version: "1.0"
category: analytical
risk_tier: T1-autonomous
description: >
  Generate or rectify a Western Tropical natal chart. Use when someone needs
  a standard natal chart, chart rectification (adjusting uncertain birth time),
  or a focused tropical reading without the full Soul Stratigraphy treatment.
  Triggers on: "natal chart", "birth chart", "western tropical", "chart
  rectification", or when birth data is provided with a request for astrological
  analysis. If the request calls for all three systems, use soul_stratigraphy
  instead.
requires:
  services: []
  tools: []
  files: []
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
  formats: [.md]
  destinations:
    - conversation or /mnt/user-data/outputs/
---

# Western Tropical Natal Chart

## Purpose

Standard Western Tropical natal chart generation and interpretation. This is
Layer 1 of Soul Stratigraphy as a standalone skill — for when a full tri-field
analysis isn't needed.

## Pre-Flight Checks

1. Verify birth data: date, time, location all provided.
2. If birth time is uncertain and rectification is requested, gather life
   events (marriage, children, career changes, accidents, moves) with dates.
3. Confirm house system — default Placidus, offer Whole Sign as alternative.

## Process

### Step 1: Calculate Positions

Compute tropical zodiac positions for:
- Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto
- North Node, South Node
- Ascendant, Midheaven, Descendant, IC
- House cusps for all 12 houses

### Step 2: Identify Key Features

- Chart ruler (lord of Ascendant sign)
- Stellia (3+ planets in one sign or house)
- T-squares, grand trines, grand crosses, yods
- Chart shape (bowl, bucket, locomotive, seesaw, splash, bundle)
- Dispositor chain
- Mutual receptions
- Planets on angles (within 5° of ASC/MC/DSC/IC)

### Step 3: Calculate Aspects

Major aspects with standard orbs:
- Conjunction (0°): 8° orb (10° for luminaries)
- Opposition (180°): 8° orb
- Trine (120°): 8° orb
- Square (90°): 7° orb
- Sextile (60°): 6° orb

Note applying vs. separating for each aspect.

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

### Step 5: Rectification (if requested)

If birth time is uncertain and events are provided:
- Test candidate times by checking whether major life events align with
  transits, progressions, and solar arcs to angles
- Narrow the time window until angles (especially MC and ASC) align with
  the known life story
- Present the rectified time with confidence assessment

### Step 6: Format Output

Markdown report with positions table, aspect grid, key features, and
interpretation sections.

## Validation

- All positions mathematically consistent with ephemeris data
- Aspects calculated correctly (within stated orbs)
- House cusps valid for the given location and time
- Interpretation references actual chart positions, not generic descriptions

---

_Last updated: 2026-02-22_
_Author: Ka'tuar'el_
