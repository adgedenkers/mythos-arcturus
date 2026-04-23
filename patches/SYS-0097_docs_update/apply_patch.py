#!/usr/bin/env python3
"""
SYS-0097: Docs update -- SYS-0096 ollama-analyze completion record

Appends completion record to TODO.md.
SYSTEM_PATCH.md does not exist on Arcturus (SYS-0089 never landed).

Tables: none. Services: none. Blast radius: LOW (docs only).
"""
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

TODO_PATH = '/opt/mythos/docs/TODO.md'

patch = PatchBase(
    stream='SYS',
    number=97,
    description='docs update -- SYS-0096 ollama-analyze completion record',
    patch_type='PATCH',
)
patch.begin()

print('\n' + '=' * 70)
print('SYS-0097 -- Docs update: ollama-analyze completion record')
print('=' * 70 + '\n')

print('PHASE 1: Update TODO.md')
print('-' * 70)

patch.append_to_file(
    TODO_PATH,
    content=(
        '\n### 2026-04-22: ollama-analyze microtool + PatchBase.ollama_analyze()\n'
        '\n'
        '- [x] **SYS-0096:** `ollama_analyze.py` deployed -- 4 preset tasks:\n'
        '  `sql-drift`, `py-signatures`, `review`, `sql-analyze`. Default model\n'
        '  `qwen3:30b-a3b`. Dry-run aware. Strips qwen3 `<think>` blocks.\n'
        '  Symlinked at `/opt/mythos/bin/ollama-analyze`.\n'
        '- [x] **PatchBase.ollama_analyze()** -- added manually to `patch_base.py`\n'
        '  (bootstrapping constraint: patch_base.py cannot edit itself via str_replace).\n'
        '  Now registered: `patchbase-methods` shows 24 public methods.\n'
        '- CLI verified: `ollama-analyze --list-tasks` and dry-run stub both clean.\n'
    ),
    guard='SYS-0096: `ollama_analyze.py` deployed',
    label='TODO.md -- SYS-0096 completion',
)
if patch.errors:
    patch.finish(); sys.exit(1)

print('\n' + '=' * 70)
print('✓ SYS-0097 complete -- TODO.md updated')
print('=' * 70 + '\n')

patch.finish()
