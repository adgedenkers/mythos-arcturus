"""MNE-0014 - meditation bgmix stream_loop fix"""
import sys, os
sys.path.insert(0, "/opt/mythos/patches/scripts")
from patch_base import PatchBase

patch = PatchBase(stream="MNE", number=14,
                  description="meditation bgmix stream_loop fix",
                  patch_type="PATCH")
patch.begin()

BASE = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(BASE, "opt", "mythos", "voice", "mmf.py")
patch.deploy_file(src, "/opt/mythos/voice/mmf.py")

with open("/opt/mythos/voice/mmf.py") as f:
    content = f.read()
assert "stream_loop" in content, "stream_loop not found after deploy"
assert '"-stream_loop", "-1"' in content, "stream_loop flag not in subprocess call"
print("✓ stream_loop fix verified")

patch.finish()
print("Done. Test: iris-meditate /tmp/creek_test.yaml")
