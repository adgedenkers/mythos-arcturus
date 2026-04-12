#!/usr/bin/env python3
"""
SYS-0069: Session note for 2026-04-12 cleanup work.

Minimal pipeline smoke test. Deploys ONE markdown file to
/opt/mythos/docs/sessions/. No sudo, no services, no wrappers.
If this patch works cleanly, the patch pipeline is healthy.
"""
import sys
import os

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase


def main():
    patch = PatchBase(
        stream='SYS',
        number=69,
        description='session note for 2026-04-12 cleanup work',
        patch_type='PATCH',
    )
    patch.begin()

    # Ensure target directory exists (PatchBase.deploy_file also mkdirs, but
    # being explicit makes the intent clear for a docs-only patch).
    os.makedirs('/opt/mythos/docs/sessions', exist_ok=True)

    patch.deploy_file(
        'opt/mythos/docs/sessions/2026-04-12-cleanup.md',
        '/opt/mythos/docs/sessions/2026-04-12-cleanup.md',
    )

    patch.finish()


if __name__ == '__main__':
    main()
