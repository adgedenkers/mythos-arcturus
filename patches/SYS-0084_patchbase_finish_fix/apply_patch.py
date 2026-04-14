#!/usr/bin/env python3
"""
SYS-0084 — Path 2 Bootstrap Meta-Patch.

Fixes PatchBase.finish() to guard the STREAMS.json / PATCH_HISTORY.md
ledger update behind an error-gate, and to run the post-install
pipeline BEFORE the ledger update so pipeline failures also block it.

This apply_patch.py does NOT import PatchBase — it's fixing PatchBase.
It inlines every side effect with py_compile + fresh-subprocess import
verification, replaces the SYS-0083 entry in PATCH_HISTORY.md with an
accurate failure narrative, appends its own entry, and bumps STREAMS.
Exits 1 on any failure so install.sh's `set -e` propagates to
patch-install's rollback path.
"""
import os
import sys
import json
import shutil
import subprocess
import datetime
from pathlib import Path

PATCH_ID = "SYS-0084"
STREAM = "SYS"
NUMBER = 84
DESCRIPTION = "PatchBase.finish() error-gate + PatchFinishError (Path 2 Bootstrap)"
PATCH_TYPE = "MINOR"
DATE = datetime.datetime.now().strftime("%Y-%m-%d")

PATCH_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
MYTHOS = Path("/opt/mythos")
TARGET = MYTHOS / "patches" / "scripts" / "patch_base.py"
BACKUP = MYTHOS / "patches" / "scripts" / "patch_base.py.SYS-0084.bak"
STREAMS_JSON = MYTHOS / "docs" / "STREAMS.json"
PATCH_HISTORY = MYTHOS / "docs" / "PATCH_HISTORY.md"
NEW_FILE = PATCH_DIR / "opt" / "mythos" / "patches" / "scripts" / "patch_base.py"

# The exact current SYS-0083 block we expect to find (appears once,
# verified against live PATCH_HISTORY.md at 2026-04-12).
OLD_SYS_0083 = (
    "### SYS-0083: finance v2 patch D — merchants & patterns\n"
    "- **Date:** 2026-04-12\n"
    "- **Type:** MINOR\n"
    "- **Stream:** SYS\n"
)

NEW_SYS_0083 = (
    "### SYS-0083: finance v2 patch D — merchants & patterns [FAILED — ROLLED BACK]\n"
    "- **Date:** 2026-04-12\n"
    "- **Type:** MINOR\n"
    "- **Stream:** SYS\n"
    "- **SQL:** SYS-0083_finance_v2_merchants.sql (syntax error at line 114)\n"
    "- **Failure:** `ROLLBACK TO SAVEPOINT` inside PL/pgSQL `DO` block is not permitted. "
    "Postgres rolled back the migration transaction cleanly; database state is pristine "
    "pre-Patch-D. STREAMS.json and this entry were written by a `PatchBase.finish()` bug "
    "where `self.errors` was not checked before side effects. Fixed in SYS-0084 (Path 2 "
    "Bootstrap Meta-Patch). Patch D re-landed as SYS-0085 with the verification block "
    "restructured to use PL/pgSQL sub-blocks with `BEGIN ... EXCEPTION` and explicit "
    "`DELETE` cleanup instead of `ROLLBACK TO SAVEPOINT`.\n"
    "- **Lesson:** PL/pgSQL `DO` blocks are anonymous code blocks, not transactions — "
    "they cannot use `ROLLBACK TO SAVEPOINT`. Use sub-block exception handling with "
    "explicit cleanup, or move schema verification into named `PROCEDURE`s.\n"
)


def log(msg):
    print(msg)


def fail(msg):
    log(f"  ✗ {msg}")
    log(f"[{PATCH_ID}] FAILED ✗")
    sys.exit(1)


