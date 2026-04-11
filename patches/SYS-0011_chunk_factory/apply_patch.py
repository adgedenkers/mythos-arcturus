import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=11,
    description='Chunk Factory — eval harness, challenge system, and chunk-builder skill reference',
    patch_type='MAJOR',
)
patch.begin()

# ── Eval harness core ─────────────────────────────────────────────────────
patch.deploy_file(
    'opt/mythos/eval/ollama_builder.py',
    '/opt/mythos/eval/ollama_builder.py'
)
patch.deploy_file(
    'opt/mythos/eval/chunk-eval.sh',
    '/opt/mythos/eval/chunk-eval.sh'
)

# ── Skill reference (used by eval harness to construct prompts) ───────────
patch.deploy_file(
    'opt/mythos/eval/skill_reference/SKILL.md',
    '/opt/mythos/eval/skill_reference/SKILL.md'
)

# ── Challenge template ────────────────────────────────────────────────────
patch.deploy_file(
    'opt/mythos/eval/templates/challenge_schema.json',
    '/opt/mythos/eval/templates/challenge_schema.json'
)

# ── First challenge: people_lookup ────────────────────────────────────────
patch.deploy_file(
    'opt/mythos/eval/challenges/people_lookup/challenge_spec.json',
    '/opt/mythos/eval/challenges/people_lookup/challenge_spec.json'
)
patch.deploy_file(
    'opt/mythos/eval/challenges/people_lookup/gold/people_lookup.py',
    '/opt/mythos/eval/challenges/people_lookup/gold/people_lookup.py'
)

# ── Gold standard skill also deployable to skills/data/ ──────────────────
patch.deploy_file(
    'opt/mythos/eval/challenges/people_lookup/gold/people_lookup.py',
    '/opt/mythos/skills/data/people_lookup.py'
)

# ── Post-deploy: permissions, dirs, symlink ──────────────────────────────
import subprocess
import os

if not patch.dry_run:
    # Make executable
    os.chmod('/opt/mythos/eval/ollama_builder.py', 0o755)
    os.chmod('/opt/mythos/eval/chunk-eval.sh', 0o755)
    patch.logger.log("  ✓ Set executable permissions")

    # Create results directory
    os.makedirs('/opt/mythos/eval/results', exist_ok=True)
    patch.logger.log("  ✓ Created eval/results/ directory")

    # Symlink chunk-eval to /usr/local/bin
    try:
        link_path = '/usr/local/bin/chunk-eval'
        if os.path.exists(link_path) or os.path.islink(link_path):
            os.remove(link_path)
        subprocess.run(
            ['sudo', 'ln', '-sf', '/opt/mythos/eval/chunk-eval.sh', link_path],
            check=True, capture_output=True
        )
        patch.logger.log("  ✓ Symlinked chunk-eval → /usr/local/bin/")
    except Exception as e:
        patch.logger.log(f"  ⚠ Could not create symlink: {e}")
else:
    patch.logger.log("  ✓ [validate] chmod, mkdir, symlink — skipped (dry run)")

# Restart API to pick up the new people_lookup skill
patch.restart_service('mythos-api.service')

patch.finish()
