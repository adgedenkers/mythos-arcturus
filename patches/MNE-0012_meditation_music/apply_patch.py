"""
MNE-0012 — Meditation Music + OGG Segfault Fix

Changes:
  - voice/mmf.py       — rewritten: WAV+ffmpeg pipeline (fixes segfault),
                          background music mixing, global config support
  - voice/meditation_config.yaml — new global config file
  - bin/iris-music-fetch         — Freesound track downloader
  - public/meditations/music/    — music directory (created, empty)
"""
import sys, os
sys.path.insert(0, "/opt/mythos/patches/scripts")
from patch_base import PatchBase

patch = PatchBase(
    stream="MNE",
    number=12,
    description="meditation music and ogg fix",
    patch_type="MINOR",
)
patch.begin()

BASE = os.path.dirname(os.path.abspath(__file__))

patch.deploy_file(f"{BASE}/opt/mythos/voice/mmf.py",
                  "/opt/mythos/voice/mmf.py")
patch.deploy_file(f"{BASE}/opt/mythos/voice/meditation_config.yaml",
                  "/opt/mythos/voice/meditation_config.yaml")
patch.deploy_file(f"{BASE}/opt/mythos/bin/iris-music-fetch",
                  "/opt/mythos/bin/iris-music-fetch")

os.makedirs("/opt/mythos/public/meditations/music", exist_ok=True)
os.chmod("/opt/mythos/bin/iris-music-fetch", 0o755)

patch.finish()

print("""
✓ mmf.py updated — OGG segfault fixed (WAV→ffmpeg pipeline)
✓ Background music support added
✓ Global config: /opt/mythos/voice/meditation_config.yaml
✓ Music downloader: iris-music-fetch
✓ Music directory: /opt/mythos/public/meditations/music/

Next steps:
  1. Fetch some tracks:
       iris-music-fetch                     # list all
       iris-music-fetch --download bowls    # singing bowls + crystal bowl
       iris-music-fetch --download all      # everything

  2. Enable globally in meditation_config.yaml:
       background:
         track: singing_bowl_loop.ogg
         volume: 0.22

  3. Or enable per-meditation in the YAML spec:
       defaults:
         background:
           track: tibetan_bowl_deep.ogg
           volume: 0.18
           fade_in: 4.0
           fade_out: 6.0

  4. Re-render:
       iris-meditate /opt/mythos/public/meditations/scripts/expanded_bandwidth.yaml

  Without a track set, renders work exactly as before (no music).
""")
