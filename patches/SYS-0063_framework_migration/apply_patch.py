#!/usr/bin/env python3
"""
SYS-0063: Framework migration — patch_base.py uses SYS-0062 wrappers.

This patch modifies /opt/mythos/patches/scripts/patch_base.py to:
  1. Add sudo_wrapper() method that calls /usr/local/libexec/mythos/<name>
  2. Add convenience methods: start_service, stop_service, is_service_active,
     install_systemd_unit, install_cloudflared_config, scan_perms,
     fix_ownership, backup_git, clean_tmp_pack, allowlist_append_unit
  3. Replace restart_service() body to call the mythos-servicectl wrapper
  4. Add a privilege foundation sanity check inside begin()

This is a bootstrap-adjacent patch: it modifies patch_base.py itself. We
do NOT use PatchBase.str_replace() for the edit — instead we read the file,
do all str.replace ops in memory, syntax-check, import-check, and atomic-move.
On any failure, we restore the backup.
"""
import sys
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

PATCH_BASE_PATH = Path('/opt/mythos/patches/scripts/patch_base.py')
BACKUP_PATH = Path('/tmp/patch_base.py.pre_SYS-0063.bak')


# ── The replacements ────────────────────────────────────────────────────────

# 1. Replace the entire restart_service method body
OLD_RESTART_SERVICE = '''    def restart_service(self, service_name: str):
        """Restart a systemd service. In dry-run, just validates the service exists."""
        if self.dry_run:
            # Check service exists
            try:
                result = subprocess.run(
                    ['systemctl', 'cat', service_name],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    self.errors.append(f"service not found: {service_name}")
                    self.logger.log(f"  ✗ [validate] service {service_name}: not found")
                else:
                    self.validations.append(f"service {service_name} — exists")
                    self.logger.log(f"  ✓ [validate] service {service_name} — exists")
            except Exception as e:
                self.errors.append(f"service check {service_name}: {e}")
                self.logger.log(f"  ✗ [validate] service {service_name}: {e}")
            return

        # Real restart (--no-block prevents hanging on slow services)
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'restart', '--no-block', service_name],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                self.errors.append(f"restart {service_name}: {result.stderr.strip()}")
                self.logger.log(f"  ✗ restart {service_name}: {result.stderr.strip()}")
            else:
                self.services_restarted.append(service_name)
                self.logger.log(f"  ✓ restarted {service_name}")
        except Exception as e:
            self.errors.append(f"restart {service_name}: {e}")
            self.logger.log(f"  ✗ restart {service_name}: {e}")

    # ── STREAMS.json ──────────────────────────────────────────────────────────'''

