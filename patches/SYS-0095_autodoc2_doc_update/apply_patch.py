import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=95,
    description='autodoc2 documentation update — reflect completed A→G arc',
    patch_type='PATCH',
)
patch.begin()

patch.deploy_file(
    'opt/mythos/docs/SYSTEM_AUTODOC2.md',
    '/opt/mythos/docs/SYSTEM_AUTODOC2.md',
)

patch.deploy_file(
    'opt/mythos/docs/AUTODOC2_V2.md',
    '/opt/mythos/docs/AUTODOC2_V2.md',
)

patch.deploy_file(
    'opt/mythos/docs/autodoc2/NEXT_PATCH_SPEC.md',
    '/opt/mythos/docs/autodoc2/NEXT_PATCH_SPEC.md',
)

content = patch.read_file('/opt/mythos/docs/SYSTEM_AUTODOC2.md')
if content and 'SYS-0094' in content and 'COMPLETE' in content:
    patch.logger.log('  \u2713 SYSTEM_AUTODOC2.md: content verified')
else:
    patch.errors.append('SYSTEM_AUTODOC2.md missing expected content')
    patch.logger.log('  \u2717 SYSTEM_AUTODOC2.md: content check failed')

content2 = patch.read_file('/opt/mythos/docs/autodoc2/NEXT_PATCH_SPEC.md')
if content2 and 'Letter F' in content2:
    patch.logger.log('  \u2713 NEXT_PATCH_SPEC.md: Letter F spec confirmed')
else:
    patch.errors.append('NEXT_PATCH_SPEC.md missing Letter F content')
    patch.logger.log('  \u2717 NEXT_PATCH_SPEC.md: content check failed')

patch.finish()
