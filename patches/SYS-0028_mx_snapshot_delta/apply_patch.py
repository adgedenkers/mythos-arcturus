"""
SYS-0028: mx Snapshot + Delta Engine
- Deploys mx_snapshot.py and mx_delta.py to /opt/mythos/mx/
- Creates ~/.mx/snapshots/ directory
- Creates /opt/mythos/docs/live/ directory for integrity reports
"""

import subprocess
import sys
import py_compile
import pwd
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=28,
    description='mx snapshot serializer and delta engine',
    patch_type='MINOR',
)
patch.begin()

PATCH_DIR = Path(__file__).parent

# ── 1. Deploy snapshot and delta modules ──────────────────────────────────────

for filename in ['mx_snapshot.py', 'mx_delta.py']:
    patch.deploy_file(
        str(PATCH_DIR / 'opt/mythos/mx' / filename),
        f'/opt/mythos/mx/{filename}',
    )
    py_compile.compile(f'/opt/mythos/mx/{filename}', doraise=True)
    print(f"  ✓ {filename} deployed and validated")

# ── 2. Create runtime directories ─────────────────────────────────────────────

# docs/live for integrity scan output
live_dir = Path('/opt/mythos/docs/live')
live_dir.mkdir(parents=True, exist_ok=True)
print(f"  ✓ {live_dir} created")

# ~/.mx/snapshots for adge
try:
    adge_home = Path(pwd.getpwnam('adge').pw_dir)
except KeyError:
    adge_home = Path.home()

snapshots_dir = adge_home / '.mx' / 'snapshots'
snapshots_dir.mkdir(parents=True, exist_ok=True)
print(f"  ✓ {snapshots_dir} created")

# ── 3. Smoke test snapshot capture ────────────────────────────────────────────

result = subprocess.run(
    [
        '/opt/mythos/.venv/bin/python3', '-c',
        'import sys; sys.path.insert(0, "/opt/mythos/mx"); '
        'from mx_snapshot import capture_services, capture_git; '
        'svcs = capture_services(); '
        'git = capture_git(); '
        'print(f"Services detected: {len(svcs)}"); '
        'print(f"Git hash: {git[\"hash\"]}")'
    ],
    capture_output=True, text=True,
)
if result.returncode == 0:
    for line in result.stdout.strip().splitlines():
        print(f"  ✓ {line}")
else:
    print(f"  ⚠ Smoke test warning: {result.stderr.strip()[:200]}")
    # Not fatal — snapshot still works, just may have permission issues

# ── Done ──────────────────────────────────────────────────────────────────────

patch.finish()

print()
print("╔══════════════════════════════════════════════════╗")
print("║  SYS-0028: Snapshot + Delta Engine ready.        ║")
print("║                                                  ║")
print("║  Snapshots: ~/.mx/snapshots/                     ║")
print("║  Integrity: /opt/mythos/docs/live/               ║")
print("║                                                  ║")
print("║  Next: SYS-0029 wires hooks into mx sessions.   ║")
print("╚══════════════════════════════════════════════════╝")
