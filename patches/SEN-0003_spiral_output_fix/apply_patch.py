#!/usr/bin/env python3
"""
SEN-0003: Spiral Time Skill Output Fix
=======================================
Strips grid node names and emojis from the spiral_time skill summary.

The skill was returning summaries like:
  "Spiral Day 2 of Cycle 19 — 🌊 ECHO day. Memory. Reflection."

Iris was parroting "ECHO" and "🌊" in conversation because she's told
"skill results are ground truth." But she's also told "never reference
grid node names in conversation." Contradictory instructions — the skill
was setting her up to fail.

Now returns:
  "Spiral Day 2 of Cycle 19. Memory and reflection. What patterns are repeating?"

Node name and emoji stay in the data dict for internal/API use.
"""

import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SEN',
    number=3,
    description='spiral_output_fix',
    patch_type='PATCH',
)
patch.begin()

patch.deploy_file(
    'opt/mythos/skills/data/spiral_time.py',
    '/opt/mythos/skills/data/spiral_time.py'
)

# Restart the API so the skill engine picks up the new file
patch.restart_service('mythos-api.service')

patch.finish()

print("\n" + "="*60)
print("SEN-0003 COMPLETE — Spiral time no longer leaks grid nodes")
print("="*60)
print("\nOld: 'Spiral Day 2 of Cycle 19 — 🌊 ECHO day. Memory. Reflection.'")
print("New: 'Spiral Day 2 of Cycle 19. Memory and reflection. What patterns are repeating?'")
