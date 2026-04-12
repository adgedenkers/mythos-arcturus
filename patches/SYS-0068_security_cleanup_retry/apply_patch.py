#!/usr/bin/env python3
"""
SYS-0068: Security cleanup retry — remove cp * rule from mythos-monitor.

Reships the work that SYS-0064 should have completed. SYS-0064 had a
buggy post-install verify that substring-matched '/usr/bin/cp *' against
the full file content, which false-positived on the patch's own comment
lines referencing the removed rule. The install succeeded but the
verify triggered a rollback, restoring the dangerous file.

This patch uses a regex that matches ONLY active (non-comment) sudoers
directives, ignoring comment lines entirely.

Must run as root (via patch-install → sudo bash install.sh).
"""
import sys
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

MONITOR_FILE = Path('/etc/sudoers.d/mythos-monitor')
BACKUP_FILE = Path('/tmp/mythos-monitor.pre_SYS-0068.bak')

# Regex matches an ACTIVE sudoers directive (not a comment) granting cp *.
# - Start of line, optional whitespace
# - First significant char is not '#'
# - Contains NOPASSWD: and /usr/bin/cp followed by whitespace then *
DANGEROUS_RULE_RE = re.compile(
    r'^\s*[^#\s].*NOPASSWD:.*?/usr/bin/cp\s+\*',
    re.MULTILINE,
)

NEW_CONTENT = """# /etc/sudoers.d/mythos-monitor
# Cleaned by SYS-0068 (retry of SYS-0064, which had a buggy verify).
#
# REMOVED (security findings from SYS-0062 install audit):
#   - cp *             (effective root via arbitrary file overwrite)
#   - systemctl restart mythos-*            (duplicated in /etc/sudoers.d/mythos)
#   - systemctl restart mythos-api.service  (duplicate)
#   - systemctl restart mythos-bot.service  (duplicate)
#   - psql -d mythos * (duplicated in /etc/sudoers.d/mythos)
#
# RETAINED:
#   - bash install.sh — required for the patch-install workflow.
#
# The bash install.sh rule is itself a privilege escalation path
# (adge owns /opt/mythos/patches/, so adge can write any install.sh
# and have it run as root). Intentional for the patch workflow and
# matches the prior state. Out of scope for this patch.

adge ALL=(ALL) NOPASSWD: /usr/bin/bash /opt/mythos/patches/*/install.sh
adge ALL=(ALL) NOPASSWD: /bin/bash /opt/mythos/patches/*/install.sh
"""


def has_dangerous_rule(content: str) -> bool:
    """True if an active (non-comment) cp * rule is present."""
    return bool(DANGEROUS_RULE_RE.search(content))


def _chown_mythos_to_adge(patch):
    """Chown /opt/mythos/ recursively back to adge:adge.

    patch.finish() writes STREAMS.json, PATCH_HISTORY.md, /tmp/*.log,
    /tmp/*.json as root. Those files in /opt/mythos/ would be root-owned
    and break subsequent adge-run git operations. This fixes that.

    Also chowns /tmp/SYS-0068_* log files to adge so future runs can
    read them.
    """
    try:
        r = subprocess.run(
            ['/usr/bin/chown', '-R', 'adge:adge', '/opt/mythos'],
            capture_output=True, text=True, timeout=120,
        )
        if r.returncode == 0:
            patch.logger.log("  ✓ chown -R adge:adge /opt/mythos")
        else:
            patch.logger.log(f"  ⚠ chown /opt/mythos failed: {r.stderr.strip()}")
    except Exception as e:
        patch.logger.log(f"  ⚠ chown /opt/mythos exception: {e}")

    # Chown the SYS-0068 log files so adge can read/delete them
    try:
        for p in ['/tmp/SYS-0068_output.log',
                  '/tmp/SYS-0068_result.json',
                  '/tmp/last_patch_output.log',
                  '/tmp/last_patch_result.json',
                  str(BACKUP_FILE)]:
            if os.path.exists(p):
                subprocess.run(['/usr/bin/chown', 'adge:adge', p],
                               capture_output=True, text=True)
    except Exception:
        pass


def main():
    patch = PatchBase(
        stream='SYS',
        number=68,
        description='security cleanup retry — remove cp * rule (SYS-0064 had buggy verify)',
        patch_type='MAJOR',
    )
    patch.begin()

    try:
        _main_body(patch)
    finally:
        # Always chown back to adge, even on failure/early-exit.
        # patch.finish() may have already run inside _main_body — that's fine,
        # chown is idempotent.
        _chown_mythos_to_adge(patch)


