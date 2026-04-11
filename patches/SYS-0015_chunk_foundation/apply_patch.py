import sys
import os
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase
import subprocess

patch = PatchBase(
    stream='SYS',
    number=15,
    description='Chunk Foundation — chunk registry, pattern library, grinder engine, build plan',
    patch_type='MAJOR',
)
patch.begin()

# ── Chunk registry ────────────────────────────────────────────────────────
patch.deploy_file(
    'opt/mythos/chunks/CHUNK_CONTRACT.json',
    '/opt/mythos/chunks/CHUNK_CONTRACT.json'
)
patch.deploy_file(
    'opt/mythos/chunks/PLAN.md',
    '/opt/mythos/chunks/PLAN.md'
)

# ── Pattern library ───────────────────────────────────────────────────────
patch.deploy_file(
    'opt/mythos/patterns/PATTERNS.json',
    '/opt/mythos/patterns/PATTERNS.json'
)

# ── Grinder engine ────────────────────────────────────────────────────────
patch.deploy_file(
    'opt/mythos/eval/ollama_grinder.py',
    '/opt/mythos/eval/ollama_grinder.py'
)
patch.deploy_file(
    'opt/mythos/eval/chunk-grind.sh',
    '/opt/mythos/eval/chunk-grind.sh'
)

# ── Scoring v3 update for ollama_builder ──────────────────────────────────
patch.deploy_file(
    'opt/mythos/eval/ollama_builder.py',
    '/opt/mythos/eval/ollama_builder.py'
)

is_dry_run = os.environ.get('MYTHOS_PATCH_DRY_RUN', '0') == '1'

if not is_dry_run:
    # Permissions
    os.chmod('/opt/mythos/eval/ollama_grinder.py', 0o755)
    os.chmod('/opt/mythos/eval/chunk-grind.sh', 0o755)
    os.chmod('/opt/mythos/eval/ollama_builder.py', 0o755)
    patch.logger.log("  ✓ Set executable permissions")

    # Symlink chunk-grind
    try:
        link_path = '/usr/local/bin/chunk-grind'
        if os.path.exists(link_path) or os.path.islink(link_path):
            os.remove(link_path)
        subprocess.run(
            ['sudo', 'ln', '-sf', '/opt/mythos/eval/chunk-grind.sh', link_path],
            check=True, capture_output=True
        )
        patch.logger.log("  ✓ Symlinked chunk-grind → /usr/local/bin/")
    except Exception as e:
        patch.logger.log(f"  ⚠ Could not create symlink: {e}")
else:
    patch.logger.log("  ✓ [validate] chmod, symlink — skipped (dry run)")

patch.finish()