NEW_RESTART_AND_WRAPPERS = '''    def restart_service(self, service_name: str):
        """Restart a systemd service via the SYS-0062 mythos-servicectl wrapper."""
        if self.dry_run:
            try:
                result = subprocess.run(
                    ['systemctl', 'cat', service_name],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    self.errors.append(f"service not found: {service_name}")
                    self.logger.log(f"  ✗ [validate] service {service_name}: not found")
                else:
                    self.validations.append(f"service {service_name} — exists")
                    self.logger.log(f"  ✓ [validate] service {service_name} — exists")
            except Exception as e:
                self.errors.append(f"service check {service_name}: {e}")
                self.logger.log(f"  ✗ [validate] service {service_name}: {e}")
            return

        try:
            self.sudo_wrapper('mythos-servicectl', 'restart', service_name, timeout=30)
            self.services_restarted.append(service_name)
            self.logger.log(f"  ✓ restarted {service_name}")
        except subprocess.CalledProcessError as e:
            stderr = (e.stderr or '').strip()
            self.errors.append(f"restart {service_name}: {stderr}")
            self.logger.log(f"  ✗ restart {service_name}: {stderr}")
        except Exception as e:
            self.errors.append(f"restart {service_name}: {e}")
            self.logger.log(f"  ✗ restart {service_name}: {e}")

    # ── Privilege wrappers (SYS-0062 / SYS-0063) ──────────────────────────────

    def sudo_wrapper(self, wrapper_name: str, *args, timeout: int = 120, check: bool = True):
        """Invoke a /usr/local/libexec/mythos/ wrapper via passwordless sudo.

        Wrappers are installed by SYS-0062. They are root-owned, validated,
        and whitelisted in /etc/sudoers.d/mythos-patches for adge.
        """
        wrapper_path = f"/usr/local/libexec/mythos/{wrapper_name}"
        if not os.path.isfile(wrapper_path):
            raise RuntimeError(
                f"Mythos privilege wrapper not found: {wrapper_path}. "
                f"Install SYS-0062 first."
            )
        cmd = ["sudo", "-n", wrapper_path] + [str(a) for a in args]
        return subprocess.run(
            cmd,
            check=check,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    def start_service(self, service_name: str):
        """Start a systemd service via mythos-servicectl."""
        try:
            self.sudo_wrapper('mythos-servicectl', 'start', service_name, timeout=30)
            self.logger.log(f"  ✓ started {service_name}")
        except subprocess.CalledProcessError as e:
            stderr = (e.stderr or '').strip()
            self.errors.append(f"start {service_name}: {stderr}")
            self.logger.log(f"  ✗ start {service_name}: {stderr}")
        except Exception as e:
            self.errors.append(f"start {service_name}: {e}")
            self.logger.log(f"  ✗ start {service_name}: {e}")

    def stop_service(self, service_name: str):
        """Stop a systemd service via mythos-servicectl."""
        try:
            self.sudo_wrapper('mythos-servicectl', 'stop', service_name, timeout=30)
            self.logger.log(f"  ✓ stopped {service_name}")
        except subprocess.CalledProcessError as e:
            stderr = (e.stderr or '').strip()
            self.errors.append(f"stop {service_name}: {stderr}")
            self.logger.log(f"  ✗ stop {service_name}: {stderr}")
        except Exception as e:
            self.errors.append(f"stop {service_name}: {e}")
            self.logger.log(f"  ✗ stop {service_name}: {e}")

    def is_service_active(self, service_name: str) -> bool:
        """Return True if the service is currently active. Never raises."""
        try:
            result = self.sudo_wrapper(
                'mythos-servicectl', 'is-active', service_name,
                timeout=10, check=False,
            )
            return result.stdout.strip() == 'active'
        except Exception:
            return False

    def install_systemd_unit(self, basename: str):
        """Deploy a systemd unit from /opt/mythos/systemd/<basename> to /etc/systemd/system/."""
        try:
            self.sudo_wrapper('mythos-install-unit', basename, timeout=30)
            self.logger.log(f"  ✓ installed unit {basename}")
        except subprocess.CalledProcessError as e:
            stderr = (e.stderr or '').strip()
            self.errors.append(f"install_systemd_unit {basename}: {stderr}")
            self.logger.log(f"  ✗ install unit {basename}: {stderr}")
        except Exception as e:
            self.errors.append(f"install_systemd_unit {basename}: {e}")
            self.logger.log(f"  ✗ install unit {basename}: {e}")

    def install_cloudflared_config(self):
        """Deploy /opt/mythos/cloudflared/config.yml to /etc/cloudflared/config.yml."""
        try:
            self.sudo_wrapper('mythos-install-cloudflared-config', timeout=30)
            self.logger.log(f"  ✓ installed cloudflared config")
        except subprocess.CalledProcessError as e:
            stderr = (e.stderr or '').strip()
            self.errors.append(f"install_cloudflared_config: {stderr}")
            self.logger.log(f"  ✗ install cloudflared config: {stderr}")
        except Exception as e:
            self.errors.append(f"install_cloudflared_config: {e}")
            self.logger.log(f"  ✗ install cloudflared config: {e}")

    def scan_perms(self) -> int:
        """Count files under /opt/mythos/ not owned by adge. Returns -1 on failure."""
        try:
            result = self.sudo_wrapper('mythos-scan-perms', timeout=60, check=False)
            out = result.stdout.strip()
            # wrapper output format: "count=N" or just "N"
            if '=' in out:
                out = out.split('=', 1)[1].strip()
            return int(out)
        except Exception as e:
            self.logger.log(f"  ⚠ scan_perms failed: {e}")
            return -1

    def fix_ownership(self):
        """Recursive chown /opt/mythos/ to adge:adge."""
        try:
            self.sudo_wrapper('mythos-fix-ownership', timeout=120)
            self.logger.log(f"  ✓ fixed ownership of /opt/mythos/")
        except subprocess.CalledProcessError as e:
            stderr = (e.stderr or '').strip()
            self.errors.append(f"fix_ownership: {stderr}")
            self.logger.log(f"  ✗ fix_ownership: {stderr}")
        except Exception as e:
            self.errors.append(f"fix_ownership: {e}")
            self.logger.log(f"  ✗ fix_ownership: {e}")

    def backup_git(self) -> str:
        """Create a timestamped tar.gz of /opt/mythos/.git in /tmp/. Returns path or empty string."""
        try:
            result = self.sudo_wrapper('mythos-backup-git', timeout=300)
            path = result.stdout.strip()
            self.logger.log(f"  ✓ git backup: {path}")
            return path
        except subprocess.CalledProcessError as e:
            stderr = (e.stderr or '').strip()
            self.errors.append(f"backup_git: {stderr}")
            self.logger.log(f"  ✗ backup_git: {stderr}")
            return ''
        except Exception as e:
            self.errors.append(f"backup_git: {e}")
            self.logger.log(f"  ✗ backup_git: {e}")
            return ''

    def clean_tmp_pack(self):
        """Remove stale tmp_pack_* files from /opt/mythos/.git/."""
        try:
            self.sudo_wrapper('mythos-clean-tmp-pack', timeout=30)
            self.logger.log(f"  ✓ cleaned tmp_pack files")
        except subprocess.CalledProcessError as e:
            stderr = (e.stderr or '').strip()
            self.errors.append(f"clean_tmp_pack: {stderr}")
            self.logger.log(f"  ✗ clean_tmp_pack: {stderr}")
        except Exception as e:
            self.errors.append(f"clean_tmp_pack: {e}")
            self.logger.log(f"  ✗ clean_tmp_pack: {e}")

    def allowlist_append_unit(self, unit: str):
        """Atomically add a unit to /etc/mythos/allowed-units.txt."""
        try:
            self.sudo_wrapper('mythos-allowlist-append', unit, timeout=10)
            self.logger.log(f"  ✓ allowlisted {unit}")
        except subprocess.CalledProcessError as e:
            stderr = (e.stderr or '').strip()
            self.errors.append(f"allowlist_append_unit {unit}: {stderr}")
            self.logger.log(f"  ✗ allowlist {unit}: {stderr}")
        except Exception as e:
            self.errors.append(f"allowlist_append_unit {unit}: {e}")
            self.logger.log(f"  ✗ allowlist {unit}: {e}")

    # ── STREAMS.json ──────────────────────────────────────────────────────────'''

