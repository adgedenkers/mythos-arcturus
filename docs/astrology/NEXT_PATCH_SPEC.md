---
title: "Astrology Next Patch Spec — Letter E"
category: spec
status: active
stream: SEN
location: docs/astrology
tags: [astrology, spec, next-patch]
created: 2026-04-21
updated: 2026-04-21
author: Adge Denkers
---

# Astrology Next Patch Spec — Letter E (Daily Transits Refactor)

> **This file is rewritten wholesale at the end of every feature patch.**
> It describes exactly one patch ahead of the current state.
>
> **Current state:** Letter D (SEN-0008) shipped — natal_generator.py
> deployed, charts/ka.json and charts/seraphe.json generated from
> Postgres, Adge (chart_id=9) and Seraphe (chart_id=11) both confirmed
> present with correct birth data.
>
> **This spec covers:** Letter E — Daily Transits Refactor.
> **Expected patch number:** SEN-0009 (verify via `mythos-diag streams`).

---

## Scope

Refactor the existing daily_transits.py to use:
- `astrology.ephemeris` for all calculations (replacing inline swisseph calls)
- `astrology.natal_generator.load_natal()` for natal chart data
  (no birth data re-entry, reads from Postgres)
- Proper applying/separating detection (was broken in original due to
  the flags=0 footgun fixed in SEN-0005)

The existing `daily_transits.py` (uploaded 2026-04-21, 357 lines)
serves as the reference for feature parity. It computes:
  - All transiting planet positions for a given date
  - Aspects between transiting planets and natal positions
  - Orb values, applying/separating, transit quality

### Target interface

```python
from astrology.transit_engine import compute_transits, format_transit_report

# Compute transits for Adge on a date
transits = compute_transits(
    natal_name='Adge',       # loads from natal_generator
    transit_date='2026-04-28',
    tz_str='America/New_York',
)

# Format for Telegram or console
report = format_transit_report(transits, style='telegram')
```

---

## Files created

| File | Purpose |
|---|---|
| `/opt/mythos/astrology/transit_engine.py` | Daily transits computation module |

---

## Files modified

None. Pure addition patch.

---

## SQL

None.

---

## Services restarted

None.

---

## Verification

1. **Import smoke test** on transit_engine.py
2. **Compute Adge transits for 2026-04-28** — must match the golden
   fixtures (Uranus opp Sun at 0.0017° orb, etc.) to within 0.005°
3. **Applying/separating is non-null** — all aspects must have
   applying field set (True or False), not None
4. **All 5 existing golden fixtures still pass**

---

## Blast radius

**Low.** New module, no existing code touched, no services restarted,
no schema changes.

---

## After Letter E ships

- Rewrite this file to describe Letter F (Integration — CLI + Telegram)
- Update SYSTEM_ASTROLOGY.md to mark E shipped
- Letter F will wire transit_engine into the Telegram /transits command

---

*End of Letter E spec.*
