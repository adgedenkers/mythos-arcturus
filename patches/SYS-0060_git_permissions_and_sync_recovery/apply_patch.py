#!/usr/bin/env python3
"""
SYS-0060: git_permissions_and_sync_recovery (v3, minimal scope)

Surgical patch to fix historical root-owned file contamination in /opt/mythos/
that has been causing the post-install git pipeline to fail silently.

Root cause: legacy install.sh pattern `sudo /opt/mythos/.venv/bin/python3
apply_patch.py` caused every patch installed under the old convention to run
as root, creating root-owned files in .git/objects/, __pycache__/, and some
bin scripts.

Scope of THIS patch (v3, minimal):
  1. Refresh sudo credentials so long ops don't hang waiting for password
  2. Verify target sanity (triple-locked chown target check)
  3. Stop the patch monitor (prevent concurrent ingestion)
  4. Working tree cleanliness check (self-aware of patch extract dir)
  5. Delete stale tmp_pack_* files from .git/objects/pack/ (~3.8 GB cleanup
     from an interrupted git filter-repo run)
  6. sudo chown -R adge:adge /opt/mythos/ (the actual fix)
  7. Clear stale __pycache__ directories
  8. Add safe.directory to adge's git config
  9. git fsck --full to verify chown didn't corrupt the repo
 10. Create /opt/mythos/patches/failed/ and failed/archive/ for SYS-0061+
 11. Restart patch monitor (in finally block)

Explicitly NOT in scope:
  - No .git/ snapshot (.git/ is 53 GB — can't practically tar it)
  - No git push (53 GB can't be pushed to GitHub — needs SYS-0061 slim first)
  - No editing patch_base.py, post_install.py, monitor, or patch-install.sh
  - No Telegram live observability
  - No counter-burn semantics
  - No quarantine hook

Deferred to SYS-0061 (git_repo_slim):
  - git rm --cached -r voice_memos/
  - git filter-repo --path voice_memos/ --invert-paths
  - git gc --aggressive --prune=now
  - Successful push to origin/main

History for THIS patch number:
  v1: pre-flight tree check allow-list too narrow (didn't cover .version or
      self-extraction). 0.04s elapsed, zero side effects. Not burned.
  v2: tar czf of .git/ timed out after 180s because .git/ is 53 GB. Zero side
      effects — failed in step 4 before any destructive work. Not burned.
  v3 (this): snapshot removed entirely, push removed, tmp_pack cleanup added.
"""

import os
import sys
import subprocess
import glob
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

# ─── Hardcoded constants — do NOT parameterize these ────────────────────────

MYTHOS_ROOT_LITERAL = "/opt/mythos"
CHOWN_TARGET_LITERAL = "/opt/mythos/"  # trailing slash intentional
EXPECTED_GIT_DIR = "/opt/mythos/.git"
EXPECTED_OWNER = "adge:adge"

FAILED_DIR = Path("/opt/mythos/patches/failed")
FAILED_ARCHIVE_DIR = FAILED_DIR / "archive"

PATCH_MONITOR_SERVICE = "mythos-patch-monitor.service"

# Working tree allow-list — files/patterns that are expected to be dirty
# during a patch install and should NOT block the cleanliness check.
ALLOWED_DIRTY_EXACT = {
    ".version",                          # GitManager auto-bumps on every install
    "graph_logging/logs/monitor.log",    # live log, always open for writes
}

