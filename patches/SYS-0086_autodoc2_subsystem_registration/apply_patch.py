import sys
import os
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=86,
    description='autodoc2 subsystem registration',
    patch_type='PATCH',
)
patch.begin()

# ── Deploy the three new subsystem docs ──────────────────────────────────────

patch.deploy_file(
    'opt/mythos/docs/SYSTEM_AUTODOC2.md',
    '/opt/mythos/docs/SYSTEM_AUTODOC2.md',
)

patch.deploy_file(
    'opt/mythos/docs/AUTODOC2_V2.md',
    '/opt/mythos/docs/AUTODOC2_V2.md',
)

patch.deploy_file(
    'opt/mythos/docs/autodoc2/NEXT_PATCH_SPEC.md',
    '/opt/mythos/docs/autodoc2/NEXT_PATCH_SPEC.md',
)

# ── Edit ARCHITECTURE.md — add SYSTEM_AUTODOC2.md to subsystem docs list ─────

patch.str_replace(
    '/opt/mythos/docs/ARCHITECTURE.md',
    old='> - `docs/SUB-SYSTEMS.md` — Universal sub-system pattern (ACTIVE, N=2)  <!-- SEN-0015 -->',
    new='> - `docs/SUB-SYSTEMS.md` — Universal sub-system pattern (ACTIVE, N=3)  <!-- SYS-0086 -->\n> - `docs/SYSTEM_AUTODOC2.md` — AutoDoc2 codebase documentation engine (registered SYS-0086)  <!-- SYS-0086 -->',
)

# ── Edit SUB-SYSTEMS.md — increment N=2 to N=3, add AutoDoc2 as example ──────

patch.str_replace(
    '/opt/mythos/docs/SUB-SYSTEMS.md',
    old='> **Status: ACTIVE.** This pattern is now validated against two\n> sub-systems: Finance v2 (original) and Astrology v2 (completed\n> 2026-04-21). The pattern held. Promoted from DRAFT.\n>\n> Next revision target: when a third sub-system ships Letter A.',
    new='> **Status: ACTIVE.** This pattern is now validated against three\n> sub-systems: Finance v2, Astrology v2 (completed 2026-04-21), and\n> AutoDoc2 (registered 2026-04-21). The pattern held across all three.\n>\n> Next revision target: when a fourth sub-system ships Letter A.',
)

patch.str_replace(
    '/opt/mythos/docs/SUB-SYSTEMS.md',
    old='- **Finance v2** — double-entry ledger on Postgres (A→L, 12 letters)\n- **Astrology v2** — chart calculation + transit engine on Swiss Ephemeris (A→F, 7 patches)\n- Future candidates: **Voice Memos v2**, **Iris Memory v3**, **Calendar v2**',
    new='- **Finance v2** — double-entry ledger on Postgres (A→L, 12 letters)\n- **Astrology v2** — chart calculation + transit engine on Swiss Ephemeris (A→F, 7 patches)\n- **AutoDoc2** — multi-language codebase documentation engine, Neo4j graph + gemma4:26b analysis (A→G, 7 letters)\n- Future candidates: **Voice Memos v2**, **Iris Memory v3**, **Calendar v2**',
)

# ── Edit _INDEX.md — add AutoDoc2 doc entries ─────────────────────────────────

patch.str_replace(
    '/opt/mythos/docs/_INDEX.md',
    old='| `SYSTEM_FINANCE.md` | SYSTEM: Finance v2 | active | SYS |',
    new='| `AUTODOC2_V2.md` | AutoDoc2 Design Plan | active | SYS |\n| `SYSTEM_AUTODOC2.md` | SYSTEM: AutoDoc2 | active | SYS |\n| `SYSTEM_FINANCE.md` | SYSTEM: Finance v2 | active | SYS |',
)

patch.finish()
