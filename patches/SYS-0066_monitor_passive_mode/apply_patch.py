#!/usr/bin/env python3
"""
SYS-0066: Monitor passive mode + patch-install git integration.

BEFORE: mythos-patch-monitor watches Downloads, auto-extracts patches,
runs install.sh as root via sudo, handles git snapshots + commits + push.
This caused monitor-vs-manual race conditions (SYS-0063 shipped twice,
SYS-0064 never ran as root).

AFTER: Monitor only DETECTS patches and sends a Telegram notification.
patch-install.sh does everything: copy to archive, extract, git snapshot,
run install.sh, commit + tag + push. Zip stays in Downloads until user
explicitly runs patch-install <ID>.

Files modified:
  1. /opt/mythos/archive/mythos_patch_monitor.py  (process_patch replaced)
  2. /opt/mythos/bin/patch-install.sh             (git integration added)

Services restarted:
  - mythos-patch-monitor.service (via SYS-0062 wrapper from SYS-0063)
"""
import sys
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

MONITOR_PATH = Path('/opt/mythos/archive/mythos_patch_monitor.py')
PATCH_INSTALL_PATH = Path('/opt/mythos/bin/patch-install.sh')
MONITOR_BACKUP = Path('/tmp/mythos_patch_monitor.py.pre_SYS-0066.bak')
PATCH_INSTALL_BACKUP = Path('/tmp/patch-install.sh.pre_SYS-0066.bak')


# ── Monitor edits ─────────────────────────────────────────────────────────────

# 1. Flip AUTO_EXECUTE_INSTALL (belt-and-suspenders — we're also replacing the method)
OLD_AUTO_EXECUTE = "AUTO_EXECUTE_INSTALL = True"
NEW_AUTO_EXECUTE = "AUTO_EXECUTE_INSTALL = False  # SYS-0066: monitor is passive; patch-install does the work"

# 2. Replace the entire process_patch() method with a passive detect-and-notify
#    We anchor on the method signature + trailing method-boundary comment so the
#    match is unique. Paste the exact current body verbatim.
OLD_PROCESS_PATCH = '''    def process_patch(self, zip_path):
        name = zip_path.name
        if name in self.processing:
            return
        try:
            self.processing.add(name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if not self._is_valid_zip(zip_path):
                logger.error(f"Invalid patch zip: {name}")
                return
            PATCH_DIR.mkdir(parents=True, exist_ok=True)
            PATCH_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
            PATCH_LOG_DIR.mkdir(parents=True, exist_ok=True)
            # ---- GIT: Create pre-patch snapshot ----
            if git_manager and git_manager.is_repo():
                pre_tag = f"pre-patch-{name.replace('.zip', '')}-{timestamp}"
                git_manager.create_snapshot(pre_tag, f"State before {name}")
                logger.info(f"✓ Git snapshot: {pre_tag}")
            # Copy zip to patches directory
            dest = PATCH_DIR / name
            shutil.copy2(zip_path, dest)
            # Extract
            extract_dir = None
            with zipfile.ZipFile(dest, "r") as z:
                # Get list of extracted files
                files_in_zip = z.namelist()
                z.extractall(PATCH_DIR)
                
                # Determine extract directory (usually the first directory in zip)
                for f in files_in_zip:
                    if '/' in f:
                        extract_dir = PATCH_DIR / f.split('/')[0]
                        break
            # Archive the zip
            shutil.move(dest, PATCH_ARCHIVE_DIR / name)
            
            # Remove original from Downloads
            zip_path.unlink()
            logger.info(f"✓ Patch extracted: {name}")
            if extract_dir:
                logger.info(f"  Extract location: {extract_dir}")
            # ---- GIT: Commit patch and tag new version ----
            if git_manager and git_manager.is_repo():
                current_version = git_manager.get_current_version()
                
                # Try manifest version first, fall back to auto-increment
                new_version = None
                if extract_dir:
                    new_version = git_manager.get_manifest_version(extract_dir)
                if not new_version:
                    new_version = git_manager.increment_version(current_version)
                    logger.warning(f"No manifest version found, auto-incremented to {new_version}")
                
                git_manager.commit_patch(name, files_in_zip)
                git_manager.tag_version(new_version, f"After applying {name}")
                
                # Update .version file
                git_manager.update_version_file(new_version)
                
                # Push to GitHub if enabled
                if GITHUB_PUSH_ENABLED:
                    git_manager.push()
                
                logger.info(f"✓ Git versioned: {current_version} → {new_version}")
            # Log the patch application
            log_entry = {
                "timestamp": timestamp,
                "patch": name,
                "files": files_in_zip if 'files_in_zip' in dir() else [],
                "status": "success"
            }
            self._write_patch_log(log_entry)
            # ---- AUTO-EXECUTE install.sh if present ----
            if AUTO_EXECUTE_INSTALL and extract_dir:
                install_script = extract_dir / "install.sh"
                if install_script.exists():
                    logger.info(f"Running install.sh from {extract_dir}")
                    try:
                        # Make executable
                        install_script.chmod(0o755)
                        # Run with sudo so patches can write root-owned files,
                        # restart services, and compile __pycache__
                        result = subprocess.run(
                            ["sudo", "bash", str(install_script)],
                            cwd=str(extract_dir),
                            capture_output=True,
                            text=True,
                            timeout=300
                        )
                        if result.returncode == 0:
                            logger.info(f"✓ install.sh completed successfully")
                        else:
                            logger.error(f"install.sh failed: {result.stderr}")
                    except subprocess.TimeoutExpired:
                        logger.error("install.sh timed out (5 min limit)")
                    except Exception as e:
                        logger.error(f"install.sh error: {e}")
            logger.info(f"✓ Patch processed: {name}")
        except Exception as e:
            logger.error(f"Patch error {name}: {e}", exc_info=True)
            self._write_patch_log({
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "patch": name,
                "status": "error",
                "error": str(e)
            })
        finally:
            self.processing.discard(name)'''

