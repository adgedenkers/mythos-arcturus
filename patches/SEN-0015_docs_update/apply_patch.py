#!/usr/bin/env python3
"""
SEN-0015: Documentation update — post-launch hotfix record

Updates three docs to reflect the complete state of Astrology v2
including post-A→F hotfixes (SEN-0011 through SEN-0015):

1. SYSTEM_ASTROLOGY.md — full patch ledger including hotfixes,
   updated architecture notes, corrected how-to-use (run_daily_pressure
   vs get_todays_pressure), new known issues (slow interpretations,
   astro_events no chart_id), full incoming notes chain.

2. ARCHITECTURE.md — update astrology pointer from "Letter A shipped"
   to "v2 complete + stable", bump version to 6.4.0, update current patch.

3. TODO.md — add Astrology v2 + transit engine to Recently Completed,
   add qwen3 num_predict lesson to Key Insights.

Tables: none. Services: none. Blast radius: LOW (docs only).
"""
import sys
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

SYSTEM_ASTRO_PATH = Path('/opt/mythos/docs/SYSTEM_ASTROLOGY.md')
ARCHITECTURE_PATH = Path('/opt/mythos/docs/ARCHITECTURE.md')
TODO_PATH         = Path('/opt/mythos/docs/TODO.md')


def log(patch, msg):
    patch.logger.log(msg)


def deploy_system_astrology(patch) -> bool:
    patch.deploy_file(
        'opt/mythos/docs/SYSTEM_ASTROLOGY.md',
        str(SYSTEM_ASTRO_PATH),
    )
    log(patch, '  ✓ SYSTEM_ASTROLOGY.md updated — full ledger A→F + SEN-0011→0015')
    return not patch.errors


def fix_architecture(patch) -> bool:
    path = ARCHITECTURE_PATH
    if not path.exists():
        patch.errors.append('ARCHITECTURE.md missing')
        return False
    current = path.read_text()

    edits = [
        (
            '> - `docs/SYSTEM_ASTROLOGY.md` — Astrology v2 (active build, Letter A shipped)  <!-- SEN-0004 -->',
            '> - `docs/SYSTEM_ASTROLOGY.md` — Astrology v2 (complete + stable, SEN-0004→0015)  <!-- SEN-0015 -->',
            'astrology pointer'
        ),
        (
            '> - `docs/SUB-SYSTEMS.md` — Universal sub-system pattern (DRAFT, N=1)  <!-- SEN-0004 -->',
            '> - `docs/SUB-SYSTEMS.md` — Universal sub-system pattern (ACTIVE, N=2)  <!-- SEN-0015 -->',
            'sub-systems pointer'
        ),
        (
            '> **Version:** 6.3.0',
            '> **Version:** 6.4.0',
            'version bump'
        ),
        (
            '> **Last Updated:** 2026-04-12',
            '> **Last Updated:** 2026-04-21',
            'last updated'
        ),
        (
            '> **Current Patch:** SYS-0069 (patch system stabilized — monitor passive, privilege foundation live)',
            '> **Current Patch:** SEN-0015 (astrology v2 complete + stable — /transits live with Iris interpretations)',
            'current patch'
        ),
    ]

    backup = path.with_suffix('.md.sen0015.bak')
    backup.write_text(current)
    updated = current

    for old, new, label in edits:
        if new in updated:
            log(patch, f'  ✓ {label}: already applied')
            continue
        if old not in updated:
            log(patch, f'  ⚠ {label}: anchor not found — skipping')
            continue
        updated = updated.replace(old, new, 1)
        log(patch, f'  ✓ {label}: updated')

    path.write_text(updated)
    if hasattr(patch, 'files_deployed'):
        patch.files_deployed.append(str(path))
    return True


