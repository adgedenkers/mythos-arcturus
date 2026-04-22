---
title: "Astrology Next Patch Spec — POST v2"
category: spec
status: complete
stream: SEN
location: docs/astrology
updated: 2026-04-21
---

# Astrology v2 — Complete

Astrology v2 (A→F) shipped 2026-04-21 across 7 patches (SEN-0004
through SEN-0010). There is no Letter G.

## Post-v2 work

Three items are filed in `/opt/mythos/docs/REQUESTS.md`:

1. **SYS: Full graph coverage + post-patch verification gate**
   — every deployed tool mapped in Neo4j, post-scan gate on patch-install

2. **SYS: PatchBase microtool kit with Ollama integration**
   — `ollama-analyze` microtool callable from apply_patch.py

3. **SEN: Comprehensive astrology tool audit + dedup**
   — inventory all 23+ astrology .py files, unify around ephemeris.py,
     dedup one-offs, fold unique features into canonical modules

## Starting the next astrology conversation

Run the standard session-start diagnostic:

```bash
D=~/diag.txt; > "$D"
echo "=== TODO ===" >> "$D"; cat /opt/mythos/docs/TODO.md >> "$D"
echo "\n\n=== ARCHITECTURE ===" >> "$D"; cat /opt/mythos/docs/ARCHITECTURE.md >> "$D"
echo "\n\n=== STREAMS ===" >> "$D"; cat /opt/mythos/docs/STREAMS.md >> "$D"
cat "$D" | xclip -selection clipboard && echo "✓"
```

Then share `SYSTEM_ASTROLOGY.md` for astrology-specific context.

*End — arc complete.*
