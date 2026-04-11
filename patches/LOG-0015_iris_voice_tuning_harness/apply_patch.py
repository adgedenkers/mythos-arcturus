#!/usr/bin/env python3
"""
LOG-0015: Iris Voice Tuning Harness
=====================================
Iterative prompt tuning loop for Iris voice quality.
Runs V-01 through V-06 against any model using the live
prompt_layers.yaml as the system prompt.
Results stored as JSONL — every iteration is comparable.
"""
import sys
import os
import stat
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='LOG',
    number=15,
    description='iris_voice_tuning_harness',
    patch_type='MINOR',
)
patch.begin()

patch.deploy_file(
    'opt/mythos/orchestrator/voice_tuning/tune.py',
    '/opt/mythos/orchestrator/voice_tuning/tune.py',
)

# Make executable
path = '/opt/mythos/orchestrator/voice_tuning/tune.py'
st = os.stat(path)
os.chmod(path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

# Create runs directory
os.makedirs('/opt/mythos/orchestrator/voice_tuning/runs', exist_ok=True)

# CLI symlink in /opt/mythos/bin/
bin_dir = '/opt/mythos/bin'
os.makedirs(bin_dir, exist_ok=True)
link_path = f'{bin_dir}/iris-voice-tune'
if os.path.islink(link_path):
    os.unlink(link_path)
os.symlink('/opt/mythos/orchestrator/voice_tuning/tune.py', link_path)

patch.finish()

print("\n✓ Voice tuning harness installed")
print("  Commands:")
print("    iris-voice-tune --model nous-hermes2:latest --label baseline")
print("    iris-voice-tune --model nous-hermes2:latest --label after-tweak")
print("    iris-voice-tune --compare baseline after-tweak")
print("    iris-voice-tune --list")
print("    iris-voice-tune --model nous-hermes2:latest --task V-01  # single task")
