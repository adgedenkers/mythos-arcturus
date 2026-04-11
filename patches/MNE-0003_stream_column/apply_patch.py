#!/usr/bin/env python3
"""
MNE-0003: Add stream column to idea_backlog, seed stream assignments,
update /backlog command with stream display and filtering.
"""
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='MNE',
    number=3,
    description='Stream column + backlog filtering by stream',
    patch_type='MINOR',
)
patch.begin()

# ── 1. Run SQL migration ─────────────────────────────────────────────────────
patch.run_sql('opt/mythos/migrations/mne_0003_stream_column.sql')

# ── 2. Deploy updated backlog handler ────────────────────────────────────────
patch.deploy_file(
    'opt/mythos/telegram_bot/handlers/backlog_handler.py',
    '/opt/mythos/telegram_bot/handlers/backlog_handler.py'
)

# ── 3. Restart bot ───────────────────────────────────────────────────────────
patch.restart_service('mythos-bot.service')

patch.finish()
