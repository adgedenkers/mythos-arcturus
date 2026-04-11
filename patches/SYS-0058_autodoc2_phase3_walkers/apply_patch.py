#!/usr/bin/env python3
"""
SYS-0058_autodoc2_phase3_walkers
================================
Phase 3 of AutoDoc2: adds 7 new language walkers (SQL, PHP, Go, Bash, YAML,
JSON, Rust) bringing total supported languages to 11. Also fixes the
empty-target bug where crawls against directories with zero source files
would still create stub AutodocCrawl nodes in Neo4j.

Deploys:
  - tools/autodoc2/walkers/sql_walker.py    (NEW)
  - tools/autodoc2/walkers/php_walker.py    (NEW)
  - tools/autodoc2/walkers/go_walker.py     (NEW)
  - tools/autodoc2/walkers/bash_walker.py   (NEW)
  - tools/autodoc2/walkers/yaml_walker.py   (NEW)
  - tools/autodoc2/walkers/json_walker.py   (NEW)
  - tools/autodoc2/walkers/rust_walker.py   (NEW)
  - tools/autodoc2/walkers/__init__.py      (UPDATED — registers all 11)
  - tools/autodoc2/filters.py               (UPDATED — adds .json/.rs maps,
                                              skips lockfiles)
  - tools/autodoc2/engine.py                (UPDATED — empty-target preflight)

No new dependencies needed: tree-sitter-language-pack 1.4.1 already
provides sql, php, go, bash, yaml, json, rust grammars.

No service restart needed. AutoDoc2 is a CLI tool.

After file deployment, smoke test runs:
  /opt/mythos/bin/autodoc2 --status
which must list all 11 supported languages or the patch fails.
"""

import sys
import shutil
import subprocess
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

PATCH_DIR = Path(__file__).parent.resolve()


def main():
    patch = PatchBase(
        stream='SYS',
        number=58,
        description='autodoc2_phase3_walkers',
        patch_type='MINOR',
    )
    patch.begin()

    # Deploy all 10 files
    files = [
        ('opt/mythos/tools/autodoc2/walkers/sql_walker.py',
         '/opt/mythos/tools/autodoc2/walkers/sql_walker.py'),
        ('opt/mythos/tools/autodoc2/walkers/php_walker.py',
         '/opt/mythos/tools/autodoc2/walkers/php_walker.py'),
        ('opt/mythos/tools/autodoc2/walkers/go_walker.py',
         '/opt/mythos/tools/autodoc2/walkers/go_walker.py'),
        ('opt/mythos/tools/autodoc2/walkers/bash_walker.py',
         '/opt/mythos/tools/autodoc2/walkers/bash_walker.py'),
        ('opt/mythos/tools/autodoc2/walkers/yaml_walker.py',
         '/opt/mythos/tools/autodoc2/walkers/yaml_walker.py'),
        ('opt/mythos/tools/autodoc2/walkers/json_walker.py',
         '/opt/mythos/tools/autodoc2/walkers/json_walker.py'),
        ('opt/mythos/tools/autodoc2/walkers/rust_walker.py',
         '/opt/mythos/tools/autodoc2/walkers/rust_walker.py'),
        ('opt/mythos/tools/autodoc2/walkers/__init__.py',
         '/opt/mythos/tools/autodoc2/walkers/__init__.py'),
        ('opt/mythos/tools/autodoc2/filters.py',
         '/opt/mythos/tools/autodoc2/filters.py'),
        ('opt/mythos/tools/autodoc2/engine.py',
         '/opt/mythos/tools/autodoc2/engine.py'),
    ]
    for src_rel, dst in files:
        patch.deploy_file(src_rel, dst)

    # Clear bytecode cache so the new modules import cleanly
    for pycache in (
        Path('/opt/mythos/tools/autodoc2/walkers/__pycache__'),
        Path('/opt/mythos/tools/autodoc2/__pycache__'),
    ):
        if pycache.exists():
            shutil.rmtree(pycache)
            print(f"  → Cleared {pycache}")

    # Smoke test: run autodoc2 --status and confirm all 11 languages registered
    print("  → Running smoke test: autodoc2 --status")
    result = subprocess.run(
        ['/opt/mythos/.venv/bin/python3', '/opt/mythos/tools/autodoc2/cli.py', '--status'],
        capture_output=True, text=True, timeout=30,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"  ✗ Smoke test stderr:\n{result.stderr}")
        raise RuntimeError(f"smoke test failed with exit {result.returncode}")

    expected = {'python', 'javascript', 'typescript', 'tsx',
                'sql', 'php', 'go', 'bash', 'yaml', 'json', 'rust'}
    out_lower = result.stdout.lower()
    missing = [lang for lang in expected if lang not in out_lower]
    if missing:
        raise RuntimeError(f"smoke test missing languages: {missing}")
    print(f"  ✓ Smoke test PASS — all 11 languages registered")

    patch.finish()


if __name__ == '__main__':
    main()
