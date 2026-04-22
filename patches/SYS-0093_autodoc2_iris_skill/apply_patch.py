import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=93,
    description='autodoc2 iris skill — natural language codebase queries',
    patch_type='MINOR',
)
patch.begin()

patch.deploy_file(
    'opt/mythos/skills/data/autodoc2_query.py',
    '/opt/mythos/skills/data/autodoc2_query.py',
)

patch.py_compile_check(
    '/opt/mythos/skills/data/autodoc2_query.py',
    'autodoc2_query.py',
)

# Verify file is present and class name is in source (no import needed)
content = patch.read_file('/opt/mythos/skills/data/autodoc2_query.py')
if content and 'class Autodoc2QuerySkill' in content:
    patch.logger.log('  \u2713 Autodoc2QuerySkill class present in deployed file')
else:
    patch.errors.append('Autodoc2QuerySkill class not found in deployed file')
    patch.logger.log('  \u2717 class check failed')

patch.finish()