# 2. Add privilege foundation sanity check inside begin()
OLD_BEGIN = '''    def begin(self):
        self._start_time = datetime.datetime.now()
        mode_tag = " [DRY RUN]" if self.dry_run else ""
        self.logger.log(f"[{self.patch_id}]{mode_tag} {self.description}")
        self.logger.log("=" * 55)'''

NEW_BEGIN = '''    def begin(self):
        self._start_time = datetime.datetime.now()
        mode_tag = " [DRY RUN]" if self.dry_run else ""
        self.logger.log(f"[{self.patch_id}]{mode_tag} {self.description}")
        self.logger.log("=" * 55)
        # SYS-0063: privilege foundation sanity check
        wrapper_check = "/usr/local/libexec/mythos/mythos-servicectl"
        if os.path.isfile(wrapper_check):
            try:
                subprocess.run(
                    ["sudo", "-n", wrapper_check, "is-active", "mythos-bot.service"],
                    check=False, capture_output=True, timeout=5,
                )
                self.logger.log("  ✓ privilege foundation (SYS-0062) installed")
            except Exception as e:
                self.logger.log(f"  ⚠ privilege foundation check failed: {e}")
        else:
            self.logger.log(
                "  ⚠ privilege foundation (SYS-0062) not installed. "
                "Patches using sudo may prompt for passwords."
            )'''


