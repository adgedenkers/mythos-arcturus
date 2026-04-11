#!/usr/bin/env python3
"""
SYS-0009: Dry-run mode + clipboard flag for patch-install
- PatchBase gains dry-run support (MYTHOS_PATCH_DRY_RUN=1)
- patch-install gains --clip and --dry-run flags
- Updates .bashrc to source the new patch-install function
"""
import sys
import os
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=9,
    description='Dry-run mode + clipboard flag for patch-install',
    patch_type='MINOR',
)
patch.begin()

# ── 1. Deploy updated PatchBase with dry-run support ─────────────────────────
patch.deploy_file(
    'opt/mythos/patches/scripts/patch_base.py',
    '/opt/mythos/patches/scripts/patch_base.py'
)

# ── 2. Deploy new patch-install shell function ────────────────────────────────
patch.deploy_file(
    'opt/mythos/bin/patch-install.sh',
    '/opt/mythos/bin/patch-install.sh'
)

# ── 3. Deploy updated patches README ─────────────────────────────────────────
patch.deploy_file(
    'opt/mythos/patches/README.md',
    '/opt/mythos/patches/README.md'
)

# ── 4. Update .bashrc to source the new function ─────────────────────────────
bashrc_path = os.path.expanduser('~/.bashrc')
source_line = '# Mythos patch-install function\nsource /opt/mythos/bin/patch-install.sh'
old_source = 'source /opt/mythos/bin/patch-install.sh'

try:
    with open(bashrc_path, 'r') as f:
        bashrc = f.read()

    if old_source in bashrc:
        print("  · patch-install already sourced in .bashrc")
    else:
        # Check if there's an existing patch-install function defined inline
        if 'patch-install()' in bashrc:
            # Replace the inline function with the source line
            # Find the function boundaries
            lines = bashrc.split('\n')
            new_lines = []
            skip = False
            replaced = False
            for line in lines:
                if 'patch-install()' in line and not skip:
                    skip = True
                    replaced = True
                    new_lines.append('')
                    new_lines.append(source_line)
                    continue
                if skip:
                    # Skip until we find the closing brace
                    if line.strip() == '}':
                        skip = False
                    continue
                new_lines.append(line)

            if replaced:
                bashrc = '\n'.join(new_lines)
                with open(bashrc_path, 'w') as f:
                    f.write(bashrc)
                print("  ✓ Replaced inline patch-install function with source line in .bashrc")
            else:
                # Couldn't find boundaries, just append
                with open(bashrc_path, 'a') as f:
                    f.write(f'\n\n{source_line}\n')
                print("  ✓ Added patch-install source to .bashrc")
        else:
            with open(bashrc_path, 'a') as f:
                f.write(f'\n\n{source_line}\n')
            print("  ✓ Added patch-install source to .bashrc")
except Exception as e:
    patch.errors.append(f".bashrc update: {e}")
    print(f"  ⚠ .bashrc: {e}")

patch.finish()