NEW_PROCESS_PATCH = '''    def process_patch(self, zip_path):
        """SYS-0066: PASSIVE MODE.

        The monitor no longer extracts, installs, or touches the zip.
        It only detects the patch and sends a Telegram notification.
        The user runs 'patch-install <ID>' manually when ready.
        patch-install.sh handles: copy-to-archive, extract, git snapshot,
        install.sh execution, commit, tag, push.
        """
        name = zip_path.name
        if name in self.processing:
            return
        try:
            self.processing.add(name)

            # Validate the zip is readable before notifying
            if not self._is_valid_zip(zip_path):
                logger.error(f"Invalid patch zip: {name}")
                send_telegram_notification(
                    f"⚠️ Patch zip is invalid or corrupted\\n\\n{name}\\n\\n"
                    f"File left in Downloads — please re-upload."
                )
                return

            # Derive the patch ID from the filename — STREAM-NNNN_desc.zip or patch_NNNN_desc.zip
            m = re.match(r"^([A-Z]{3}-\\d{4})_", name)
            if m:
                patch_id = m.group(1)
            else:
                legacy = re.match(r"^patch_(\\d{4})_", name)
                patch_id = legacy.group(1) if legacy else name.replace(".zip", "")

            logger.info(f"✓ Patch detected (passive mode): {name}")
            logger.info(f"  Patch ID: {patch_id}")
            logger.info(f"  Run: patch-install {patch_id}")

            send_telegram_notification(
                f"📦 *Patch Detected*\\n\\n"
                f"`{name}`\\n\\n"
                f"Run to install:\\n"
                f"`patch-install {patch_id}`\\n\\n"
                f"_Zip remains in Downloads until installed._"
            )
        except Exception as e:
            logger.error(f"Patch detect error {name}: {e}", exc_info=True)
        finally:
            self.processing.discard(name)'''


# ── patch-install.sh edits ────────────────────────────────────────────────────

# We need to add git work. The current script has these phases:
#   1. find zip, archive it (cp)
#   2. extract
#   3. chmod install.sh
#   4. (optional) dry-run phase
#   5. real install phase
#   6. on failure: auto-rollback
#
# We inject:
#   - Before phase 1: nothing (git snapshot needs timestamp; inject between 2 and 3)
#   - Between phase 2 (extract) and phase 3 (chmod): create pre-patch git snapshot/tag
#   - After successful install (inside the `if [ $exit_code -eq 0 ]`): commit, tag, push, update .version
#
# Anchor 1: the "# Make install.sh executable" comment (unique)
# Anchor 2: the "echo \"✅ $patch_id installed\"" line (unique)

OLD_CHMOD_ANCHOR = '''    # Make install.sh executable
    chmod +x "$patch_dir/install.sh" 2>/dev/null'''

