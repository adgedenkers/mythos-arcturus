#!/usr/bin/env python3
"""
/opt/mythos/patches/scripts/patch_base.py
Standard base class for all Mythos apply_patch.py scripts.

Usage in any apply_patch.py:
    import sys
    sys.path.insert(0, '/opt/mythos/patches/scripts')
    from patch_base import PatchBase

    patch = PatchBase(
        stream='SYS',       # NEU, LOG, MNE, SEN, SYS
        number=8,            # integer patch number
        description='my feature',
        patch_type='MINOR', # MAJOR, MINOR, PATCH
    )
    patch.begin()           # prints header, sets up paths, opens log

    # --- your work here ---
    patch.deploy_file('opt/mythos/some/file.py', '/opt/mythos/some/file.py')
    patch.run_sql('opt/mythos/migrations/migration.sql')
    patch.restart_service('mythos-bot.service')
    # ----------------------

    patch.finish()          # bumps STREAMS.json, writes PATCH_HISTORY, writes logs, prints summary
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


class PatchLogger:
    """Dual-output logger: writes to terminal and captures structured data."""

    def __init__(self, patch_id: str):
        self.patch_id = patch_id
        self.human_lines = []
        self.log_path = LOG_DIR / f"{patch_id}_output.log"
        self.json_path = LOG_DIR / f"{patch_id}_result.json"
        # Also write to a stable "last patch" location for easy clipboard
        self.last_log_path = LOG_DIR / "last_patch_output.log"
        self.last_json_path = LOG_DIR / "last_patch_result.json"

    def log(self, message: str):
        """Print to terminal and capture for log file."""
        print(message)
        self.human_lines.append(message)

    def write_logs(self, result: dict):
        """Write both human-readable and JSON logs."""
        # Human-readable log
        human_text = "\n".join(self.human_lines) + "\n"
        self.log_path.write_text(human_text)
        self.last_log_path.write_text(human_text)

        # JSON structured log
        json_text = json.dumps(result, indent=2, default=str)
        self.json_path.write_text(json_text)
        self.last_json_path.write_text(json_text)


class PatchBase:
    def __init__(self, stream: str, number: int, description: str, patch_type: str = "PATCH"):
        self.stream = stream.upper()
        self.number = number
        self.description = description
        self.patch_type = patch_type.upper()
        self.patch_id = f"{self.stream}-{self.number:04d}"
        self.patch_dir = Path(os.path.dirname(os.path.abspath(sys.argv[0])))
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.files_deployed = []
        self.services_restarted = []
        self.sql_run = []
        self.errors = []

        # Structured logging
        self.logger = PatchLogger(self.patch_id)
        self._start_time = None

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def begin(self):
        self._start_time = datetime.datetime.now()
        self.logger.log(f"[{self.patch_id}] {self.description}")
        self.logger.log("=" * 55)

    def finish(self):
        """Bump STREAMS.json, write PATCH_HISTORY entry, write logs, print summary."""
        self._bump_streams_json()
        self._write_patch_history()

        elapsed = None
        if self._start_time:
            elapsed = (datetime.datetime.now() - self._start_time).total_seconds()

        self.logger.log("")
        self.logger.log(f"[{self.patch_id}] Complete ✓")

        if self.files_deployed:
            for f in self.files_deployed:
                self.logger.log(f"  ✓ {f}")
        if self.services_restarted:
            for s in self.services_restarted:
                self.logger.log(f"  ✓ restarted {s}")
        if self.errors:
            self.logger.log("")
            for e in self.errors:
                self.logger.log(f"  ⚠ {e}")

        # Build structured result
        result = {
            "patch_id": self.patch_id,
            "stream": self.stream,
            "number": self.number,
            "description": self.description,
            "patch_type": self.patch_type,
            "timestamp": self.timestamp,
            "date": self.date,
            "elapsed_seconds": round(elapsed, 2) if elapsed else None,
            "success": len(self.errors) == 0,
            "files_deployed": self.files_deployed,
            "services_restarted": self.services_restarted,
            "sql_run": self.sql_run,
            "errors": self.errors,
        }

        # Write log files
        self.logger.write_logs(result)

    # ── File Operations ───────────────────────────────────────────────────────

    def deploy_file(self, source_rel: str, target_abs: str):
        """Copy a file from the patch directory to the target path."""
        source = self.patch_dir / source_rel
        target = Path(target_abs)

        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(source), str(target))
            self.files_deployed.append(target_abs)
            self.logger.log(f"  ✓ {Path(target_abs).name}")
        except Exception as e:
            self.errors.append(f"deploy_file {source_rel} → {target_abs}: {e}")
            self.logger.log(f"  ✗ {Path(target_abs).name}: {e}")

    # ── SQL ────────────────────────────────────────────────────────────────────

    def run_sql(self, sql_rel: str):
        """Run a SQL file against the mythos database."""
        sql_path = self.patch_dir / sql_rel

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

    # ── Services ──────────────────────────────────────────────────────────────

    def restart_service(self, service_name: str):
        """Restart a systemd service."""
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'restart', service_name],
                capture_output=True, text=True
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

    # ── STREAMS.json ──────────────────────────────────────────────────────────

    def _bump_streams_json(self):
        """Increment next_patch for this stream in STREAMS.json."""
        try:
            with open(STREAMS_JSON, 'r') as f:
                data = json.load(f)

            stream_key = self.stream
            # Find the stream entry
            streams = data.get('streams', {})
            for key in streams:
                if streams[key].get('prefix', '').upper() == stream_key or key.upper() == stream_key:
                    stream_entry = streams[key]
                    old_next = stream_entry.get('next_patch', self.number)
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

    # ── PATCH_HISTORY ─────────────────────────────────────────────────────────

    def _write_patch_history(self):
        """Append entry to PATCH_HISTORY.md."""
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

            with open(PATCH_HISTORY, 'a') as f:
                f.write(entry)

            self.logger.log(f"  ✓ PATCH_HISTORY.md updated")
        except Exception as e:
            self.errors.append(f"PATCH_HISTORY: {e}")
            self.logger.log(f"  ⚠ PATCH_HISTORY: {e}")
