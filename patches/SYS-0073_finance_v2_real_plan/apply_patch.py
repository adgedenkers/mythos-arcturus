#!/usr/bin/env python3
"""
SYS-0073: Overwrite FINANCE_V2.md with the real canonical plan.

The FINANCE_V2.md shipped in SYS-0072 was a shallow reconstruction from
memory. This patch replaces it with the actual 1,375-line plan consolidated
across five review rounds (Castor + Jeff Pro + Jeff Thinking), and deletes
the superseded FINANCE_V2_ARCHITECTURE.md (the real plan has its own
architecture section).
"""
import sys
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=73,
    description='finance_v2_real_plan',
    patch_type='MINOR',
)
patch.begin()

# Overwrite FINANCE_V2.md with the real plan
patch.deploy_file(
    'opt/mythos/docs/FINANCE_V2.md',
    '/opt/mythos/docs/FINANCE_V2.md',
)

# Delete the superseded architecture doc
superseded = Path('/opt/mythos/docs/FINANCE_V2_ARCHITECTURE.md')
if superseded.exists():
    print(f"Removing superseded doc: {superseded}")
    superseded.unlink()
    print("  Removed.")
else:
    print(f"{superseded} does not exist — nothing to remove.")

patch.finish()
