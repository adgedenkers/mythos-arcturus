#!/usr/bin/env python3
"""
SYS-0099: Deploy SYSTEM_PATCH.md

SYSTEM_PATCH.md is the canonical state doc for the Mythos patch system,
documenting the full PatchBase API (24 methods), the patch-install workflow,
the post-install pipeline, and all non-negotiable rules.

It was built during SYS-0089 but never landed because that patch kept
rolling back on unrelated str_replace failures. This patch just deploys
the file -- nothing else.

Tables: none. Services: none. Blast radius: LOW (new file only).
"""
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=99,
    description='deploy SYSTEM_PATCH.md -- patch system canonical state doc',
    patch_type='PATCH',
)
patch.begin()

print('\n' + '=' * 70)
print('SYS-0099 -- Deploy SYSTEM_PATCH.md')
print('=' * 70 + '\n')

patch.deploy_file(
    'opt/mythos/docs/SYSTEM_PATCH.md',
    '/opt/mythos/docs/SYSTEM_PATCH.md',
)
if patch.errors:
    patch.finish(); sys.exit(1)

patch.logger.log('  ✓ SYSTEM_PATCH.md -- canonical patch system state doc deployed')

print('\n' + '=' * 70)
print('✓ SYS-0099 complete')
print('=' * 70 + '\n')

patch.finish()
