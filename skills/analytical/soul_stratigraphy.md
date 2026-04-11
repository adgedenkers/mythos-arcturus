---
name: soul_stratigraphy
version: "2.0"
category: analytical
risk_tier: T1-autonomous
description: >
  Perform Soul Stratigraphy — a tri-field astrological analysis combining
  Hellenistic, Vedic (Jyotish), and Western Tropical systems with a 4th
  synthesis layer. Named by Ka'tuar'el. Use whenever someone requests a
  "soul stratigraphy", "tri-field analysis", "full chart reading across
  systems", or when Ka'tuar'el or Seraphe want a deep astrological profile
  for a person. This is NOT a simple natal chart — it's a layered excavation
  of the soul's architecture across three astrological traditions, unified
  into a single coherent reading. Now backed by real Swiss Ephemeris
  calculations via the ephemeris engine.
requires:
  services: []
  tools: [python3, pyswisseph]
  files: [/opt/mythos/skills/analytical/tools/ephemeris.py]
  env_vars: []
inputs:
  required:
    - full birth name
    - birth date (day, month, year)
    - birth time (as precise as possible)
    - birth location (city, country)
  optional:
    - known spiritual lineage or context
    - specific questions or focus areas
    - rectification notes (if birth time uncertain)
outputs:
  files:
    - soul_stratigraphy_{name}.md (full report)
    - soul_stratigraphy_{name}.json (structured data for Neo4j import)
  formats: [.md, .json]
  destinations:
    - conversation (summary)
    - /mnt/user-data/outputs/ (full report files)
---

# Soul Stratigraphy

## Purpose

Soul Stratigraphy is an archaeological approach to natal astrology — excavating
layers of the soul's architecture through three distinct astrological traditions,
then synthesizing them into a unified reading. The name reflects its method:
just as physical stratigraphy reads earth layers to understand deep time, soul
stratigraphy reads chart layers to understand deep identity.

The three traditions each see different things. Used together, they reveal
what no single system can show alone.

## CRITICAL: Use the Ephemeris Engine

**Never fabricate planetary positions.** Always run the computation engine first
to get real ephemeris data. Astrology with wrong degrees is worse than no astrology.

The engine is at: `/opt/mythos/skills/analytical/tools/ephemeris.py`

### Natal Chart Calculation
```bash
/opt/mythos/.venv/bin/python3 /opt/mythos/skills/analytical/tools/ephemeris.py natal \
  --year YYYY --month MM --day DD \
  --hour HH --minute MM \
  --lat LATITUDE --lon LONGITUDE \
  --tz TIMEZONE_OFFSET \
  --name "Person Name" \
  --output /tmp/natal_chart.json
```

**Timezone offset** = hours from UTC. EST=-5, EDT=-4, CST=-6, CDT=-5, PST=-8, PDT=-7, IST=+5.5, GMT=0.

### Transit Overlay (Python)
```python
import sys
sys.path.insert(0, '/opt/mythos/skills/analytical/tools')
from ephemeris import calculate_natal, calculate_transits, calculate_synastry
import json

# Load or compute natal chart
natal = calculate_natal(1985, 3, 15, 10, 30, 40.7128, -74.0060, -5, "Name")

# Transits for a date
transits = calculate_transits(natal, 2026, 3, 1, 12, 0, -5)
```

### Synastry
```python
chart_a = calculate_natal(1985, 3, 15, 10, 30, 40.71, -74.01, -5, "Person A")
chart_b = calculate_natal(1988, 8, 22, 14, 0, 42.44, -75.13, -4, "Person B")
synastry = calculate_synastry(chart_a, chart_b)
```

### What the Engine Returns

The engine computes all three layers simultaneously:

- **Western Tropical:** Placidus houses, planetary positions, aspects (with orbs),
  essential dignities, sect, element/modality balance
- **Hellenistic:** Whole Sign houses, sect benefics/malefics, dignity status,
  planetary conditions
