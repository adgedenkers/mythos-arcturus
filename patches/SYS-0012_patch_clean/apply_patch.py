import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=12,
    description='patch-clean function — full rollback of deployed patches',
    patch_type='MINOR',
)
patch.begin()

# Deploy the script
patch.deploy_file(
    'opt/mythos/bin/patch-clean.sh',
    '/opt/mythos/bin/patch-clean.sh'
)

if not patch.dry_run:
    import os
    import subprocess

    # Make executable
    os.chmod('/opt/mythos/bin/patch-clean.sh', 0o755)
    patch.logger.log("  ✓ Set executable permissions")

    # Add source line to .bashrc if not already present
    bashrc = os.path.expanduser('~/.bashrc')
    source_line = 'source /opt/mythos/bin/patch-clean.sh'

    with open(bashrc, 'r') as f:
        content = f.read()

    if source_line not in content:
        with open(bashrc, 'a') as f:
            f.write(f'\n# Mythos patch-clean function\n{source_line}\n')
        patch.logger.log("  ✓ Added source line to .bashrc")
    else:
        patch.logger.log("  ✓ .bashrc already has source line")
else:
    patch.logger.log("  ✓ [validate] chmod, bashrc — skipped (dry run)")

patch.finish()
