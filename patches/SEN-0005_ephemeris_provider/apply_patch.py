#!/usr/bin/env python3
"""
SEN-0005 (Letter B): Astrology v2 Ephemeris Provider

What this patch changes:
- Creates /opt/mythos/astrology/__init__.py (first-time package declaration)
- Creates /opt/mythos/astrology/ephemeris.py (Master Ephemeris Provider,
  ~495 lines, pyswisseph wrapper with shared constants and helpers)
- Appends SE_EPHE_PATH=/opt/mythos/astrology/ephe to /opt/mythos/.env
  (idempotent — skipped if line already present)

Services restarted: none (new module, not yet imported by any live code)
Tables touched: none

Gating:
- Module must import cleanly after deployment
- self_check() smoke test must pass (Sun position calculation)
- All 5 golden fixtures from SEN-0004 must PASS (not informational)
- Any failure populates patch.errors; PatchBase halts and rolls back.

Letter B is pure addition. No legacy code is touched. Letter C (next)
will consolidate ephemeris files and update the 5 legacy scripts to
import from this module.

Note on __init__.py: /opt/mythos/astrology/ was not previously a Python
package (confirmed via diagnostic dump 2026-04-21). Existing scripts
there run as standalones and do not import from `astrology.*`. Adding
__init__.py is a pure addition — makes `from astrology import ephemeris`
possible without breaking any existing standalone usage.
"""
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase


ENV_PATH = Path('/opt/mythos/.env')
ENV_LINE = 'SE_EPHE_PATH=/opt/mythos/astrology/ephe'
ENV_MARKER = '# SEN-0005: astrology v2 master ephemeris provider'

EPHEMERIS_MODULE_PATH = '/opt/mythos/astrology/ephemeris.py'
ASTROLOGY_INIT_PATH = '/opt/mythos/astrology/__init__.py'
CHECK_ACCURACY_PATH = '/opt/mythos/astrology/tests/check_accuracy.py'


def append_env_path(patch):
    """Append SE_EPHE_PATH to /opt/mythos/.env if not already present.

    Idempotent: checks for both the marker comment AND the bare line,
    skips if either is found.
    """
    if not ENV_PATH.exists():
        patch.errors.append(".env not found at %s" % ENV_PATH)
        patch.logger.log("  ✗ %s missing — cannot set SE_EPHE_PATH" % ENV_PATH)
        return

    current = ENV_PATH.read_text()

    # Idempotency
    if ENV_MARKER in current or ENV_LINE in current:
        patch.validations.append(".env SE_EPHE_PATH — already present, skipping")
        patch.logger.log("  ✓ SE_EPHE_PATH already in .env (idempotent skip)")
        return

    if getattr(patch, 'dry_run', False):
        patch.validations.append(".env append — would succeed")
        patch.logger.log("  ✓ [validate] .env append ok")
        return

    # Backup before edit
    backup = ENV_PATH.with_suffix('.env.sen0005.bak')
    backup.write_text(current)
    patch.logger.log("  ✓ backed up .env -> %s" % backup.name)

    # Append with trailing newline safety
    if current and not current.endswith('\n'):
        current += '\n'
    appended = current + '\n' + ENV_MARKER + '\n' + ENV_LINE + '\n'
    ENV_PATH.write_text(appended)

    # Post-edit sanity
    verify = ENV_PATH.read_text()
    if ENV_LINE not in verify or ENV_MARKER not in verify:
        patch.errors.append(".env post-edit verification failed — restoring backup")
        patch.logger.log("  ✗ .env sanity check failed, restoring backup")
        ENV_PATH.write_text(backup.read_text())
        return

    if hasattr(patch, 'files_deployed'):
        patch.files_deployed.append(str(ENV_PATH))
    patch.logger.log("  ✓ appended to .env: %s" % ENV_LINE)


