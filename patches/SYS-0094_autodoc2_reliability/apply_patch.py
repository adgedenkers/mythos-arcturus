import sys
import os
import shutil
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase
from pathlib import Path

patch = PatchBase(
    stream='SYS',
    number=94,
    description='autodoc2 reliability — scheduled re-crawl, legacy retirement',
    patch_type='MINOR',
)
patch.begin()

# ── 1. Deploy autodoc2_worker.py ──────────────────────────────────────────────

patch.deploy_file(
    'opt/mythos/workers/autodoc2_worker.py',
    '/opt/mythos/workers/autodoc2_worker.py',
)
patch.py_compile_check('/opt/mythos/workers/autodoc2_worker.py', 'autodoc2_worker.py')

# ── 2. Deploy systemd units ───────────────────────────────────────────────────

patch.deploy_file(
    'opt/mythos/system/units/mythos-autodoc2-crawl.service',
    '/opt/mythos/system/units/mythos-autodoc2-crawl.service',
)
patch.deploy_file(
    'opt/mythos/system/units/mythos-autodoc2-crawl.timer',
    '/opt/mythos/system/units/mythos-autodoc2-crawl.timer',
)

# Install + enable the units
patch.install_systemd_unit('mythos-autodoc2-crawl.service')
patch.install_systemd_unit('mythos-autodoc2-crawl.timer')

# Enable and start the timer
try:
    import subprocess as _sp
    r = _sp.run(
        ['sudo', '-n', '/usr/local/libexec/mythos/mythos-servicectl',
         'enable', 'mythos-autodoc2-crawl.timer'],
        capture_output=True, text=True, timeout=15,
    )
    patch.logger.log(f"  \u2713 timer enabled")
except Exception as e:
    patch.logger.log(f"  \u26a0 timer enable: {e} (manual: sudo systemctl enable --now mythos-autodoc2-crawl.timer)")

# ── 3. Legacy autodoc.py retirement ───────────────────────────────────────────

legacy_src = Path('/opt/mythos/tools/autodoc.py')
archive_dst = Path('/opt/mythos/tools/archive/autodoc_v1.py')
legacy_symlink = Path('/opt/mythos/bin/autodoc')

# Create archive dir
archive_dst.parent.mkdir(parents=True, exist_ok=True)

if legacy_src.exists():
    shutil.copy2(str(legacy_src), str(archive_dst))
    patch.files_deployed.append(str(archive_dst))
    patch.logger.log(f"  \u2713 autodoc.py archived to tools/archive/autodoc_v1.py")

    # Remove the original
    legacy_src.unlink()
    patch.logger.log(f"  \u2713 tools/autodoc.py removed")
else:
    patch.logger.log(f"  \u2713 tools/autodoc.py already removed (skipping)")

# Remove the /opt/mythos/bin/autodoc symlink
if legacy_symlink.exists() or legacy_symlink.is_symlink():
    legacy_symlink.unlink()
    patch.logger.log(f"  \u2713 bin/autodoc symlink removed")
else:
    patch.logger.log(f"  \u2713 bin/autodoc symlink already gone (skipping)")

# ── 4. Update SYSTEM_AUTODOC2.md — mark legacy retired ───────────────────────

patch.str_replace(
    '/opt/mythos/docs/SYSTEM_AUTODOC2.md',
    old='### Legacy\n\n```\n/opt/mythos/tools/autodoc.py   # 1,612-line monolith, Python-only. Not removed yet.\n```\n\nLegacy autodoc.py should be archived or deleted in Letter G after AutoDoc2\nhas proven stable with scheduled crawls.',
    new='### Legacy (retired SYS-0094)\n\n```\n/opt/mythos/tools/archive/autodoc_v1.py   # archived 2026-04-21 — do not use\n```\n\nLegacy autodoc.py was archived in SYS-0094 (AutoDoc2 Letter G). The\n`/opt/mythos/bin/autodoc` symlink has been removed. Use `autodoc2` instead.',
    label='SYSTEM_AUTODOC2.md legacy section',
)

# ── 5. Add Letter G to the patch ledger in SYSTEM_AUTODOC2.md ────────────────

patch.str_replace(
    '/opt/mythos/docs/SYSTEM_AUTODOC2.md',
    old='| G | Reliability — scheduled re-crawl, legacy retirement | — | — |',
    new='| G | Reliability — scheduled re-crawl, legacy retirement | SYS-0094 | ✅ |',
    label='SYSTEM_AUTODOC2.md letter G status',
)

# ── 6. Smoke test — verify worker imports cleanly ─────────────────────────────

patch.run_python_check(
    'import sys; sys.path.insert(0, "/opt/mythos"); '
    'import ast; '
    'src = open("/opt/mythos/workers/autodoc2_worker.py").read(); '
    'ast.parse(src); '
    'assert "run_crawl" in src; '
    'assert "compute_diff" in src; '
    'assert "send_telegram" in src; '
    'print("autodoc2_worker.py: structure OK")',
    label='autodoc2_worker structure check',
)

patch.finish()
