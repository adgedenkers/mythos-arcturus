import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

import yaml
from pathlib import Path

patch_dir = Path(__file__).parent
with open(patch_dir / 'patch.yaml', 'r') as f:
    config = yaml.safe_load(f)

patch_number = config['number']
if patch_number == 'DRAFT':
    print("ERROR: Patch number is still DRAFT. Run mythos-diag streams and update patch.yaml")
    sys.exit(1)

patch = PatchBase(
    stream=config['stream'],
    number=int(patch_number),
    description=config['description'],
    patch_type=config.get('patch_type', 'MINOR'),
)
patch.begin()

# 1. Deploy post_install.py
patch.deploy_file(
    'opt/mythos/patches/scripts/post_install.py',
    '/opt/mythos/patches/scripts/post_install.py'
)

# 2. Modify patch_base.py to call the pipeline in finish()
pb_path = Path('/opt/mythos/patches/scripts/patch_base.py')
content = pb_path.read_text()

if 'post_install' not in content:
    # Find the insertion point: right before self.logger.write_logs(result)
    # in the finish() method
    old = '        self.logger.write_logs(result)'
    new = '''        # ── Post-install pipeline ──────────────────────────────────
        if not self.dry_run and len(self.errors) == 0:
            try:
                from post_install import run_pipeline
                pipeline_results = run_pipeline(
                    patch_id=self.patch_id,
                    stream=self.stream,
                    number=self.number,
                    description=self.description,
                    patch_type=self.patch_type,
                    files_deployed=self.files_deployed,
                    services_restarted=self.services_restarted,
                    sql_run=self.sql_run,
                    errors=self.errors,
                )
                result['pipeline'] = pipeline_results
            except Exception as e:
                self.logger.log(f"  ⚠ Post-install pipeline failed: {e}")
                result['pipeline_error'] = str(e)

        self.logger.write_logs(result)'''

    if old in content:
        content = content.replace(old, new)
        pb_path.write_text(content)
        print('  ✓ patch_base.py updated with post-install pipeline hook')
    else:
        print('  ⚠ Could not find insertion point in patch_base.py')
else:
    print('  ⊘ patch_base.py already has post_install hook')

# NOTE: This patch does NOT call finish() with the pipeline active,
# because the pipeline wasn't installed yet when this patch started.
# The NEXT patch will be the first one to use the pipeline.
patch.finish()
