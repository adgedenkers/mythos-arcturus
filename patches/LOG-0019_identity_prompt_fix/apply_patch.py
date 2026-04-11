import sys
import os
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='LOG',
    number=19,
    description='Identity prompt fix — skill results ground truth rule, anti-hallucination for video intake',
    patch_type='PATCH',
)
patch.begin()

# ── 1. Deploy updated identity prompt ──
print("[1/2] Deploying updated iris_identity.md...")
patch.deploy_file(
    'opt/mythos/prompts/iris_identity.md',
    '/opt/mythos/prompts/iris_identity.md'
)
print("  ✓ iris_identity.md updated")
print("  ✓ Fixed: duplicate Seraphe/Fitz entries removed")
print("  ✓ Added: SKILL RESULTS ARE GROUND TRUTH section")
print("  ✓ Added: cosmological framework does not license data fabrication")

# ── 2. Restart API to load new prompt ──
print("[2/2] Restarting API service...")
import subprocess
subprocess.run(['sudo', 'systemctl', 'restart', 'mythos-api.service'], check=True)
import time
time.sleep(2)
result = subprocess.run(['sudo', 'systemctl', 'is-active', 'mythos-api.service'],
                       capture_output=True, text=True)
if 'active' in result.stdout:
    print("  ✓ mythos-api.service restarted")
else:
    print("  ⚠ API may not be running — check: sudo systemctl status mythos-api.service")

print()
print("=" * 50)
print("  LOG-0019 Complete")
print("=" * 50)
print()
print("  Changes to iris_identity.md:")
print("  1. Removed duplicate Seraphe/Fitz entries (lines 10-11)")
print("  2. Added SKILL RESULTS to 'what you can speak from' list")
print("  3. Added 'SKILL RESULTS ARE GROUND TRUTH' section")
print("     — Response MUST reflect actual skill data")
print("     — Do NOT invent video content, quotes, or summaries")
print("     — Confirm ingestion with title/creator/word count only")
print("  4. Added clarification to cosmological framework:")
print("     — Framework is for discussion/opinion, not fabricating data")
print()
print("  Test: Send a YouTube URL to Iris. She should confirm ingestion")
print("  with the real title and word count, not hallucinated content.")
print()

patch.finish()
