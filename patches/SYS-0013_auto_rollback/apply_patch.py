import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=13,
    description='patch-install auto-rollback on failure + integrated artifact cleanup',
    patch_type='MINOR',
)
patch.begin()

# Deploy the updated patch-install
patch.deploy_file(
    'opt/mythos/bin/patch-install.sh',
    '/opt/mythos/bin/patch-install.sh'
)

import os
is_dry_run = os.environ.get('MYTHOS_PATCH_DRY_RUN', '0') == '1'

if not is_dry_run:
    os.chmod('/opt/mythos/bin/patch-install.sh', 0o755)
    patch.logger.log("  ✓ Set executable permissions")
else:
    patch.logger.log("  ✓ [validate] chmod — skipped (dry run)")

patch.finish()
