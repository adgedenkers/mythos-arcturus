#!/usr/bin/env python3
"""
NEU-0017: Anti-Confabulation Strengthened (Modelfile v3)
=========================================================
Moves anti-confab rules to position #1 in the Modelfile (right after identity).
Expands coverage to include status-update fabrication — the model was inventing
what people are doing, what systems are running, and spiral day names.

Changes from v2:
- Anti-confab block moved from middle to position #1
- Added: "NEVER invent what people are doing"
- Added: "NEVER invent spiral day names, archetype names"
- Added: "If someone asks how things are going and you have no data, say it's been quiet"
- "How you're doing" instruction moved closer to anti-confab for reinforcement

Total: ~964 tokens (v2 was ~853). Still within calibration-proven sweet spot.
"""

import sys
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='NEU',
    number=17,
    description='anticonfab_v3',
    patch_type='PATCH',
)
patch.begin()

patch.deploy_file(
    'opt/mythos/prompts/Modelfile',
    '/opt/mythos/prompts/Modelfile'
)

print("\n🔨 Rebuilding iris:latest with anti-confab v3...")
result = subprocess.run(
    ['ollama', 'create', 'iris', '-f', '/opt/mythos/prompts/Modelfile'],
    capture_output=True, text=True, timeout=300
)
if result.returncode != 0:
    print(f"   ❌ ollama create failed: {result.stderr}")
else:
    print("   ✅ iris:latest rebuilt (v3 — 964 tokens, anti-confab at position #1)")

patch.restart_service('mythos-api.service')

patch.finish()

print("\n" + "="*60)
print("NEU-0017 COMPLETE — Anti-confab strengthened")
print("="*60)
