#!/usr/bin/env python3
"""
SEN-0004 (Letter A): Astrology v2 Anchor

What this patch changes:
- Creates /opt/mythos/docs/SUB-SYSTEMS.md (draft pattern doc, N=1)
- Creates /opt/mythos/docs/SYSTEM_ASTROLOGY.md (canonical state doc)
- Creates /opt/mythos/docs/ASTROLOGY_V2.md (locked design plan + Castor review)
- Creates /opt/mythos/docs/astrology/NEXT_PATCH_SPEC.md (Letter B spec)
- Creates /opt/mythos/astrology/tests/check_accuracy.py (golden fixture harness)
- Creates /opt/mythos/astrology/tests/__init__.py
- Creates /opt/mythos/astrology/tests/fixtures/expected_aspects.json
- Edits /opt/mythos/docs/ARCHITECTURE.md (adds astrology + sub-systems
  to the SYSTEM docs pointer list installed by SYS-0077)

Services restarted: none (docs + harness only, no live code changes)
Tables touched: none

Uses the SYS-0077 pattern for in-place edits: anchor uniqueness check,
marker-based idempotency, pre-edit backup, post-edit sanity verify.
PatchBase does not expose an in-place edit method (verified 2026-04-21
against the live patch_base.py — only deploy_file / run_sql /
restart_service + the privilege wrappers exist).

Post-install: runs check_accuracy.py for informational pass/fail
baseline. Patch does NOT fail on fixture failure at Letter A — we're
shipping INTO a messy state and the baseline output is diagnostic
information for Letter B+.
"""
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase


ARCH_PATH = Path('/opt/mythos/docs/ARCHITECTURE.md')

# ── ARCHITECTURE.md edit plan ─────────────────────────────────────────
# SYS-0077 installed this line inside an admonition block at the top of
# ARCHITECTURE.md:
#   > - `docs/SYSTEM_FINANCE.md` — Finance v2 (active build, Patch B shipped)
# We append two bullet lines immediately after it. The anchor is checked
# for uniqueness; a post-replace marker confirms the edit took effect;
# a pre-edit backup enables manual restoration if anything goes sideways.

ARCH_ANCHOR = '> - `docs/SYSTEM_FINANCE.md` — Finance v2 (active build, Patch B shipped)'

ARCH_INSERT = (
    '> - `docs/SYSTEM_FINANCE.md` — Finance v2 (active build, Patch B shipped)\n'
    '> - `docs/SYSTEM_ASTROLOGY.md` — Astrology v2 (active build, Letter A shipped)  <!-- SEN-0004 -->\n'
    '> - `docs/SUB-SYSTEMS.md` — Universal sub-system pattern (DRAFT, N=1)  <!-- SEN-0004 -->'
)

ARCH_MARKER = '<!-- SEN-0004 -->'


def edit_architecture(patch):
    """Insert the Astrology + SUB-SYSTEMS pointers after the Finance pointer.

    Follows the SYS-0077 pattern verbatim: idempotency via marker,
    uniqueness check on anchor, backup before edit, post-edit sanity
    verify, auto-restore on sanity failure.
    """
    if not ARCH_PATH.exists():
        patch.errors.append(f"ARCHITECTURE.md not found at {ARCH_PATH}")
        patch.logger.log(f"  ✗ {ARCH_PATH} missing")
        return

    current = ARCH_PATH.read_text()

    # Idempotency: if marker already present, skip
    if ARCH_MARKER in current:
        patch.validations.append("ARCHITECTURE.md pointer — already present, skipping")
        patch.logger.log("  ✓ ARCHITECTURE.md pointer already present (idempotent skip)")
        return

    # Uniqueness check on anchor
    occurrences = current.count(ARCH_ANCHOR)
    if occurrences == 0:
        patch.errors.append(
            "ARCHITECTURE.md: anchor not found — cannot edit safely. "
            "Expected SYS-0077's Finance pointer line."
        )
        patch.logger.log("  ✗ anchor not found in ARCHITECTURE.md — is SYS-0077 installed?")
        return
    if occurrences > 1:
        patch.errors.append(
            "ARCHITECTURE.md: anchor appears %d×, ambiguous" % occurrences
        )
        patch.logger.log("  ✗ anchor is ambiguous (%d matches)" % occurrences)
        return

    if getattr(patch, 'dry_run', False):
        patch.validations.append("ARCHITECTURE.md edit — anchor unique, would succeed")
        patch.logger.log("  ✓ [validate] ARCHITECTURE.md anchor unique")
        return

    # Backup before edit
    backup = ARCH_PATH.with_suffix('.md.sen0004.bak')
    backup.write_text(current)
    patch.logger.log("  ✓ backed up ARCHITECTURE.md -> %s" % backup.name)

    # Do the replacement
    updated = current.replace(ARCH_ANCHOR, ARCH_INSERT, 1)

    # Sanity: must now contain marker exactly twice (once per new line)
    marker_count = updated.count(ARCH_MARKER)
    if marker_count != 2:
        patch.errors.append(
            "ARCHITECTURE.md post-edit: marker count %d, expected 2 — aborting" % marker_count
        )
        patch.logger.log("  ✗ post-edit sanity check failed, restoring backup")
        ARCH_PATH.write_text(current)
        return

    ARCH_PATH.write_text(updated)
    if hasattr(patch, 'files_deployed'):
        patch.files_deployed.append(str(ARCH_PATH))
    patch.logger.log("  ✓ ARCHITECTURE.md edited (Astrology + SUB-SYSTEMS pointers added)")


