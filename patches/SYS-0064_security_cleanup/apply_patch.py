#!/usr/bin/env python3
"""
SYS-0064: Security cleanup — remove dangerous 'cp *' rule from mythos-monitor.

WHAT THIS DOES:
  1. Verifies running as root (it must — patch-install invokes us via sudo).
  2. Backs up /etc/sudoers.d/mythos-monitor → /tmp/mythos-monitor.pre_SYS-0064.bak
  3. Replaces the file with a cleaned version that retains ONLY the
     'bash install.sh' rules (needed for patch-install to function).
     Removes:
       - /usr/bin/cp *           ← effective root via file overwrite (DANGEROUS)
       - systemctl restart mythos-*  ← duplicated in /etc/sudoers.d/mythos
       - systemctl restart mythos-api.service  ← duplicate
       - systemctl restart mythos-bot.service  ← duplicate
       - psql -d mythos *  ← duplicated in /etc/sudoers.d/mythos
  4. Validates with `visudo -c` BEFORE installing — abort if invalid.
  5. Atomic install with mode 0440, owner root:root.
  6. Verifies the dangerous rule is gone.

WHAT THIS DOES NOT DO:
  - Modify any historical SYS-* patches that use 'sudo cp'. They are
    frozen history. Per skill: never modify shipped patches.
  - Touch /etc/sudoers.d/mythos (the keeper file with the legitimate rules).
  - Touch /etc/sudoers.d/mythos-patches (SYS-0062 wrapper allowlist).
  - Solve the broader 'bash install.sh' privilege escalation. That's a
    separate architectural issue for a future patch.

This patch must run as root. It will be invoked via 'sudo bash install.sh'
through the patch-install workflow (which uses the existing bash install.sh
sudoers rule that we are preserving).
"""
import sys
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

MONITOR_FILE = Path('/etc/sudoers.d/mythos-monitor')
BACKUP_FILE = Path('/tmp/mythos-monitor.pre_SYS-0064.bak')

NEW_CONTENT = """# /etc/sudoers.d/mythos-monitor
# Cleaned by SYS-0064 (2026-04-11).
#
# REMOVED (security findings from SYS-0062 install audit):
#   - /usr/bin/cp *           ← effective root via arbitrary file overwrite
#   - systemctl restart mythos-*           ← duplicated in /etc/sudoers.d/mythos
#   - systemctl restart mythos-api.service ← duplicate
#   - systemctl restart mythos-bot.service ← duplicate
#   - /usr/bin/psql -d mythos *            ← duplicated in /etc/sudoers.d/mythos
#
# RETAINED:
#   - bash install.sh — required for the patch-install workflow.
#
# NOTE: The bash install.sh rule is itself a privilege escalation path
# (adge owns /opt/mythos/patches/, so adge can write any install.sh and
# have it run as root with no password). This is intentional for the
# patch workflow and matches the prior state. A future architectural
# change could require patches to be signed or originate from a
# root-owned directory. Out of scope for SYS-0064.

adge ALL=(ALL) NOPASSWD: /usr/bin/bash /opt/mythos/patches/*/install.sh
adge ALL=(ALL) NOPASSWD: /bin/bash /opt/mythos/patches/*/install.sh
"""


