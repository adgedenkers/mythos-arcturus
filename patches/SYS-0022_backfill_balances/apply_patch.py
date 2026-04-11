#!/usr/bin/env python3
"""
SYS-0022: Backfill Transaction Balances
- Reusable script to calculate NULL balances from last known anchor
- CLI command: backfill-balances
- Runs backfill immediately on install
- Updates accounts.current_balance to match final calculated balance
"""
import sys
import os
import stat
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=22,
    description='Backfill NULL transaction balances + CLI tool + update account balances',
    patch_type='MINOR',
)
patch.begin()

# ── 1. Deploy backfill script ───────────────────────────────
patch.deploy_file(
    'opt/mythos/finance/scripts/backfill_balances.py',
    '/opt/mythos/finance/scripts/backfill_balances.py'
)

# ── 2. Deploy CLI wrapper and symlink ────────────────────────
wrapper_src = os.path.join(os.path.dirname(__file__), 'opt/mythos/bin/backfill-balances')
wrapper_dst = '/opt/mythos/bin/backfill-balances'

# Copy wrapper
import shutil
shutil.copy2(wrapper_src, wrapper_dst)
os.chmod(wrapper_dst, os.stat(wrapper_dst).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
print(f'  ✓ Deployed {wrapper_dst}')

# ── 3. Run backfill now ─────────────────────────────────────
print('\n  Running balance backfill...')
import subprocess
result = subprocess.run(
    ['/opt/mythos/.venv/bin/python3', '/opt/mythos/finance/scripts/backfill_balances.py'],
    capture_output=True,
    text=True,
)
print(result.stdout)
if result.stderr:
    print(result.stderr)

if result.returncode != 0:
    print('  ⚠ Backfill had issues but patch continues')
else:
    print('  ✓ Balance backfill complete')

patch.finish()