def verify_ephemeris_import(patch):
    """Import the new ephemeris module via two styles as a smoke test.

    Tests both:
      1. Direct: sys.path has /opt/mythos/astrology, `import ephemeris`
      2. Package: sys.path has /opt/mythos, `from astrology import ephemeris`

    Both must succeed. Subprocess isolation avoids contaminating our
    own sys.modules.
    """
    # Test 1: direct import (for legacy-style scripts in /opt/mythos/astrology/)
    cmd1 = [
        '/opt/mythos/.venv/bin/python3', '-c',
        'import sys; sys.path.insert(0, "/opt/mythos/astrology"); '
        'import ephemeris as e; '
        'import json; print(json.dumps(e.self_check(), default=str))',
    ]
    try:
        out1 = subprocess.run(cmd1, capture_output=True, text=True, timeout=30)
        if out1.returncode != 0:
            patch.errors.append(
                "ephemeris direct import failed: %s" % out1.stderr.strip()
            )
            patch.logger.log("  ✗ ephemeris direct import FAILED")
            patch.logger.log("     stderr: %s" % out1.stderr.strip())
            return False
        patch.logger.log("  ✓ ephemeris imports as direct module")
    except subprocess.TimeoutExpired:
        patch.errors.append("ephemeris direct import timed out")
        patch.logger.log("  ✗ ephemeris direct import timed out")
        return False
    except Exception as e:
        patch.errors.append("ephemeris direct import error: %s" % e)
        patch.logger.log("  ✗ ephemeris direct import error: %s" % e)
        return False

    # Test 2: package import (for future Mythos callers)
    cmd2 = [
        '/opt/mythos/.venv/bin/python3', '-c',
        'import sys; sys.path.insert(0, "/opt/mythos"); '
        'from astrology import ephemeris as e; '
        'import json; print(json.dumps(e.self_check(), default=str))',
    ]
    try:
        out2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=30)
        if out2.returncode != 0:
            patch.errors.append(
                "ephemeris package import failed: %s" % out2.stderr.strip()
            )
            patch.logger.log("  ✗ ephemeris package import FAILED")
            patch.logger.log("     stderr: %s" % out2.stderr.strip())
            return False
        patch.logger.log("  ✓ ephemeris imports as astrology.ephemeris")
    except subprocess.TimeoutExpired:
        patch.errors.append("ephemeris package import timed out")
        return False
    except Exception as e:
        patch.errors.append("ephemeris package import error: %s" % e)
        return False

    # Parse self_check output and validate smoke_test
    try:
        import json
        result = json.loads(out2.stdout.strip())
        patch.logger.log("  — self_check output —")
        for k, v in result.items():
            patch.logger.log("    %s: %s" % (k, v))

        if result.get('smoke_test') != 'pass':
            patch.errors.append(
                "ephemeris smoke_test did not pass: %s" % result.get('smoke_test')
            )
            patch.logger.log("  ✗ smoke_test did not pass")
            return False

        if not result.get('ephe_path_exists'):
            # NOT a hard fail — files may still be at old location until Letter C.
            # swisseph falls back to its compiled-in defaults in that case, which
            # is why the golden fixtures still produce correct values.
            patch.logger.log(
                "  ⚠ %s does not yet exist — expected pre-Letter-C" %
                result.get('ephe_path')
            )
            patch.logger.log(
                "    swisseph uses fallback path; Letter C consolidates files."
            )
        return True
    except Exception as e:
        patch.errors.append("self_check parse error: %s" % e)
        patch.logger.log("  ✗ self_check parse error: %s" % e)
        return False


def run_golden_fixtures(patch):
    """Run the golden fixture harness. Letter B GATES on pass."""
    if not os.path.isfile(CHECK_ACCURACY_PATH):
        patch.errors.append("check_accuracy.py not found at %s" % CHECK_ACCURACY_PATH)
        patch.logger.log("  ✗ check_accuracy.py missing — is SEN-0004 installed?")
        return False

    try:
        result = subprocess.run(
            ['/opt/mythos/.venv/bin/python3', CHECK_ACCURACY_PATH],
            capture_output=True, text=True, timeout=60,
        )
        patch.logger.log("  — golden fixture output —")
        for line in result.stdout.splitlines():
            patch.logger.log("    %s" % line)
        if result.returncode == 0:
            patch.logger.log("  ✓ all 5 golden fixtures PASS")
            return True
        patch.errors.append(
            "golden fixture check failed with exit code %d" % result.returncode
        )
        patch.logger.log("  ✗ golden fixtures FAILED (exit %d)" % result.returncode)
        return False
    except subprocess.TimeoutExpired:
        patch.errors.append("check_accuracy.py timed out")
        patch.logger.log("  ✗ golden fixture check timed out")
        return False
    except Exception as e:
        patch.errors.append("golden fixture run error: %s" % e)
        patch.logger.log("  ✗ golden fixture run error: %s" % e)
        return False


# ═══════════════════════════════════════════════════════════════════════
# Main patch flow
# ═══════════════════════════════════════════════════════════════════════

patch = PatchBase(
    stream='SEN',
    number=5,
    description='ephemeris provider (letter B)',
    patch_type='MINOR',
)
patch.begin()

# === DEPLOY MODULE + PACKAGE INIT ===

os.makedirs('/opt/mythos/astrology', exist_ok=True)

patch.deploy_file(
    'opt/mythos/astrology/__init__.py',
    ASTROLOGY_INIT_PATH,
)

patch.deploy_file(
    'opt/mythos/astrology/ephemeris.py',
    EPHEMERIS_MODULE_PATH,
)

# === APPEND SE_EPHE_PATH TO .env ===

append_env_path(patch)

# === GATING: verify import + smoke test ===

print("\n" + "=" * 70)
print("VERIFICATION — ephemeris.py import + self_check")
print("=" * 70)

import_ok = verify_ephemeris_import(patch)

if not import_ok:
    print("\n✗ ephemeris.py import/smoke test FAILED.")
    print("  patch.errors populated — PatchBase will halt and roll back.")
else:
    # === GATING: run golden fixtures ===
    print("\n" + "=" * 70)
    print("GOLDEN FIXTURE GATING CHECK")
    print("=" * 70)
    print("Letter B gates on all 5 fixtures passing.\n")

    fixtures_ok = run_golden_fixtures(patch)

    if not fixtures_ok:
        print("\n✗ Golden fixtures FAILED.")
        print("  patch.errors populated — PatchBase will halt and roll back.")
    else:
        print("\n✓ All gating checks passed. ephemeris.py is live.")

print("=" * 70 + "\n")

patch.finish()