def main():
    patch = PatchBase(
        stream='SYS',
        number=63,
        description='framework migration to SYS-0062 wrappers',
        patch_type='MINOR',
    )
    patch.begin()

    if not PATCH_BASE_PATH.is_file():
        patch.errors.append(f"patch_base.py not found at {PATCH_BASE_PATH}")
        patch.logger.log(f"  ✗ patch_base.py not found at {PATCH_BASE_PATH}")
        patch.finish()
        sys.exit(1)

    # Read source
    original_source = PATCH_BASE_PATH.read_text()
    patch.logger.log(f"  · read patch_base.py ({len(original_source.splitlines())} lines)")

    # Idempotency check — if sudo_wrapper already exists, skip
    if 'def sudo_wrapper(' in original_source:
        patch.logger.log("  ⊙ sudo_wrapper already present — patch_base.py already migrated")
        patch.validations.append("patch_base.py already migrated (idempotent skip)")
        patch.finish()
        return

    # Backup
    if patch.dry_run:
        patch.logger.log(f"  · [dry run] would backup to {BACKUP_PATH}")
    else:
        shutil.copy2(str(PATCH_BASE_PATH), str(BACKUP_PATH))
        patch.logger.log(f"  ✓ backup → {BACKUP_PATH}")

    # Apply edits in-memory
    new_source = original_source

    # Edit 1: replace restart_service body + insert wrapper methods
    if OLD_RESTART_SERVICE not in new_source:
        patch.errors.append("Edit 1 anchor not found: restart_service block")
        patch.logger.log("  ✗ Edit 1 anchor not found (restart_service)")
        patch.finish()
        sys.exit(1)
    if new_source.count(OLD_RESTART_SERVICE) != 1:
        patch.errors.append(f"Edit 1 anchor matched {new_source.count(OLD_RESTART_SERVICE)} times, expected 1")
        patch.logger.log("  ✗ Edit 1 anchor not unique")
        patch.finish()
        sys.exit(1)
    new_source = new_source.replace(OLD_RESTART_SERVICE, NEW_RESTART_AND_WRAPPERS)
    patch.logger.log("  ✓ edit 1: restart_service migrated + 11 wrapper methods added")

    # Edit 2: privilege check inside begin()
    if OLD_BEGIN not in new_source:
        patch.errors.append("Edit 2 anchor not found: begin() block")
        patch.logger.log("  ✗ Edit 2 anchor not found (begin)")
        if not patch.dry_run:
            shutil.copy2(str(BACKUP_PATH), str(PATCH_BASE_PATH))
            patch.logger.log("  ⊙ restored from backup")
        patch.finish()
        sys.exit(1)
    if new_source.count(OLD_BEGIN) != 1:
        patch.errors.append(f"Edit 2 anchor matched {new_source.count(OLD_BEGIN)} times, expected 1")
        patch.logger.log("  ✗ Edit 2 anchor not unique")
        if not patch.dry_run:
            shutil.copy2(str(BACKUP_PATH), str(PATCH_BASE_PATH))
            patch.logger.log("  ⊙ restored from backup")
        patch.finish()
        sys.exit(1)
    new_source = new_source.replace(OLD_BEGIN, NEW_BEGIN)
    patch.logger.log("  ✓ edit 2: begin() privilege check added")

    # Write to tempfile and syntax-check
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.py', delete=False, dir='/tmp'
    ) as tf:
        tf.write(new_source)
        tmp_path = tf.name

    syntax_result = subprocess.run(
        ['/opt/mythos/.venv/bin/python3', '-m', 'py_compile', tmp_path],
        capture_output=True, text=True,
    )
    if syntax_result.returncode != 0:
        patch.errors.append(f"py_compile failed: {syntax_result.stderr.strip()}")
        patch.logger.log(f"  ✗ syntax check failed: {syntax_result.stderr.strip()}")
        os.unlink(tmp_path)
        patch.finish()
        sys.exit(1)
    patch.logger.log("  ✓ py_compile syntax check passed")

    if patch.dry_run:
        patch.logger.log("  · [dry run] would atomic-move tempfile to patch_base.py")
        patch.logger.log("  · [dry run] would run import check")
        os.unlink(tmp_path)
        patch.validations.append("dry-run: edits applied, syntax OK")
        patch.finish()
        return

    # Atomic move
    shutil.move(tmp_path, str(PATCH_BASE_PATH))
    patch.files_deployed.append(str(PATCH_BASE_PATH))
    patch.logger.log(f"  ✓ atomic move → {PATCH_BASE_PATH}")

    # Import check via subprocess (fresh interpreter — current process has stale class)
    import_check = subprocess.run(
        ['/opt/mythos/.venv/bin/python3', '-c',
         "import sys; sys.path.insert(0, '/opt/mythos/patches/scripts'); "
         "from patch_base import PatchBase; "
         "assert hasattr(PatchBase, 'sudo_wrapper'), 'sudo_wrapper missing'; "
         "assert hasattr(PatchBase, 'restart_service'), 'restart_service missing'; "
         "assert hasattr(PatchBase, 'start_service'), 'start_service missing'; "
         "assert hasattr(PatchBase, 'stop_service'), 'stop_service missing'; "
         "assert hasattr(PatchBase, 'is_service_active'), 'is_service_active missing'; "
         "assert hasattr(PatchBase, 'install_systemd_unit'), 'install_systemd_unit missing'; "
         "assert hasattr(PatchBase, 'install_cloudflared_config'), 'install_cloudflared_config missing'; "
         "assert hasattr(PatchBase, 'scan_perms'), 'scan_perms missing'; "
         "assert hasattr(PatchBase, 'fix_ownership'), 'fix_ownership missing'; "
         "assert hasattr(PatchBase, 'backup_git'), 'backup_git missing'; "
         "assert hasattr(PatchBase, 'clean_tmp_pack'), 'clean_tmp_pack missing'; "
         "assert hasattr(PatchBase, 'allowlist_append_unit'), 'allowlist_append_unit missing'; "
         "print('OK')"],
        capture_output=True, text=True,
    )
    if import_check.returncode != 0 or 'OK' not in import_check.stdout:
        patch.errors.append(f"import check failed: {import_check.stderr.strip() or import_check.stdout.strip()}")
        patch.logger.log(f"  ✗ import check failed: {import_check.stderr.strip() or import_check.stdout.strip()}")
        # Restore
        shutil.copy2(str(BACKUP_PATH), str(PATCH_BASE_PATH))
        patch.logger.log("  ⊙ restored from backup")
        patch.finish()
        sys.exit(1)
    patch.logger.log("  ✓ import check: all 12 methods present")
    patch.validations.append("import check passed (sudo_wrapper + 11 conveniences)")

    patch.finish()


if __name__ == '__main__':
    main()
