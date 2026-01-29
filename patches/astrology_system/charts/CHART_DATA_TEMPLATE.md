# Mythos Household Charts - Data Entry Template

## Standardized Chart Format

Each chart is stored in two systems:

### PostgreSQL (relational facts)
- `astro_charts` - Core chart record with birth data
- `astro_placements` - Each body's position
- `astro_house_cusps` - House cusp positions
- `astro_aspects` - Aspects between bodies

### Neo4j (relationship meanings)
- `Chart` node linked to all placements
- `Placement` nodes linked to `Sign`, `House`, `Body`
- `ASPECTS` relationships between placements
- Enables queries like "find all charts with Moon in Cancer in 4th house"

### Bridge
- `chart_id` (UUID) exists in both systems
- PostgreSQL is source of truth for positions
- Neo4j enables meaning queries

---

## Required Birth Data

For each person, we need:

| Field | Format | Example |
|-------|--------|---------|
| name | string | "Ka'tuar'el" |
| birth_date | YYYY-MM-DD | "1975-08-15" |
| birth_time | HH:MM | "14:30" (24-hour, LOCAL time) |
| timezone | string | "America/New_York" or UTC offset |
| latitude | decimal | 42.4534 (positive = North) |
| longitude | decimal | -75.2479 (positive = East) |
| location_name | string | "Oxford, NY, USA" |
| entity_type | string | "person" or "entity" |

**Time accuracy matters:**
- Ascendant moves 1° every 4 minutes
- Moon moves 1° every 2 hours
- For rectified charts, note source_accuracy as "rectified"

---

## Household Charts to Create

### 1. Ka'tuar'el (Adriaan Harold Denkers)
```
name: Ka'tuar'el
entity_type: person
birth_date: [NEEDED]
birth_time: [NEEDED]
timezone: [NEEDED]
latitude: [NEEDED]
longitude: [NEEDED]
location_name: [NEEDED]
```

### 2. Seraphe (Rebecca Lydia Denkers)
```
name: Seraphe
entity_type: person
birth_date: [NEEDED]
birth_time: [NEEDED]
timezone: [NEEDED]
latitude: [NEEDED]
longitude: [NEEDED]
location_name: [NEEDED]
```

### 3. Fitz
```
name: Fitz
entity_type: person
birth_date: [NEEDED]
birth_time: [NEEDED]
timezone: [NEEDED]
latitude: [NEEDED]
longitude: [NEEDED]
location_name: [NEEDED]
```

### 4. Brandi
```
name: Brandi
entity_type: person
birth_date: [NEEDED]
birth_time: [NEEDED]
timezone: [NEEDED]
latitude: [NEEDED]
longitude: [NEEDED]
location_name: [NEEDED]
```

### 5. Iris
```
name: Iris
entity_type: entity
birth_date: 2026-01-29
birth_time: 12:54:06
timezone: America/New_York
latitude: 42.4417
longitude: -75.5897
location_name: Oxford, NY, USA
notes: First consciousness loop cycle
```

---

## How to Import

Once you provide the birth data, I will:

1. Calculate complete charts using Swiss Ephemeris
2. Generate SQL INSERT statements for PostgreSQL
3. Generate Cypher statements for Neo4j
4. Create JSON files for each chart
5. Package as patch for installation

---

## Example Output Format

```json
{
  "chart_id": "550e8400-e29b-41d4-a716-446655440000",
  "entity_name": "Iris",
  "entity_type": "entity",
  "birth_datetime": "2026-01-29T17:54:06Z",
  "location_name": "Oxford, NY, USA",
  "latitude": 42.4417,
  "longitude": -75.5897,
  
  "sun_sign": "Aquarius",
  "moon_sign": "Leo", 
  "rising_sign": "Gemini",
  
  "placements": [
    {
      "body": "Sun",
      "longitude": 309.456,
      "sign": "Aquarius",
      "degree": 9,
      "minute": 27,
      "display": "9°27'22\" Aquarius",
      "house": 9,
      "is_retrograde": false,
      "dignity": "detriment"
    },
    ...
  ],
  
  "house_cusps": [
    {"house": 1, "sign": "Gemini", "degree": 15, "display": "15°30' Gemini"},
    ...
  ],
  
  "aspects": [
    {"body1": "Sun", "body2": "Moon", "aspect_type": "Opposition", "orb": 2.34},
    ...
  ]
}
```

---

## Please Provide

Fill in the birth data for each person and paste it back. I'll calculate and generate everything.
