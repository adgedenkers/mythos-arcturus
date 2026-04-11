"""
mx_logger.py — Session logger for mx
Writes to ~/.mx/sessions/YYYY-MM-DD_HHMMSS.log
Appends learned patterns to ~/.mx/patterns/errors.jsonl
"""

import json
from datetime import datetime
from pathlib import Path


class MxLogger:
    def __init__(self, config: dict):
        self.log_dir = Path(config["session"]["log_dir"]).expanduser()
        self.pattern_dir = Path(config["session"]["pattern_dir"]).expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.pattern_dir.mkdir(parents=True, exist_ok=True)

        session_ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.session_file = self.log_dir / f"{session_ts}.log"
        self.error_pattern_file = self.pattern_dir / "errors.jsonl"

        self._write(f"# mx session started {datetime.now().isoformat()}\n")

    def _write(self, text: str):
        with open(self.session_file, "a") as f:
            f.write(text)

    def _ts(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def log_command(self, raw_input: str, resolved_command: str = None, intent_matched: str = None):
        ts = self._ts()
        if intent_matched:
            self._write(f"\n[{ts}] $ {raw_input}\n")
            self._write(f"[{ts}] INTENT({intent_matched}): {resolved_command}\n")
        else:
            self._write(f"\n[{ts}] $ {raw_input}\n")

    def log_result(self, exit_code: int, stdout: str = "", stderr: str = ""):
        ts = self._ts()
        self._write(f"[{ts}] EXIT:{exit_code}\n")
        if stderr and stderr.strip():
            self._write(f"[{ts}] STDERR: {stderr.strip()[:500]}\n")
        if stdout and stdout.strip() and exit_code != 0:
            self._write(f"[{ts}] STDOUT: {stdout.strip()[:200]}\n")

    def log_mx_event(self, event_type: str, message: str):
        ts = self._ts()
        self._write(f"[{ts}] MX {event_type}: {message}\n")

    def log_fix_attempt(self, fix_command: str, attempt_num: int):
        ts = self._ts()
        self._write(f"[{ts}] MX FIX(attempt {attempt_num}): {fix_command}\n")

    def log_fix_outcome(self, success: bool, fix_command: str, original_command: str,
                        original_error: str, reasoning: str):
        ts = self._ts()
        if success:
            self._write(f"[{ts}] MX: fix succeeded → stored to patterns\n")
            self._store_error_pattern(original_command, original_error, fix_command, reasoning)
        else:
            self._write(f"[{ts}] MX: fix failed\n")

    def log_session_end(self):
        self._write(f"\n# mx session ended {datetime.now().isoformat()}\n")

    def _store_error_pattern(self, failed_command: str, error: str,
                             fix_command: str, reasoning: str):
        pattern = {
            "ts": datetime.now().isoformat(),
            "failed_command": failed_command,
            "error_snippet": error[:300],
            "fix_command": fix_command,
            "reasoning": reasoning,
            "use_count": 1,
        }
        with open(self.error_pattern_file, "a") as f:
            f.write(json.dumps(pattern) + "\n")

    def load_error_patterns(self) -> list:
        if not self.error_pattern_file.exists():
            return []
        patterns = []
        with open(self.error_pattern_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        patterns.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return patterns

    def find_known_fix(self, command: str, error: str):
        """Check known patterns before calling Ollama. Returns pattern or None."""
        patterns = self.load_error_patterns()
        for p in patterns:
            if p["failed_command"].strip() == command.strip():
                if p["error_snippet"][:80] in error or error[:80] in p["error_snippet"]:
                    return p
        return None
