#!/usr/bin/env python3
"""
Patch 0107: Update patch monitor to run install.sh with sudo,
and update ARCHITECTURE.md with Patch Standard v2.

Changes to mythos_patch_monitor.py:
- install.sh now runs via: sudo bash install.sh
- This allows apply_patch.py scripts to write to root-owned dirs,
  restart services, and compile __pycache__ without permission errors

Changes to ARCHITECTURE.md:
- Replaces patch section with v2 standard (Python-based patches)
"""

import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

MONITOR = "/opt/mythos/mythos_patch_monitor.py"
ARCH_DOC = "/opt/mythos/docs/ARCHITECTURE.md"


def backup(path):
    if not Path(path).exists():
        print(f"  skip backup (not found): {path}")
        return
    dest = f"{path}.bak.{TIMESTAMP}"
    shutil.copy2(path, dest)
    print(f"  backup: {dest}")


def patch_file(path, replacements):
    with open(path, "r") as f:
        content = f.read()
    for old, new in replacements:
        if old not in content:
            print(f"  ✗ FAILED: Could not find expected text in {path}")
            print(f"    Looking for: {repr(old[:100])}...")
            sys.exit(1)
        count = content.count(old)
        content = content.replace(old, new)
        print(f"  replaced {count} occurrence(s)")
    with open(path, "w") as f:
        f.write(content)


def verify(path, must_contain):
    with open(path, "r") as f:
        content = f.read()
    for check in must_contain:
        if check not in content:
            print(f"  ✗ VERIFY FAILED: '{check}' not found in {path}")
            sys.exit(1)
    print(f"  ✓ {path} verified")


