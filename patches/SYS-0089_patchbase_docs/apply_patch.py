#!/usr/bin/env python3
"""
SYS-0089: Documentation update — patch system + PatchBase microtool kit

Three changes:
1. Deploy SYSTEM_PATCH.md — new canonical state doc for the patch system.
2. Update ARCHITECTURE.md — subsystem pointer, version, current patch,
   PatchBase rules, tools section.
3. Update TODO.md — SYS-0087/0089 completion + bootstrapping insight.

Tables: none. Services: none. Blast radius: LOW (docs only).
"""
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

ARCHITECTURE_PATH = '/opt/mythos/docs/ARCHITECTURE.md'
TODO_PATH         = '/opt/mythos/docs/TODO.md'

patch = PatchBase(
    stream='SYS',
    number=89,
    description='docs update — patch system + PatchBase microtool kit',
    patch_type='PATCH',
)
patch.begin()

print('\n' + '=' * 70)
print('SYS-0089 — Documentation update: patch system + PatchBase microtool kit')
print('=' * 70 + '\n')

# ── PHASE 1: Deploy SYSTEM_PATCH.md ──────────────────────────────
print('PHASE 1: Deploy SYSTEM_PATCH.md')
print('-' * 70)
patch.deploy_file(
    'opt/mythos/docs/SYSTEM_PATCH.md',
    '/opt/mythos/docs/SYSTEM_PATCH.md',
)
if patch.errors:
    patch.finish(); sys.exit(1)
patch.logger.log('  ✓ SYSTEM_PATCH.md — new canonical state doc for patch system')

# ── PHASE 2: Update ARCHITECTURE.md ──────────────────────────────
print('\nPHASE 2: Update ARCHITECTURE.md')
print('-' * 70)

if not patch.assert_file_exists(ARCHITECTURE_PATH, 'ARCHITECTURE.md'):
    patch.finish(); sys.exit(1)

# 2a: Add SYSTEM_PATCH.md to subsystem docs pointer.
# Live file has em dash (U+2014) and a blank line between AUTODOC2 and Version.
patch.str_replace(
    ARCHITECTURE_PATH,
    old=(
        '> - `docs/SYSTEM_AUTODOC2.md` — AutoDoc2 codebase documentation engine (registered SYS-0086)  <!-- SYS-0086 -->\n'
        '\n'
        '> **Version:** 6.4.0'
    ),
    new=(
        '> - `docs/SYSTEM_AUTODOC2.md` — AutoDoc2 codebase documentation engine (registered SYS-0086)  <!-- SYS-0086 -->\n'
        '> - `docs/SYSTEM_PATCH.md` — Patch system + PatchBase API reference (SYS-0087→0089)  <!-- SYS-0089 -->\n'
        '\n'
        '> **Version:** 6.5.0'
    ),
    label='subsystem docs pointer + version bump',
)

# 2b: Update current patch pointer
patch.str_replace(
    ARCHITECTURE_PATH,
    old='> **Current Patch:** SEN-0015 (astrology v2 complete + stable — /transits live with Iris interpretations)',
    new='> **Current Patch:** SYS-0089 (patch system docs + PatchBase microtool kit fully documented)',
    label='current patch pointer',
)

# 2c: Add new PatchBase methods after the existing "raises on miss" line.
# Exact anchor from lines 445-446.
patch.str_replace(
    ARCHITECTURE_PATH,
    old="- Fail-fast if the anchor isn't found exactly once — `PatchBase.str_replace` raises on miss\n- `py_compile` syntax check happens automatically before any service restart; rollback on failure",
    new=("- Fail-fast if the anchor isn't found exactly once — `PatchBase.str_replace` raises on miss\n"
         "- **SYS-0087 microtool kit** — 8 new PatchBase methods eliminate copy-paste boilerplate:\n"
         "  - `str_replace(path, old, new, label)` — canonical in-place edit with backup, verify, py_compile\n"
         "  - `append_to_file(path, content, guard, label)` — append with optional idempotency guard\n"
         "  - `prepend_to_file(path, content, guard, label)` — same, writes at top\n"
         "  - `ensure_line_in_file(path, line, after, label)` — idempotent single-line insert\n"
         "  - `read_file(path, label)` — returns contents or None + error on missing\n"
         "  - `assert_file_exists(path, label)` — phase gate; adds to errors if missing\n"
         "  - `run_python_check(code, label, timeout)` — runs snippet in venv, replaces subprocess pattern\n"
         "  - `py_compile_check(path, label)` — explicit syntax gate after deploy_file of .py files\n"
         "- `py_compile` syntax check happens automatically before any service restart; rollback on failure"),
    label='PatchBase microtool methods',
)