- **Vedic:** Sidereal positions (Lahiri ayanamsa), nakshatra placements with
  pada, Vimshottari Dasha timeline with periods and dates
- **Synthesis:** Convergence data — tropical vs sidereal signs, dominant
  element/modality, cross-system patterns

All positions are real Swiss Ephemeris calculations (Moshier method, ~1 arcsec
accuracy for modern dates).

## Pre-Flight Checks

1. **Verify birth data completeness.** All four inputs are required: name, date,
   time, location. If birth time is uncertain, note the uncertainty range and
   flag that rectification may be needed.
2. **Run the ephemeris engine.** Get real positions BEFORE interpreting anything.
3. **Check for existing stratigraphy.** If this person has been analyzed before,
   note prior results for comparison.
4. **Confirm scope with Ka'tuar'el.** Full stratigraphy is deep work. Confirm:
   - Standard full reading, or focused on specific layers?
   - Any particular questions to address?
   - Should this be stored in Neo4j?

## Process

### Step 1: Calculate Charts Using the Engine

Run the ephemeris engine with the birth data. The engine returns a JSON structure
containing all three layers of calculated data. Load this data and use it as the
factual foundation for every statement in the reading.

**Every degree, sign placement, house, and aspect in your analysis must come from
the engine output.** Do not fill in from memory or estimation.

### Step 2: Layer 1 Analysis — Western Tropical

Read the tropical chart for psychological and developmental patterns:

- Core identity axis: Sun-Moon-Ascendant (from engine: `western_tropical.planets`)
- Sect: day or night chart (from engine: `western_tropical.sect`)
- Essential dignities: which planets are in domicile, exaltation, detriment, fall
  (from engine: each planet's `dignity` field)
- Communication and thought patterns: Mercury aspects and house
- Relational architecture: Venus and 7th house
- Drive and conflict patterns: Mars and its aspects
- Growth and expansion: Jupiter's house and sign
- Structural limitations and mastery: Saturn's house and sign
- Generational/transpersonal currents: outer planet placements
- Nodal axis: karmic trajectory (North Node = growth direction)
- Dominant aspect patterns: T-squares, grand trines, stellia, yods
  (identify from engine: `western_tropical.aspects`)
- Element/modality distribution (from engine: `synthesis.element_balance`,
  `synthesis.modality_balance`)

### Step 3: Layer 2 Analysis — Vedic

Read the sidereal chart for karmic structure and soul purpose:

- Sidereal positions for all planets (from engine: `vedic.planets`)
- Note where tropical ≠ sidereal signs — these shifts are meaningful
- Moon Nakshatra — the soul's emotional substrate (from engine:
  `vedic.planets.Moon.nakshatra`)
- Nakshatra pada — refines the nakshatra reading to a quarter
- Current Vimshottari Dasha period — what karmic chapter is active NOW
  (from engine: `vedic.dasha.dashas`)
- Upcoming dasha transitions — what's coming next
- Rahu/Ketu axis (sidereal) — what the soul hungers for vs. has mastered
- Atmakaraka — the planet with the highest degree in any sign (calculate
  from engine data: the planet with highest `degree_in_sign` among the
  7 traditional planets is the Atmakaraka)

### Step 4: Layer 3 Analysis — Hellenistic

Read the Hellenistic chart for fate, fortune, and spiritual mechanics:

