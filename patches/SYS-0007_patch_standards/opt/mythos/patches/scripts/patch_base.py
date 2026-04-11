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
        number=8,           # integer patch number
        description='my feature',
        patch_type='MINOR', # MAJOR, MINOR, PATCH
    )

    patch.begin()           # prints header, sets up paths

    # --- your work here ---
    patch.deploy_file('opt/mythos/some/file.py', '/opt/mythos/some/file.py')
    patch.run_sql('opt/mythos/migrations/migration.sql')
    patch.restart_service('mythos-bot.service')
    # ----------------------

    patch.finish()          # bumps STREAMS.json, writes PATCH_HISTORY, prints summary
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

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def begin(self):
        print(f"[{self.patch_id}] {self.description}")
        print("=" * 55)

    def finish(self):
        """Bump STREAMS.json, write PATCH_HISTORY entry, print summary."""
        self._bump_streams_json()
        self._write_patch_history()
        print()
        print(f"[{self.patch_id}] Complete ✓")
        if self.files_deployed:
            for f in self.files_deployed:
                print(f"  ✓ {f}")
        if self.services_restarted:
            for s in self.services_restarted:
                print(f"  ✓ restarted {s}")
        if self.errors:
            print()
            for e in self.errors:
                print(f"  ⚠ {e}")

    # ── File Operations ───────────────────────────────────────────────────────

    def deploy_file(self, src_relative: str, dest: str):
        """
        Copy a file from the patch directory to its destination.
        src_relative: path relative to patch dir (e.g. 'opt/mythos/core/foo.py')
        dest: absolute destination path (e.g. '/opt/mythos/core/foo.py')
        No sudo needed — /opt/mythos is adge:adge owned.
        """
        src = self.patch_dir / src_relative
        dest_path = Path(dest)

        if not src.exists():
            self._abort(f"Source not found: {src}")

        # Backup if exists
        if dest_path.exists():
            backup = Path(f"{dest}.bak.{self.timestamp}")
            shutil.copy2(dest_path, backup)

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest_path)
        print(f"  ✓ {dest_path.name}")
        self.files_deployed.append(str(dest_path))

    def deploy_executable(self, src_relative: str, dest: str):
        """Deploy a file and make it executable."""
        self.deploy_file(src_relative, dest)
        Path(dest).chmod(0o755)

    def patch_file(self, filepath: str, old: str, new: str):
        """
        Replace exact string in a file using str.replace().
        Aborts if old string not found.
        """
        p = Path(filepath)
        if not p.exists():
            self._abort(f"File not found for patching: {filepath}")

        # Backup
        shutil.copy2(p, f"{filepath}.bak.{self.timestamp}")

        content = p.read_text()
        if old not in content:
            self._abort(f"Expected string not found in {filepath}:\n  {repr(old[:80])}")

        p.write_text(content.replace(old, new, 1))
        print(f"  ✓ patched {p.name}")

    def write_file(self, dest: str, content: str, executable: bool = False):
        """Write content directly to a file."""
        p = Path(dest)
        if p.exists():
            shutil.copy2(p, f"{dest}.bak.{self.timestamp}")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        if executable:
            p.chmod(0o755)
        print(f"  ✓ wrote {p.name}")
        self.files_deployed.append(dest)

    # ── SQL ───────────────────────────────────────────────────────────────────

    def run_sql(self, sql_relative: str):
        """Run a SQL migration file via psql."""
        sql_file = self.patch_dir / sql_relative
        if not sql_file.exists():
            self._abort(f"SQL file not found: {sql_file}")

        result = subprocess.run(
            ["sudo", "-u", "postgres", "psql", "-d", "mythos", "-f", str(sql_file)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            self._abort(f"SQL failed:\n{result.stderr}")
        print(f"  ✓ SQL: {sql_file.name}")
        self.sql_run.append(str(sql_file))

    def run_sql_string(self, sql: str):
        """Run a SQL string directly."""
        result = subprocess.run(
            ["sudo", "-u", "postgres", "psql", "-d", "mythos", "-c", sql],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            self._abort(f"SQL failed:\n{result.stderr}")
        print(f"  ✓ SQL executed")

    # ── Services ──────────────────────────────────────────────────────────────

    def restart_service(self, service: str):
        """Restart a systemd service (uses sudo for systemctl only)."""
        result = subprocess.run(
            ["sudo", "systemctl", "restart", service],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            self.errors.append(f"Service restart failed: {service}\n{result.stderr}")
            print(f"  ⚠ restart failed: {service}")
        else:
            print(f"  ✓ restarted {service}")
            self.services_restarted.append(service)

    def install_symlink(self, target: str, link: str):
        """Create a symlink in /usr/local/bin (requires sudo)."""
        subprocess.run(["sudo", "rm", "-f", link], capture_output=True)
        result = subprocess.run(
            ["sudo", "ln", "-s", target, link],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            self.errors.append(f"Symlink failed: {link} → {target}")
        else:
            print(f"  ✓ symlink {link} → {target}")

    # ── Utilities ─────────────────────────────────────────────────────────────

    def syntax_check(self, filepath: str):
        """Python syntax check before deploying."""
        import py_compile
        try:
            py_compile.compile(filepath, doraise=True)
            print(f"  ✓ syntax OK: {Path(filepath).name}")
        except py_compile.PyCompileError as e:
            self._abort(f"Syntax error in {filepath}:\n{e}")

    def run(self, cmd: str, check: bool = True) -> str:
        """Run an arbitrary shell command."""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            self._abort(f"Command failed: {cmd}\n{result.stderr}")
        return result.stdout.strip()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _abort(self, msg: str):
        print(f"\n  ❌ {msg}")
        sys.exit(1)

    def _bump_streams_json(self):
        """Increment next_patch and set last_patch for this stream in STREAMS.json."""
        if not STREAMS_JSON.exists():
            self.errors.append("STREAMS.json not found — counter not bumped")
            return
        try:
            with open(STREAMS_JSON) as f:
                data = json.load(f)

            stream = data["streams"].get(self.stream)
            if not stream:
                self.errors.append(f"Stream {self.stream} not found in STREAMS.json")
                return

            stream["last_patch"] = self.number
            stream["next_patch"] = self.number + 1
            stream["active_work"] = None
            data["meta"]["updated"] = datetime.datetime.now().isoformat()
            data["meta"]["updated_by"] = self.patch_id

            with open(STREAMS_JSON, "w") as f:
                json.dump(data, f, indent=2)

            print(f"  ✓ STREAMS.json: {self.stream} next_patch → {self.number + 1}")
        except Exception as e:
            self.errors.append(f"STREAMS.json update failed: {e}")

    def _write_patch_history(self):
        """Append entry to PATCH_HISTORY.md."""
        if not PATCH_HISTORY.exists():
            self.errors.append("PATCH_HISTORY.md not found")
            return

        files_list = "\n".join(f"- `{f}`" for f in self.files_deployed) or "- (none)"
        sql_list = "\n".join(f"- `{s}`" for s in self.sql_run) if self.sql_run else ""
        services_list = "\n".join(f"- `{s}`" for s in self.services_restarted) if self.services_restarted else ""

        entry = f"""
### {self.patch_id}: {self.description}
**Date:** {self.date}
**Stream:** {self.stream}
**Type:** {self.patch_type}

**Files modified/created:**
{files_list}
"""
        if sql_list:
            entry += f"\n**SQL migrations:**\n{sql_list}\n"
        if services_list:
            entry += f"\n**Services restarted:**\n{services_list}\n"

        try:
            content = PATCH_HISTORY.read_text()
            marker = "## Verification Template"
            if marker in content:
                PATCH_HISTORY.write_text(content.replace(marker, entry + marker, 1))
            else:
                with open(PATCH_HISTORY, "a") as f:
                    f.write(entry)
            print(f"  ✓ PATCH_HISTORY.md updated")
        except Exception as e:
            self.errors.append(f"PATCH_HISTORY update failed: {e}")