# 2d: Add self-patching bootstrapping rule after the idempotency line.
# Exact anchor from line 449.
patch.str_replace(
    ARCHITECTURE_PATH,
    old="- Idempotency markers must come from content unique to the NEW version — first-80-chars doesn't count if NEW appends to OLD (see SYS-0067 lesson)\n- In-memory edits using `tempfile.mkdtemp()`",
    new=("- Idempotency markers must come from content unique to the NEW version — first-80-chars doesn't count if NEW appends to OLD (see SYS-0067 lesson)\n"
         "- **Self-patching bootstrapping rule (SYS-0087):** Any patch replacing `patch_base.py` cannot call new methods on the running `patch` object — it was instantiated from the OLD code. New methods can only be exercised via fresh subprocesses spawned after the deploy.\n"
         "- In-memory edits using `tempfile.mkdtemp()`"),
    label='self-patching bootstrapping rule',
)

# 2e: Add SYSTEM_PATCH.md to tools section.
# Exact anchor: the closing line of the bash block then the ``` closer.
patch.str_replace(
    ARCHITECTURE_PATH,
    old='/opt/mythos/patches/scripts/patch_base.py      # PatchBase class + wrappers\n```',
    new=('/opt/mythos/patches/scripts/patch_base.py      # PatchBase class + wrappers\n'
         '/opt/mythos/docs/SYSTEM_PATCH.md               # Full PatchBase API reference\n'
         '```'),
    label='tools section — SYSTEM_PATCH.md reference',
)

if patch.errors:
    patch.logger.log(f'\n  ✗ ARCHITECTURE.md: {len(patch.errors)} error(s) — aborting')
    patch.finish(); sys.exit(1)
patch.logger.log('  ✓ ARCHITECTURE.md: all edits applied')

# ── PHASE 3: Update TODO.md ───────────────────────────────────────
print('\nPHASE 3: Update TODO.md')
print('-' * 70)

if not patch.assert_file_exists(TODO_PATH, 'TODO.md'):
    patch.finish(); sys.exit(1)

# 3a: Add SYS-0087/0089 completion block before Astrology v2 entry (line 185)
patch.str_replace(
    TODO_PATH,
    old=(
        '- Post-install verifies against active-directive sudoers rules need regex (`^\\s*[^#].*NOPASSWD`), not substring matching. Comments referencing removed rules will otherwise false-positive.\n'
        '### 2026-04-21: Astrology v2 — Complete + Transit Engine Live'
    ),
    new=(
        '- Post-install verifies against active-directive sudoers rules need regex (`^\\s*[^#].*NOPASSWD`), not substring matching. Comments referencing removed rules will otherwise false-positive.\n'
        '### 2026-04-21: PatchBase Microtool Kit + Patch System Docs\n'
         '- [x] **SYS-0087:** PatchBase microtool kit — 8 new methods: `str_replace`, `append_to_file`,\n'
         '  `prepend_to_file`, `ensure_line_in_file`, `read_file`, `assert_file_exists`,\n'
         '  `run_python_check`, `py_compile_check`. Eliminates copy-paste `edit_file()` boilerplate.\n'
         '- [x] **SYS-0089:** `SYSTEM_PATCH.md` created — canonical state doc for the patch system\n'
         '  with full PatchBase API reference, bootstrapping rule, and non-negotiable rules.\n'
         '- **Key lesson:** Self-patching patches cannot call new methods on the running `patch`\n'
         '  object — it was instantiated from old code. Use fresh subprocesses after the deploy.\n'
         '\n'
         '### 2026-04-21: Astrology v2 — Complete + Transit Engine Live'),
    label='SYS-0087/0089 completion block',
)

# 3b: Add self-patching insight before qwen3 section (line 244)
patch.str_replace(
    TODO_PATH,
    old=(
        '- Calibrate before deploying: `iris-calibrate` runs 60 tests across 6 message types\n'
        '### qwen3 num_predict / thinking mode (2026-04-21)'
    ),
    new=(
        '- Calibrate before deploying: `iris-calibrate` runs 60 tests across 6 message types\n'
        '### Self-patching bootstrapping rule (2026-04-21)\n'
         'Any patch that replaces `patch_base.py` must use ONLY the old API throughout the entire run.\n'
         'The `patch` object is instantiated from the old code at import time — deploying a new file\n'
         'to disk does not hot-swap the running object. New methods can only be exercised by spawning\n'
         'a fresh subprocess after the deploy. Discovered during SYS-0087 (two failed installs).\n'
         '\n'
         '### qwen3 num_predict / thinking mode (2026-04-21)'),
    label='self-patching insight',
)

if patch.errors:
    patch.logger.log(f'\n  ✗ TODO.md: {len(patch.errors)} error(s) — aborting')
    patch.finish(); sys.exit(1)
patch.logger.log('  ✓ TODO.md: all edits applied')

# ── Done ──────────────────────────────────────────────────────────
print('\n' + '=' * 70)
print('✓ SYS-0089 complete — patch system fully documented')
print('  SYSTEM_PATCH.md: full PatchBase API reference created')
print('  ARCHITECTURE.md: microtool methods + bootstrapping rule added')
print('  TODO.md: SYS-0087/0089 completion + bootstrapping insight added')
print('=' * 70 + '\n')

patch.finish()
