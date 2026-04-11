import sys
import os
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='MNE',
    number=6,
    description='Fix YouTube transcript intake for youtube-transcript-api >= 1.2.0',
    patch_type='PATCH',
)
patch.begin()

# ── 1. Deploy updated skill ──
print("[1/3] Deploying updated youtube_intake.py...")
patch.deploy_file(
    'opt/mythos/skills/data/youtube_intake.py',
    '/opt/mythos/skills/data/youtube_intake.py'
)
print("  ✓ youtube_intake.py updated")

# ── 2. Clear pycache ──
print("[2/3] Clearing skill cache...")
import glob
for f in glob.glob('/opt/mythos/skills/data/__pycache__/youtube_intake*'):
    os.remove(f)
    print(f"  ✓ Removed {os.path.basename(f)}")

# ── 3. Test the fix ──
print("[3/3] Testing transcript fetch...")
try:
    sys.path.insert(0, '/opt/mythos/skills/data')
    # Direct test of the new API pattern
    from youtube_transcript_api import YouTubeTranscriptApi
    api = YouTubeTranscriptApi()
    result = api.fetch('8S0FDjFBj8o')  # TEDx talk we already have
    snippet_count = len(result.snippets)
    print(f"  ✓ API works: fetched {snippet_count} snippets from test video")
except Exception as e:
    print(f"  ⚠ Test failed: {e}")
    print("    The skill is deployed but may need further debugging")

print()
print("=" * 50)
print("  MNE-0006 Complete")
print("=" * 50)
print()
print("  Fixed: youtube-transcript-api 1.2.x compatibility")
print("  Changed: YouTubeTranscriptApi() is now instance-based")
print("  Changed: .fetch() returns FetchedTranscript with .snippets")
print("  Changed: snippets have .text/.start/.duration attributes (not dict keys)")
print()
print("  To retry failed videos, send the URLs to Iris again.")
print("  Failed videos from March 12-19:")
print("    https://youtu.be/DbVQPD5t9A0")
print("    https://www.youtube.com/watch?v=glcL5_3IoSo")
print("    https://youtu.be/iBLHJLfrvRY")
print("    https://youtu.be/8s88UdL4unE")
print()

patch.finish()