def main():
    patch = PatchBase(
        stream='SYS',
        number=64,
        description='security cleanup — remove cp * rule from mythos-monitor',
        patch_type='MAJOR',
    )
    patch.begin()

    # Must be root
    if os.geteuid() != 0:
        patch.errors.append(
            "SYS-0064 must run as root. Invoke via 'patch-install SYS-0064' "
            "or 'sudo bash install.sh', not directly."
        )
        patch.logger.log("  ✗ not running as root")
        patch.finish()
        sys.exit(1)
    patch.logger.log("  ✓ running as root")

    if not MONITOR_FILE.is_file():
        patch.logger.log(f"  ⊙ {MONITOR_FILE} does not exist — nothing to clean (idempotent skip)")
        patch.validations.append("mythos-monitor already absent")
        patch.finish()
        return

    # Idempotency check
    current = MONITOR_FILE.read_text()
    if '/usr/bin/cp *' not in current:
        patch.logger.log("  ⊙ 'cp *' rule already absent — patch already applied (idempotent skip)")
        patch.validations.append("cp * rule already removed")
        patch.finish()
        return

    patch.logger.log(f"  · current mythos-monitor: {len(current)} bytes, {len(current.splitlines())} lines")
    patch.logger.log(f"  · contains dangerous 'cp *' rule: confirmed")

    # Backup
    if patch.dry_run:
        patch.logger.log(f"  · [dry run] would backup → {BACKUP_FILE}")
    else:
        shutil.copy2(str(MONITOR_FILE), str(BACKUP_FILE))
        patch.logger.log(f"  ✓ backup → {BACKUP_FILE}")

    # Write new content to a tempfile and validate with visudo
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.sudoers', delete=False, dir='/tmp'
    ) as tf:
        tf.write(NEW_CONTENT)
        tmp_path = tf.name
    os.chmod(tmp_path, 0o440)

    # visudo validation
    visudo = subprocess.run(
        ['/usr/sbin/visudo', '-c', '-f', tmp_path],
        capture_output=True, text=True,
    )
    if visudo.returncode != 0:
        patch.errors.append(f"visudo validation failed: {visudo.stderr.strip()}")
        patch.logger.log(f"  ✗ visudo -c FAILED: {visudo.stderr.strip()}")
        os.unlink(tmp_path)
        patch.finish()
        sys.exit(1)
    patch.logger.log(f"  ✓ visudo -c passed: {visudo.stdout.strip() or 'parsed OK'}")

    if patch.dry_run:
        patch.logger.log(f"  · [dry run] would install {tmp_path} → {MONITOR_FILE} (root:root 0440)")
        os.unlink(tmp_path)
        patch.validations.append("dry-run: visudo passed, would install")
        patch.finish()
        return

    # Atomic install via /usr/bin/install — sets owner, group, mode in one shot
    install_result = subprocess.run(
        ['/usr/bin/install', '-o', 'root', '-g', 'root', '-m', '0440',
         tmp_path, str(MONITOR_FILE)],
        capture_output=True, text=True,
    )
    if install_result.returncode != 0:
        patch.errors.append(f"install failed: {install_result.stderr.strip()}")
        patch.logger.log(f"  ✗ install FAILED: {install_result.stderr.strip()}")
        # Restore from backup
        shutil.copy2(str(BACKUP_FILE), str(MONITOR_FILE))
        os.chmod(str(MONITOR_FILE), 0o440)
        patch.logger.log("  ⊙ restored from backup")
        os.unlink(tmp_path)
        patch.finish()
        sys.exit(1)
    os.unlink(tmp_path)
    patch.files_deployed.append(str(MONITOR_FILE))
    patch.logger.log(f"  ✓ installed → {MONITOR_FILE} (root:root 0440)")

    # Verify the dangerous rule is gone
    new_content = MONITOR_FILE.read_text()
    if '/usr/bin/cp *' in new_content:
        patch.errors.append("VERIFICATION FAILED: cp * rule still present after install")
        patch.logger.log("  ✗ POST-INSTALL VERIFY: cp * rule STILL PRESENT")
        # Restore
        shutil.copy2(str(BACKUP_FILE), str(MONITOR_FILE))
        os.chmod(str(MONITOR_FILE), 0o440)
        patch.logger.log("  ⊙ restored from backup")
        patch.finish()
        sys.exit(1)
    patch.logger.log("  ✓ verify: 'cp *' rule is GONE")
    patch.validations.append("dangerous cp * rule removed")

    # Verify bash install.sh rule is still present (so patch-install keeps working)
    if 'bash /opt/mythos/patches/*/install.sh' not in new_content:
        patch.errors.append("VERIFICATION FAILED: bash install.sh rule missing")
        patch.logger.log("  ✗ POST-INSTALL VERIFY: install.sh rule MISSING — patch-install will break")
        shutil.copy2(str(BACKUP_FILE), str(MONITOR_FILE))
        os.chmod(str(MONITOR_FILE), 0o440)
        patch.logger.log("  ⊙ restored from backup")
        patch.finish()
        sys.exit(1)
    patch.logger.log("  ✓ verify: bash install.sh rule retained — patch-install will keep working")
    patch.validations.append("bash install.sh rule retained")

    # Verify visudo -c on the live file (final sanity)
    final_check = subprocess.run(
        ['/usr/sbin/visudo', '-c', '-f', str(MONITOR_FILE)],
        capture_output=True, text=True,
    )
    if final_check.returncode != 0:
        patch.errors.append(f"final visudo check failed: {final_check.stderr.strip()}")
        patch.logger.log(f"  ✗ final visudo FAILED: {final_check.stderr.strip()}")
        shutil.copy2(str(BACKUP_FILE), str(MONITOR_FILE))
        os.chmod(str(MONITOR_FILE), 0o440)
        patch.logger.log("  ⊙ restored from backup")
        patch.finish()
        sys.exit(1)
    patch.logger.log(f"  ✓ final visudo: {final_check.stdout.strip() or 'parsed OK'}")
    patch.validations.append("live file passes visudo -c")

    patch.finish()


if __name__ == '__main__':
    main()
