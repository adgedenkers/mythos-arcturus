#!/usr/bin/env python3
"""
SYS-0072: Finance v2 plan + architecture docs + v1 cleanup.

Creates the two canonical Finance v2 docs on disk, drops all ten v1_*
finance tables, and removes /opt/mythos/finance/ if it exists. No schema,
no code — just the plan and a clean slate.
"""
import sys
import shutil
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=72,
    description='finance_v2_plan',
    patch_type='MINOR',
)
patch.begin()

# --- 1. Deploy the two docs ---
patch.deploy_file(
    'opt/mythos/docs/FINANCE_V2.md',
    '/opt/mythos/docs/FINANCE_V2.md',
)
patch.deploy_file(
    'opt/mythos/docs/FINANCE_V2_ARCHITECTURE.md',
    '/opt/mythos/docs/FINANCE_V2_ARCHITECTURE.md',
)

# --- 2. Drop v1 tables (static SQL shipped with patch) ---
patch.run_sql('drop_v1.sql')

# --- 3. Remove /opt/mythos/finance/ if it exists ---
finance_dir = Path('/opt/mythos/finance')
if finance_dir.exists():
    print(f"Removing {finance_dir} ...")
    shutil.rmtree(finance_dir)
    print("  Removed.")
else:
    print(f"{finance_dir} does not exist — nothing to remove.")

patch.finish()
