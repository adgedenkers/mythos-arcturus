#!/usr/bin/env python3
"""
SYS-0010: Dry-run prompt — after successful dry-run, ask to proceed or abort.
"""
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=10,
    description='Dry-run auto-prompt to proceed or abort',
    patch_type='PATCH',
)
patch.begin()

patch.deploy_file(
    'opt/mythos/bin/patch-install.sh',
    '/opt/mythos/bin/patch-install.sh'
)

patch.finish()
