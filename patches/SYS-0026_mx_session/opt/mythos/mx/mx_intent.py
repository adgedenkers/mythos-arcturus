"""
mx_intent.py — Intent resolver for mx
Maps terse phrases to real shell commands.
"""

import re
import yaml
from pathlib import Path


class IntentResolver:
    def __init__(self, config: dict):
        self.config = config
        self.intents = {}
        self._load_intents()

    def _load_intents(self):
        primary = Path("/opt/mythos/mx/mx_intents.yaml")
        if primary.exists():
            with open(primary) as f:
                data = yaml.safe_load(f)
                self.intents.update(data.get("intents", {}))

        intent_dir = Path(self.config["session"]["intent_dir"]).expanduser()
        if intent_dir.exists():
            for f in intent_dir.glob("*.yaml"):
                with open(f) as fh:
                    data = yaml.safe_load(fh)
                    if data:
                        self.intents.update(data.get("intents", {}))

    def resolve(self, user_input: str):
        """
        Try to resolve user_input to a real command.
        Returns (resolved_command, intent_key, flags_used) or (None, None, {})
        """
        user_input = user_input.strip()
        sorted_intents = sorted(self.intents.keys(), key=len, reverse=True)

        for phrase in sorted_intents:
            intent_data = self.intents[phrase]

            if "{" in phrase:
                matched, resolved, flags = self._match_template(phrase, intent_data, user_input)
                if matched:
                    return resolved, phrase, flags
            else:
                if user_input.lower() == phrase.lower():
                    command = intent_data if isinstance(intent_data, str) else intent_data.get("command", "")
                    return command, phrase, {}
                if user_input.lower().startswith(phrase.lower() + " "):
                    remainder = user_input[len(phrase):].strip()
                    command = intent_data if isinstance(intent_data, str) else intent_data.get("command", "")
                    return f"{command} {remainder}", phrase, {}

        return None, None, {}

    def _match_template(self, phrase: str, intent_data, user_input: str):
        pattern = re.escape(phrase)
        arg_names = re.findall(r'\\\{(\w+)\\\}', pattern)
        for name in arg_names:
            pattern = pattern.replace(f'\\{{{name}\\}}', f'(?P<{name}>\\S+)')
        pattern = f"^{pattern}(\\s+.*)?$"

        m = re.match(pattern, user_input, re.IGNORECASE)
        if not m:
            return False, None, {}

        args = {k: v for k, v in m.groupdict().items() if v and k in arg_names}
        command = intent_data if isinstance(intent_data, str) else intent_data.get("command", "")

        for name, value in args.items():
            command = command.replace(f"{{{name}}}", value)

        remainder = (m.group(len(arg_names) + 1) or "").strip()
        flags_map = {}
        if isinstance(intent_data, dict) and "flags" in intent_data and remainder:
            flags_map = intent_data["flags"]
            tokens = remainder.split()
            translated = [flags_map.get(t, t) for t in tokens]
            command = f"{command} {' '.join(translated)}"

        return True, command.strip(), flags_map

    def add_intent(self, phrase: str, command: str, source: str = "ollama"):
        """Persist a learned intent to ~/.mx/intents/learned.yaml"""
        intent_dir = Path(self.config["session"]["intent_dir"]).expanduser()
        intent_dir.mkdir(parents=True, exist_ok=True)
        learned_file = intent_dir / "learned.yaml"

        existing = {}
        if learned_file.exists():
            with open(learned_file) as f:
                data = yaml.safe_load(f) or {}
                existing = data.get("intents", {})

        existing[phrase] = {"command": command, "source": source}

        with open(learned_file, "w") as f:
            yaml.dump({"intents": existing}, f, default_flow_style=False)

        self.intents[phrase] = {"command": command, "source": source}

    def is_valid_bash(self, user_input: str) -> bool:
        """Heuristic: does this look like real shell syntax vs a terse phrase?"""
        first_token = user_input.strip().split()[0] if user_input.strip() else ""

        bash_prefixes = [
            "sudo", "ls", "cd", "cat", "echo", "grep", "find", "cp", "mv",
            "rm", "mkdir", "chmod", "chown", "systemctl", "journalctl",
            "python3", "python", "pip", "git", "curl", "wget", "ssh", "scp",
            "nano", "vim", "vi", "less", "more", "tail", "head", "awk", "sed",
            "ps", "top", "htop", "kill", "pkill", "df", "du", "free",
            "redis-cli", "psql", "cypher-shell", "docker",
            "patch-install", "mythos-diag",
            "/opt/", "/usr/", "/home/", "~/", "./", "../",
        ]

        for prefix in bash_prefixes:
            if first_token == prefix or first_token.startswith(prefix) or user_input.startswith(prefix):
                return True

        for op in ["|", "&&", "||", ";", "$(", "`"]:
            if op in user_input:
                return True

        return False