def _main_body(patch):

    # install.sh self-escalates to root via sudo before invoking this script.
    if os.geteuid() != 0:
        patch.errors.append(
            "not running as root — install.sh should self-escalate. "
            "If you see this, the self-escalation block is missing or sudoers rule is gone."
        )
        patch.logger.log("  ✗ not running as root (install.sh should have self-escalated)")
        patch.finish()
        sys.exit(1)
    patch.logger.log("  ✓ running as root (via install.sh self-escalation)")

    if not MONITOR_FILE.is_file():
        patch.logger.log(f"  ⊙ {MONITOR_FILE} does not exist — nothing to do")
        patch.validations.append("mythos-monitor absent")
        patch.finish()
        return

    current = MONITOR_FILE.read_text()
    patch.logger.log(f"  · current: {len(current)} bytes, {len(current.splitlines())} lines")

    # Sanity self-test: the new content we're about to write must NOT
    # trigger has_dangerous_rule. If it does, our regex or content is wrong.
    if has_dangerous_rule(NEW_CONTENT):
        patch.errors.append(
            "SELF-TEST FAIL: NEW_CONTENT matches DANGEROUS_RULE_RE — "
            "regex or content is wrong"
        )
        patch.logger.log("  ✗ SELF-TEST FAIL: regex would false-positive on NEW_CONTENT")
        patch.finish()
        sys.exit(1)
    patch.logger.log("  ✓ self-test: NEW_CONTENT does not match dangerous-rule regex")

    # Sanity self-test: the current file (which we KNOW has the rule) must match.
    if not has_dangerous_rule(current):
        patch.logger.log("  ⊙ current file has no active cp * rule — nothing to do")
        patch.validations.append("cp * rule already absent (idempotent skip)")
        patch.finish()
        return
    patch.logger.log("  ✓ self-test: current file has active cp * rule (as expected)")

    # Backup
    shutil.copy2(str(MONITOR_FILE), str(BACKUP_FILE))
    patch.logger.log(f"  ✓ backup → {BACKUP_FILE}")

    # Write candidate to tempfile
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.sudoers', delete=False, dir='/tmp'
    ) as tf:
        tf.write(NEW_CONTENT)
        tmp_path = tf.name
    os.chmod(tmp_path, 0o440)

    try:
        # visudo validation
        r = subprocess.run(
            ['/usr/sbin/visudo', '-c', '-f', tmp_path],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            patch.errors.append(f"visudo validation failed: {r.stderr.strip()}")
            patch.logger.log(f"  ✗ visudo -c FAILED: {r.stderr.strip()}")
            patch.finish()
            sys.exit(1)
        patch.logger.log(f"  ✓ visudo -c: {r.stdout.strip() or 'parsed OK'}")

        # Atomic install
        r = subprocess.run(
            ['/usr/bin/install', '-o', 'root', '-g', 'root', '-m', '0440',
             tmp_path, str(MONITOR_FILE)],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            patch.errors.append(f"install failed: {r.stderr.strip()}")
            patch.logger.log(f"  ✗ install FAILED: {r.stderr.strip()}")
            shutil.copy2(str(BACKUP_FILE), str(MONITOR_FILE))
            os.chmod(str(MONITOR_FILE), 0o440)
            patch.logger.log("  ⊙ restored from backup")
            patch.finish()
            sys.exit(1)
        patch.files_deployed.append(str(MONITOR_FILE))
        patch.logger.log(f"  ✓ installed → {MONITOR_FILE} (root:root 0440)")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    # Post-install verification — use the FIXED regex
    new_content = MONITOR_FILE.read_text()
    if has_dangerous_rule(new_content):
        patch.errors.append("POST-VERIFY: active cp * rule STILL PRESENT")
        patch.logger.log("  ✗ POST-VERIFY: active cp * rule STILL PRESENT — rolling back")
        shutil.copy2(str(BACKUP_FILE), str(MONITOR_FILE))
        os.chmod(str(MONITOR_FILE), 0o440)
        patch.logger.log("  ⊙ restored from backup")
        patch.finish()
        sys.exit(1)
    patch.logger.log("  ✓ post-verify: no active cp * rule")
    patch.validations.append("dangerous cp * rule removed")

    # Verify bash install.sh rule retained
    if 'bash /opt/mythos/patches/*/install.sh' not in new_content:
        patch.errors.append("POST-VERIFY: bash install.sh rule missing")
        patch.logger.log("  ✗ POST-VERIFY: bash install.sh rule MISSING — rolling back")
        shutil.copy2(str(BACKUP_FILE), str(MONITOR_FILE))
        os.chmod(str(MONITOR_FILE), 0o440)
        patch.logger.log("  ⊙ restored from backup")
        patch.finish()
        sys.exit(1)
    patch.logger.log("  ✓ post-verify: bash install.sh rule retained")
    patch.validations.append("bash install.sh rule retained")

    # Final live-file visudo check
    r = subprocess.run(
        ['/usr/sbin/visudo', '-c', '-f', str(MONITOR_FILE)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        patch.errors.append(f"final visudo failed: {r.stderr.strip()}")
        patch.logger.log(f"  ✗ final visudo FAILED: {r.stderr.strip()}")
        shutil.copy2(str(BACKUP_FILE), str(MONITOR_FILE))
        os.chmod(str(MONITOR_FILE), 0o440)
        patch.logger.log("  ⊙ restored from backup")
        patch.finish()
        sys.exit(1)
    patch.logger.log(f"  ✓ final visudo: {r.stdout.strip() or 'parsed OK'}")
    patch.validations.append("live file passes visudo -c")

    patch.finish()


if __name__ == '__main__':
    main()
