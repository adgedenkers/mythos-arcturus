import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=49,
    description='TODO.md cleanup — deduplicate, update active work, restructure',
    patch_type='PATCH',
)
patch.begin()

patch.deploy_file('opt/mythos/docs/TODO.md', '/opt/mythos/docs/TODO.md')

patch.finish()
print("\n✅ SYS-0049 complete — TODO.md cleaned up")
print("   Removed: duplicated sections, stale references, completed items still in 'next up'")
print("   Added: today's session work, LoRA as priority #1, Phase 1.9 in roadmap")
print("   Restructured: backlog renumbered, completions condensed, conventions grouped")
