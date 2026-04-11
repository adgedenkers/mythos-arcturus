#!/usr/bin/env python3
"""
SYS-0062: privilege foundation (wrappers + sudoers + allowlist)

Installs root-owned wrapper scripts at /usr/local/libexec/mythos/ and a
narrow sudoers drop-in at /etc/sudoers.d/mythos-patches that whitelists
ONLY those wrappers. After this lands, Mythos patches no longer prompt
for passwords on privileged operations.

This is the LAST patch that requires interactive sudo for its own
bootstrap. After SYS-0062 + SYS-0063 (framework migration), all subsequent
patches use the wrappers and work without a TTY.

REQUIRES: Interactive terminal. Cannot be installed via the patch monitor.

Approved by Castor (Gemini) and Jeff Thinking after two rounds of peer review.
"""

# ─── TTY CHECK FIRST — before any other imports ──────────────────────────────
import sys

if not sys.stdin.isatty():
    print("=" * 60, file=sys.stderr)
    print("ERROR: SYS-0062 must be run from an interactive terminal.", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("", file=sys.stderr)
    print("This patch is the BOOTSTRAP for the privilege foundation.", file=sys.stderr)
    print("It needs interactive sudo because the wrappers it installs", file=sys.stderr)
    print("don't exist yet — there's nothing to bypass the password prompt.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Do NOT drop this patch into ~/Downloads/ — the patch monitor", file=sys.stderr)
    print("cannot provide a TTY for the password prompt.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Run manually:  patch-install SYS-0062", file=sys.stderr)
    print("", file=sys.stderr)
    print("After SYS-0062 + SYS-0063 land, ALL future patches will work", file=sys.stderr)
    print("without a TTY (including monitor-triggered installs).", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    sys.exit(2)

# ─── Now safe to import the rest ─────────────────────────────────────────────
import os
import re
import shutil
import stat
import subprocess
import datetime
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

# ─── Constants ───────────────────────────────────────────────────────────────

WRAPPER_DIR = "/usr/local/libexec/mythos"
SUDOERS_FILE = "/etc/sudoers.d/mythos-patches"
ALLOWLIST_DIR = "/etc/mythos"
ALLOWLIST_FILE = "/etc/mythos/allowed-units.txt"

TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
SUDOERS_BACKUP_DIR = f"/tmp/sudoers.d.backup.{TIMESTAMP}"

# Wrappers in install order (those without args first, those with args second)
EXPECTED_WRAPPERS = [
    "mythos-servicectl",
    "mythos-install-unit",
    "mythos-install-cloudflared-config",
    "mythos-fix-ownership",
    "mythos-scan-perms",
    "mythos-backup-git",
    "mythos-clean-tmp-pack",
    "mythos-allowlist-append",
]

# Which wrappers take arguments (need trailing wildcard in sudoers)
WRAPPERS_WITH_ARGS = {
    "mythos-servicectl",
    "mythos-install-unit",
    "mythos-allowlist-append",
}

# Initial allowed-units.txt content
ALLOWLIST_CONTENT = """# Mythos allowed-units list
# Managed by SYS patches. Root-owned. Read by mythos-servicectl.
# One unit name per line. Blank lines and # comments ignored.
# To add a unit: use mythos-allowlist-append, or ship a SYS patch that
# updates this file via the wrapper.

mythos-bot.service
mythos-api.service
mythos-patch-monitor.service
mythos-jupyter.service
cloudflared.service
"""

# Sudoers file content — generated, not hand-edited
def generate_sudoers_content():
    lines = [
        "# /etc/sudoers.d/mythos-patches",
        "# Installed by SYS-0062. Do not edit manually.",
        "# Validated with visudo -c before install.",
        "#",
        "# Each entry points at a root-owned wrapper script that validates",
        "# its own arguments. The wrapper is the security boundary, not sudoers.",
        "",
    ]
    for w in EXPECTED_WRAPPERS:
        if w in WRAPPERS_WITH_ARGS:
            lines.append(f"adge ALL=(root) NOPASSWD: {WRAPPER_DIR}/{w} *")
        else:
            lines.append(f"adge ALL=(root) NOPASSWD: {WRAPPER_DIR}/{w}")
    lines.append("")  # trailing newline
    return "\n".join(lines)

# Dangerous tokens that should never appear in our sudoers file
# (defense in depth — if these show up, we have a bug)
DANGEROUS_TOKENS = [
    "bash", "sh ", "perl", "python", "awk", "sed ", "vim", "less", "more",
    "/bin/cp", "/bin/mv", "dd ", "/bin/nc", "/bin/find", "/bin/tar",
    "/bin/chmod", "/bin/chown",
]


# ─── Helpers ─────────────────────────────────────────────────────────────────

def run(cmd, check=True, capture=True, timeout=None, cwd=None):
    return subprocess.run(
        cmd, check=check, capture_output=capture, text=True,
        timeout=timeout, cwd=cwd,
    )


def log(patch, msg):
    patch.logger.log(f"  → {msg}")


def log_ok(patch, msg):
    patch.logger.log(f"  ✓ {msg}")


def log_skip(patch, msg):
    patch.logger.log(f"  ⊙ {msg}")


def log_warn(patch, msg):
    patch.logger.log(f"  ⚠ {msg}")


def log_err(patch, msg):
    patch.logger.log(f"  ✗ {msg}")


# ─── Step 1: Initial sudo cache (interactive) ────────────────────────────────

def initial_sudo_cache(patch):
    if patch.dry_run:
        log(patch, "[validate] would refresh sudo cache")
        return True

    log(patch, "this is the LAST time SYS patches will prompt for a password")
    try:
        run(["sudo", "-v"], timeout=120)
        log_ok(patch, "sudo credentials cached")
        return True
    except subprocess.CalledProcessError as e:
        patch.errors.append(f"could not cache sudo credentials: {e.stderr}")
        return False
    except subprocess.TimeoutExpired:
        patch.errors.append("sudo -v timed out after 120s")
        return False


# ─── Step 2: Verify target system ────────────────────────────────────────────

def verify_target_system(patch):
    if patch.dry_run:
        log(patch, "[validate] would verify target system")
        return True

    checks = [
        ("/usr/local/libexec", "directory"),
        ("/etc/sudoers.d", "directory"),
        ("/opt/mythos/patches/scripts/patch_base.py", "file"),
        ("/opt/mythos/.venv/bin/python3", "file"),
    ]

    for path, kind in checks:
        if kind == "directory":
            if not os.path.isdir(path):
                patch.errors.append(f"required directory missing: {path}")
                return False
        else:
            if not os.path.isfile(path):
                patch.errors.append(f"required file missing: {path}")
                return False
        log_ok(patch, f"present: {path}")

    # Check visudo and install commands
    for cmd in ["visudo", "install"]:
        result = run(["which", cmd], check=False)
        if result.returncode != 0:
            patch.errors.append(f"required command missing: {cmd}")
            return False
        log_ok(patch, f"command available: {cmd}")

    return True


# ─── Step 3: Stop patch monitor ──────────────────────────────────────────────

def stop_patch_monitor(patch):
    if patch.dry_run:
        log(patch, "[validate] would stop mythos-patch-monitor.service")
        return True

    try:
        result = run(
            ["systemctl", "is-active", "mythos-patch-monitor.service"],
            check=False,
        )
        state = (result.stdout or "").strip()
        if state != "active":
            log_skip(patch, f"mythos-patch-monitor.service is {state} — not stopping")
            return True

        run(["sudo", "systemctl", "stop", "mythos-patch-monitor.service"])
        log_ok(patch, "stopped mythos-patch-monitor.service")
        return True
    except subprocess.CalledProcessError as e:
        patch.errors.append(f"stop monitor: {e.stderr}")
        return False


def start_patch_monitor(patch):
    if patch.dry_run:
        return
    try:
        run(["sudo", "systemctl", "start", "mythos-patch-monitor.service"])
        log_ok(patch, "started mythos-patch-monitor.service")
    except subprocess.CalledProcessError as e:
        patch.errors.append(f"start monitor: {e.stderr}")
        patch.logger.log(
            "  ⚠ CRITICAL: monitor could not be restarted. "
            "Run manually: sudo systemctl start mythos-patch-monitor.service"
        )


# ─── Step 4: Backup /etc/sudoers.d/ listing ──────────────────────────────────

def backup_sudoers_d(patch):
    if patch.dry_run:
        log(patch, f"[validate] would back up /etc/sudoers.d/ listing to {SUDOERS_BACKUP_DIR}")
        return True

    try:
        os.makedirs(SUDOERS_BACKUP_DIR, exist_ok=True)
        backup_file = os.path.join(SUDOERS_BACKUP_DIR, "sudoers.d.listing.txt")
        result = run(
            ["sudo", "ls", "-la", "/etc/sudoers.d/"],
            check=False,
        )
        with open(backup_file, "w") as f:
            f.write("# /etc/sudoers.d/ listing captured before SYS-0062\n")
            f.write(f"# timestamp: {TIMESTAMP}\n\n")
            f.write(result.stdout or "")
            if result.stderr:
                f.write(f"\n# stderr:\n{result.stderr}")
        log_ok(patch, f"backed up listing to {backup_file}")
        return True
    except Exception as e:
        log_warn(patch, f"backup_sudoers_d: {e} (non-fatal)")
        return True


# ─── Step 5: Create /etc/mythos/ ─────────────────────────────────────────────

def create_etc_mythos(patch):
    if patch.dry_run:
        log(patch, f"[validate] would create {ALLOWLIST_DIR}")
        return True

    try:
        run(["sudo", "install", "-d", "-m", "0755", "-o", "root", "-g", "root", ALLOWLIST_DIR])
        log_ok(patch, f"created {ALLOWLIST_DIR}/ (root:root 0755)")
        return True
    except subprocess.CalledProcessError as e:
        patch.errors.append(f"create {ALLOWLIST_DIR}: {e.stderr}")
        return False


# ─── Step 6: Create /usr/local/libexec/mythos/ ───────────────────────────────

def create_wrapper_dir(patch):
    if patch.dry_run:
        log(patch, f"[validate] would create {WRAPPER_DIR}")
        return True

    try:
        run(["sudo", "install", "-d", "-m", "0755", "-o", "root", "-g", "root", WRAPPER_DIR])
        log_ok(patch, f"created {WRAPPER_DIR}/ (root:root 0755)")
        return True
    except subprocess.CalledProcessError as e:
        patch.errors.append(f"create {WRAPPER_DIR}: {e.stderr}")
        return False


# ─── Step 7: Install allowed-units.txt ───────────────────────────────────────

def install_allowlist(patch):
    if patch.dry_run:
        log(patch, f"[validate] would install {ALLOWLIST_FILE}")
        return True

    try:
        tempfile = f"/tmp/allowed-units.{TIMESTAMP}.txt"
        with open(tempfile, "w") as f:
            f.write(ALLOWLIST_CONTENT)

        run(["sudo", "install", "-m", "0644", "-o", "root", "-g", "root",
             tempfile, ALLOWLIST_FILE])
        os.unlink(tempfile)

        # Verify
        result = run(["sudo", "test", "-f", ALLOWLIST_FILE], check=False)
        if result.returncode != 0:
            patch.errors.append(f"{ALLOWLIST_FILE} not present after install")
            return False

        # Count units in the file
        units = [
            line.strip() for line in ALLOWLIST_CONTENT.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        log_ok(patch, f"{ALLOWLIST_FILE} installed (root:root 0644, {len(units)} units)")
        return True
    except subprocess.CalledProcessError as e:
        patch.errors.append(f"install allowlist: {e.stderr}")
        return False
    except Exception as e:
        patch.errors.append(f"install allowlist: {e}")
        return False


# ─── Step 8: Install wrapper scripts ─────────────────────────────────────────

def install_wrappers(patch, patch_dir):
    if patch.dry_run:
        log(patch, f"[validate] would install {len(EXPECTED_WRAPPERS)} wrappers")
        return True

    wrappers_src_dir = os.path.join(patch_dir, "wrappers")
    if not os.path.isdir(wrappers_src_dir):
        patch.errors.append(f"wrapper source directory missing: {wrappers_src_dir}")
        return False

    for wrapper in EXPECTED_WRAPPERS:
        src = os.path.join(wrappers_src_dir, wrapper)
        if not os.path.isfile(src):
            patch.errors.append(f"wrapper source missing: {src}")
            return False

        dest = f"{WRAPPER_DIR}/{wrapper}"
        log(patch, f"installing {wrapper}")

        try:
            run(["sudo", "install", "-m", "0755", "-o", "root", "-g", "root", src, dest])
        except subprocess.CalledProcessError as e:
            patch.errors.append(f"install {wrapper}: {e.stderr}")
            return False

        # Verify the wrapper landed correctly
        if not verify_wrapper_installed(patch, wrapper):
            return False

    log_ok(patch, f"all {len(EXPECTED_WRAPPERS)} wrappers installed and verified")
    return True


def verify_wrapper_installed(patch, wrapper_name):
    """Verify a wrapper is in place with correct mode/owner/shebang."""
    path = f"{WRAPPER_DIR}/{wrapper_name}"

    # 1. Must exist
    if not os.path.exists(path):
        patch.errors.append(f"{path} does not exist after install")
        return False

    # 2. Must NOT be a symlink
    if os.path.islink(path):
        patch.errors.append(f"{path} is a symlink")
        return False

    # 3. Must be a regular file
    if not os.path.isfile(path):
        patch.errors.append(f"{path} is not a regular file")
        return False

    # 4. Must start with #!/bin/bash
    try:
        with open(path, 'rb') as f:
            first_line = f.readline()
        if not first_line.startswith(b'#!/bin/bash'):
            patch.errors.append(f"{path} does not start with #!/bin/bash")
            return False
    except PermissionError:
        # Root-owned, mode 0755 — adge can read it via the o+r bit
        # If we can't read it, that's a problem
        patch.errors.append(f"{path} not readable by adge")
        return False

    # 5. Must have mode 0755
    st = os.stat(path)
    mode = stat.S_IMODE(st.st_mode)
    if mode != 0o755:
        patch.errors.append(f"{path} has wrong mode: {oct(mode)} (expected 0o755)")
        return False

    # 6. Must be root-owned
    if st.st_uid != 0:
        patch.errors.append(f"{path} is not owned by root (uid={st.st_uid})")
        return False
    if st.st_gid != 0:
        patch.errors.append(f"{path} is not in group root (gid={st.st_gid})")
        return False

    return True


# ─── Step 9: Write sudoers tempfile ──────────────────────────────────────────

def write_sudoers_tempfile(patch):
    if patch.dry_run:
        log(patch, "[validate] would write sudoers tempfile")
        return None

    tempfile = f"/tmp/mythos-patches.sudoers.{TIMESTAMP}"
    content = generate_sudoers_content()

    try:
        with open(tempfile, "w") as f:
            f.write(content)
        log_ok(patch, f"wrote tempfile: {tempfile} ({len(content)} bytes)")
        return tempfile
    except Exception as e:
        patch.errors.append(f"write tempfile: {e}")
        return None


# ─── Step 10: visudo -c validation ───────────────────────────────────────────

def visudo_validate(patch, tempfile):
    if patch.dry_run:
        log(patch, "[validate] would run visudo -c")
        return True

    try:
        result = run(["sudo", "visudo", "-c", "-f", tempfile], check=False)
        if result.returncode != 0:
            patch.errors.append(
                f"visudo validation failed:\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}"
            )
            return False
        log_ok(patch, "visudo -c passed")
        return True
    except Exception as e:
        patch.errors.append(f"visudo: {e}")
        return False


# ─── Step 11: Content linting ────────────────────────────────────────────────

def lint_sudoers_content(patch, tempfile):
    if patch.dry_run:
        log(patch, "[validate] would lint sudoers content")
        return True

    try:
        size = os.path.getsize(tempfile)
        if size > 2048:
            patch.errors.append(f"sudoers file too large: {size} bytes")
            return False
        log_ok(patch, f"file size: {size} bytes (under 2KB limit)")

        with open(tempfile, "r") as f:
            content = f.read()

        if not content.endswith("\n"):
            patch.errors.append("sudoers file does not end with newline")
            return False
        log_ok(patch, "ends with newline")

        # Pattern matching every non-comment, non-blank line
        pattern = re.compile(
            r'^adge ALL=\(root\) NOPASSWD: /usr/local/libexec/mythos/([a-z-]+)( \*)?$'
        )

        seen_wrappers = set()
        rule_count = 0

        for lineno, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            m = pattern.match(stripped)
            if not m:
                patch.errors.append(
                    f"line {lineno}: does not match expected pattern: {stripped}"
                )
                return False

            wrapper_name = m.group(1)
            has_wildcard = m.group(2) is not None

            if wrapper_name not in EXPECTED_WRAPPERS:
                patch.errors.append(f"line {lineno}: unknown wrapper: {wrapper_name}")
                return False

            expected_wildcard = wrapper_name in WRAPPERS_WITH_ARGS
            if has_wildcard != expected_wildcard:
                patch.errors.append(
                    f"line {lineno}: wrapper {wrapper_name} wildcard mismatch "
                    f"(has={has_wildcard}, expected={expected_wildcard})"
                )
                return False

            seen_wrappers.add(wrapper_name)
            rule_count += 1

        log_ok(patch, f"{rule_count} rules, all match expected pattern")

        # All expected wrappers must be present
        missing = set(EXPECTED_WRAPPERS) - seen_wrappers
        if missing:
            patch.errors.append(f"missing sudoers rules: {missing}")
            return False
        log_ok(patch, f"all {len(EXPECTED_WRAPPERS)} expected wrappers present")

        # Dangerous token check (defense in depth)
        for token in DANGEROUS_TOKENS:
            for lineno, line in enumerate(content.splitlines(), 1):
                if line.strip().startswith("#"):
                    continue
                # Allow the wrapper path itself (mythos-* under wrapper dir)
                cleaned = line.replace(WRAPPER_DIR + "/mythos-", "")
                if token in cleaned:
                    patch.errors.append(
                        f"line {lineno}: dangerous token '{token.strip()}' found"
                    )
                    return False
        log_ok(patch, "no dangerous tokens")
        log_ok(patch, "linting passed")
        return True
    except Exception as e:
        patch.errors.append(f"lint_sudoers_content: {e}")
        return False


# ─── Step 12: Atomic install of sudoers file ─────────────────────────────────

def install_sudoers_file(patch, tempfile):
    if patch.dry_run:
        log(patch, "[validate] would install sudoers file")
        return True

    try:
        run(["sudo", "install", "-m", "0440", "-o", "root", "-g", "root",
             tempfile, SUDOERS_FILE])
        log_ok(patch, f"installed {SUDOERS_FILE} (root:root 0440)")
        return True
    except subprocess.CalledProcessError as e:
        patch.errors.append(f"install sudoers: {e.stderr}")
        return False


# ─── Step 13: Post-install verification ──────────────────────────────────────

def verify_wrappers_work(patch):
    """Test 4 wrappers via sudo -n to confirm they work without password."""
    if patch.dry_run:
        log(patch, "[validate] would verify wrappers work without password")
        return True

    # Test 1: arg-taking wrapper, service class
    log(patch, "test 1/4: mythos-servicectl is-active mythos-bot.service")
    try:
        result = run(
            ["sudo", "-n", f"{WRAPPER_DIR}/mythos-servicectl",
             "is-active", "mythos-bot.service"],
            check=False, timeout=10,
        )
        # is-active returns 0 for active, 3 for inactive — both mean it ran
        # What we're checking is that sudo -n didn't prompt
        if "password is required" in (result.stderr or "").lower():
            patch.errors.append("mythos-servicectl: sudo -n prompted for password")
            return False
        log_ok(patch, "mythos-servicectl: OK")
    except Exception as e:
        patch.errors.append(f"mythos-servicectl test: {e}")
        return False

    # Test 2: no-arg wrapper, returns count
    log(patch, "test 2/4: mythos-scan-perms")
    try:
        result = run(
            ["sudo", "-n", f"{WRAPPER_DIR}/mythos-scan-perms"],
            check=True, timeout=60,
        )
        try:
            count = int(result.stdout.strip())
            log_ok(patch, f"mythos-scan-perms: OK (count={count})")
        except ValueError:
            patch.errors.append(
                f"mythos-scan-perms unexpected output: {result.stdout!r}"
            )
            return False
    except subprocess.CalledProcessError as e:
        if "password is required" in (e.stderr or "").lower():
            patch.errors.append("mythos-scan-perms: sudo -n prompted for password")
        else:
            patch.errors.append(f"mythos-scan-perms failed: {e.stderr}")
        return False
    except Exception as e:
        patch.errors.append(f"mythos-scan-perms test: {e}")
        return False

    # Test 3: no-arg wrapper, safe no-op
    log(patch, "test 3/4: mythos-clean-tmp-pack")
    try:
        result = run(
            ["sudo", "-n", f"{WRAPPER_DIR}/mythos-clean-tmp-pack"],
            check=True, timeout=10,
        )
        if "removed:" not in result.stdout:
            patch.errors.append(
                f"mythos-clean-tmp-pack unexpected output: {result.stdout!r}"
            )
            return False
        log_ok(patch, f"mythos-clean-tmp-pack: OK ({result.stdout.strip()})")
    except subprocess.CalledProcessError as e:
        if "password is required" in (e.stderr or "").lower():
            patch.errors.append("mythos-clean-tmp-pack: sudo -n prompted for password")
        else:
            patch.errors.append(f"mythos-clean-tmp-pack failed: {e.stderr}")
        return False
    except Exception as e:
        patch.errors.append(f"mythos-clean-tmp-pack test: {e}")
        return False

    # Test 4: arg-taking, idempotent (already in allowlist)
    log(patch, "test 4/4: mythos-allowlist-append mythos-bot.service")
    try:
        result = run(
            ["sudo", "-n", f"{WRAPPER_DIR}/mythos-allowlist-append",
             "mythos-bot.service"],
            check=True, timeout=10,
        )
        if "already in allowlist" not in result.stdout:
            patch.errors.append(
                f"mythos-allowlist-append did not detect duplicate: {result.stdout!r}"
            )
            return False
        log_ok(patch, "mythos-allowlist-append: OK (idempotent)")
    except subprocess.CalledProcessError as e:
        if "password is required" in (e.stderr or "").lower():
            patch.errors.append("mythos-allowlist-append: sudo -n prompted for password")
        else:
            patch.errors.append(f"mythos-allowlist-append failed: {e.stderr}")
        return False
    except Exception as e:
        patch.errors.append(f"mythos-allowlist-append test: {e}")
        return False

    log_ok(patch, "all 4 verification checks passed")
    return True


# ─── Pre-verification cleanup (rollback partial install) ─────────────────────

def cleanup_partial_install(patch):
    """Remove anything we may have partially installed."""
    if patch.dry_run:
        return

    log(patch, "rolling back partial privilege foundation install...")

    # Remove sudoers file FIRST so the next sudo calls don't pick it up
    try:
        run(["sudo", "rm", "-f", SUDOERS_FILE], check=False)
    except Exception:
        pass

    # Remove wrappers
    for wrapper in EXPECTED_WRAPPERS:
        try:
            run(["sudo", "rm", "-f", f"{WRAPPER_DIR}/{wrapper}"], check=False)
        except Exception:
            pass

    # Remove allowlist file
    try:
        run(["sudo", "rm", "-f", ALLOWLIST_FILE], check=False)
    except Exception:
        pass

    # Try to remove empty directories (won't fail if they have other content)
    try:
        run(["sudo", "rmdir", "--ignore-fail-on-non-empty", WRAPPER_DIR], check=False)
        run(["sudo", "rmdir", "--ignore-fail-on-non-empty", ALLOWLIST_DIR], check=False)
    except Exception:
        pass

    log(patch, "cleanup complete")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    patch = PatchBase(
        stream='SYS',
        number=62,
        description='privilege foundation (wrappers + sudoers)',
        patch_type='MAJOR',
    )
    patch.begin()

    sudoers_committed = False
    monitor_was_stopped = False
    patch_dir = patch.patch_dir

    try:
        patch.logger.log("\n[1/13] Refreshing sudo cache (interactive)")
        if not initial_sudo_cache(patch):
            patch.finish(); return 1

        patch.logger.log("\n[2/13] Verifying target system")
        if not verify_target_system(patch):
            patch.finish(); return 1

        patch.logger.log("\n[3/13] Stopping patch monitor")
        if not stop_patch_monitor(patch):
            patch.finish(); return 1
        monitor_was_stopped = True

        patch.logger.log("\n[4/13] Backing up /etc/sudoers.d/ listing")
        backup_sudoers_d(patch)

        patch.logger.log("\n[5/13] Creating /etc/mythos/")
        if not create_etc_mythos(patch):
            patch.finish(); return 1

        patch.logger.log("\n[6/13] Creating /usr/local/libexec/mythos/")
        if not create_wrapper_dir(patch):
            patch.finish(); return 1

        patch.logger.log("\n[7/13] Installing /etc/mythos/allowed-units.txt")
        if not install_allowlist(patch):
            patch.finish(); return 1

        patch.logger.log("\n[8/13] Installing wrapper scripts")
        if not install_wrappers(patch, patch_dir):
            patch.finish(); return 1

        patch.logger.log("\n[9/13] Writing sudoers tempfile")
        tempfile = write_sudoers_tempfile(patch)
        if tempfile is None:
            patch.finish(); return 1

        patch.logger.log("\n[10/13] Validating with visudo -c")
        if not visudo_validate(patch, tempfile):
            patch.finish(); return 1

        patch.logger.log("\n[11/13] Content linting")
        if not lint_sudoers_content(patch, tempfile):
            patch.finish(); return 1

        patch.logger.log("\n[12/13] Atomic install of sudoers drop-in")
        if not install_sudoers_file(patch, tempfile):
            patch.finish(); return 1

        patch.logger.log("\n[13/13] Post-install verification")
        if not verify_wrappers_work(patch):
            patch.finish(); return 1

        # COMMIT POINT
        sudoers_committed = True
        patch.logger.log("")
        patch.logger.log("  ✓ COMMIT POINT — privilege foundation will not be rolled back")

        patch.validations.append("8 wrappers installed at /usr/local/libexec/mythos/")
        patch.validations.append(f"sudoers drop-in at {SUDOERS_FILE}")
        patch.validations.append(f"allowlist at {ALLOWLIST_FILE}")
        patch.validations.append("post-install verification: 4/4 wrappers work without password")

    except Exception as e:
        patch.errors.append(f"unexpected exception: {e}")

    finally:
        if not sudoers_committed and not patch.dry_run:
            cleanup_partial_install(patch)

        if monitor_was_stopped:
            patch.logger.log("\n[cleanup] Restarting patch monitor")
            start_patch_monitor(patch)

    # Summary banner
    if not patch.errors and not patch.dry_run:
        patch.logger.log("")
        patch.logger.log("=" * 55)
        patch.logger.log("  SYS-0062: PRIVILEGE FOUNDATION INSTALLED")
        patch.logger.log("=" * 55)
        patch.logger.log(f"  ✓ 8 wrappers at {WRAPPER_DIR}/")
        patch.logger.log(f"  ✓ sudoers drop-in at {SUDOERS_FILE}")
        patch.logger.log(f"  ✓ allowlist at {ALLOWLIST_FILE}")
        patch.logger.log("")
        patch.logger.log("  From now on:")
        patch.logger.log("  • No password prompts during patch installs")
        patch.logger.log("  • Monitor-triggered installs work without TTY")
        patch.logger.log("  • New privileged ops ship via new wrappers")
        patch.logger.log("")
        patch.logger.log("  Next: SYS-0063 (framework migration to use wrappers)")
        patch.logger.log("=" * 55)

    patch.finish()
    return 1 if patch.errors else 0


if __name__ == '__main__':
    sys.exit(main())
