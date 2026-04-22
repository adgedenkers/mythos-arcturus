#!/usr/bin/env python3
"""
SYS-0086: PatchBase microtool kit

Adds 8 new methods to PatchBase that eliminate the copy-paste
edit_file() / apply_edit() boilerplate every patch was hand-rolling:

  str_replace(path, old, new, label)
      Canonical in-place edit. Unique anchor check (0 or >1 = fail),
      backup, replace, post-edit verify, py_compile for .py files,
      appends to files_deployed. Dry-run validates anchor presence.

  append_to_file(path, content, guard, label)
      Append content to a file with optional idempotency guard string.

  prepend_to_file(path, content, guard, label)
      Same contract, writes at top of file.

  ensure_line_in_file(path, line, after, label)
      Ensures a single line exists. If `after` anchor provided, inserts
      after that line; otherwise appends. Idempotent.

  read_file(path, label)
      Returns file contents or None + error on missing file.

  assert_file_exists(path, label)
      Adds to self.errors if path missing. Use at phase gates.

  run_python_check(code, label, timeout)
      Runs a Python snippet in the Mythos venv. Replaces the
      subprocess.run([VENV_PYTHON, '-c', ...]) verification pattern.
      sys.path.insert(0, '/opt/mythos') prepended automatically.

  py_compile_check(path, label)
      Explicit py_compile gate, callable outside of str_replace —
      e.g. after deploy_file() of a .py you want to validate.

No schema changes. No service restarts. Blast radius: LOW.
"""
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

PATCH_BASE_PATH = '/opt/mythos/patches/scripts/patch_base.py'

patch = PatchBase(
    stream='SYS',
    number=87,
    description='PatchBase microtool kit — str_replace + 7 helpers',
    patch_type='MINOR',
)
patch.begin()

print('\n' + '=' * 70)
print('SYS-0087 — PatchBase microtool kit')
print('=' * 70 + '\n')

# ── PHASE 1: Pre-flight (old API only — new methods not live yet) ─
print('PHASE 1: Pre-flight')
print('-' * 70)
from pathlib import Path as _Path
if not _Path(PATCH_BASE_PATH).exists():
    patch.errors.append(f'patch_base.py not found: {PATCH_BASE_PATH}')
    patch.logger.log('  ✗ patch_base.py: not found')
    patch.finish()
    sys.exit(1)
patch.logger.log('  ✓ patch_base.py: exists')

# ── PHASE 2: Deploy new patch_base.py ────────────────────────────
# Must happen before any new methods are called — this IS the bootstrap.
print('\nPHASE 2: Deploy patch_base.py')
print('-' * 70)
patch.deploy_file(
    'opt/mythos/patches/scripts/patch_base.py',
    PATCH_BASE_PATH,
)
if patch.errors:
    patch.finish()
    sys.exit(1)

# ── PHASE 3: py_compile gate (manual — new methods not live yet) ──
print('\nPHASE 3: Syntax check')
print('-' * 70)
import py_compile as _pyc
try:
    _pyc.compile(PATCH_BASE_PATH, doraise=True)
    patch.logger.log('  ✓ patch_base.py: py_compile clean')
except _pyc.PyCompileError as e:
    patch.errors.append(f'py_compile failed: {e}')
    patch.logger.log(f'  ✗ patch_base.py: py_compile FAILED: {e}')
    patch.finish()
    sys.exit(1)

# ── PHASE 4: Smoke-test new methods via run_python_check ─────────
# patch_base.py is now on disk — new methods ARE live for this check.
print('\nPHASE 4: Smoke tests')
print('-' * 70)

