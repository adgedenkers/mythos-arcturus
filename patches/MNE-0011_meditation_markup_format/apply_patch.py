"""MNE-0011 — Meditation Markup Format (MMF) renderer and YAML spec."""
import sys, os
sys.path.insert(0, "/opt/mythos/patches/scripts")
from patch_base import PatchBase

patch = PatchBase(
    stream="MNE",
    number=11,
    description="meditation markup format",
    patch_type="MINOR",
)
patch.begin()

BASE = os.path.dirname(os.path.abspath(__file__))

patch.deploy_file(f"{BASE}/opt/mythos/voice/mmf.py",
                  "/opt/mythos/voice/mmf.py")
patch.deploy_file(f"{BASE}/opt/mythos/bin/iris-meditate",
                  "/opt/mythos/bin/iris-meditate")
patch.deploy_file(
    f"{BASE}/opt/mythos/public/meditations/scripts/expanded_bandwidth.yaml",
    "/opt/mythos/public/meditations/scripts/expanded_bandwidth.yaml",
)

os.makedirs("/opt/mythos/public/meditations/scripts", exist_ok=True)
os.chmod("/opt/mythos/bin/iris-meditate", 0o755)

patch.finish()

print("""
✓ MMF renderer deployed: /opt/mythos/voice/mmf.py
✓ CLI updated: iris-meditate now handles .txt and .yaml
✓ First spec: /opt/mythos/public/meditations/scripts/expanded_bandwidth.yaml

Test:
    iris-meditate --estimate /opt/mythos/public/meditations/scripts/expanded_bandwidth.yaml
    iris-meditate /opt/mythos/public/meditations/scripts/expanded_bandwidth.yaml

Convert existing .txt to .yaml skeleton:
    iris-meditate --to-yaml /opt/mythos/public/meditations/scripts/somefile.txt
""")
