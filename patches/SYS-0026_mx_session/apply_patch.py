"""
SYS-0026: mx Session — Self-healing, intent-aware Mythos shell
"""

import subprocess
import sys
import py_compile
import pwd
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=26,
    description='mx session - self-healing intent-aware shell',
    patch_type='MINOR',
)
patch.begin()

PATCH_DIR = Path(__file__).parent

# ── 1. Deploy mx module files ─────────────────────────────────────────────────

for filename in ['mx_session.py', 'mx_intent.py', 'mx_logger.py', 'mx_config.yaml']:
    patch.deploy_file(
        str(PATCH_DIR / 'opt/mythos/mx' / filename),
        f'/opt/mythos/mx/{filename}',
    )
    print(f"  ✓ Deployed {filename}")

# Only deploy intents if not already present — preserve user edits
intents_target = Path('/opt/mythos/mx/mx_intents.yaml')
if not intents_target.exists():
    patch.deploy_file(
        str(PATCH_DIR / 'opt/mythos/mx/mx_intents.yaml'),
        '/opt/mythos/mx/mx_intents.yaml',
    )
    print("  ✓ mx_intents.yaml deployed (first install)")
else:
    print("  ℹ mx_intents.yaml exists — skipping to preserve your edits")

# ── 2. Make executable ────────────────────────────────────────────────────────

subprocess.run(['chmod', '+x', '/opt/mythos/mx/mx_session.py'], check=True)
print("  ✓ mx_session.py made executable")

# ── 3. Syntax check ───────────────────────────────────────────────────────────

for f in ['mx_session.py', 'mx_intent.py', 'mx_logger.py']:
    py_compile.compile(f'/opt/mythos/mx/{f}', doraise=True)
print("  ✓ Syntax check passed")

# ── 4. Install dependencies ───────────────────────────────────────────────────

subprocess.run(
    ['/opt/mythos/.venv/bin/pip', 'install', '--quiet', 'requests', 'pyyaml'],
    check=True
)
print("  ✓ Dependencies confirmed (requests, pyyaml)")

# ── 5. Symlink in /opt/mythos/bin/ ───────────────────────────────────────────

symlink = Path('/opt/mythos/bin/mx')
if symlink.exists() or symlink.is_symlink():
    symlink.unlink()
symlink.symlink_to('/opt/mythos/mx/mx_session.py')
print(f"  ✓ Symlink: /opt/mythos/bin/mx → /opt/mythos/mx/mx_session.py")

# ── 6. Create ~/.mx directory structure ──────────────────────────────────────

try:
    adge_home = Path(pwd.getpwnam('adge').pw_dir)
except KeyError:
    adge_home = Path.home()

for subdir in ['sessions', 'patterns', 'intents']:
    d = adge_home / '.mx' / subdir
    d.mkdir(parents=True, exist_ok=True)
print(f"  ✓ ~/.mx/{{sessions,patterns,intents}} created")

# ── 7. Smoke test ─────────────────────────────────────────────────────────────

result = subprocess.run(
    ['/opt/mythos/.venv/bin/python3', '/opt/mythos/mx/mx_session.py', '--version'],
    capture_output=True, text=True,
)
if result.returncode == 0:
    print(f"  ✓ Smoke test: {result.stdout.strip()}")
else:
    raise RuntimeError(f"Smoke test failed: {result.stderr.strip()}")

# ── Done ──────────────────────────────────────────────────────────────────────

patch.finish()

print()
print("╔══════════════════════════════════════════════════╗")
print("║  SYS-0026: mx is ready.                          ║")
print("║                                                  ║")
print("║  mx                  Start a session             ║")
print("║  mx --model X        Use specific Ollama model   ║")
print("║  mx --no-heal        Intent resolution only      ║")
print("║                                                  ║")
print("║  Edit intents:  /opt/mythos/mx/mx_intents.yaml   ║")
print("║  Session logs:  ~/.mx/sessions/                  ║")
print("║  Learned fixes: ~/.mx/patterns/errors.jsonl      ║")
print("╚══════════════════════════════════════════════════╝")