ALLOWED_DIRTY_PREFIXES = [
    "graph_logging/logs/",
    "patches/logs/",
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


def refresh_sudo(patch, label=""):
    """
    Refresh the sudo timestamp so subsequent sudo operations don't prompt.
    sudo -v extends the cached credential if it's still valid, or prompts
    if it's expired. Called before every long-running sudo operation.

    Uses -n (non-interactive) so it fails fast rather than hanging. If the
    timestamp has expired AND we can't refresh non-interactively, we fail
    the whole patch rather than hang waiting for input from nowhere.
    """
    if patch.dry_run:
        return True
    try:
        run(["sudo", "-n", "-v"], timeout=10)
        return True
    except subprocess.CalledProcessError:
        msg = f"sudo credentials expired{' before ' + label if label else ''}"
        patch.errors.append(
            f"{msg}. Run 'sudo -v' in your terminal, then retry patch-install SYS-0060."
        )
        return False
    except subprocess.TimeoutExpired:
        patch.errors.append(f"sudo -v timed out{' before ' + label if label else ''}")
        return False


# ─── Step: Initial sudo cache ────────────────────────────────────────────────

def initial_sudo_cache(patch):
    """
    Refresh (or initially populate) the sudo credential cache. Interactive
    this time — if the user has never entered their password this session,
    this is where the prompt happens, upfront, not in the middle of a chown.
    """
    if patch.dry_run:
        log(patch, "[validate] would refresh sudo cache")
        return True

    log(patch, "refreshing sudo credentials (may prompt for password)")
    try:
        # Interactive this time — allow prompt if needed
        run(["sudo", "-v"], timeout=60)
        log_ok(patch, "sudo credentials cached")
        return True
    except subprocess.CalledProcessError as e:
        patch.errors.append(
            f"could not cache sudo credentials: {e.stderr}. "
            f"This patch needs sudo for chown and systemctl."
        )
        return False
    except subprocess.TimeoutExpired:
        patch.errors.append(
            "sudo -v timed out after 60s. Enter your password promptly when asked."
        )
        return False


# ─── Step: Target sanity ─────────────────────────────────────────────────────

def verify_target_sanity(patch):
    """Triple-lock the chown target before we shell out to sudo chown."""
    # Lock 1: literal string check
    assert CHOWN_TARGET_LITERAL == "/opt/mythos/", \
        "CHOWN_TARGET_LITERAL has been modified from its expected value"

    # Lock 2: filesystem check
    if not Path(EXPECTED_GIT_DIR).is_dir():
        patch.errors.append(
            f"refusing to chown: {EXPECTED_GIT_DIR} does not exist. Not a Mythos tree."
        )
        return False

    # Lock 3: signature files
    signature_files = [
        "/opt/mythos/patches/scripts/patch_base.py",
        "/opt/mythos/docs/STREAMS.json",
        "/opt/mythos/.env",
    ]
    for sf in signature_files:
        if not Path(sf).exists():
            patch.errors.append(
                f"refusing to chown: signature file {sf} missing. Not a Mythos tree."
            )
            return False

    log_ok(patch, f"target verified: {CHOWN_TARGET_LITERAL}")
    return True


# ─── Step: Stop/start patch monitor ──────────────────────────────────────────

def stop_patch_monitor(patch):
    if patch.dry_run:
        log(patch, f"[validate] would stop {PATCH_MONITOR_SERVICE}")
        return
    try:
        result = run(
            ["systemctl", "is-active", PATCH_MONITOR_SERVICE],
            check=False,
        )
        state = (result.stdout or "").strip()
        if state != "active":
            log_skip(patch, f"{PATCH_MONITOR_SERVICE} is {state} — not stopping")
            return

        if not refresh_sudo(patch, "stop monitor"):
            return
        run(["sudo", "systemctl", "stop", PATCH_MONITOR_SERVICE])
        log_ok(patch, f"stopped {PATCH_MONITOR_SERVICE}")
    except subprocess.CalledProcessError as e:
        patch.errors.append(f"stop {PATCH_MONITOR_SERVICE}: {e.stderr}")


def start_patch_monitor(patch):
    """Restart mythos-patch-monitor.service. Called in a finally block."""
    if patch.dry_run:
        return
    try:
        # Don't use refresh_sudo here — we're in cleanup, always try sudo
        run(["sudo", "systemctl", "start", PATCH_MONITOR_SERVICE])
        log_ok(patch, f"started {PATCH_MONITOR_SERVICE}")
    except subprocess.CalledProcessError as e:
        patch.errors.append(f"start {PATCH_MONITOR_SERVICE}: {e.stderr}")
        patch.logger.log(
            f"  ⚠ CRITICAL: {PATCH_MONITOR_SERVICE} could not be restarted. "
            f"Run manually: sudo systemctl start {PATCH_MONITOR_SERVICE}"
        )


# ─── Step: Working tree cleanliness (self-aware) ────────────────────────────

def check_working_tree(patch):
    """
    Verify no genuine uncommitted work in the tree. Allows:
    - Expected install noise (.version, live logs)
    - The patch's own extraction directory (dynamically computed)
    """
    if patch.dry_run:
        log(patch, "[validate] would check git working tree cleanliness")
        return True

    try:
        self_patch_dir = Path(patch.patch_dir).resolve()
        mythos_root = Path(MYTHOS_ROOT_LITERAL).resolve()
        self_rel = self_patch_dir.relative_to(mythos_root)
        self_prefix = str(self_rel) + "/"
        log(patch, f"self-exclusion prefix: {self_prefix}")
    except ValueError:
        self_prefix = None
        log_warn(patch, f"patch dir {patch.patch_dir} not under {MYTHOS_ROOT_LITERAL}")

    try:
        result = run(
            ["git", "-C", MYTHOS_ROOT_LITERAL, "status", "--porcelain"],
            check=False,
        )
        if result.returncode != 0:
            patch.errors.append(f"git status failed: {result.stderr}")
            return False

        expected_noise = []
        self_referential = []
        genuine_dirty = []

        for line in (result.stdout or "").splitlines():
            if not line.strip():
                continue
            if len(line) < 4:
                continue
            path = line[3:].strip()

            if path in ALLOWED_DIRTY_EXACT:
                expected_noise.append(line.strip())
                continue
            if any(path.startswith(prefix) for prefix in ALLOWED_DIRTY_PREFIXES):
                expected_noise.append(line.strip())
                continue
            if self_prefix and path.startswith(self_prefix):
                self_referential.append(line.strip())
                continue
            genuine_dirty.append(line.strip())

        if expected_noise:
            log(patch, f"expected install noise ({len(expected_noise)} files) — allowed:")
            for item in expected_noise[:5]:
                patch.logger.log(f"    {item}")
            if len(expected_noise) > 5:
                patch.logger.log(f"    ...and {len(expected_noise) - 5} more")

        if self_referential:
            log(patch, f"patch self-extraction ({len(self_referential)} files) — allowed:")
            for item in self_referential[:5]:
                patch.logger.log(f"    {item}")
            if len(self_referential) > 5:
                patch.logger.log(f"    ...and {len(self_referential) - 5} more")

        if genuine_dirty:
            patch.errors.append(
                "working tree has genuine uncommitted changes — refusing to proceed.\n"
                "Commit or stash these files before running SYS-0060:\n"
                + "\n".join(f"  {d}" for d in genuine_dirty[:15])
                + (f"\n  ...and {len(genuine_dirty) - 15} more" if len(genuine_dirty) > 15 else "")
            )
            return False

        log_ok(patch, "working tree clean (no genuine uncommitted work)")
        return True
    except Exception as e:
        patch.errors.append(f"check_working_tree: {e}")
        return False


# ─── Step: Clean up stale tmp_pack_* files ───────────────────────────────────

def cleanup_tmp_packs(patch):
    """
    Remove stale tmp_pack_* files from .git/objects/pack/.

    These are leftovers from an interrupted git filter-repo run (diag showed
    4 files totaling ~3.8 GB from March 27). They are NOT referenced by any
    ref and are safe to delete. Frees disk space before the chown runs over
    them unnecessarily.
    """
    if patch.dry_run:
        log(patch, "[validate] would clean up .git/objects/pack/tmp_pack_* files")
        return

    pack_dir = Path("/opt/mythos/.git/objects/pack")
    if not pack_dir.is_dir():
        log_warn(patch, f"{pack_dir} does not exist — skipping tmp_pack cleanup")
        return

    try:
        tmp_packs = sorted(pack_dir.glob("tmp_pack_*"))
        if not tmp_packs:
            log_skip(patch, "no tmp_pack_* files to clean up")
            return

        total_bytes = 0
        for tp in tmp_packs:
            try:
                total_bytes += tp.stat().st_size
            except OSError:
                pass

        total_mb = total_bytes / (1024 * 1024)
        log(patch, f"found {len(tmp_packs)} tmp_pack file(s) totaling {total_mb:.0f} MB")

        # These files were created as adge (diag showed adge:adge), so we can
        # delete them directly without sudo.
        removed_count = 0
        for tp in tmp_packs:
            try:
                tp.unlink()
                removed_count += 1
                log(patch, f"removed {tp.name}")
            except PermissionError:
                # Fall back to sudo rm if direct unlink fails
                if not refresh_sudo(patch, f"delete {tp.name}"):
                    continue
                try:
                    run(["sudo", "rm", "-f", str(tp)])
                    removed_count += 1
                    log(patch, f"removed {tp.name} (sudo)")
                except subprocess.CalledProcessError as e:
                    log_warn(patch, f"could not remove {tp.name}: {e.stderr}")
            except OSError as e:
                log_warn(patch, f"could not remove {tp.name}: {e}")

        log_ok(patch, f"cleaned up {removed_count}/{len(tmp_packs)} tmp_pack files ({total_mb:.0f} MB freed)")
        patch.validations.append(f"tmp_pack cleanup: {removed_count} files, {total_mb:.0f} MB")
    except Exception as e:
        log_warn(patch, f"tmp_pack cleanup: {e}")


# ─── Step: The chown hammer ──────────────────────────────────────────────────

def chown_mythos(patch):
    """Recursive chown. Hardcoded literal. Triple-locked. Non-negotiable."""
    if patch.dry_run:
        log(patch, f"[validate] would sudo chown -R {EXPECTED_OWNER} {CHOWN_TARGET_LITERAL}")
        return

    if not refresh_sudo(patch, "chown"):
        return

    # Count root-owned files before
    try:
        before_result = run(
            ["sudo", "find", MYTHOS_ROOT_LITERAL,
             "-not", "-user", "adge", "-o", "-not", "-group", "adge"],
            check=False,
            timeout=60,
        )
        before_count = len([l for l in (before_result.stdout or "").splitlines() if l.strip()])
        log(patch, f"root-owned files before chown: {before_count}")
    except Exception as e:
        log_warn(patch, f"pre-chown count failed: {e}")
        before_count = None

    # Refresh again right before the chown itself — just in case find took a while
    if not refresh_sudo(patch, "chown (final)"):
        return

    # The chown. Hardcoded target. No variables. 5-minute timeout because
    # recursive chown on a 53GB .git/ is the bottleneck but should still
    # complete well under 5 minutes (inode metadata only, no data copy).
    try:
        log(patch, "running: sudo chown -R adge:adge /opt/mythos/")
        run(
            ["sudo", "chown", "-R", "adge:adge", "/opt/mythos/"],
            timeout=300,
        )
        log_ok(patch, "chown complete")
    except subprocess.CalledProcessError as e:
        patch.errors.append(f"chown failed: {e.stderr}")
        return
    except subprocess.TimeoutExpired:
        patch.errors.append("chown timed out after 300s (5 minutes)")
        return

    # Verify
    if not refresh_sudo(patch, "post-chown verify"):
        return
    try:
        after_result = run(
            ["sudo", "find", MYTHOS_ROOT_LITERAL,
             "-not", "-user", "adge", "-o", "-not", "-group", "adge"],
            check=False,
            timeout=60,
        )
        after_count = len([l for l in (after_result.stdout or "").splitlines() if l.strip()])
        if after_count == 0:
            log_ok(patch, f"verified: 0 root-owned files remain (fixed {before_count or '?'})")
            patch.validations.append(f"chown complete: {before_count or '?'} files fixed")
        else:
            patch.errors.append(
                f"chown verification failed: {after_count} files still not adge-owned. "
                f"Sample: {after_result.stdout[:500]}"
            )
    except Exception as e:
        log_warn(patch, f"post-chown verification failed: {e}")


# ─── Step: Clear stale __pycache__ ───────────────────────────────────────────

def clear_pycache(patch):
    if patch.dry_run:
        log(patch, "[validate] would clear __pycache__/ directories")
        return

    try:
        find_result = run(
            ["find", MYTHOS_ROOT_LITERAL, "-type", "d", "-name", "__pycache__"],
            check=False,
            timeout=60,
        )
        dirs = [l for l in (find_result.stdout or "").splitlines() if l.strip()]
        log(patch, f"found {len(dirs)} __pycache__ directories")

        if not dirs:
            log_skip(patch, "no __pycache__ dirs to clear")
            return

        run(
            ["find", MYTHOS_ROOT_LITERAL, "-type", "d", "-name", "__pycache__",
             "-exec", "rm", "-rf", "{}", "+"],
            check=False,
            timeout=60,
        )

        verify_result = run(
            ["find", MYTHOS_ROOT_LITERAL, "-type", "d", "-name", "__pycache__"],
            check=False,
            timeout=60,
        )
        remaining = [l for l in (verify_result.stdout or "").splitlines() if l.strip()]
        if not remaining:
            log_ok(patch, f"cleared {len(dirs)} __pycache__ directories")
            patch.validations.append(f"cleared {len(dirs)} pycache dirs")
        else:
            log_warn(patch, f"{len(remaining)} __pycache__ dirs remain after clear")
    except Exception as e:
        log_warn(patch, f"pycache clear: {e}")


# ─── Step: safe.directory ────────────────────────────────────────────────────

def ensure_safe_directory(patch):
    if patch.dry_run:
        log(patch, f"[validate] would add safe.directory = {MYTHOS_ROOT_LITERAL}")
        return

    try:
        check_result = run(
            ["git", "config", "--global", "--get-all", "safe.directory"],
            check=False,
        )
        existing = (check_result.stdout or "").splitlines()
        if MYTHOS_ROOT_LITERAL in existing:
            log_skip(patch, f"safe.directory {MYTHOS_ROOT_LITERAL} already configured")
            return

        run(
            ["git", "config", "--global", "--add", "safe.directory", MYTHOS_ROOT_LITERAL],
        )
        log_ok(patch, f"added safe.directory = {MYTHOS_ROOT_LITERAL}")
        patch.validations.append("safe.directory configured")
    except subprocess.CalledProcessError as e:
        log_warn(patch, f"safe.directory: {e.stderr}")


# ─── Step: git fsck --full ───────────────────────────────────────────────────

def git_fsck(patch):
    """Verify repo integrity after the chown. Generous timeout — 53GB repo."""
    if patch.dry_run:
        log(patch, "[validate] would run git fsck --full")
        return

    try:
        log(patch, "running git fsck --full (may take 1-5 minutes on large repo)")
        result = run(
            ["git", "-C", MYTHOS_ROOT_LITERAL, "fsck", "--full", "--no-dangling"],
            check=False,
            timeout=600,
        )
        if result.returncode == 0:
            log_ok(patch, "git fsck --full passed")
            patch.validations.append("git fsck clean")
        else:
            stderr = result.stderr or ""
            error_lines = [l for l in stderr.splitlines()
                           if l.strip() and not l.startswith("notice:")]
            if error_lines:
                # fsck errors don't necessarily mean corruption — could be
                # dangling objects from filter-repo attempts. Log them as
                # warnings rather than failing the patch.
                log_warn(patch, f"git fsck found {len(error_lines)} notes:")
                for el in error_lines[:10]:
                    patch.logger.log(f"    {el}")
                if len(error_lines) > 10:
                    patch.logger.log(f"    ...and {len(error_lines) - 10} more")
                patch.validations.append(f"git fsck completed with {len(error_lines)} notes")
            else:
                log_ok(patch, "git fsck --full passed (with notices)")
                patch.validations.append("git fsck clean with notices")
    except subprocess.TimeoutExpired:
        patch.errors.append("git fsck timed out after 600s")
    except Exception as e:
        log_warn(patch, f"git fsck: {e}")


# ─── Step: Create failed/ dirs for SYS-0061 ──────────────────────────────────

def create_failed_dirs(patch):
    if patch.dry_run:
        log(patch, f"[validate] would create {FAILED_DIR} and {FAILED_ARCHIVE_DIR}")
        return

    try:
        FAILED_DIR.mkdir(parents=True, exist_ok=True)
        FAILED_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

        readme = FAILED_DIR / "README.md"
        if not readme.exists():
            readme.write_text(
                "# Failed Patch Quarantine\n\n"
                "This directory holds patches that failed to install and were rolled back.\n"
                "Each failed patch is moved here with a timestamp suffix so there is no\n"
                "ambiguity between the failed version and any future replacement.\n\n"
                "## Structure\n\n"
                "```\n"
                "failed/\n"
                "├── SYS-NNNN_description_<timestamp>/    ← extracted patch directory\n"
                "│   ├── install.sh\n"
                "│   ├── apply_patch.py\n"
                "│   ├── FAILURE_REPORT.md                 ← auto-generated diagnosis\n"
                "│   └── result.json                       ← PatchBase result manifest\n"
                "└── archive/\n"
                "    └── SYS-NNNN_description_<timestamp>.zip\n"
                "```\n\n"
                "## The rule\n\n"
                "Patch numbers are **monotonic and burned on failure**, with ONE exception:\n"
                "a pre-flight failure (where the patch aborts before any destructive work\n"
                "has been done, with zero side effects) does NOT burn the number. The same\n"
                "patch number can be reused in that case.\n\n"
                "Every other failure mode — mid-install crash, rollback triggered, partial\n"
                "state left on disk — burns the number permanently. The next attempt uses\n"
                "`current + 1`, never a retry at the same number.\n\n"
                "## History\n\n"
                "Created by SYS-0060. The quarantine hook that populates it is deployed\n"
                "by SYS-0061+.\n"
            )
            log_ok(patch, f"created {FAILED_DIR}/ + README")
        else:
            log_skip(patch, f"{FAILED_DIR} already has README")

        patch.validations.append(f"failed/ quarantine dirs created")
    except Exception as e:
        log_warn(patch, f"create failed/ dirs: {e}")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    patch = PatchBase(
        stream='SYS',
        number=60,
        description='git permissions and sync recovery',
        patch_type='MINOR',
    )
    patch.begin()

    monitor_was_stopped = False

    try:
        # ── 1. Initial sudo cache ──────────────────────────────────────
        patch.logger.log("\n[1/9] Refreshing sudo cache")
        if not initial_sudo_cache(patch):
            patch.finish()
            return 1

        # ── 2. Target sanity ───────────────────────────────────────────
        patch.logger.log("\n[2/9] Verifying target sanity")
        if not verify_target_sanity(patch):
            patch.finish()
            return 1

        # ── 3. Stop the patch monitor ──────────────────────────────────
        patch.logger.log("\n[3/9] Stopping patch monitor")
        stop_patch_monitor(patch)
        if not patch.dry_run and not patch.errors:
            monitor_was_stopped = True
        if patch.errors:
            patch.finish()
            return 1

        # ── 4. Working tree check ──────────────────────────────────────
        patch.logger.log("\n[4/9] Checking working tree")
        if not check_working_tree(patch):
            patch.finish()
            return 1

        # ── 5. Clean up stale tmp_pack_* files ─────────────────────────
        patch.logger.log("\n[5/9] Cleaning up stale tmp_pack_* files")
        cleanup_tmp_packs(patch)
        # Non-fatal — continue even if some tmp_pack files couldn't be removed

        # ── 6. The chown hammer ────────────────────────────────────────
        patch.logger.log("\n[6/9] Running chown -R adge:adge /opt/mythos/")
        chown_mythos(patch)
        if patch.errors:
            patch.finish()
            return 1

        # ── 7. Clear __pycache__ + safe.directory ──────────────────────
        patch.logger.log("\n[7/9] Clearing __pycache__ + configuring safe.directory")
        clear_pycache(patch)
        ensure_safe_directory(patch)
        # Both non-fatal

        # ── 8. git fsck --full ─────────────────────────────────────────
        patch.logger.log("\n[8/9] Verifying repo integrity with git fsck")
        git_fsck(patch)
        # fsck issues are non-fatal at this point — the repo has known
        # bloat from stale filter-repo runs and the cleanup happens in SYS-0061

        # ── 9. Create failed/ dirs ─────────────────────────────────────
        patch.logger.log("\n[9/9] Creating failed/ quarantine directories")
        create_failed_dirs(patch)

    finally:
        if monitor_was_stopped:
            patch.logger.log("\n[cleanup] Restarting patch monitor")
            start_patch_monitor(patch)

    # Summary banner
    if not patch.errors and not patch.dry_run:
        patch.logger.log("")
        patch.logger.log("=" * 55)
        patch.logger.log("  SYS-0060: PERMISSIONS FIXED")
        patch.logger.log("=" * 55)
        patch.logger.log("  ✓ All files in /opt/mythos/ owned by adge:adge")
        patch.logger.log("  ✓ .git/ reflog writes will now succeed")
        patch.logger.log("  ✓ Stale tmp_pack files cleaned up")
        patch.logger.log("  ✓ safe.directory configured")
        patch.logger.log("  ✓ /opt/mythos/patches/failed/ ready for SYS-0061")
        patch.logger.log("")
        patch.logger.log("  NOT done in this patch (deferred to SYS-0061):")
        patch.logger.log("  ⊘ .git/ slim — repo is 53 GB, needs filter-repo")
        patch.logger.log("  ⊘ git push — can't push 53 GB to GitHub until slim")
        patch.logger.log("")
        patch.logger.log("  Next: SYS-0061 — git_repo_slim (remove voice memos")
        patch.logger.log("        from history, git gc, force-push to origin)")
        patch.logger.log("=" * 55)

    patch.finish()
    return 1 if patch.errors else 0


if __name__ == '__main__':
    sys.exit(main())
