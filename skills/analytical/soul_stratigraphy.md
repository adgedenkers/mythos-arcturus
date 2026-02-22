---
name: soul_stratigraphy
version: "1.0"
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
  into a single coherent reading.
requires:
  services: []
  tools: []
  files: []
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

## Pre-Flight Checks

1. **Verify birth data completeness.** All four inputs are required: name, date,
   time, location. If birth time is uncertain, note the uncertainty range and
   flag that rectification may be needed.

2. **Check for existing stratigraphy.** If this person has been analyzed before,
   note prior results for comparison.

3. **Confirm scope with Ka'tuar'el.** Full stratigraphy is deep work. Confirm:
   - Standard full reading, or focused on specific layers?
   - Any particular questions to address?
   - Should this be stored in Neo4j?

## Process

### Step 1: Calculate Charts in All Three Systems

For the given birth data, compute:

**Layer 1 — Western Tropical:**
- Tropical zodiac positions for all planets (Sun through Pluto + nodes)
- House cusps (Placidus default, Whole Sign as secondary)
- Major aspects (conjunction, opposition, trine, square, sextile)
- Chart ruler, sect light, mutual receptions

**Layer 2 — Vedic (Jyotish):**
- Sidereal zodiac positions (Lahiri ayanamsa)
- Rashi (sign) and Nakshatra placements for all grahas
- Bhava (house) positions using Whole Sign from Ascendant
- Dasha periods — current Mahadasha, Antardasha, Pratyantardasha
- Yogas (notable planetary combinations)
- Atmakaraka (soul significator) and Ishta Devata

**Layer 3 — Hellenistic:**
- Whole Sign houses from Ascendant
- Sect (diurnal or nocturnal chart)
- Sect benefics and malefics
- Domicile lords and their conditions
- Lots (Part of Fortune, Part of Spirit, Part of Eros at minimum)
- Planetary condition: essential dignity, accidental dignity, bonification/maltreatment
- Profection year (current annual lord)
- Zodiacal releasing from Spirit and Fortune

### Step 2: Layer 1 Analysis — Western Tropical

Read the tropical chart for psychological and developmental patterns:
- Core identity axis: Sun-Moon-Ascendant
- Communication and thought patterns: Mercury aspects and house
- Relational architecture: Venus and 7th house
- Drive and conflict patterns: Mars and its aspects
- Growth and expansion: Jupiter's house and sign
- Structural limitations and mastery: Saturn's house and sign
- Generational/transpersonal currents: outer planet placements
- Nodal axis: karmic trajectory (North Node = growth direction)
- Dominant aspect patterns: T-squares, grand trines, stellia, yods
- Chart shape: bowl, bucket, locomotive, splash, etc.

### Step 3: Layer 2 Analysis — Vedic

Read the sidereal chart for karmic structure and soul purpose:
- Ascendant (Lagna) lord condition — the body's story
- Moon Nakshatra — emotional substrate and inner nature
- Atmakaraka — the soul's deepest lesson this incarnation
- D9 (Navamsa) — the soul's true nature and marriage/dharma pattern
- D10 (Dasamsa) — career and public role
- Current dasha period — what karmic chapter is active NOW
- Key yogas — Raja yogas (power), Dhana yogas (wealth),
  Viparita yogas (growth through difficulty)
- Ketu placement — what the soul has already mastered
- Rahu placement — what the soul is hungry for

### Step 4: Layer 3 Analysis — Hellenistic

Read the Hellenistic chart for fate, fortune, and spiritual mechanics:
- Sect analysis — which planets are the most supportive vs. problematic
- Lot of Fortune — material circumstances and body
- Lot of Spirit — will, intellect, and spiritual path
- Annual profection lord — what planet is activated THIS year
- Zodiacal releasing — major life chapters, peak periods, transitions
- Planetary conditions — which planets can deliver on their promises,
  which are impaired
- Fixed stars on angles or key planets (if applicable)

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
- Where the soul has been (Ketu, Lot of Fortune, past dashas)
- Where it is now (current dasha, profection lord, transits)
- Where it's going (Rahu, Lot of Spirit, upcoming ZR shifts)

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

## Layer 1: Western Tropical
{analysis}

## Layer 2: Vedic (Jyotish)
{analysis}

## Layer 3: Hellenistic
{analysis}

## Layer 4: Synthesis
### Convergences
### Tensions
### Temporal Hot Zones
### Soul Trajectory
### Spiritual Identity Markers (if present)

## Current Activation
What's live right now — dasha, profection, transits, ZR period.

## Summary
Three to five sentences capturing the essential architecture.
```

**JSON data** (`soul_stratigraphy_{name}.json`):
```json
{
  "subject": { "name": "", "birth_date": "", "birth_time": "", "birth_location": "" },
  "western_tropical": {
    "sun": { "sign": "", "house": "", "degree": 0 },
    "moon": { "sign": "", "house": "", "degree": 0, "nakshatra": "" },
    "ascendant": { "sign": "", "degree": 0 },
    "planets": {},
    "aspects": [],
    "patterns": []
  },
  "vedic": {
    "lagna": "",
    "moon_nakshatra": "",
    "atmakaraka": "",
    "current_dasha": { "maha": "", "antar": "", "pratyantar": "" },
    "yogas": [],
    "rahu_ketu": {}
  },
  "hellenistic": {
    "sect": "",
    "lot_fortune": { "sign": "", "house": "" },
    "lot_spirit": { "sign": "", "house": "" },
    "profection_year": { "house": 0, "lord": "" },
    "zr_spirit": { "period": "", "subperiod": "" },
    "planetary_conditions": {}
  },
  "synthesis": {
    "convergences": [],
    "tensions": [],
    "hot_zones": [],
    "trajectory": "",
    "spiritual_markers": []
  }
}
```

## Validation

- All three chart layers are internally consistent with the birth data
- Sidereal positions offset from tropical by current ayanamsa (~24°)
- Dasha periods are mathematically correct for the Moon's nakshatra
- Profection year matches actual age
- Synthesis layer references specific positions from all three layers
- No generic or hedging language — every statement tied to chart data

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Birth time unknown | No time provided | Note limitation, use solar chart (noon), flag unreliable houses |
| Birth time uncertain (±30min) | Approximate time | Run both extremes, note which placements change |
| Location ambiguous | Common city name | Confirm exact coordinates (lat/long) |
| Systems wildly disagree | Normal for some charts | Name it as a tension in synthesis, don't force agreement |

---

_Last updated: 2026-02-22_
_Author: Ka'tuar'el_