smoke = """
import tempfile, os
from patch_base import PatchBase

p = PatchBase(stream='SYS', number=9999, description='smoke', patch_type='PATCH')
p.begin()

# ── read_file ────────────────────────────────────────────────────
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
    f.write('hello world')
    tmp = f.name

result = p.read_file(tmp)
assert result == 'hello world', f'read_file: got {repr(result)}'
print('  ✓ read_file')

# ── assert_file_exists (pass) ────────────────────────────────────
ok = p.assert_file_exists(tmp)
assert ok, 'assert_file_exists should return True for existing file'
print('  ✓ assert_file_exists (exists)')

# ── assert_file_exists (fail) ────────────────────────────────────
pre_errors = len(p.errors)
ok = p.assert_file_exists('/nonexistent/path/file.txt')
assert not ok, 'assert_file_exists should return False for missing file'
assert len(p.errors) == pre_errors + 1, 'should have added one error'
p.errors.pop()  # clear the test error
print('  ✓ assert_file_exists (missing)')

# ── str_replace ───────────────────────────────────────────────────
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
    f.write('the quick brown fox')
    tmp2 = f.name

ok = p.str_replace(tmp2, 'brown fox', 'lazy dog', 'str_replace test')
assert ok, 'str_replace should succeed'
assert open(tmp2).read() == 'the quick lazy dog', 'str_replace: content wrong'
print('  ✓ str_replace (basic)')

# str_replace idempotency
ok = p.str_replace(tmp2, 'brown fox', 'lazy dog', 'str_replace idempotent')
assert ok, 'str_replace idempotent should return True'
print('  ✓ str_replace (idempotent)')

# str_replace anchor-not-found
pre = len(p.errors)
ok = p.str_replace(tmp2, 'DOES_NOT_EXIST', 'x', 'str_replace miss')
assert not ok
assert len(p.errors) == pre + 1
p.errors.pop()
print('  ✓ str_replace (anchor not found)')

# ── append_to_file ────────────────────────────────────────────────
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
    f.write('line1')
    tmp3 = f.name

ok = p.append_to_file(tmp3, '\\nline2', guard='line2')
assert ok
assert 'line2' in open(tmp3).read()
print('  ✓ append_to_file')

# append idempotency via guard
ok = p.append_to_file(tmp3, '\\nline2', guard='line2')
assert ok
print('  ✓ append_to_file (idempotent guard)')

# ── prepend_to_file ───────────────────────────────────────────────
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
    f.write('body')
    tmp4 = f.name

ok = p.prepend_to_file(tmp4, 'header\\n', guard='header')
assert ok
content = open(tmp4).read()
assert content.startswith('header'), f'prepend failed: {repr(content)}'
print('  ✓ prepend_to_file')

# ── ensure_line_in_file (append mode) ────────────────────────────
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
    f.write('alpha\\nbeta\\n')
    tmp5 = f.name

ok = p.ensure_line_in_file(tmp5, 'gamma')
assert ok
assert 'gamma' in open(tmp5).read()
print('  ✓ ensure_line_in_file (append)')

# idempotency
ok = p.ensure_line_in_file(tmp5, 'gamma')
assert ok
print('  ✓ ensure_line_in_file (idempotent)')

# after-anchor mode
ok = p.ensure_line_in_file(tmp5, 'after_alpha', after='alpha')
assert ok
lines = open(tmp5).read().splitlines()
idx_alpha = next(i for i, l in enumerate(lines) if 'alpha' in l)
assert lines[idx_alpha + 1] == 'after_alpha', f'after-anchor insert wrong: {lines}'
print('  ✓ ensure_line_in_file (after anchor)')

# ── run_python_check ──────────────────────────────────────────────
ok = p.run_python_check(
    code="x = 1 + 1\\nassert x == 2\\nprint(f'  1+1={x}')",
    label='basic arithmetic',
    timeout=10,
)
assert ok, 'run_python_check should pass'
print('  ✓ run_python_check (pass)')

pre = len(p.errors)
ok = p.run_python_check(
    code="raise AssertionError('intentional failure')",
    label='intentional fail',
    timeout=10,
)
assert not ok
assert len(p.errors) == pre + 1
p.errors.pop()
print('  ✓ run_python_check (fail captured)')

# ── py_compile_check ─────────────────────────────────────────────
import tempfile
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write('def hello():\\n    return 42\\n')
    tmp_py = f.name

ok = p.py_compile_check(tmp_py, 'valid python')
assert ok
print('  ✓ py_compile_check (valid)')

with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write('def hello(\\n')
    tmp_bad_py = f.name

pre = len(p.errors)
ok = p.py_compile_check(tmp_bad_py, 'invalid python')
assert not ok
assert len(p.errors) == pre + 1
p.errors.pop()
print('  ✓ py_compile_check (invalid captured)')

# cleanup
for t in [tmp, tmp2, tmp3, tmp4, tmp5, tmp_py, tmp_bad_py]:
    try: os.unlink(t)
    except: pass

print('\\n  All smoke tests passed.')
"""

import subprocess as _sp
smoke_result = _sp.run(
    ['/opt/mythos/.venv/bin/python3', '-c',
     'import sys; sys.path.insert(0, "/opt/mythos/patches/scripts")\n' + smoke],
    capture_output=True, text=True, timeout=30,
)
for line in smoke_result.stdout.strip().splitlines():
    patch.logger.log(f'  {line}')
if smoke_result.returncode != 0:
    snippet = (smoke_result.stderr or '').strip()[:300]
    patch.errors.append(f'smoke tests failed: {snippet}')
    patch.logger.log('  ✗ smoke tests FAILED')
    if snippet:
        patch.logger.log(f'    {snippet[:200]}')
    patch.finish()
    sys.exit(1)
patch.validations.append('microtool smoke tests: all passed')

# ── Done ──────────────────────────────────────────────────────────
print('\n' + '=' * 70)
print('✓ SYS-0087 complete — PatchBase microtool kit deployed')
print('  New methods: str_replace, append_to_file, prepend_to_file,')
print('  ensure_line_in_file, read_file, assert_file_exists,')
print('  run_python_check, py_compile_check')
print('=' * 70 + '\n')

patch.finish()