NEW_CHMOD_ANCHOR = '''    # Make install.sh executable
    chmod +x "$patch_dir/install.sh" 2>/dev/null
    # ── SYS-0066: Pre-patch git snapshot ──────────────────────────────────
    local ts=$(date +%Y%m%d_%H%M%S)
    local pre_tag="pre-patch-${base_name}-${ts}"
    if cd "$mythos_root" 2>/dev/null; then
        if [ -d .git ]; then
            if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
                git add -A >/dev/null 2>&1
                git commit -m "Auto-commit before ${pre_tag}" >/dev/null 2>&1
            fi
            git tag -a "$pre_tag" -m "State before $base_name" >/dev/null 2>&1 && \\
                echo "  📌 Git snapshot: $pre_tag"
        fi
        cd - >/dev/null 2>&1
    fi'''

OLD_SUCCESS_ANCHOR = '''    if [ $exit_code -eq 0 ]; then
        echo "✅ $patch_id installed"
    else'''

NEW_SUCCESS_ANCHOR = '''    if [ $exit_code -eq 0 ]; then
        echo "✅ $patch_id installed"
        # ── SYS-0066: Post-install git commit + tag + push ───────────────
        if cd "$mythos_root" 2>/dev/null; then
            if [ -d .git ]; then
                git add -A >/dev/null 2>&1
                if [ -n "$(git status --porcelain --cached 2>/dev/null)" ]; then
                    git commit -m "Applied patch: ${base_name}.zip" >/dev/null 2>&1 && \\
                        echo "  📌 Git: committed patch changes"
                fi
                # Determine new version: read manifest.json if present, else auto-increment
                local new_version=""
                if [ -f "$patch_dir/manifest.json" ]; then
                    new_version=$(python3 -c "
import json, sys
try:
    m = json.load(open('$patch_dir/manifest.json'))
    v = (m.get('versioning', {}).get('new_system_version')
         or m.get('patch', {}).get('semantic_version'))
    if v and not v.startswith('v'):
        v = 'v' + v
    print(v or '')
except Exception:
    print('')
" 2>/dev/null)
                fi
                if [ -z "$new_version" ]; then
                    local current=$(git tag -l 'v*' --sort=-v:refname 2>/dev/null | head -1)
                    [ -z "$current" ] && current="v0.0.0"
                    new_version=$(python3 -c "
import re
m = re.match(r'v(\\d+)\\.(\\d+)\\.(\\d+)', '$current')
if m:
    a, b, c = map(int, m.groups())
    print(f'v{a}.{b}.{c+1}')
else:
    print('v1.0.0')
" 2>/dev/null)
                fi
                if [ -n "$new_version" ]; then
                    git tag -a "$new_version" -m "After applying ${base_name}.zip" >/dev/null 2>&1 && \\
                        echo "  📌 Git: tagged $new_version"
                    echo "${new_version#v}" > "$mythos_root/.version"
                fi
                # Push to origin main (tags included)
                if git remote get-url origin >/dev/null 2>&1; then
                    if git push origin main --tags >/dev/null 2>&1; then
                        echo "  📌 Git: pushed to origin/main"
                    else
                        echo "  ⚠ Git push failed (check SSH / network)"
                    fi
                fi
            fi
            cd - >/dev/null 2>&1
        fi
    else'''


