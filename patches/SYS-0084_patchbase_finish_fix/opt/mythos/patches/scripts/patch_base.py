#!/usr/bin/env python3
"""
/opt/mythos/patches/scripts/patch_base.py
Standard base class for all Mythos apply_patch.py scripts.

SYS-0084: PatchBase.finish() no longer writes STREAMS.json or
PATCH_HISTORY.md when self.errors is non-empty, and the post-install
pipeline runs BEFORE the ledger update so pipeline failures also block
it. Raises PatchFinishError (caught by install.sh set -e via exit 1)
on failure.
"""
import os
import sys
import json
import shutil
import subprocess
import datetime
from pathlib import Path

MYTHOS = Path("/opt/mythos")
DOCS = MYTHOS / "docs"
STREAMS_JSON = DOCS / "STREAMS.json"
PATCH_HISTORY = DOCS / "PATCH_HISTORY.md"
LOG_DIR = Path("/tmp")


class PatchFinishError(Exception):
    """Raised by PatchBase.finish() when errors prevent ledger update."""
    pass


class PatchLogger:
    """Dual-output logger: writes to terminal and captures structured data."""
    def __init__(self, patch_id: str):
        self.patch_id = patch_id
        self.human_lines = []
        self.log_path = LOG_DIR / f"{patch_id}_output.log"
        self.json_path = LOG_DIR / f"{patch_id}_result.json"
        self.last_log_path = LOG_DIR / "last_patch_output.log"
        self.last_json_path = LOG_DIR / "last_patch_result.json"
    def log(self, message: str):
        print(message)
        self.human_lines.append(message)
    def write_logs(self, result: dict):
        human_text = "\n".join(self.human_lines) + "\n"
        self.log_path.write_text(human_text)
        self.last_log_path.write_text(human_text)
        json_text = json.dumps(result, indent=2, default=str)
        self.json_path.write_text(json_text)
        self.last_json_path.write_text(json_text)


