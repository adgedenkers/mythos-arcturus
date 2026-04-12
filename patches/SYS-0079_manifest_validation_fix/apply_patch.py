#!/usr/bin/env python3
"""
SYS-0079: Handoff manifest validation fix (Finance)

Two issues in docs/finance/MANIFEST.yaml:

1. The "deferred balance trigger is DEFERRABLE" validation cast
   tgdeferrable to text, which returns 'true' instead of 't'.
   Drop the cast — psql -tA already renders bool as t/f.

2. Add "empty ledger" guards so the handoff explicitly confirms
   that transactional tables are still at zero rows. Protects
   against accidentally starting a new patch conversation on a
   polluted foundation.

Ships only a str.replace on MANIFEST.yaml. No schema, no services,
no other files touched.
"""
import sys
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase


MANIFEST_PATH = Path('/opt/mythos/docs/finance/MANIFEST.yaml')

# The exact broken line, verbatim from SYS-0078
OLD_TGDEFERRABLE = (
    '  - name: "deferred balance trigger is DEFERRABLE"\n'
    '    sql: "SELECT tgdeferrable::text FROM pg_trigger '
    "WHERE tgname='entries_enforce_balance'\"\n"
    '    expect: "t"'
)

NEW_TGDEFERRABLE_AND_GUARDS = (
    '  - name: "deferred balance trigger is DEFERRABLE"\n'
    '    sql: "SELECT tgdeferrable FROM pg_trigger '
    "WHERE tgname='entries_enforce_balance'\"\n"
    '    expect: "t"\n'
    '  - name: "deferred balance trigger is INITIALLY DEFERRED"\n'
    '    sql: "SELECT tginitdeferred FROM pg_trigger '
    "WHERE tgname='entries_enforce_balance'\"\n"
    '    expect: "t"\n'
    '  # ── Empty-ledger guards (SYS-0079): the transactional core\n'
    '  # should be empty until Patch E (importer) runs. If any of\n'
    '  # these trip, someone has been inserting rows outside the\n'
    '  # patch flow and the foundation is no longer clean.\n'
    '  - name: "imports table is empty (pre-Patch-E guard)"\n'
    '    sql: "SELECT count(*)::text FROM finance.imports"\n'
    '    expect: "0"\n'
    '  - name: "transactions table is empty (pre-Patch-E guard)"\n'
    '    sql: "SELECT count(*)::text FROM finance.transactions"\n'
    '    expect: "0"\n'
    '  - name: "entries table is empty (pre-Patch-E guard)"\n'
    '    sql: "SELECT count(*)::text FROM finance.entries"\n'
    '    expect: "0"\n'
    '  - name: "source_observations table is empty (pre-Patch-E guard)"\n'
    '    sql: "SELECT count(*)::text FROM finance.source_observations"\n'
    '    expect: "0"'
)

MARKER = '"deferred balance trigger is INITIALLY DEFERRED"'


def main():
    patch = PatchBase(
        stream='SYS',
        number=79,
        description='fix tgdeferrable validation cast + add empty-ledger guards',
        patch_type='PATCH',
    )
    patch.begin()

    if not MANIFEST_PATH.exists():
        patch.errors.append(f"{MANIFEST_PATH} not found — install SYS-0078 first")
        patch.finish()
        return

    content = MANIFEST_PATH.read_text()

    # Idempotency: if marker already present, we've already applied
    if MARKER in content:
        patch.validations.append("MANIFEST.yaml already patched (idempotent skip)")
        patch.logger.log("  ✓ already patched")
        patch.finish()
        return

    # Uniqueness check on the broken line
    count = content.count(OLD_TGDEFERRABLE)
    if count == 0:
        patch.errors.append(
            "MANIFEST.yaml: broken tgdeferrable validation not found — "
            "either SYS-0078 wasn't installed, or the manifest has already "
            "been hand-edited. Bailing out."
        )
        patch.logger.log("  ✗ anchor not found in MANIFEST.yaml")
        patch.finish()
        return
    if count > 1:
        patch.errors.append(f"MANIFEST.yaml: anchor appears {count}× (ambiguous)")
        patch.logger.log(f"  ✗ anchor ambiguous ({count} matches)")
        patch.finish()
        return

    if patch.dry_run:
        patch.validations.append("MANIFEST.yaml edit — anchor unique, would succeed")
        patch.logger.log("  ✓ [validate] anchor unique")
        patch.finish()
        return

    # Backup + edit
    backup = MANIFEST_PATH.with_suffix('.yaml.sys0079.bak')
    backup.write_text(content)
    patch.logger.log(f"  ✓ backed up MANIFEST.yaml → {backup.name}")

    updated = content.replace(OLD_TGDEFERRABLE, NEW_TGDEFERRABLE_AND_GUARDS, 1)

    if MARKER not in updated:
        patch.errors.append("post-edit: marker missing, restoring backup")
        MANIFEST_PATH.write_text(content)
        patch.logger.log("  ✗ post-edit sanity failed, rolled back")
        patch.finish()
        return

    # Parse check: make sure YAML is still valid after the edit
    try:
        import yaml
        parsed = yaml.safe_load(updated)
        validations = parsed.get('validations', [])
        names = [v.get('name', '') for v in validations]
        expected_new = [
            "deferred balance trigger is DEFERRABLE",
            "deferred balance trigger is INITIALLY DEFERRED",
            "imports table is empty (pre-Patch-E guard)",
            "transactions table is empty (pre-Patch-E guard)",
            "entries table is empty (pre-Patch-E guard)",
            "source_observations table is empty (pre-Patch-E guard)",
        ]
        missing = [n for n in expected_new if n not in names]
        if missing:
            patch.errors.append(f"post-edit YAML: missing validation names: {missing}")
            MANIFEST_PATH.write_text(content)
            patch.logger.log("  ✗ YAML validation list incomplete, rolled back")
            patch.finish()
            return
    except Exception as e:
        patch.errors.append(f"post-edit YAML parse failed: {e}")
        MANIFEST_PATH.write_text(content)
        patch.logger.log(f"  ✗ YAML parse failed: {e}, rolled back")
        patch.finish()
        return

    MANIFEST_PATH.write_text(updated)
    patch.files_deployed.append(str(MANIFEST_PATH))
    patch.logger.log("  ✓ MANIFEST.yaml edited")
    patch.validations.append(
        f"MANIFEST.yaml now has {len(validations)} validations "
        f"(was 7, +4 empty-ledger guards = 11, +1 INITIALLY DEFERRED check = ?)"
    )

    # Post-edit live check: run mythos-handoff finance --stdout and confirm
    # no validation failures this time
    import subprocess
    try:
        r = subprocess.run(
            ['/opt/mythos/.venv/bin/python3',
             '/opt/mythos/bin/mythos-handoff', 'finance', '--stdout'],
            capture_output=True, text=True, timeout=60,
        )
        if 'VALIDATION FAILURES' in r.stdout:
            # Find which ones
            patch.errors.append(
                "post-edit: mythos-handoff finance still reports VALIDATION FAILURES. "
                "Check stderr: " + r.stderr[:500]
            )
            patch.logger.log("  ✗ post-edit: handoff still has failures")
        elif 'All' in r.stdout and 'validations passed' in r.stdout:
            patch.validations.append("live handoff run: all validations pass")
            patch.logger.log("  ✓ live handoff: all validations pass")
        else:
            patch.logger.log(
                f"  ⚠ live handoff: couldn't determine pass/fail from output"
            )
    except Exception as e:
        patch.logger.log(f"  ⚠ live handoff check failed: {e}")

    patch.finish()


if __name__ == '__main__':
    main()