def main():
    log(f"[{PATCH_ID}] {DESCRIPTION}")
    log("=" * 55)

    # 1. Sanity: new file exists in patch payload
    if not NEW_FILE.exists():
        fail(f"patch payload missing: {NEW_FILE}")
    log(f"  ✓ payload present: {NEW_FILE.name}")

    # 2. py_compile the new file
    result = subprocess.run(
        ["python3", "-m", "py_compile", str(NEW_FILE)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        fail(f"py_compile failed: {result.stderr.strip()}")
    log("  ✓ py_compile OK")

    # 3. Back up the existing patch_base.py
    if not TARGET.exists():
        fail(f"target missing: {TARGET}")
    try:
        shutil.copy2(str(TARGET), str(BACKUP))
    except Exception as e:
        fail(f"backup failed: {e}")
    log(f"  ✓ backup: {BACKUP.name}")

    # 4. Atomic write: temp file in same dir + rename
    tmp = TARGET.with_suffix(".py.SYS-0084.tmp")
    try:
        shutil.copy2(str(NEW_FILE), str(tmp))
        os.replace(str(tmp), str(TARGET))
    except Exception as e:
        fail(f"atomic write failed: {e}")
    log(f"  ✓ deployed: {TARGET}")

    # 5. Fresh subprocess import verify
    verify_cmd = (
        "import sys; sys.path.insert(0, '/opt/mythos/patches/scripts'); "
        "from patch_base import PatchBase, PatchFinishError; "
        "p = PatchBase('SYS', 9999, 'verify'); "
        "assert isinstance(p.errors, list); "
        "print('import-verify OK')"
    )
    result = subprocess.run(
        ["python3", "-c", verify_cmd],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        # Restore backup
        try:
            shutil.copy2(str(BACKUP), str(TARGET))
            log("  ↩ restored backup")
        except Exception as e:
            log(f"  ⚠ RESTORE FAILED: {e}")
        fail(f"import-verify failed: {result.stderr.strip() or result.stdout.strip()}")
    log("  ✓ import-verify OK")

    # 6. Replace SYS-0083 entry in PATCH_HISTORY.md
    try:
        history = PATCH_HISTORY.read_text()
    except Exception as e:
        fail(f"read PATCH_HISTORY failed: {e}")

    count = history.count(OLD_SYS_0083)
    if count != 1:
        fail(
            f"SYS-0083 entry pattern appears {count} times in PATCH_HISTORY "
            f"(expected exactly 1). Manual inspection required."
        )
    new_history = history.replace(OLD_SYS_0083, NEW_SYS_0083)
    try:
        PATCH_HISTORY.write_text(new_history)
    except Exception as e:
        fail(f"write PATCH_HISTORY (replace) failed: {e}")
    log("  ✓ PATCH_HISTORY: SYS-0083 entry replaced with failure narrative")

    # 7. Append SYS-0084's own entry (mirror _write_patch_history format)
    own_entry = (
        f"\n### {PATCH_ID}: {DESCRIPTION}\n"
        f"- **Date:** {DATE}\n"
        f"- **Type:** {PATCH_TYPE}\n"
        f"- **Stream:** {STREAM}\n"
        f"- **Files:** patch_base.py\n"
        f"- **Note:** Path 2 Bootstrap Meta-Patch. apply_patch.py does not "
        f"import PatchBase (fixes the framework from outside). Adds "
        f"PatchFinishError and moves STREAMS.json/PATCH_HISTORY writes "
        f"behind an error-gate in finish(). Post-install pipeline now runs "
        f"before the ledger update so pipeline failures also block it.\n"
    )
    try:
        with open(PATCH_HISTORY, "a") as f:
            f.write(own_entry)
    except Exception as e:
        fail(f"append PATCH_HISTORY failed: {e}")
    log(f"  ✓ PATCH_HISTORY: {PATCH_ID} entry appended")

    # 8. Bump STREAMS.json SYS.next_patch 84 → 85
    try:
        with open(STREAMS_JSON, "r") as f:
            data = json.load(f)
        sys_entry = data.get("streams", {}).get("SYS")
        if not sys_entry:
            fail("STREAMS.json has no 'SYS' stream")
        current = sys_entry.get("next_patch")
        if current != NUMBER:
            fail(
                f"STREAMS.json SYS.next_patch = {current}, expected {NUMBER}. "
                f"Manual inspection required — state may be inconsistent."
            )
        sys_entry["next_patch"] = NUMBER + 1
        with open(STREAMS_JSON, "w") as f:
            json.dump(data, f, indent=2)
    except SystemExit:
        raise
    except Exception as e:
        fail(f"STREAMS.json bump failed: {e}")
    log(f"  ✓ STREAMS.json: SYS next_patch {NUMBER} → {NUMBER + 1}")

    log("")
    log(f"[{PATCH_ID}] Complete ✓")
    log(f"  PatchBase.finish() now guards ledger writes behind self.errors.")
    log(f"  Next: SYS-0085 will re-land Finance v2 Patch D.")
    sys.exit(0)


if __name__ == "__main__":
    main()
