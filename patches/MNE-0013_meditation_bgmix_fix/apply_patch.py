"""
MNE-0013 — Background music sample rate fix

Problem: background tracks (stereo, 44100–96000 Hz) don't mix with the
voice track (mono, 24000 Hz) — ffmpeg's amix silently drops the background.

Fix: add aresample=24000 and aformat=channel_layouts=mono to the ffmpeg
filter chain before mixing, normalizing the background to match the voice.
"""
import sys, os
sys.path.insert(0, "/opt/mythos/patches/scripts")
from patch_base import PatchBase

patch = PatchBase(
    stream="MNE",
    number=13,
    description="meditation bgmix sample rate fix",
    patch_type="PATCH",
)
patch.begin()

MMF_PATH = "/opt/mythos/voice/mmf.py"

# Read current file
with open(MMF_PATH, "r", encoding="utf-8") as f:
    content = f.read()

OLD = (
    '    filter_complex = (\n'
    '        f"[1:a]"\n'
    '        f"volume={volume},"\n'
    '        f"aloop=loop=-1:size=2e+09,"\n'
    '        f"afade=t=in:st=0:d={fade_in}"\n'
    '        f"[bg];"\n'
    '        f"[0:a][bg]amix=inputs=2:duration=first:dropout_transition={fade_out}[out]"\n'
    '    )'
)

NEW = (
    '    filter_complex = (\n'
    '        f"[1:a]"\n'
    '        f"aresample=24000,"\n'
    '        f"aformat=channel_layouts=mono,"\n'
    '        f"volume={volume},"\n'
    '        f"aloop=loop=-1:size=2e+09,"\n'
    '        f"afade=t=in:st=0:d={fade_in}"\n'
    '        f"[bg];"\n'
    '        f"[0:a][bg]amix=inputs=2:duration=first:dropout_transition={fade_out}[out]"\n'
    '    )'
)

if OLD not in content:
    print("ERROR: Could not find target filter_complex block in mmf.py")
    print("The file may have already been patched or differs from expected.")
    print("Manual fix — in /opt/mythos/voice/mmf.py, find the second")
    print("filter_complex = ( block in _mix_background() and add these")
    print("two lines after f\"[1:a]\":")
    print('        f"aresample=24000,"')
    print('        f"aformat=channel_layouts=mono,"')
    sys.exit(1)

patched = content.replace(OLD, NEW, 1)

if patched == content:
    print("ERROR: str.replace made no changes — patch may already be applied")
    sys.exit(1)

with open(MMF_PATH, "w", encoding="utf-8") as f:
    f.write(patched)

print(f"✓ Patched {MMF_PATH}")

# Verify the patch landed
with open(MMF_PATH, "r") as f:
    verify = f.read()
if "aresample=24000" in verify:
    print("✓ Verified: aresample=24000 present in mmf.py")
else:
    print("ERROR: Verification failed — aresample not found after write")
    sys.exit(1)

patch.finish()

print("""
✓ Background music mix fixed — sample rate normalization added.

Background tracks of any sample rate or channel count will now be
resampled to mono 24000 Hz before mixing with the voice track.

Re-render to test:
    iris-meditate /opt/mythos/public/meditations/scripts/expanded_bandwidth.yaml

Verify the creek is audible in the output.
""")
