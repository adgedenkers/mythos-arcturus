#!/usr/bin/env python3
"""
SYS-0005: mythos-diag — Standardized terminal diagnostic command

Installs /opt/mythos/bin/mythos-diag as an executable shell command.
Symlinks to /usr/local/bin/mythos-diag for global access.

Usage after install:
    mythos-diag              # full summary
    mythos-diag services     # service states
    mythos-diag db           # postgres + neo4j + redis
    mythos-diag hw           # disk/RAM/GPU
    mythos-diag patches      # version + stream counters
    mythos-diag streams      # stream ownership table
    mythos-diag redis        # redis keyspace detail
    mythos-diag workers      # worker service states
    mythos-diag all          # everything
    mythos-diag help         # help
"""

import os
import sys
import shutil
import subprocess
import datetime

PATCH_DIR = os.path.dirname(os.path.abspath(__file__))
MYTHOS = "/opt/mythos"
BIN_DIR = f"{MYTHOS}/bin"
SCRIPT_NAME = "mythos-diag"
TARGET = f"{BIN_DIR}/{SCRIPT_NAME}"
SYMLINK = f"/usr/local/bin/{SCRIPT_NAME}"

def run(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  ❌ Command failed: {cmd}")
        print(f"     stderr: {result.stderr.strip()}")
        sys.exit(1)
    return result

print("[SYS-0005] mythos-diag terminal command")
print("=" * 50)

# Ensure bin dir exists
run(f"sudo mkdir -p {BIN_DIR}")

# Backup existing if present
if os.path.exists(TARGET):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run(f"sudo cp {TARGET} {TARGET}.bak.{ts}")
    print(f"  ✓ Backup: {TARGET}.bak.{ts}")

# Deploy script
src = os.path.join(PATCH_DIR, f"opt/mythos/bin/{SCRIPT_NAME}")
run(f"sudo cp {src} {TARGET}")
run(f"sudo chmod +x {TARGET}")
print(f"  ✓ Deployed: {TARGET}")

# Symlink to /usr/local/bin for global access
if os.path.exists(SYMLINK) or os.path.islink(SYMLINK):
    run(f"sudo rm -f {SYMLINK}")
run(f"sudo ln -s {TARGET} {SYMLINK}")
print(f"  ✓ Symlink: {SYMLINK} → {TARGET}")

# Verify
result = run(f"{TARGET} help", check=False)
if result.returncode == 0:
    print(f"  ✓ Script runs cleanly")
else:
    print(f"  ⚠ Script returned non-zero (may be OK — some checks need sudo)")

# Update PATCH_HISTORY
history = f"{MYTHOS}/docs/PATCH_HISTORY.md"
entry = """
### SYS-0005: mythos-diag Terminal Command
**Date:** 2026-03-04
**Stream:** SYS
**Type:** MINOR (new tooling)

**What:**
- New shell command: `mythos-diag` (installed to `/opt/mythos/bin/`, symlinked to `/usr/local/bin/`)
- Blocks: services, workers, db, hw, patches, streams, redis, summary, all
- Reads `docs/STREAMS.json` directly for live stream counter display
- Colored output, fail/warn/ok indicators
- Completes backlog item #13

**Files created:**
- `/opt/mythos/bin/mythos-diag`
- `/usr/local/bin/mythos-diag` (symlink)

"""

if os.path.exists(history):
    with open(history, "r") as f:
        content = f.read()
    marker = "## Verification Template"
    if marker in content:
        with open(history, "w") as f:
            f.write(content.replace(marker, entry + marker, 1))
    else:
        with open(history, "a") as f:
            f.write(entry)
    print(f"  ✓ PATCH_HISTORY.md updated")

print()
print("[SYS-0005] Complete ✓")
print(f"  Run: mythos-diag")
print(f"  Run: mythos-diag help")