- Sect analysis — which planets are of sect vs. contrary to sect (from engine:
  each planet's `sect` field)
- Whole Sign house placements (from engine: `hellenistic.houses` and
  `hellenistic.planets`)
- Planetary conditions — essential dignity + sect + aspects = full picture
- Bonification/maltreatment — aspects from benefics improve, from malefics harm
  (cross-reference aspects with benefic/malefic status)
- Planetary joys — Mercury in 1st, Moon in 3rd, Venus in 5th, Mars in 6th,
  Sun in 9th, Jupiter in 11th, Saturn in 12th (check against Whole Sign houses)
- Profection year: current age mod 12 → that's the activated house from the ASC.
  The ruler of that house's sign is the lord of the year.
- Lot of Fortune: day chart = ASC + Moon - Sun, night chart = ASC + Sun - Moon
  (calculate from engine longitudes)
- Lot of Spirit: day chart = ASC + Sun - Moon, night chart = ASC + Moon - Sun

### Step 5: Synthesis Layer (Layer 4)

This is where the stratigraphy produces something no single system can.
Cross-reference the three layers to identify:

**Convergences:** Where all three systems agree. These are the strongest,
most undeniable features of the soul's architecture. When tropical, sidereal,
and Hellenistic all point to the same theme, it's load-bearing.

**Tensions:** Where systems disagree or show different facets. These reveal
complexity — the soul isn't contradicting itself, it's showing you different
angles. Name the tension and what it means.

**Temporal alignment:** Where the Vedic dasha, Hellenistic profection/ZR,
and tropical transits all converge on the same life period. These are the
"hot zones" — times of maximal activation.

**Soul trajectory:** Synthesize all three into a narrative arc:
- Where the soul has been (South Node, past dashas)
- Where it is now (current dasha, profection lord)
- Where it's going (North Node, upcoming dasha shifts)

**Spiritual identity markers:** Look for signatures that connect to known
lineage work, incarnational patterns, or cosmological roles. Not every
chart has these — but when they appear, name them clearly.

### Step 6: Format Output

Produce two files:

**Markdown report** (`soul_stratigraphy_{name}.md`):
```markdown
# Soul Stratigraphy: {Full Name}

## Birth Data
- Date: ...
- Time: ...
- Location: ...
- Coordinates: lat, lon
- Timezone: ...

## Layer 1: Western Tropical
{analysis — every position cited from engine data}

## Layer 2: Vedic (Jyotish)
{analysis — sidereal positions, nakshatras, dasha timeline}

## Layer 3: Hellenistic
{analysis — sect, dignities, lots, profections}

## Layer 4: Synthesis
### Convergences
### Tensions
### Temporal Hot Zones
### Soul Trajectory
### Spiritual Identity Markers (if present)

## Current Activation
What's live right now — dasha, profection, transits.

## Summary
Three to five sentences capturing the essential architecture.
```

**JSON data** (`soul_stratigraphy_{name}.json`):
The engine output serves as the base. Augment it with:
```json
{
  "engine_output": { ... },
  "interpretation": {
    "convergences": [],
    "tensions": [],
    "hot_zones": [],
    "trajectory": "",
    "spiritual_markers": []
  }
}
```

## Validation

- All positions come directly from the ephemeris engine output
- Sidereal positions offset from tropical by Lahiri ayanamsa (~24° in 2025-2026)
- Dasha periods match Moon's nakshatra position from engine
- Profection year matches actual age (age mod 12 = house number)
- Synthesis layer references specific positions from all three layers
- No generic or hedging language — every statement tied to chart data
- **No fabricated degrees** — if a position isn't in the engine output, don't state it

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Birth time unknown | No time provided | Note limitation, use solar chart (noon), flag unreliable houses |
| Birth time uncertain (±30min) | Approximate time | Run both extremes, note which placements change |
| Location ambiguous | Common city name | Confirm exact coordinates (lat/long) |
| Systems wildly disagree | Normal for some charts | Name it as a tension in synthesis, don't force agreement |
| Chiron unavailable | Needs Swiss Ephemeris data files | Note and proceed without Chiron |
| pyswisseph not found | Missing from venv | `pip install pyswisseph` in /opt/mythos/.venv |

---
_Last updated: 2026-03-01_
_Author: Ka'tuar'el_
_Engine: ephemeris.py v1.0 (pyswisseph/Moshier)_