def edit_file(patch, path, backup_path, old_new_pairs, label):
    """Read file, apply all str.replace pairs in memory, syntax-check if .py,
    atomic write with preserved perms, on failure restore from backup.
    Returns True on success."""
    if not path.is_file():
        patch.errors.append(f"{label}: not found at {path}")
        patch.logger.log(f"  ✗ {label}: not found")
        return False

    original = path.read_text()
    patch.logger.log(f"  · read {label} ({len(original.splitlines())} lines)")

    # Idempotency: if the new_content marker is already present, skip
    first_new = old_new_pairs[0][1][:80]
    if first_new in original:
        patch.logger.log(f"  ⊙ {label} already migrated (idempotent skip)")
        patch.validations.append(f"{label} already migrated")
        return True

    new_source = original
    for i, (old, new) in enumerate(old_new_pairs, 1):
        count = new_source.count(old)
        if count != 1:
            patch.errors.append(f"{label} edit {i}: anchor matched {count} times, expected 1")
            patch.logger.log(f"  ✗ {label} edit {i}: anchor matched {count} times")
            return False
        new_source = new_source.replace(old, new)
        patch.logger.log(f"  ✓ {label} edit {i}: applied")

    # Backup
    if patch.dry_run:
        patch.logger.log(f"  · [dry run] would backup → {backup_path}")
    else:
        shutil.copy2(str(path), str(backup_path))
        patch.logger.log(f"  ✓ backup → {backup_path}")

    # Write candidate into an adge-owned tempdir so __pycache__ collisions
    # with pre-existing root-owned /tmp/__pycache__ cannot happen.
    import tempfile as _tempfile
    tmp_dir = _tempfile.mkdtemp(prefix=f'sys0066_{label}_')
    tmp_path = os.path.join(tmp_dir, path.name)
    with open(tmp_path, 'w') as tf:
        tf.write(new_source)

    try:
        if path.suffix == '.py':
            # Use in-process py_compile with an explicit cfile path inside our tmpdir.
            # This avoids any __pycache__ directory resolution entirely.
            import py_compile
            cfile = os.path.join(tmp_dir, path.name + 'c')
            try:
                py_compile.compile(tmp_path, cfile=cfile, doraise=True)
            except py_compile.PyCompileError as e:
                patch.errors.append(f"{label}: py_compile failed: {e}")
                patch.logger.log(f"  ✗ {label}: syntax check failed: {e}")
                shutil.rmtree(tmp_dir, ignore_errors=True)
                return False
            except PermissionError as e:
                patch.errors.append(f"{label}: py_compile permission error: {e}")
                patch.logger.log(f"  ✗ {label}: py_compile permission error: {e}")
                shutil.rmtree(tmp_dir, ignore_errors=True)
                return False
            patch.logger.log(f"  ✓ {label}: py_compile passed")
        elif path.suffix == '.sh':
            r = subprocess.run(['/bin/bash', '-n', tmp_path], capture_output=True, text=True)
            if r.returncode != 0:
                patch.errors.append(f"{label}: bash -n failed: {r.stderr.strip()}")
                patch.logger.log(f"  ✗ {label}: bash syntax check failed: {r.stderr.strip()}")
                shutil.rmtree(tmp_dir, ignore_errors=True)
                return False
            patch.logger.log(f"  ✓ {label}: bash -n passed")

        if patch.dry_run:
            patch.logger.log(f"  · [dry run] would atomic-move → {path}")
            patch.validations.append(f"{label}: dry-run OK")
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return True

        # Preserve permissions from the target file, then atomic-move
        shutil.copystat(str(path), tmp_path)
        shutil.move(tmp_path, str(path))
        patch.files_deployed.append(str(path))
        patch.logger.log(f"  ✓ {label}: atomic-moved into place")
        return True
    finally:
        # Clean up tmpdir if anything is left (after successful move, the
        # source file is gone but the dir remains)
        shutil.rmtree(tmp_dir, ignore_errors=True)


def main():
    patch = PatchBase(
        stream='SYS',
        number=66,
        description='monitor passive mode + patch-install git integration',
        patch_type='MINOR',
    )
    patch.begin()

    # Edit 1: monitor
    ok1 = edit_file(
        patch, MONITOR_PATH, MONITOR_BACKUP,
        [
            (OLD_AUTO_EXECUTE, NEW_AUTO_EXECUTE),
            (OLD_PROCESS_PATCH, NEW_PROCESS_PATCH),
        ],
        label="mythos_patch_monitor.py",
    )
    if not ok1:
        patch.finish()
        sys.exit(1)

    # Edit 2: patch-install.sh
    ok2 = edit_file(
        patch, PATCH_INSTALL_PATH, PATCH_INSTALL_BACKUP,
        [
            (OLD_CHMOD_ANCHOR, NEW_CHMOD_ANCHOR),
            (OLD_SUCCESS_ANCHOR, NEW_SUCCESS_ANCHOR),
        ],
        label="patch-install.sh",
    )
    if not ok2:
        # Roll back monitor if it was applied
        if not patch.dry_run and MONITOR_BACKUP.is_file():
            shutil.copy2(str(MONITOR_BACKUP), str(MONITOR_PATH))
            patch.logger.log("  ⊙ restored monitor from backup")
        patch.finish()
        sys.exit(1)

    # Restart the monitor service via the new wrapper (SYS-0063)
    if not patch.dry_run:
        patch.restart_service('mythos-patch-monitor.service')

    patch.finish()


if __name__ == '__main__':
    main()
