# Mythos Astro Events System

## Quick CLI Command

Run this single command to create the table and load all data:

```bash
sudo -u postgres psql -d mythos -f ~/astro_events.sql
```

Or if you've already downloaded the SQL file to Arcturus:

```bash
sudo -u postgres psql -d mythos -f /path/to/astro_events.sql
```

---

## Schema Design

The `astro_events` table is designed for flexibility and queryability:

| Column | Type | Purpose |
|--------|------|---------|
| `event_date` | DATE | When it happens |
| `event_time` | TIME | Exact time (NULL if unknown) |
| `event_type` | VARCHAR | ingress, aspect, station, eclipse, lunation, cazimi, stellium, other |
| `primary_body` | VARCHAR | Main planet/point involved |
| `secondary_body` | VARCHAR | Second planet (for aspects) |
| `aspect_type` | VARCHAR | conjunction, trine, square, sextile, opposition, etc. |
| `sign_1` / `sign_2` | VARCHAR | Zodiac signs involved |
| `degree_1` / `degree_2` | DECIMAL | Degree within sign (0-29.99) |
| `absolute_degree_1/2` | DECIMAL | Full zodiac degree (0-359.99) |
| `direction` | VARCHAR | direct, retrograde, stationary |
| `eclipse_type` | VARCHAR | solar, lunar, annular, total, partial |
| `significance` | VARCHAR | major, significant, normal, minor |
| `notes` | TEXT | Human-readable description |
| `cycle_info` | TEXT | Context about larger cycles |

---

## Useful Queries

### All major events in a date range
```sql
SELECT event_date, event_type, primary_body, secondary_body, aspect_type, notes 
FROM astro_events 
WHERE significance = 'major' 
  AND event_date BETWEEN '2026-01-01' AND '2026-04-30'
ORDER BY event_date;
```

### All ingresses (planets changing signs)
```sql
SELECT event_date, primary_body, sign_1, notes 
FROM astro_events 
WHERE event_type = 'ingress'
ORDER BY event_date;
```

### All retrograde/direct stations
```sql
SELECT event_date, primary_body, sign_1, degree_1, direction, notes 
FROM astro_events 
WHERE event_type = 'station'
ORDER BY event_date;
```

### All aspects involving a specific planet
```sql
SELECT event_date, primary_body, secondary_body, aspect_type, sign_1, sign_2, notes 
FROM astro_events 
WHERE event_type = 'aspect' 
  AND (primary_body = 'Saturn' OR secondary_body = 'Saturn')
ORDER BY event_date;
```

### Events in a specific sign
```sql
SELECT event_date, event_type, primary_body, notes 
FROM astro_events 
WHERE sign_1 = 'Aries' OR sign_2 = 'Aries'
ORDER BY event_date;
```

### All eclipses
```sql
SELECT event_date, eclipse_type, sign_1, degree_1, notes, cycle_info 
FROM astro_events 
WHERE event_type = 'eclipse'
ORDER BY event_date;
```

### Events this week
```sql
SELECT event_date, event_type, primary_body, secondary_body, notes 
FROM astro_events 
WHERE event_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
ORDER BY event_date, event_time;
```

---

## Future Enhancements

Ideas for extending this system:

1. **Automated ingestion**: Script to pull from ephemeris APIs and populate future events
2. **Natal chart correlation**: Join with soul/incarnation data to find transits to natal positions
3. **Event tagging**: Add categories like "financial", "relationship", "spiritual", "health"
4. **Retrograde shadows**: Track pre/post retrograde shadow periods
5. **Aspect orbs**: Store applying vs separating, exact vs approaching
6. **House positions**: If we know a chart, calculate house placements
7. **Telegram alerts**: Bot notification for major upcoming transits

---

## Data Sources

This initial dataset compiled from:
- Cafe Astrology (cafeastrology.com)
- CHANI app key dates
- Astro-Seek ephemeris
- AstroTwins 2026 overview

For ongoing maintenance, consider:
- Swiss Ephemeris API
- Astro.com ephemeris downloads
- PyEphem or Skyfield Python libraries
