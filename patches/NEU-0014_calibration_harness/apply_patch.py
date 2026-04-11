#!/usr/bin/env python3
"""
NEU-0014: Prompt Calibration Harness
=====================================
Deploys iris-calibrate — a layered prompt testing tool that builds the
system prompt one instruction at a time to find the model's capacity ceiling.

Installs:
  /opt/mythos/tools/iris_calibrate.py
  /opt/mythos/bin/iris-calibrate (symlink)
  /opt/mythos/orchestrator/benchmark/calibration/ (results dir)
"""

import sys
import os

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='NEU',
    number=14,
    description='calibration_harness',
    patch_type='MINOR',
)
patch.begin()

# Deploy the tool
patch.deploy_file(
    'opt/mythos/tools/iris_calibrate.py',
    '/opt/mythos/tools/iris_calibrate.py'
)

# Make executable
os.chmod('/opt/mythos/tools/iris_calibrate.py', 0o755)

# Create results directory
os.makedirs('/opt/mythos/orchestrator/benchmark/calibration', exist_ok=True)

# Create CLI symlink in /opt/mythos/bin/ (adge-owned, on PATH)
symlink_path = '/opt/mythos/bin/iris-calibrate'
target_path = '/opt/mythos/tools/iris_calibrate.py'

if os.path.islink(symlink_path) or os.path.exists(symlink_path):
    os.remove(symlink_path)
os.symlink(target_path, symlink_path)
print(f"  ✓ Symlinked {symlink_path} → {target_path}")

patch.finish()

print("\n" + "="*60)
print("NEU-0014 COMPLETE — Calibration Harness Deployed")
print("="*60)
print()
print("Usage:")
print("  iris-calibrate                      # Interactive — step through layers")
print("  iris-calibrate --all                # Full battery — all layers at once")
print("  iris-calibrate --compare 0,4,7,9    # Side-by-side comparison")
print("  iris-calibrate --layer 0            # Single layer test")
print("  iris-calibrate --message casual     # Different test message")
print("  iris-calibrate --model qwen3:32b    # Different model")
print("  iris-calibrate --list-layers        # Show all layer definitions")
print("  iris-calibrate --list-messages      # Show available test messages")
print()
print("Start with:  iris-calibrate --compare 0,4,7,9")
print("This tests raw baseline, +voice rules, +grid rules, and full prompt")
print("side-by-side so you can see exactly where behavior degrades.")
