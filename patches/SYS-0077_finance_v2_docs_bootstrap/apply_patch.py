#!/usr/bin/env python3
"""
SYS-0077: Finance v2 — Workflow & Documentation Bootstrap (Patch C)

Ships docs only. No schema, no code, no services restarted.

Deploys:
  - /opt/mythos/docs/WORKFLOW.md     (new)
  - /opt/mythos/docs/SYSTEM_FINANCE.md (new)

Edits in place:
  - /opt/mythos/docs/ARCHITECTURE.md  (adds SYSTEM-docs pointer)

Handoff diag script is deliberately excluded — pending external
review (Gemini). Will land in a follow-up doc patch.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase


ARCH_PATH = Path('/opt/mythos/docs/ARCHITECTURE.md')

# Uniqueness-checked anchor from near the top of ARCHITECTURE.md
# (header line that has appeared since 6.2.0, stable across recent patches)
ARCH_ANCHOR = '# Mythos System Architecture'

# Block we inject immediately after the top H1. Contains a marker so
# idempotent re-runs can detect prior installation.
ARCH_INSERT = '''# Mythos System Architecture

<!-- SYS-0077: SYSTEM docs pointer -->
> **Subsystem docs:** Multi-patch features now have per-system
> canonical state docs living alongside this one. When working on
> a subsystem, read its `SYSTEM_<name>.md` first — it holds the
> current patch letter, architecture summary, next-up spec, and
> incoming notes. See `docs/WORKFLOW.md` for the full loop.
>
> Current system docs:
> - `docs/SYSTEM_FINANCE.md` — Finance v2 (active build, Patch B shipped)
'''

ARCH_MARKER = '<!-- SYS-0077: SYSTEM docs pointer -->'


def edit_architecture(patch: PatchBase) -> None:
    """Insert the SYSTEM-docs pointer block at the top of ARCHITECTURE.md."""
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
            f"ARCHITECTURE.md: anchor {ARCH_ANCHOR!r} not found — cannot edit safely"
        )
        patch.logger.log(f"  ✗ anchor not found in ARCHITECTURE.md")
        return
    if occurrences > 1:
        patch.errors.append(
            f"ARCHITECTURE.md: anchor {ARCH_ANCHOR!r} appears {occurrences}×, ambiguous"
        )
        patch.logger.log(f"  ✗ anchor is ambiguous ({occurrences} matches)")
        return

    if patch.dry_run:
        patch.validations.append("ARCHITECTURE.md edit — anchor unique, would succeed")
        patch.logger.log("  ✓ [validate] ARCHITECTURE.md anchor unique")
        return

    # Backup before edit
    backup = ARCH_PATH.with_suffix('.md.sys0077.bak')
    backup.write_text(current)
    patch.logger.log(f"  ✓ backed up ARCHITECTURE.md → {backup.name}")

    # Do the replacement
    updated = current.replace(ARCH_ANCHOR, ARCH_INSERT, 1)

    # Sanity: must now contain marker exactly once
    if updated.count(ARCH_MARKER) != 1:
        patch.errors.append("ARCHITECTURE.md post-edit: marker not exactly 1× — aborting")
        patch.logger.log("  ✗ post-edit sanity check failed, restoring backup")
        ARCH_PATH.write_text(current)
        return

    ARCH_PATH.write_text(updated)
    patch.files_deployed.append(str(ARCH_PATH))
    patch.logger.log(f"  ✓ ARCHITECTURE.md — SYSTEM-docs pointer inserted")


def verify_docs(patch: PatchBase) -> None:
    """Post-install sanity checks."""
    checks = [
        ('/opt/mythos/docs/WORKFLOW.md', 'WORKFLOW.md'),
        ('/opt/mythos/docs/SYSTEM_FINANCE.md', 'SYSTEM_FINANCE.md'),
    ]
    for path, label in checks:
        p = Path(path)
        if p.exists() and p.stat().st_size > 0:
            patch.validations.append(f"{label} present ({p.stat().st_size} bytes)")
            patch.logger.log(f"  ✓ verify: {label} present")
        else:
            patch.errors.append(f"{label} missing or empty at {path}")
            patch.logger.log(f"  ✗ verify: {label} missing or empty")

    # Confirm ARCHITECTURE.md contains the marker
    if ARCH_PATH.exists() and ARCH_MARKER in ARCH_PATH.read_text():
        patch.validations.append("ARCHITECTURE.md marker present")
        patch.logger.log("  ✓ verify: ARCHITECTURE.md marker present")
    else:
        patch.errors.append("ARCHITECTURE.md marker not found after edit")
        patch.logger.log("  ✗ verify: ARCHITECTURE.md marker missing")


def main():
    patch = PatchBase(
        stream='SYS',
        number=77,
        description='finance v2 workflow & documentation bootstrap (Patch C)',
        patch_type='PATCH',
    )
    patch.begin()

    # 1. Deploy the two new doc files
    patch.deploy_file(
        'opt/mythos/docs/WORKFLOW.md',
        '/opt/mythos/docs/WORKFLOW.md',
    )
    patch.deploy_file(
        'opt/mythos/docs/SYSTEM_FINANCE.md',
        '/opt/mythos/docs/SYSTEM_FINANCE.md',
    )

    # 2. Edit ARCHITECTURE.md in place
    if not patch.errors:
        edit_architecture(patch)

    # 3. Verify
    if not patch.dry_run and not patch.errors:
        verify_docs(patch)

    patch.finish()


if __name__ == '__main__':
    main()
