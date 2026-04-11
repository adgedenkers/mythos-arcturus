#!/usr/bin/env python3
"""
SYS-0054_autodoc2_fix_treesitter

Fix the tree-sitter dependency from SYS-0053. The combination
  tree-sitter 0.25.2 + tree-sitter-languages 1.10.2
is broken — tree-sitter-languages was abandoned and never updated for the
breaking Language() API change in tree-sitter 0.22+. The replacement is
tree-sitter-language-pack (kreuzberg-dev/Goldziher fork), which is actively
maintained and pinned to current tree-sitter versions.

This patch:
  1. Uninstalls tree-sitter-languages from /opt/mythos/.venv
  2. Installs tree-sitter-language-pack
  3. Replaces python_walker.py with one that imports from tree_sitter_language_pack
  4. Verifies the Python grammar loads
"""

import sys
import subprocess

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=54,
    description='autodoc2_fix_treesitter',
    patch_type='PATCH',
)
patch.begin()

venv_pip = '/opt/mythos/.venv/bin/pip'

# 1. Uninstall the broken package
print("[fix] Uninstalling tree-sitter-languages (broken/abandoned)...")
subprocess.run(
    [venv_pip, 'uninstall', '-y', 'tree-sitter-languages'],
    check=False,  # ok if it's already gone
)

# 2. Install the maintained replacement
print("[fix] Installing tree-sitter-language-pack...")
subprocess.run(
    [venv_pip, 'install', '--upgrade', 'tree-sitter-language-pack'],
    check=True,
)

# 3. Deploy the fixed Python walker
patch.deploy_file(
    'opt/mythos/tools/autodoc2/walkers/python_walker.py',
    '/opt/mythos/tools/autodoc2/walkers/python_walker.py',
)

# 4. Verify
print("[fix] Verifying tree-sitter-language-pack import...")
try:
    result = subprocess.run(
        ['/opt/mythos/.venv/bin/python3', '-c',
         'from tree_sitter_language_pack import get_parser; '
         'p = get_parser("python"); '
         't = p.parse(b"def hello():\\n    return 42\\n"); '
         'print("tree-sitter OK, root node:", t.root_node.type, '
         '"children:", len(t.root_node.children))'],
        check=True, capture_output=True, text=True,
    )
    print(f"[fix] {result.stdout.strip()}")
except subprocess.CalledProcessError as e:
    print(f"[fix] FAILED:")
    print(f"      stdout: {e.stdout}")
    print(f"      stderr: {e.stderr}")
    sys.exit(1)

# 5. Smoke-test the autodoc2 import path end-to-end
print("[fix] Smoke-testing autodoc2 walker import...")
try:
    result = subprocess.run(
        ['/opt/mythos/.venv/bin/python3', '-c',
         'import sys; sys.path.insert(0, "/opt/mythos/tools"); '
         'from autodoc2.walkers import get_walker, supported_languages; '
         'w = get_walker("python"); '
         'print("walker:", w.__class__.__name__, '
         '"available:", w._available, '
         '"languages:", supported_languages())'],
        check=True, capture_output=True, text=True,
    )
    print(f"[fix] {result.stdout.strip()}")
except subprocess.CalledProcessError as e:
    print(f"[fix] FAILED:")
    print(f"      stdout: {e.stdout}")
    print(f"      stderr: {e.stderr}")
    sys.exit(1)

patch.finish()
