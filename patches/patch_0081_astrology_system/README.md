# Mythos Astrology System

Complete natal astrology database and calculation system with Swiss Ephemeris integration.

## Overview

This system provides:
- **Natal chart calculation** with Swiss Ephemeris (most accurate)
- **Birth chart storage** in PostgreSQL (charts, placements, houses, aspects)
- **Chart comparisons** (bi-wheel, synastry, composite)
- **Group analysis** (find all Mars in Aries, compare house placements across people)
- **Multiple house systems** (Placidus, Whole Sign, Equal, Koch, etc.)
- **Telegram interface** for quick chart lookups

## Database Schema

### Core Tables

**astro_charts** - Chart metadata
- Birth/event datetime and location
- Person linkage (to `people` table)
- House system and zodiac type

**astro_placements** - Planet positions
- All bodies (planets, asteroids, nodes, angles)
- Sign and house positions
- Retrograde status
- Dignity (domicile, exaltation, detriment, fall, peregrine)

**astro_house_cusps** - House cusps
- All 12 houses for each chart
- Sign positions
- Interception tracking

**astro_aspects** - Natal aspects
- Conjunction, opposition, trine, square, sextile, etc.
- Orb calculations
- Major/minor distinction

**astro_chart_comparisons** - Comparison tracking
- Synastry, composite, davison
- Links between charts

**astro_comparison_aspects** - Inter-chart aspects
- Aspects between different charts
- Harmony scoring

## Calculator Usage

### Single Chart

```bash
# Calculate for a person in people table
python calculator.py --person-id 1

# Or by name
python calculator.py --name "Ka'tuar'el" --person-id 1
```

### Batch Processing

```bash
# Calculate for all people with birth data
python calculator.py --batch-all
```

### View Chart

```bash
# Show chart summary
python calculator.py --show <chart-id>
```

## Telegram Commands

### Basic Commands

```
/chart Ka              - Show Ka'tuar'el's natal chart
/planets Seraphe       - Just planet positions
/houses Fitz           - Just house cusps
/aspects Ka            - Major natal aspects
```

### Comparisons

```
/chart Ka Seraphe      - Compare inner planets (bi-wheel view)
```

### Group Analysis

```
/group_planets Mars Aries     - Find all with Mars in Aries
/group_planets Sun Leo        - Find all Leo Suns
```

## Database Queries

### Find Charts by Planet in Sign

```sql
SELECT * FROM find_charts_by_placement('Mars', 'Aries');
```

### Get All Placements for a Chart

```sql
SELECT * FROM get_chart_placements('chart-uuid-here');
```

### Chart Summary View

```sql
SELECT * FROM astro_chart_summary;
```

### All Placements Across Charts

```sql
SELECT * FROM astro_all_placements
WHERE body_name = 'Mars'
ORDER BY sign;
```

## Supported Bodies

### Planets
- Sun, Moon, Mercury, Venus, Mars
- Jupiter, Saturn
- Uranus, Neptune, Pluto

### Points
- North Node, South Node
- Black Moon Lilith
- Chiron

### Asteroids
- Ceres, Pallas, Juno, Vesta

### Angles
- Ascendant, Descendant
- Midheaven (MC), Imum Coeli (IC)

## Aspects

### Major Aspects
- Conjunction (0°, orb 10°)
- Opposition (180°, orb 8°)
- Trine (120°, orb 8°)
- Square (90°, orb 7°)
- Sextile (60°, orb 6°)

### Minor Aspects
- Quincunx (150°, orb 3°)
- Semi-sextile (30°, orb 2°)

## House Systems

Supported:
- Placidus (default)
- Whole Sign
- Equal House
- Koch
- Campanus
- Regiomontanus
- Porphyry

## Dignity System

Each placement is evaluated for dignity:
- **Domicile** - Planet in its own sign (e.g., Mars in Aries)
- **Exaltation** - Planet in sign of exaltation (e.g., Sun in Aries)
- **Detriment** - Planet opposite its domicile (e.g., Mars in Libra)
- **Fall** - Planet opposite its exaltation (e.g., Sun in Libra)
- **Peregrine** - No essential dignity

## Swiss Ephemeris Files

The system automatically downloads essential ephemeris files on installation:
- Planetary files (seas_18.se1, semo_18.se1, sepl_18.se1)
- Asteroid files (Ceres, Pallas, Juno, Vesta)

Files are stored in `/opt/mythos/ephemeris/`.

## Future Enhancements

### Planned Features
- **SVG chart rendering** - Visual wheel diagrams
- **Transits** - Current planetary positions vs natal
- **Progressions** - Secondary progressions, solar arcs
- **Composite charts** - Relationship midpoints
- **Davison charts** - Midpoint in time/space
- **Tri-wheel support** - Compare 3 charts simultaneously
- **Telegram chart images** - Send visual charts in chat
- **Aspect patterns** - Grand trines, T-squares, yods, etc.
- **Arabic parts** - Part of Fortune, etc.
- **Fixed stars** - Conjunction tracking
- **Harmonics** - Harmonic charts

### Database Expansions
- Transit event tracking
- Progression snapshots over time
- Aspect pattern storage
- Synastry scoring algorithms

## Examples

### Example 1: Basic Chart Lookup

```
User: /chart Ka

Bot: 🌟 NATAL CHART: Ka'tuar'el

Sun          22°30'15" Sagittarius    H1
Moon         15°42'33" Cancer         H8
Mercury      8°20'10" Sagittarius ℞   H1
Venus        10°15'45" Capricorn      H2
Mars         25°18'22" Virgo          H10 👑
Jupiter      12°05'38" Aries          H5
Saturn       28°42'11" Cancer         H8
Uranus       0°30'25" Scorpio         H12
Neptune      12°15'40" Sagittarius    H1
Pluto        10°22'18" Libra          H11
Ascendant    15°10'00" Scorpio        H1
Midheaven    25°45'30" Leo            H10
```

### Example 2: Planet in Sign Search

```
User: /group_planets Mars Aries

Bot: 🔍 Mars in Aries

Seraphe         5°12'30" Aries       H4
Riley           18°45'12" Aries      H1
```

### Example 3: Comparison

```
User: /chart Ka Seraphe

Bot: 🌟 INNER PLANETS COMPARISON
Ka'tuar'el vs Seraphe

Sun        22°30'15" Sagittarius | 26°18'42" Leo
Moon       15°42'33" Cancer      | 10°25'15" Pisces
Mercury    8°20'10" Sagittarius  | 20°12'30" Leo
Venus      10°15'45" Capricorn   | 15°08'22" Leo
Mars       25°18'22" Virgo       | 5°12'30" Aries
```

## Technical Details

### Coordinate System
- Tropical zodiac (default)
- Ecliptic longitude (0-360°)
- Geocentric perspective

### Calculation Method
- Swiss Ephemeris library
- High-precision positions
- JPL ephemeris data

### Time Handling
- Local time input
- UTC storage
- Timezone-aware calculations

## Integration Points

### Links to People Table
- `person_id` foreign key
- Auto-calculate on person creation
- Update on birth data changes

### Neo4j Integration (Future)
- Soul → Chart relationships
- Chart comparison graph
- Synastry pattern storage

---

**Version:** 4.1.0  
**Patch:** 0081  
**Date:** 2026-02-16
