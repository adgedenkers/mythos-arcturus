"""
mx_journal.py — Session intent + auto journal writer (SYS-0027)
Handles:
  - Optional session intent declaration at startup
  - Session summary written to TODO.md on exit
  - Per-session work log in ~/.mx/journal/
"""

import json
import re
from datetime import datetime
from pathlib import Path

TODO_PATH = Path("/opt/mythos/docs/TODO.md")
JOURNAL_DIR = Path("~/.mx/journal").expanduser()

SESSION_LOG_HEADER = "## 🗂️ Session Log"


class MxJournal:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.intent: str | None = None
        self.start_time = datetime.now()
        self.commands_run = 0
        self.failures_healed = 0
        self.failures_unhealed = 0
        self.patches_deployed: list[str] = []
        self.services_restarted: list[str] = []
        self.pre_snapshot_path: str | None = None
        self.post_snapshot_path: str | None = None
        self.delta_summary: str | None = None
        self.regressions: list[str] = []

        JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
        self.journal_file = JOURNAL_DIR / f"{session_id}.json"

    def declare_intent(self, intent: str):
        self.intent = intent.strip()
        self._save()

    def record_command(self):
        self.commands_run += 1

    def record_heal(self, success: bool):
        if success:
            self.failures_healed += 1
        else:
            self.failures_unhealed += 1

    def record_patch_deploy(self, patch_id: str):
        if patch_id not in self.patches_deployed:
            self.patches_deployed.append(patch_id)

    def record_service_restart(self, service: str):
        svc = service.replace(".service", "")
        if svc not in self.services_restarted:
            self.services_restarted.append(svc)

    def record_snapshot(self, pre_path: str = None, post_path: str = None):
        if pre_path:
            self.pre_snapshot_path = pre_path
        if post_path:
            self.post_snapshot_path = post_path

    def record_delta(self, summary: str, regressions: list[str]):
        self.delta_summary = summary
        self.regressions = regressions

    def _save(self):
        data = {
            "session_id": self.session_id,
            "intent": self.intent,
            "start_time": self.start_time.isoformat(),
            "commands_run": self.commands_run,
            "failures_healed": self.failures_healed,
            "failures_unhealed": self.failures_unhealed,
            "patches_deployed": self.patches_deployed,
            "services_restarted": self.services_restarted,
            "pre_snapshot": self.pre_snapshot_path,
            "post_snapshot": self.post_snapshot_path,
            "delta_summary": self.delta_summary,
            "regressions": self.regressions,
        }
        with open(self.journal_file, "w") as f:
            json.dump(data, f, indent=2)

    def write_todo_entry(self) -> bool:
        """
        Append a session summary to TODO.md under the Session Log section.
        Creates the section if it doesn't exist.
        Returns True if written successfully.
        """
        if not TODO_PATH.exists():
            return False

        duration = datetime.now() - self.start_time
        mins = int(duration.total_seconds() / 60)
        duration_str = f"{mins}min" if mins > 0 else "<1min"

        ts = self.start_time.strftime("%Y-%m-%d %H:%M")
        intent_str = self.intent or "general session"

        # Build the entry
        lines = [f"\n### {ts} — {intent_str}"]
        lines.append(
            f"Commands: {self.commands_run}  |  "
            f"Healed: {self.failures_healed}  |  "
            f"Duration: {duration_str}"
        )

        if self.patches_deployed:
            lines.append(f"Patches deployed: {', '.join(self.patches_deployed)}")
        if self.services_restarted:
            lines.append(f"Services restarted: {', '.join(self.services_restarted)}")
        if self.regressions:
            lines.append(f"⚠ Regressions: {', '.join(self.regressions)}")
        if self.delta_summary:
            lines.append(f"Delta: {self.delta_summary}")

        entry = "\n".join(lines) + "\n"

        # Read current TODO
        content = TODO_PATH.read_text()

        if SESSION_LOG_HEADER in content:
            # Insert after the header line
            content = content.replace(
                SESSION_LOG_HEADER,
                SESSION_LOG_HEADER + entry
            )
        else:
            # Append section at end
            content += f"\n---\n{SESSION_LOG_HEADER}\n{entry}"

        TODO_PATH.write_text(content)
        self._save()
        return True
