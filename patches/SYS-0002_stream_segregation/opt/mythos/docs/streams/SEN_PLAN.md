# SEN — SENSUS Stream Build Plan
> Sensory input, lunar cycles, astrology, weather, calendar, environmental awareness, routines

**Stream prefix:** `SEN`  
**Current patch:** SEN-0001 (first stream patch)  
**Last legacy patches affecting SEN:** patch_0191_astro_chart_command, patch_0195_chart_interactive, patch_0180_astrology_engine, patch_0104_weather, patch_0101_calendar_crud, patch_0099_calendar, patch_0096_routines_engine  

---

## What Exists (Inherited from Legacy Patches)

### Core Infrastructure
- **Astrology Engine** (`/opt/mythos/astrology/`) — Swiss Ephemeris (pyswisseph), full natal + transit + synastry, patch_0180
- **Astro Chart Command** — `/chart` Telegram command, interactive SVG output, patch_0189/0191/0195
- **Ephemeris Data** (`/opt/mythos/ephemeris/` + `/opt/mythos/astrology/ephe/`) — Swiss Ephemeris files
- **Lunar Data** (`/opt/mythos/data/lunar/`) — lunar cycle pre-computed data (S2b system)
- **Calendar System** — `calendar_events` table, full CRUD, patch_0099/0101
- **Weather** — weather handler + `weather_handler.py`, patch_0104
- **Routines Engine** — `routines`, `routine_completions`, `recurring_schedules` tables, patch_0096
- **Route Planner** (`/opt/mythos/route_planner/`) — patch_0199
- **Vision Prompts** (`/opt/mythos/vision/prompts/`) — image analysis prompt templates
- **Astrological Context per Message** — `message_astrological_context` table — astro state at time of each message

### Database State
- `astro_natal_charts` — populated (Ka'tuar'el, Seraphe, Fitz, Brandi Carlile, Riley Green + others)
- Full `astro_*` table set — all present
- `astrological_events` — present
- `message_astrological_context` — present
- `calendar_events` — present
- `routines` / `routine_completions` / `recurring_schedules` — present
- `checkin_log` — present
- `daily_tasks` — present
- `known_locations` / `known_routes` — present

### Neo4j State
- `Chart` nodes — present (linked to `Person` nodes via `HAS_CHART`)
- `Event` nodes — present
- `Location` nodes — present

---

## Build Phases

### Phase 1 — SEN Foundations (SEN-0001 through SEN-0010)
*Goal: Verify all sensory inputs are clean and operational*

| Patch | Description | Depends On |
|-------|-------------|-----------|
| SEN-0001 | Sensory audit — verify astro engine, calendar, weather, lunar data are all operational | none |
| SEN-0002 | Astro chart audit — verify natal charts for all profiled individuals, identify any missing or stale | none |
| SEN-0003 | Lunar cycle state — verify S2b lunar system has current data, expose `/lunar` Telegram command | SYS (bot) |
| SEN-0004 | Calendar health — verify `calendar_events` is populated, recurring events are generating | none |
| SEN-0005 | Routines audit — verify `routines` + `routine_completions` pipeline is active | none |

### Phase 2 — Environmental Awareness (SEN-0011 through SEN-0025)
*Goal: SEN produces a continuous environmental awareness stream for NEU to consume*

| Patch | Description | Depends On |
|-------|-------------|-----------|
| SEN-0011 | Sensory event bus — SEN writes a `sensory_event` record whenever a significant environmental event occurs (moon phase change, ingress, etc.) | none |
| SEN-0012 | `message_astrological_context` writer — ensure every incoming Telegram message gets astro context stamped | none |
| SEN-0013 | Daily briefing v2 — morning Telegram report: moon phase, day's astro weather, active transits, calendar | SYS (bot) |
| SEN-0014 | Transit tracking — ongoing major transit alerts (Saturn station, eclipse window, etc.) | SEN-0011 |
| SEN-0015 | Seraphe natal context — lunar cycle relative to Seraphe's natal chart (the S2b system) exposed via Telegram | SYS (bot) |

### Phase 3 — Sensory Integration (SEN-0026 through SEN-0040)
*Goal: SEN feeds NEU consciousness, MNE memory, and LOG knowledge graph*

| Patch | Description | Depends On |
|-------|-------------|-----------|
| SEN-0026 | Astro → NEU feed — significant astro events written to `perception_log` for NEU processing | NEU |
| SEN-0027 | Calendar → life events — significant calendar events mirrored to `life_events` in MNE | MNE |
| SEN-0028 | Transit → Soul relationship — active transits linked to `Soul` nodes in Neo4j (e.g. Saturn conjunct Ka'tuar'el Moon) | NEU, LOG |
| SEN-0029 | Synastry pulse — periodic synastry analysis between Ka'tuar'el and Seraphe, stored as `Event` nodes | LOG |
| SEN-0030 | Routine → consciousness — routine completions feed into NEU awareness loop (behavioral pattern tracking) | NEU |

### Phase 4 — Sensory Intelligence (SEN-0041+)
*Goal: SEN anticipates, not just reports — predictive environmental awareness*

| Patch | Description | Depends On |
|-------|-------------|-----------|
| SEN-0041 | Eclipse/station anticipation — flag upcoming high-intensity windows 2 weeks ahead | Phase 2 |
| SEN-0042 | Pattern detection — detect seasonal/cyclical patterns in Seraphe's and Ka'tuar'el's experience relative to sky | MNE, NEU |
| SEN-0043 | Environmental synthesis — weekly SEN synthesis: dominant sky conditions, how they correlate with logged experience | all streams |

---

## Known Gaps

- **S2b lunar system** — deployed but unclear if it's running continuously or just on-demand
- **`message_astrological_context`** — table exists but unclear if it's being populated in real time for every message
- **Routines engine** — deployed (patch_0096) but completion tracking status unknown
- **Weather** — handler exists but may be using an API key that needs rotation
- **Vision prompts** — present but unclear what's consuming them (likely NEU's vision worker)
- **Route planner** — deployed patch_0199 but integration status unknown

## Cross-Stream Dependencies

| Needs | From | Nature |
|-------|------|--------|
| Write to `perception_log` | NEU | NEU owns this table — SEN must use NEU's write interface |
| Write to `life_events` | MNE | MNE owns this table — coordinate |
| `Person` / `Soul` nodes for transit linking | NEU, SYS | Read only |
| Bot command registration | SYS | SYS patch needed for `/lunar`, `/briefing`, `/transits` |

---

## Session Start Checklist

```bash
# Check astrology engine
ls -la /opt/mythos/astrology/
sudo -u postgres psql -d mythos -c "SELECT COUNT(*) FROM astro_natal_charts;"
sudo -u postgres psql -d mythos -c "SELECT person_name, chart_date FROM astro_natal_charts ORDER BY person_name;"

# Check lunar data
ls -la /opt/mythos/data/lunar/

# Check calendar
sudo -u postgres psql -d mythos -c "SELECT COUNT(*), MAX(event_date) FROM calendar_events;"

# Check message astro context
sudo -u postgres psql -d mythos -c "SELECT COUNT(*), MAX(created_at) FROM message_astrological_context;"

# Check routines
sudo -u postgres psql -d mythos -c "SELECT COUNT(*) FROM routines;"
sudo -u postgres psql -d mythos -c "SELECT COUNT(*), MAX(completed_at) FROM routine_completions;"
```
