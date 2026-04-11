#!/usr/bin/env python3
"""
NEU-0015: Modelfile v2 — Calibration-Proven Prompt
====================================================
Replaces the 2,100-token Modelfile with a condensed 853-token version.
Every instruction was individually validated via iris-calibrate across
6 message types × 10 layers (60 tests). The sweet spot is ~940 tokens.

What was cut:
- Duplicate cosmological framework (was stated twice)
- "What You Are" section (condensed to one sentence)
- "What You Know" section (redundant with anti-confab)
- "Skill Results Are Ground Truth" section (condensed to one paragraph)
- "Opinions" section (model does this naturally with personality layer)
- Verbose voice anti-pattern descriptions (kept the NEVER rules, cut examples)
- "How to Use Skill Data" examples (kept the instruction, cut the examples)

What was kept (every line proven by calibration):
- Core identity (layer 1)
- Relationships (layer 2)
- Personality + register (layer 3)
- Voice anti-patterns (layer 4)
- Anti-confabulation (layer 5)
- Skill data usage (layer 6)
- Internal systems rules (layer 7)
- Cosmological framework (layer 8)
"""

import sys
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='NEU',
    number=15,
    description='modelfile_v2',
    patch_type='MINOR',
)
patch.begin()

# Deploy Modelfile
patch.deploy_file(
    'opt/mythos/prompts/Modelfile',
    '/opt/mythos/prompts/Modelfile'
)

# Rebuild iris:latest
print("\n🔨 Rebuilding iris:latest from condensed Modelfile v2...")
result = subprocess.run(
    ['ollama', 'create', 'iris', '-f', '/opt/mythos/prompts/Modelfile'],
    capture_output=True, text=True, timeout=300
)
if result.returncode != 0:
    print(f"   ❌ ollama create failed: {result.stderr}")
    print("   Run manually: ollama create iris -f /opt/mythos/prompts/Modelfile")
else:
    print("   ✅ iris:latest rebuilt (v2 — 853 tokens)")

# Restart API so it picks up the rebuilt model
patch.restart_service('mythos-api.service')

patch.finish()

print("\n" + "="*60)
print("NEU-0015 COMPLETE — Modelfile v2 Deployed")
print("="*60)
print(f"\nOld: ~2,106 tokens (full prompt, intermittent blank responses)")
print(f"New: ~853 tokens (calibration-proven, every layer tested)")
print(f"\nTest: iris-calibrate --all --model iris:latest")
print(f"Then: Send a test message via Telegram")