# ═══════════════════════════════════════════════════════════════════════
# Main patch flow
# ═══════════════════════════════════════════════════════════════════════

patch = PatchBase(
    stream='SEN',
    number=4,
    description='astrology v2 anchor',
    patch_type='MINOR',
)
patch.begin()

# === DEPLOY DOCS ===

patch.deploy_file(
    'opt/mythos/docs/SUB-SYSTEMS.md',
    '/opt/mythos/docs/SUB-SYSTEMS.md',
)

patch.deploy_file(
    'opt/mythos/docs/SYSTEM_ASTROLOGY.md',
    '/opt/mythos/docs/SYSTEM_ASTROLOGY.md',
)

patch.deploy_file(
    'opt/mythos/docs/ASTROLOGY_V2.md',
    '/opt/mythos/docs/ASTROLOGY_V2.md',
)

# Ensure the docs/astrology/ subdir exists before writing NEXT_PATCH_SPEC
os.makedirs('/opt/mythos/docs/astrology', exist_ok=True)

patch.deploy_file(
    'opt/mythos/docs/astrology/NEXT_PATCH_SPEC.md',
    '/opt/mythos/docs/astrology/NEXT_PATCH_SPEC.md',
)

# === DEPLOY GOLDEN FIXTURE HARNESS ===

os.makedirs('/opt/mythos/astrology/tests', exist_ok=True)
os.makedirs('/opt/mythos/astrology/tests/fixtures', exist_ok=True)

patch.deploy_file(
    'opt/mythos/astrology/tests/__init__.py',
    '/opt/mythos/astrology/tests/__init__.py',
)

patch.deploy_file(
    'opt/mythos/astrology/tests/check_accuracy.py',
    '/opt/mythos/astrology/tests/check_accuracy.py',
)

# Make the harness executable for direct invocation
try:
    os.chmod('/opt/mythos/astrology/tests/check_accuracy.py', 0o755)
except OSError as e:
    patch.logger.log("  ⚠ chmod +x on check_accuracy.py failed: %s" % e)

patch.deploy_file(
    'opt/mythos/astrology/tests/fixtures/expected_aspects.json',
    '/opt/mythos/astrology/tests/fixtures/expected_aspects.json',
)

# === EDIT ARCHITECTURE.md (Finance-style manual edit) ===

edit_architecture(patch)

# === POST-INSTALL: BASELINE GOLDEN FIXTURE RUN ===
# Informational only — a failure here tells us which parts of the
# current system are miscalibrated before Letter B refactors anything.
# Letter A does NOT roll back on fixture failure.

print("\n" + "=" * 70)
print("BASELINE GOLDEN FIXTURE RUN (informational, not gating)")
print("=" * 70)

try:
    result = subprocess.run(
        [
            '/opt/mythos/.venv/bin/python3',
            '/opt/mythos/astrology/tests/check_accuracy.py',
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr, file=sys.stderr)
    print("Exit code: %d" % result.returncode)
    if result.returncode == 0:
        print("\n✓ All golden fixtures pass against current state.")
        print("  This is the baseline. Letter B+ must maintain this.")
    else:
        print("\n⚠ Some golden fixtures fail against current state.")
        print("  This is diagnostic information. Letter B+ must investigate.")
        print("  The patch is NOT rolled back at Letter A.")
except subprocess.TimeoutExpired:
    print("⚠ check_accuracy.py timed out (60s). Letter B should investigate.")
except Exception as e:
    print("⚠ Could not run check_accuracy.py: %s" % e)
    print("  Letter B should investigate.")

print("=" * 70 + "\n")

patch.finish()
