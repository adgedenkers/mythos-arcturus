import sys
import os
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=14,
    description='Chunk Factory v2 — fix code extractor truncation, richer error feedback, README',
    patch_type='MINOR',
)
patch.begin()

patch.deploy_file(
    'opt/mythos/eval/ollama_builder.py',
    '/opt/mythos/eval/ollama_builder.py'
)
patch.deploy_file(
    'opt/mythos/eval/README.md',
    '/opt/mythos/eval/README.md'
)

is_dry_run = os.environ.get('MYTHOS_PATCH_DRY_RUN', '0') == '1'
if not is_dry_run:
    os.chmod('/opt/mythos/eval/ollama_builder.py', 0o755)
    patch.logger.log("  ✓ Set executable permissions")
else:
    patch.logger.log("  ✓ [validate] chmod — skipped (dry run)")

patch.finish()
