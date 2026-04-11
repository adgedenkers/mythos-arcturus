import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=35,
    description='Trigger infrastructure — schema, seed data, CLI tool',
    patch_type='MAJOR',
)
patch.begin()

# Deploy SQL migration
patch.deploy_file(
    'opt/mythos/migrations/sys_0035_trigger_schema.sql',
    '/opt/mythos/migrations/sys_0035_trigger_schema.sql'
)

# Run the migration
patch.run_sql('opt/mythos/migrations/sys_0035_trigger_schema.sql')

# Deploy CLI tool
patch.deploy_file(
    'opt/mythos/bin/iris-trigger',
    '/opt/mythos/bin/iris-trigger'
)

# Make CLI executable
import subprocess
subprocess.run(['chmod', '+x', '/opt/mythos/bin/iris-trigger'], check=True)
patch.logger.log("  ✓ chmod +x iris-trigger")

patch.finish()