class PatchBase:
    def __init__(self, stream: str, number: int, description: str,
                 patch_type: str = "PATCH", review_link: str = None):
        self.stream = stream.upper()
        self.number = number
        self.description = description
        self.patch_type = patch_type.upper()
        self.review_link = review_link
        self.patch_id = f"{self.stream}-{self.number:04d}"
        self.patch_dir = Path(os.path.dirname(os.path.abspath(sys.argv[0])))
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.files_deployed = []
        self.services_restarted = []
        self.sql_run = []
        self.errors = []
        self.validations = []
        self.logger = PatchLogger(self.patch_id)
        self._start_time = None
        self.dry_run = os.environ.get('MYTHOS_PATCH_DRY_RUN', '0') == '1'

    def begin(self):
        self._start_time = datetime.datetime.now()
        mode_tag = " [DRY RUN]" if self.dry_run else ""
        self.logger.log(f"[{self.patch_id}]{mode_tag} {self.description}")
        self.logger.log("=" * 55)
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
            )

    def finish(self):
        """Finish the patch.

        SYS-0084 order of operations:
          1. Build result dict
          2. Run post-install pipeline (if clean so far)
          3. Guard: if self.errors, write logs and RAISE PatchFinishError
             BEFORE touching STREAMS.json or PATCH_HISTORY
          4. Only after the error gate, bump STREAMS and write PATCH_HISTORY
          5. Success logging + write_logs
        """
        elapsed = None
        if self._start_time:
            elapsed = (datetime.datetime.now() - self._start_time).total_seconds()

        result = {
            "patch_id": self.patch_id,
            "stream": self.stream,
            "number": self.number,
            "description": self.description,
            "patch_type": self.patch_type,
            "timestamp": self.timestamp,
            "date": self.date,
            "elapsed_seconds": round(elapsed, 2) if elapsed else None,
            "dry_run": self.dry_run,
            "success": len(self.errors) == 0,
            "files_deployed": self.files_deployed,
            "services_restarted": self.services_restarted,
            "sql_run": self.sql_run,
            "validations": self.validations,
            "errors": self.errors,
        }

        # ── Post-install pipeline ──────────────────────────────────
        # Runs BEFORE the ledger update. Failures here append to
        # self.errors and block the ledger update via the guard below.
        if not self.dry_run and len(self.errors) == 0:
            try:
                from post_install import run_pipeline
                pipeline_results = run_pipeline(
                    patch_id=self.patch_id,
                    stream=self.stream,
                    number=self.number,
                    description=self.description,
                    patch_type=self.patch_type,
                    files_deployed=self.files_deployed,
                    services_restarted=self.services_restarted,
                    sql_run=self.sql_run,
                    errors=self.errors,
                )
                result['pipeline'] = pipeline_results
            except Exception as e:
                self.errors.append(f"post-install pipeline: {e}")
                result['pipeline_error'] = str(e)

        # ── Error gate ─────────────────────────────────────────────
        # Any accumulated error blocks the ledger update.
        if self.errors and not self.dry_run:
            self.logger.log("")
            self.logger.log(f"[{self.patch_id}] FAILED ✗ — {len(self.errors)} error(s)")
            for e in self.errors:
                self.logger.log(f"  ✗ {e}")
            self.logger.log("  STREAMS.json NOT bumped. PATCH_HISTORY NOT written.")
            result['success'] = False
            self.logger.write_logs(result)
            raise PatchFinishError(
                f"{self.patch_id} failed with {len(self.errors)} error(s). "
                f"STREAMS.json and PATCH_HISTORY not updated. Fix and re-run."
            )

        # ── Ledger update ──────────────────────────────────────────
        # Only reached when clean (or dry-run).
        if not self.dry_run:
            self._bump_streams_json()
            self._write_patch_history()
            # A bump or history write itself could have failed silently
            # via self.errors — re-check.
            if self.errors:
                self.logger.log("")
                self.logger.log(
                    f"[{self.patch_id}] FAILED ✗ during ledger update — "
                    f"{len(self.errors)} error(s)"
                )
                for e in self.errors:
                    self.logger.log(f"  ✗ {e}")
                result['success'] = False
                self.logger.write_logs(result)
                raise PatchFinishError(
                    f"{self.patch_id} failed during ledger update. "
                    f"STREAMS.json/PATCH_HISTORY state may be inconsistent. "
                    f"Inspect manually."
                )
        else:
            self.logger.log("  · STREAMS.json — skipped (dry run)")
            self.logger.log("  · PATCH_HISTORY — skipped (dry run)")

        # ── Success logging ────────────────────────────────────────
        self.logger.log("")
        if self.dry_run:
            if self.errors:
                self.logger.log(f"[{self.patch_id}] DRY RUN FAILED ✗")
            else:
                self.logger.log(f"[{self.patch_id}] DRY RUN PASSED ✓")
        else:
            self.logger.log(f"[{self.patch_id}] Complete ✓")
        if self.files_deployed:
            for f in self.files_deployed:
                self.logger.log(f"  ✓ {f}")
        if self.validations:
            for v in self.validations:
                self.logger.log(f"  ✓ {v}")
        if self.services_restarted:
            for s in self.services_restarted:
                self.logger.log(f"  ✓ restarted {s}")

        self.logger.write_logs(result)

    # ── File Operations ───────────────────────────────────────────────────────
    def deploy_file(self, source_rel: str, target_abs: str):
        source = self.patch_dir / source_rel
        target = Path(target_abs)
        if self.dry_run:
            issues = []
            if not source.exists():
                issues.append(f"source not found: {source}")
            if not target.parent.exists():
                try:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.parent.rmdir()
                except Exception as e:
                    issues.append(f"cannot create target dir: {target.parent}: {e}")
            if target.exists() and not os.access(str(target), os.W_OK):
                issues.append(f"target not writable: {target_abs}")
            if issues:
                for issue in issues:
                    self.errors.append(f"deploy_file {source_rel}: {issue}")
                    self.logger.log(f"  ✗ {Path(target_abs).name}: {issue}")
            else:
                self.validations.append(f"deploy_file {Path(target_abs).name} — OK")
                self.logger.log(f"  ✓ [validate] {Path(target_abs).name}")
            return
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(source), str(target))
            self.files_deployed.append(target_abs)
            self.logger.log(f"  ✓ {Path(target_abs).name}")
        except Exception as e:
            self.errors.append(f"deploy_file {source_rel} → {target_abs}: {e}")
            self.logger.log(f"  ✗ {Path(target_abs).name}: {e}")

    def run_sql(self, sql_rel: str):
        sql_path = self.patch_dir / sql_rel
        if not sql_path.exists():
            self.errors.append(f"SQL file not found: {sql_rel}")
            self.logger.log(f"  ✗ SQL: {sql_rel} — file not found")
            return
        if self.dry_run:
            try:
                sql_content = sql_path.read_text()
                test_sql = sql_content
                for token in ('BEGIN;', 'COMMIT;', 'BEGIN', 'COMMIT'):
                    test_sql = test_sql.replace(token, '')
                dry_sql = f"BEGIN;\n{test_sql}\nROLLBACK;\n"
                result = subprocess.run(
                    ['sudo', '-u', 'postgres', 'psql', '-d', 'mythos', '-v', 'ON_ERROR_STOP=1'],
                    input=dry_sql, capture_output=True, text=True
                )
                if result.returncode != 0:
                    self.errors.append(f"SQL dry-run {sql_rel}: {result.stderr.strip()}")
                    self.logger.log(f"  ✗ [validate] SQL: {sql_rel}: {result.stderr.strip()}")
                else:
                    self.validations.append(f"SQL {sql_rel} — OK (rolled back)")
                    self.logger.log(f"  ✓ [validate] SQL: {sql_rel} — syntax OK")
            except Exception as e:
                self.errors.append(f"SQL dry-run {sql_rel}: {e}")
                self.logger.log(f"  ✗ [validate] SQL: {sql_rel}: {e}")
            return
        try:
            result = subprocess.run(
                ['sudo', '-u', 'postgres', 'psql', '-d', 'mythos', '-f', str(sql_path)],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                self.errors.append(f"SQL {sql_rel}: {result.stderr.strip()}")
                self.logger.log(f"  ✗ SQL: {sql_rel}: {result.stderr.strip()}")
            else:
                self.sql_run.append(sql_rel)
                self.logger.log(f"  ✓ SQL: {sql_rel}")
        except Exception as e:
            self.errors.append(f"SQL {sql_rel}: {e}")
            self.logger.log(f"  ✗ SQL: {sql_rel}: {e}")

    def restart_service(self, service_name: str):
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

    def verify_handoff(self, subsystem: str) -> bool:
        import subprocess as _sp
        tool = '/opt/mythos/bin/mythos-handoff'
        manifest = f'/opt/mythos/docs/{subsystem}/MANIFEST.yaml'
        if self.dry_run:
            if not os.path.isfile(tool):
                self.errors.append(f"verify_handoff: {tool} not found")
                return False
            if not os.path.isfile(manifest):
                self.errors.append(f"verify_handoff: {manifest} not found")
                return False
            self.validations.append(f"verify_handoff({subsystem}) — tool+manifest exist")
            self.logger.log(f"  ✓ [validate] verify_handoff({subsystem}) — tool+manifest exist")
            return True
        if not os.path.isfile(tool):
            self.errors.append(f"verify_handoff({subsystem}): tool missing: {tool}")
            self.logger.log(f"  ✗ verify_handoff: tool missing")
            return False
        if not os.path.isfile(manifest):
            self.errors.append(f"verify_handoff({subsystem}): manifest missing: {manifest}")
            self.logger.log(f"  ✗ verify_handoff: manifest missing")
            return False
        try:
            result = _sp.run(
                ['/opt/mythos/.venv/bin/python3', tool, subsystem, '--strict', '--stdout'],
                capture_output=True, text=True, timeout=120,
            )
        except Exception as e:
            self.errors.append(f"verify_handoff({subsystem}): subprocess failed: {e}")
            self.logger.log(f"  ✗ verify_handoff({subsystem}): {e}")
            return False
        if result.returncode == 0:
            self.validations.append(f"verify_handoff({subsystem}) — all validations passed")
            self.logger.log(f"  ✓ verify_handoff({subsystem}) — clean")
            return True
        failed_names = []
        for line in (result.stderr or '').splitlines():
            line = line.strip()
            if line.startswith('✗ '):
                failed_names.append(line[2:].strip())
        detail = ', '.join(failed_names) if failed_names else 'see tool stderr'
        self.errors.append(f"verify_handoff({subsystem}) FAILED: {detail}")
        self.logger.log(f"  ✗ verify_handoff({subsystem}): {detail}")
        return False

    def sudo_wrapper(self, wrapper_name: str, *args, timeout: int = 120, check: bool = True):
        wrapper_path = f"/usr/local/libexec/mythos/{wrapper_name}"
        if not os.path.isfile(wrapper_path):
            raise RuntimeError(
                f"Mythos privilege wrapper not found: {wrapper_path}. "
                f"Install SYS-0062 first."
            )
        cmd = ["sudo", "-n", wrapper_path] + [str(a) for a in args]
        return subprocess.run(
            cmd, check=check, capture_output=True, text=True, timeout=timeout,
        )

    def start_service(self, service_name: str):
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
        try:
            result = self.sudo_wrapper(
                'mythos-servicectl', 'is-active', service_name,
                timeout=10, check=False,
            )
            return result.stdout.strip() == 'active'
        except Exception:
            return False

    def install_systemd_unit(self, basename: str):
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
        try:
            result = self.sudo_wrapper('mythos-scan-perms', timeout=60, check=False)
            out = result.stdout.strip()
            if '=' in out:
                out = out.split('=', 1)[1].strip()
            return int(out)
        except Exception as e:
            self.logger.log(f"  ⚠ scan_perms failed: {e}")
            return -1

    def fix_ownership(self):
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

    def _bump_streams_json(self):
        try:
            with open(STREAMS_JSON, 'r') as f:
                data = json.load(f)
            stream_key = self.stream
            streams = data.get('streams', {})
            for key in streams:
                if streams[key].get('prefix', '').upper() == stream_key or key.upper() == stream_key:
                    stream_entry = streams[key]
                    stream_entry['next_patch'] = self.number + 1
                    self.logger.log(f"  ✓ STREAMS.json: {self.stream} next_patch → {self.number + 1}")
                    break
            else:
                self.errors.append(f"Stream {self.stream} not found in STREAMS.json")
                self.logger.log(f"  ⚠ Stream {self.stream} not found in STREAMS.json")
                return
            with open(STREAMS_JSON, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.errors.append(f"STREAMS.json bump: {e}")
            self.logger.log(f"  ⚠ STREAMS.json: {e}")

    def _write_patch_history(self):
        try:
            entry = (
                f"\n### {self.patch_id}: {self.description}\n"
                f"- **Date:** {self.date}\n"
                f"- **Type:** {self.patch_type}\n"
                f"- **Stream:** {self.stream}\n"
            )
            if self.files_deployed:
                entry += f"- **Files:** {', '.join(Path(f).name for f in self.files_deployed)}\n"
            if self.sql_run:
                entry += f"- **SQL:** {', '.join(Path(f).name for f in self.sql_run)}\n"
            if self.services_restarted:
                entry += f"- **Services restarted:** {', '.join(self.services_restarted)}\n"
            if self.review_link:
                entry += f"- **Review:** {self.review_link}\n"
            with open(PATCH_HISTORY, 'a') as f:
                f.write(entry)
            self.logger.log(f"  ✓ PATCH_HISTORY.md updated")
        except Exception as e:
            self.errors.append(f"PATCH_HISTORY: {e}")
            self.logger.log(f"  ⚠ PATCH_HISTORY: {e}")
