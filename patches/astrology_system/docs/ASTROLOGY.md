# Mythos Astrology System - Data Architecture

## Design Philosophy

**PostgreSQL** holds the *facts* - precise positional data, timestamps, calculations.
**Neo4j** holds the *meanings* - relationships, influences, interpretations, patterns.

A chart exists in both systems:
- PostgreSQL: "Mars is at 15°42'33" Aries in House 7"
- Neo4j: "Mars ASPECTS Venus with orb 2.3°, Mars RULES Aries, Mars IN_HOUSE 7th which GOVERNS partnerships"

The **chart_id** (UUID) bridges both systems.

---

## PostgreSQL Schema: The Facts

### What PostgreSQL Stores:
- Precise positions (degrees, minutes, seconds)
- Timestamps (birth times, transit times, event times)
- Calculated values (house cusps, aspect orbs)
- Ephemeris data (planetary positions over time)
- Chart metadata (who, when, where)

### Why PostgreSQL:
- Precise numeric calculations
- Time-series queries ("where was Mars on X date")
- Aggregations ("how many times did Saturn conjunct my Sun")
- Relational integrity (charts have placements have aspects)

---

## Neo4j Schema: The Meanings

### What Neo4j Stores:
- Sign rulerships and dignities
- Aspect interpretations
- House themes and life areas
- Planetary archetypes and keywords
- How placements relate to each other
- How transits activate natal positions
- Pattern recognition (stelliums, grand trines, T-squares)

### Why Neo4j:
- Natural relationship traversal
- Pattern matching ("find all fire grand trines")
- Meaning propagation (Mars in Aries → double fire energy)
- Interpretive synthesis

---

## The Bridge: chart_id

Every chart has a UUID that exists in both systems:

```
PostgreSQL: charts.id = 'abc-123'
Neo4j: (c:Chart {chart_id: 'abc-123'})
```

When querying a chart:
1. Get precise positions from PostgreSQL
2. Get interpretive context from Neo4j
3. Synthesize for human-readable output

---

## Celestial Bodies Tracked

### Luminaries
- Sun, Moon

### Classical Planets  
- Mercury, Venus, Mars, Jupiter, Saturn

### Modern Planets
- Uranus, Neptune, Pluto

### Dwarf Planets
- Ceres, Eris, Makemake, Haumea, Sedna, Quaoar, Orcus, Gonggong, Varuna, Ixion

### Major Asteroids
- Chiron, Pallas, Juno, Vesta, Hygiea, Psyche, Eros

### Centaurs
- Pholus, Nessus, Chariklo, Asbolus

### Lunar Points
- North Node (True), North Node (Mean)
- South Node (True), South Node (Mean)  
- Black Moon Lilith (True), Black Moon Lilith (Mean), Black Moon Lilith (Oscillating)
- Priapus (opposite Lilith)

### Calculated Points
- Part of Fortune, Part of Spirit
- Vertex, Anti-Vertex
- East Point
- Equatorial Ascendant

### Angles
- Ascendant (ASC), Midheaven (MC), Descendant (DSC), Imum Coeli (IC)

### Fixed Stars (major - within 1° orb for conjunctions)
- Regulus, Spica, Algol, Antares, Aldebaran, Fomalhaut, Sirius, Vega, Arcturus, Polaris, Betelgeuse, Rigel, Procyon, Capella, Deneb

### Arabic Parts/Lots
- Part of Fortune (Fortuna)
- Part of Spirit
- Part of Eros
- Part of Marriage
- Part of Death
- Part of Karma

---

## Aspect Types Tracked

### Major Aspects (Ptolemaic)
- Conjunction (0°) - orb 8-10°
- Opposition (180°) - orb 8°
- Trine (120°) - orb 8°
- Square (90°) - orb 7°
- Sextile (60°) - orb 6°

### Minor Aspects
- Semi-sextile (30°) - orb 2°
- Quincunx/Inconjunct (150°) - orb 3°
- Semi-square (45°) - orb 2°
- Sesquiquadrate (135°) - orb 2°
- Quintile (72°) - orb 2°
- Bi-quintile (144°) - orb 2°

### Rare/Esoteric Aspects
- Septile (51.43°) - orb 1°
- Novile (40°) - orb 1°
- Decile (36°) - orb 1°

---

## House Systems Supported

- Placidus (default)
- Whole Sign
- Equal House
- Koch
- Campanus
- Regiomontanus
- Porphyry
- Morinus
- Topocentric

Each chart stores which house system was used; house cusps stored accordingly.

---

## File Structure

```
/opt/mythos/astrology/
├── schema/
│   ├── postgres_schema.sql      # Full PostgreSQL schema
│   ├── neo4j_schema.cypher      # Neo4j constraints and seed data
│   └── seed_data/
│       ├── signs.json           # Zodiac sign meanings
│       ├── planets.json         # Planetary archetypes
│       ├── houses.json          # House meanings
│       ├── aspects.json         # Aspect interpretations
│       └── dignities.json       # Rulerships, exaltations, etc.
├── ephemeris/
│   └── update_ephemeris.py      # Daily ephemeris updater
├── charts/
│   └── chart_calculator.py      # Calculate charts from birth data
└── ASTROLOGY.md                 # This document
```