def fix_todo(patch) -> bool:
    path = TODO_PATH
    if not path.exists():
        patch.errors.append('TODO.md missing')
        return False
    current = path.read_text()

    # Add astrology completion to Recently Completed section
    COMPLETION_ANCHOR = '### 2026-04-02: Iris Voice Quality + Alias Consolidation'
    COMPLETION_INSERT = '''### 2026-04-21: Astrology v2 — Complete + Transit Engine Live

- [x] **SEN-0004→0010:** Astrology v2 A→F — ephemeris provider, natal generator, transit engine, Telegram command, CLI
- [x] **SEN-0011:** `transit_pressure.py` DB connection fix (TCP→socket) + natal positions name normalisation
- [x] **SEN-0012:** `transit_handler.py` — use `run_daily_pressure()` not `get_todays_pressure()` (cache-only)
- [x] **SEN-0013→0014:** gemma4 refuses astrology prompts; qwen3 is correct model; num_predict=512 marginal
- [x] **SEN-0015:** num_predict 2048 — qwen3 thinking mode requires headroom; `/transits` fully operational
- `/transits` command live: computes aspects, generates Iris-voiced interpretations grounded in Ka'tuar'el's lineage
- `daily-transits` CLI live: same pipeline from shell
- Golden fixture harness ran 15 times across arc — identical deltas every run

'''
    INSIGHT_ANCHOR = '### Model Aliases (2026-04-02)'
    INSIGHT_INSERT = '''### qwen3 num_predict / thinking mode (2026-04-21)
qwen3:30b-a3b uses extended thinking mode by default. With short `num_predict` budgets it
consumes all tokens on internal reasoning (`<think>...</think>`) and returns empty content.
Rule: any prompt >200 tokens needs `num_predict` ≥ 2048. Verify with:
`think=False` as a top-level `client.chat()` param suppresses thinking but gemma4 refuses
astrology content entirely. qwen3 + sufficient token budget is the correct stack.

### qwen3 `think=False` does not work in options dict (2026-04-21)
`options={"think": False}` is silently ignored. `client.chat(..., think=False)` works
syntactically but still leaks thinking into content on some prompts. The real fix is
always `num_predict` headroom, not suppressing the thinking pass.

'''

    backup = path.with_suffix('.md.sen0015.bak')
    backup.write_text(current)
    updated = current

    if '### 2026-04-21: Astrology v2' not in updated:
        if COMPLETION_ANCHOR in updated:
            updated = updated.replace(
                COMPLETION_ANCHOR,
                COMPLETION_INSERT + COMPLETION_ANCHOR,
                1
            )
            log(patch, '  ✓ TODO.md: added Astrology v2 completion block')
        else:
            log(patch, '  ⚠ TODO.md: completion anchor not found — skipping')
    else:
        log(patch, '  ✓ TODO.md: completion block already present')

    if 'qwen3 num_predict' not in updated:
        if INSIGHT_ANCHOR in updated:
            updated = updated.replace(
                INSIGHT_ANCHOR,
                INSIGHT_INSERT + INSIGHT_ANCHOR,
                1
            )
            log(patch, '  ✓ TODO.md: added qwen3 insight blocks')
        else:
            log(patch, '  ⚠ TODO.md: insight anchor not found — skipping')
    else:
        log(patch, '  ✓ TODO.md: insight blocks already present')

    path.write_text(updated)
    if hasattr(patch, 'files_deployed'):
        patch.files_deployed.append(str(path))
    return True


# ═══════════════════════════════════════════════════════════════════════
patch = PatchBase(
    stream='SEN',
    number=15,
    description='docs update — astrology v2 complete + hotfix record',
    patch_type='PATCH',
)
patch.begin()

print('\n' + '=' * 70)
print('SEN-0015 — Documentation update: Astrology v2 complete + stable')
print('=' * 70 + '\n')

print('PHASE 1: Deploy SYSTEM_ASTROLOGY.md')
print('-' * 70)
if not deploy_system_astrology(patch):
    patch.finish(); sys.exit(1)

print('\nPHASE 2: Update ARCHITECTURE.md')
print('-' * 70)
fix_architecture(patch)

print('\nPHASE 3: Update TODO.md')
print('-' * 70)
fix_todo(patch)

if patch.errors:
    patch.finish(); sys.exit(1)

print('\n' + '=' * 70)
print('✓ SEN-0015 complete — all docs reflect true current state')
print('=' * 70 + '\n')

patch.finish()
