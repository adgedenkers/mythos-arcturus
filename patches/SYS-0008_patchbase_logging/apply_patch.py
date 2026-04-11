#!/usr/bin/env python3
"""
SYS-0008: PatchBase structured logging
Upgrades PatchBase to write JSON + human-readable logs to /tmp on every patch install.
Files written:
  /tmp/{PATCH_ID}_output.log   — human-readable (same as terminal)
  /tmp/{PATCH_ID}_result.json  — structured (for graph ingestion, clipboard, analysis)
  /tmp/last_patch_output.log   — always points to most recent
  /tmp/last_patch_result.json  — always points to most recent
"""
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=8,
    description='PatchBase structured logging',
    patch_type='MINOR',
)
patch.begin()

# ── 1. Deploy updated PatchBase ──────────────────────────────────────────────
patch.deploy_file(
    'opt/mythos/patches/scripts/patch_base.py',
    '/opt/mythos/patches/scripts/patch_base.py'
)

patch.finish()
