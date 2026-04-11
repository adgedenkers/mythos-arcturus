#!/usr/bin/env python3
"""
SYS-0004: ARCHITECTURE.md documentation catch-up

Updates ARCHITECTURE.md to reflect system state as of 2026-03-04:
- All 92 PostgreSQL tables documented by stream ownership
- All 14 active services documented with stream attribution
- Voice memo pipeline (patches 0112-0113)
- Routines & calendar engine (patches 0096-0101)
- Knowledge map auto-rebuild (patch 0100)
- Consciousness pipeline feature flags (patch 0133)
- Message extractor + life context (patches 0097-0098)
- Stream patch naming convention (SYS-0003+)
- Full directory structure updated
- All Telegram commands documented
- Known issues section added
- Version bumped to 6.0.0
"""

import os
import sys
import shutil
import subprocess
import datetime

PATCH_DIR = os.path.dirname(os.path.abspath(__file__))
MYTHOS = "/opt/mythos"
DOCS = f"{MYTHOS}/docs"
TARGET = f"{DOCS}/ARCHITECTURE.md"

def run(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  ❌ Command failed: {cmd}")
        print(f"     stderr: {result.stderr.strip()}")
        sys.exit(1)
    return result

print("[SYS-0004] Architecture documentation catch-up")
print("=" * 55)

# Backup existing
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = f"{TARGET}.bak.{ts}"
if os.path.exists(TARGET):
    shutil.copy2(TARGET, backup_path)
    print(f"  ✓ Backup: {backup_path}")

# Deploy new file
src = os.path.join(PATCH_DIR, "opt/mythos/docs/ARCHITECTURE.md")
shutil.copy2(src, TARGET)
print(f"  ✓ ARCHITECTURE.md deployed (v6.0.0)")

# Update PATCH_HISTORY.md
history_path = f"{DOCS}/PATCH_HISTORY.md"
if os.path.exists(history_path):
    with open(history_path, "r") as f:
        content = f.read()

    entry = """
### SYS-0004: Architecture Documentation Catch-Up (v6.0.0)
**Date:** 2026-03-04
**Stream:** SYS
**Type:** MAJOR (documentation)

**What:**
- Full ARCHITECTURE.md rewrite to reflect system state as of 2026-03-04
- All 92 PostgreSQL tables documented and attributed to stream ownership
- All 14 active services listed with stream and patch-of-origin
- Added: voice memo pipeline (0112-0113), routines/calendar (0096-0101)
- Added: knowledge map auto-rebuild (0100), doc watcher service
- Added: consciousness pipeline feature flags (0133), message extractor (0098)
- Added: stream patch naming convention (SYS-0003+)
- Added: voice API endpoints (/api/voice/*)
- Updated: full directory structure, all Telegram commands, known issues
- Version bumped from 5.0.0 → 6.0.0

**Files modified:**
- `docs/ARCHITECTURE.md` — full replacement

"""

    # Insert after the first heading
    marker = "## Verification Template"
    if marker in content:
        new_content = content.replace(marker, entry + marker, 1)
        with open(history_path, "w") as f:
            f.write(new_content)
        print(f"  ✓ PATCH_HISTORY.md updated")
    else:
        # Append to end
        with open(history_path, "a") as f:
            f.write(entry)
        print(f"  ✓ PATCH_HISTORY.md appended")

print()
print("[SYS-0004] Complete ✓")
print(f"  ARCHITECTURE.md → v6.0.0")
print(f"  92 tables documented")
print(f"  14 services documented")
print(f"  Stream era recorded")