def main():
    print("=== Patch 0107: Patch Monitor v2 + Architecture Docs ===\n")

    # ── 1. Backups ──
    print("1. Creating backups...")
    backup(MONITOR)
    backup(ARCH_DOC)

    # ── 2. Patch the monitor: run install.sh with sudo ──
    print("\n2. Patching patch monitor...")
    patch_file(MONITOR, [
        # Replace the install.sh execution block
        (
            '                    try:\n'
            '                        # Make executable\n'
            '                        install_script.chmod(0o755)\n'
            '                        # Run it\n'
            '                        result = subprocess.run(\n'
            '                            [str(install_script)],\n'
            '                            cwd=str(extract_dir),\n'
            '                            capture_output=True,\n'
            '                            text=True,\n'
            '                            timeout=300\n'
            '                        )',
            '                    try:\n'
            '                        # Make executable\n'
            '                        install_script.chmod(0o755)\n'
            '                        # Run with sudo so patches can write root-owned files,\n'
            '                        # restart services, and compile __pycache__\n'
            '                        result = subprocess.run(\n'
            '                            ["sudo", "bash", str(install_script)],\n'
            '                            cwd=str(extract_dir),\n'
            '                            capture_output=True,\n'
            '                            text=True,\n'
            '                            timeout=300\n'
            '                        )',
        ),
    ])
    verify(MONITOR, [
        '["sudo", "bash", str(install_script)]',
    ])

    # ── 3. Update ARCHITECTURE.md patch section ──
    print("\n3. Updating ARCHITECTURE.md patch section...")

    PATCH_SECTION_OLD = (
        '## \U0001f527 Patch Monitor & Auto-Deploy (2026-02-16)\n'
        '\n'
        'The patch monitor watches `~/Downloads/` for `patch_NNNN_*.zip` files.\n'
        '\n'
        '**On detection:**\n'
        '1. Extracts to `/opt/mythos/patches/patch_NNNN_*/`\n'
        '2. Creates git tag `v{semantic_version}`\n'
        '3. Runs `install.sh`\n'
        '4. Pushes to GitHub (via SSH key env var in service)\n'
        '5. Sends Telegram notification\n'
        '\n'
        '**Install script requirements (learned 0091-0093):**\n'
        '- Use `sudo cp` \u2014 files in `/opt/mythos` are owned by root\n'
        '- Use `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` for path resolution\n'
        '- Use `sudo -u postgres psql -c` (not `-tAc`) when grepping for DB constraints\n'
        '\n'
        '**Service:** `mythos-patch-monitor.service`\n'
        '**GitHub push:** Configured via `Environment="GIT_SSH_COMMAND=ssh -i /home/adge/.ssh/id_ed25519 ..."` in service file'
    )

    PATCH_SECTION_NEW = (
        '## \U0001f527 Patch Monitor & Auto-Deploy\n'
        '\n'
        'The patch monitor watches `~/Downloads/` for `patch_NNNN_*.zip` files.\n'
        '\n'
        '**On detection:**\n'
        '1. Creates git snapshot (pre-patch tag)\n'
        '2. Extracts to `/opt/mythos/patches/patch_NNNN_*/`\n'
        '3. Runs `sudo bash install.sh`\n'
        '4. Commits + tags new version in git\n'
        '5. Pushes to GitHub (via SSH key env var in service)\n'
        '\n'
        '**Patch Standard v2 (established patch 0106):**\n'
        '\n'
        'Every patch contains:\n'
        '```\n'
        'patch_NNNN_description/\n'
        '\u251c\u2500\u2500 install.sh          # Thin bash wrapper (4 lines, calls apply_patch.py)\n'
        '\u251c\u2500\u2500 apply_patch.py      # All logic in pure Python\n'
        '\u2514\u2500\u2500 (optional files)    # SQL migrations, config files, etc.\n'
        '```\n'
        '\n'
        '**install.sh is always:**\n'
        '```bash\n'
        '#!/bin/bash\n'
        'set -e\n'
        'PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"\n'
        'sudo /opt/mythos/.venv/bin/python3 "$PATCH_DIR/apply_patch.py"\n'
        '```\n'
        '\n'
        '**apply_patch.py rules:**\n'
        '- Use `str.replace()` for exact string replacements (NEVER sed or heredocs)\n'
        '- Fail-fast: abort if expected old string not found\n'
        '- `py_compile` syntax check before restarting services\n'
        '- Auto-rollback if service fails to start\n'
        '- Backup all files before modifying\n'
        '\n'
        '**NEVER use in patches:** sed, bash heredocs, full file replacements for large files\n'
        '**ALWAYS use:** Pure Python apply_patch.py with exact string matching\n'
        '\n'
        '**Service:** `mythos-patch-monitor.service`\n'
        '**GitHub push:** Configured via `Environment="GIT_SSH_COMMAND=ssh -i /home/adge/.ssh/id_ed25519 ..."` in service file'
    )

    patch_file(ARCH_DOC, [(PATCH_SECTION_OLD, PATCH_SECTION_NEW)])
    verify(ARCH_DOC, [
        'Patch Standard v2',
        'apply_patch.py',
        'NEVER use in patches',
    ])

    # ── 4. Restart patch monitor ──
    print("\n4. Restarting patch monitor...")
    result = subprocess.run(
        ["sudo", "systemctl", "restart", "mythos-patch-monitor.service"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  ✗ Restart failed: {result.stderr}")
        sys.exit(1)

    time.sleep(3)

    result = subprocess.run(
        ["systemctl", "is-active", "mythos-patch-monitor.service"],
        capture_output=True, text=True
    )
    if result.stdout.strip() == "active":
        print("  ✓ Patch monitor restarted successfully")
    else:
        print("  ✗ Patch monitor not active! Rolling back...")
        shutil.copy2(f"{MONITOR}.bak.{TIMESTAMP}", MONITOR)
        subprocess.run(["sudo", "systemctl", "restart", "mythos-patch-monitor.service"])
        print("  Rolled back. Check: journalctl -u mythos-patch-monitor -n 20")
        sys.exit(1)

    print("\n=== Patch 0107 Complete ===")
    print("Patch monitor now runs install.sh with sudo")
    print("ARCHITECTURE.md updated with Patch Standard v2")
    print("\nAll future patches: install.sh → apply_patch.py (pure Python)")


if __name__ == "__main__":
    main()
