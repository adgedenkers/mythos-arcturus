---
title: "Astrology Next Patch Spec — Letter F"
category: spec
status: active
stream: SEN
location: docs/astrology
updated: 2026-04-21
---

# Astrology Next Patch Spec — Letter F (Integration + Completion)

> **Current state:** Letter E (SEN-0009) shipped — /transits Telegram
> command live for Adge and Seraphe, transit_pressure.py wired to
> natal_generator, bot restarted cleanly.
>
> **Expected patch number:** SEN-0010 (verify via `mythos-diag streams`).

---

## Scope

Final letter of Astrology v2. CLI tool + documentation completion.

1. **`/opt/mythos/bin/daily-transits` CLI** — shell-accessible transit
   report: `daily-transits adge` or `daily-transits seraphe 2026-04-28`

2. **Update `SYSTEM_ASTROLOGY.md`** — mark A→F complete, document full
   v2 architecture as stable.

3. **Update `SUB-SYSTEMS.md`** — increment from DRAFT (N=1) to N=2.
   Refine the pattern based on Astrology v2 experience.

4. **File a note in REQUESTS.md** that the comprehensive astrology tool
   audit can now be scheduled (pre-condition: A→F complete ✓).

---

## Files created

| File | Purpose |
|---|---|
| `/opt/mythos/bin/daily-transits` | Shell CLI for transit reports |

## Files modified

| File | Change |
|---|---|
| `/opt/mythos/docs/SYSTEM_ASTROLOGY.md` | Mark A→F complete |
| `/opt/mythos/docs/SUB-SYSTEMS.md` | Increment to N=2 |

## Services restarted: none (CLI addition only)
## SQL: none
## Blast radius: LOW

*End of Letter F spec.*
