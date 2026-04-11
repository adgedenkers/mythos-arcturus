#!/usr/bin/env python3
"""
SYS-0007: Patch Standards — ownership fix + PatchBase + install.sh template

1. Fix root-owned files in /opt/mythos (chown to adge:adge)
2. Deploy patch_base.py to /opt/mythos/patches/scripts/
3. Update sudoers to add missing rules
4. Bump STREAMS.json SYS counter to 8
"""

import os
import sys
import json
import shutil
import subprocess
import datetime
from pathlib import Path

PATCH_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
MYTHOS = Path("/opt/mythos")
DOCS = MYTHOS / "docs"
STREAMS_JSON = DOCS / "STREAMS.json"
PATCH_HISTORY = DOCS / "PATCH_HISTORY.md"

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def run(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  ❌ {cmd}\n     {result.stderr.strip()}")
        sys.exit(1)
    return result.stdout.strip()

print("[SYS-0007] Patch standards: ownership + PatchBase")
print("=" * 55)

# ── 1. Fix root-owned files in /opt/mythos ────────────────────────────────────
print("\n[1/4] Fixing root-owned files in /opt/mythos...")

# Find and chown all root-owned files/dirs under /opt/mythos
result = subprocess.run(
    "find /opt/mythos -maxdepth 4 -user root -not -path '/opt/mythos/.git/*'",
    shell=True, capture_output=True, text=True
)
root_files = [f for f in result.stdout.strip().split('\n') if f]

if root_files:
    for f in root_files:
        run(f"sudo chown adge:adge '{f}'")
        print(f"  ✓ chown adge:adge {f.replace('/opt/mythos/', '')}")
else:
    print("  ✓ No root-owned files found")

# Fix __pycache__ dirs
run("find /opt/mythos -name '__pycache__' -exec sudo chown -R adge:adge {} + 2>/dev/null || true", check=False)
print("  ✓ __pycache__ ownership fixed")

# ── 2. Deploy patch_base.py ────────────────────────────────────────────────────
print("\n[2/4] Deploying patch_base.py...")

scripts_dir = MYTHOS / "patches" / "scripts"
scripts_dir.mkdir(parents=True, exist_ok=True)

src = PATCH_DIR / "opt/mythos/patches/scripts/patch_base.py"
dest = scripts_dir / "patch_base.py"

if dest.exists():
    shutil.copy2(dest, f"{dest}.bak.{timestamp}")

shutil.copy2(src, dest)
dest.chmod(0o644)
print(f"  ✓ patch_base.py → {dest}")

# ── 3. Update STREAMS.json ────────────────────────────────────────────────────
print("\n[3/4] Updating STREAMS.json...")

if STREAMS_JSON.exists():
    with open(STREAMS_JSON) as f:
        data = json.load(f)

    data["streams"]["SYS"]["last_patch"] = 7
    data["streams"]["SYS"]["next_patch"] = 8
    data["streams"]["SYS"]["active_work"] = None
    data["meta"]["updated"] = datetime.datetime.now().isoformat()
    data["meta"]["updated_by"] = "SYS-0007_patch_standards"

    with open(STREAMS_JSON, "w") as f:
        json.dump(data, f, indent=2)
    print("  ✓ SYS next_patch → 8")
else:
    print("  ⚠ STREAMS.json not found")

# ── 4. Update PATCH_HISTORY ───────────────────────────────────────────────────
print("\n[4/4] Updating PATCH_HISTORY.md...")

entry = """
### SYS-0007: Patch Standards — Ownership Fix + PatchBase
**Date:** {date}
**Stream:** SYS
**Type:** MINOR

**What:**
- Chowned all root-owned files in /opt/mythos to adge:adge
- Deployed `patch_base.py` — standard base class for all apply_patch.py scripts
- PatchBase provides: deploy_file(), patch_file(), run_sql(), restart_service(),
  install_symlink(), syntax_check(), and automatic STREAMS.json + PATCH_HISTORY updates
- install.sh template no longer needs sudo for /opt/mythos file operations
- Only sudo needed going forward: systemctl, /usr/local/bin symlinks, psql as postgres

**New standard install.sh (4 lines, no sudo for file ops):**
```bash
#!/bin/bash
set -e
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
/opt/mythos/.venv/bin/python3 "$PATCH_DIR/apply_patch.py"
```

**New standard apply_patch.py pattern:**
```python
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase
patch = PatchBase(stream='SYS', number=8, description='my feature')
patch.begin()
patch.deploy_file('opt/mythos/some/file.py', '/opt/mythos/some/file.py')
patch.restart_service('mythos-bot.service')
patch.finish()  # auto-bumps STREAMS.json + writes PATCH_HISTORY
```

**Files created:**
- `/opt/mythos/patches/scripts/patch_base.py`

""".format(date=datetime.datetime.now().strftime("%Y-%m-%d"))

if PATCH_HISTORY.exists():
    content = PATCH_HISTORY.read_text()
    marker = "## Verification Template"
    if marker in content:
        PATCH_HISTORY.write_text(content.replace(marker, entry + marker, 1))
    else:
        with open(PATCH_HISTORY, "a") as f:
            f.write(entry)
    print("  ✓ PATCH_HISTORY.md updated")

print()
print("[SYS-0007] Complete ✓")
print()
print("  Going forward:")
print("  - No sudo needed for /opt/mythos file ops (adge owns it)")  
print("  - import PatchBase → auto STREAMS.json + PATCH_HISTORY")
print("  - sudo only for: systemctl, /usr/local/bin, psql as postgres")
