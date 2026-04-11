#!/usr/bin/env python3
"""
SYS-0023: Full Account Reimport Tool
- reimport_account.py script with balance verification
- CLI command: reimport-account
- Runs reimport for both USAA and Sunmark from the archive CSVs
"""
import sys
import os
import stat
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=23,
    description='Full account reimport tool with balance verification — wipe + reimport USAA and Sunmark',
    patch_type='MINOR',
)
patch.begin()

# ── 1. Deploy reimport script ───────────────────────────────
patch.deploy_file(
    'opt/mythos/finance/scripts/reimport_account.py',
    '/opt/mythos/finance/scripts/reimport_account.py'
)

# ── 2. Deploy CLI wrapper ───────────────────────────────────
import shutil
wrapper_src = os.path.join(os.path.dirname(__file__), 'opt/mythos/bin/reimport-account')
wrapper_dst = '/opt/mythos/bin/reimport-account'
shutil.copy2(wrapper_src, wrapper_dst)
os.chmod(wrapper_dst, os.stat(wrapper_dst).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
print(f'  ✓ Deployed {wrapper_dst}')

# ── 3. Reimport Sunmark ─────────────────────────────────────
sunmark_csv = os.path.expanduser('~/Downloads/sunmark-archive-20250101.CSV')
if os.path.exists(sunmark_csv):
    print(f'\n  Reimporting Sunmark from {sunmark_csv}...')
    result = subprocess.run(
        ['/opt/mythos/.venv/bin/python3', '/opt/mythos/finance/scripts/reimport_account.py',
         'sunmark', sunmark_csv],
        capture_output=True, text=True, timeout=120,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
else:
    print(f'  ⚠ Sunmark CSV not found at {sunmark_csv} — skipping')

# ── 4. Reimport USAA ────────────────────────────────────────
usaa_csv = os.path.expanduser('~/Downloads/usaa-archive-20250101.csv')
if os.path.exists(usaa_csv):
    print(f'\n  Reimporting USAA from {usaa_csv}...')
    result = subprocess.run(
        ['/opt/mythos/.venv/bin/python3', '/opt/mythos/finance/scripts/reimport_account.py',
         'usaa', usaa_csv],
        capture_output=True, text=True, timeout=120,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
else:
    print(f'  ⚠ USAA CSV not found at {usaa_csv} — skipping')

# ── 5. Restart API ───────────────────────────────────────────
patch.restart_service('mythos-api.service')

patch.finish()
