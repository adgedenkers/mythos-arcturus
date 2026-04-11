#!/opt/mythos/.venv/bin/python3
"""
mx — Mythos Shell Session (SYS-0026)
Self-healing, intent-aware, context-buffering terminal session.

Usage:
  mx                    Start a session
  mx --model <model>    Use a specific Ollama model
  mx --no-heal          Disable self-healing (intent resolution still active)
  mx --version          Show version
"""

import json
import os
import re
import readline
import subprocess
import sys
import time
from collections import deque
from datetime import datetime
from pathlib import Path

import requests
import yaml

VERSION = "1.1.0"
PATCH = "SYS-0032"
CONFIG_PATH = Path("/opt/mythos/mx/mx_config.yaml")
OLLAMA_BASE = "http://localhost:11434"

CYAN  = "\033[96m"
GREEN = "\033[92m"
YELLOW= "\033[93m"
RED   = "\033[91m"
BOLD  = "\033[1m"
DIM   = "\033[2m"
RESET = "\033[0m"


# ── Config ────────────────────────────────────────────────────────────────────

def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)
    return {
        "ollama": {"host": OLLAMA_BASE, "fallback_model": "gemma3:27b", "timeout": 60},
        "session": {
            "buffer_size": 20, "max_heal_attempts": 3, "countdown_seconds": 3,
            "log_dir": "~/.mx/sessions", "pattern_dir": "~/.mx/patterns",
            "intent_dir": "~/.mx/intents",
        },
        "dangerous_commands": ["rm -rf", "drop table", "drop database", "truncate",
                                "DELETE FROM", "systemctl stop", "shutdown", "reboot"],
        "suppress_heal": ["grep", "diff", "test", "ping"],
    }


def get_active_model(config: dict) -> str:
    override_file = Path("/opt/mythos/.model_overrides.json")
    if override_file.exists():
        try:
            data = json.loads(override_file.read_text())
            if data.get("model"):
                return data["model"]
        except Exception:
            pass
    return config["ollama"].get("model") or config["ollama"]["fallback_model"]


# ── Ollama ────────────────────────────────────────────────────────────────────

HEAL_SYSTEM = """You are a shell assistant for the Mythos system on Arcturus (Ubuntu 24.04).
Fix failed shell commands. System: PostgreSQL, Neo4j, Redis, FastAPI, Ollama, systemd services prefixed 'mythos-'.
Key paths: /opt/mythos/ (project root), /opt/mythos/.venv/bin/python3 (venv), /opt/mythos/bin/ (CLI tools).
Key services: mythos-api.service, mythos-bot.service, mythos-patch-monitor.service.

Respond ONLY with valid JSON, no preamble:
{
  "action": "FIX" | "FIX_SEQUENCE" | "ASK" | "EXPLAIN",
  "commands": ["cmd1", "cmd2"],
  "question": "...",
  "explanation": "...",
  "reasoning": "one line"
}

FIX = single corrected command. FIX_SEQUENCE = multiple ordered commands.
ASK = need info from user. EXPLAIN = cannot fix, say why.
Never suggest destructive commands without explicit user confirmation."""

INTENT_SYSTEM = """You are a shell assistant for the Mythos system on Arcturus (Ubuntu 24.04).
Translate a natural language phrase or short intent to the correct shell command.
Key paths: /opt/mythos/, /opt/mythos/.venv/bin/python3, /opt/mythos/bin/
Key services: mythos-api.service, mythos-bot.service, mythos-patch-monitor.service
CLI tools in /opt/mythos/bin/: lunar-report, natal-chart, transits, sky, mythos-diag, patch-install

Respond ONLY with valid JSON:
{
  "action": "COMMAND" | "ASK" | "UNKNOWN",
  "command": "exact shell command",
  "question": "...",
  "phrase": "canonical short phrase to remember this as",
  "reasoning": "one line"
}"""


def call_ollama(model: str, system: str, prompt: str, timeout: int = 60) -> str | None:
    try:
        r = requests.post(
            f"{OLLAMA_BASE}/api/chat",
            json={
                "model": model, "stream": False,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "options": {"temperature": 0.1},
            },
            timeout=timeout,
        )
        if r.status_code == 200:
            return r.json()["message"]["content"].strip()
    except Exception:
        pass
    return None


def parse_json_response(text: str) -> dict | None:
    try:
        clean = re.sub(r"```json?|```", "", text).strip()
        return json.loads(clean)
    except Exception:
        return None


# ── Execution ─────────────────────────────────────────────────────────────────

def run_command(command: str) -> tuple:
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, executable="/bin/bash"
    )
    return result.returncode, result.stdout, result.stderr


def is_dangerous(command: str, dangerous_list: list) -> bool:
    return any(d.lower() in command.lower() for d in dangerous_list)


def should_suppress(command: str, suppress_list: list) -> bool:
    first = command.strip().split()[0] if command.strip() else ""
    return first in suppress_list


def countdown_run(command: str, seconds: int, dangerous: bool = False) -> bool:
    if dangerous:
        print(f"\n{RED}⚠  DANGEROUS: {BOLD}{command}{RESET}")
        return input(f"{RED}Type 'yes' to confirm: {RESET}").strip().lower() == "yes"

    print(f"\n{CYAN}⚡ Fix:{RESET} {BOLD}{command}{RESET}")
    try:
        for i in range(seconds, 0, -1):
            print(f"  {DIM}Running in {i}s... Ctrl+C to cancel{RESET}", end="\r", flush=True)
            time.sleep(1)
        print(" " * 55, end="\r")
        return True
    except KeyboardInterrupt:
        print(f"\n{YELLOW}  Cancelled.{RESET}")
        return False


# ── Self-heal loop ────────────────────────────────────────────────────────────

def heal(failed_cmd, exit_code, stdout, stderr, buffer, model, config, logger) -> bool:
    max_attempts = config["session"]["max_heal_attempts"]
    countdown = config["session"]["countdown_seconds"]
    dangerous_list = config.get("dangerous_commands", [])

    # Fast path: known pattern
    known = logger.find_known_fix(failed_cmd, stderr)
    if known:
        print(f"\n{GREEN}📚 Known fix:{RESET} {DIM}{known['reasoning']}{RESET}")
        logger.log_mx_event("KNOWN_FIX", known["fix_command"])
        if countdown_run(known["fix_command"], countdown, is_dangerous(known["fix_command"], dangerous_list)):
            ec, so, se = run_command(known["fix_command"])
            logger.log_result(ec, so, se)
            if so.strip(): print(so.rstrip())
            if se.strip(): print(f"{DIM}{se.rstrip()}{RESET}", file=sys.stderr)
            if ec == 0:
                print(f"{GREEN}✓ Fixed.{RESET}")
                return True

    # Build context string from buffer
    ctx = "\n".join(
        f"$ {e['command']}" + (f"\n  EXIT:{e['exit_code']}" if e.get('exit_code', 0) != 0 else "")
        + (f"\n  STDERR:{e['stderr'][:120]}" if e.get('stderr') else "")
        for e in list(buffer)[-10:]
    )

    user_prompt = (
        f"Session context:\n{ctx}\n\n"
        f"Failed command: {failed_cmd}\n"
        f"Exit code: {exit_code}\n"
        f"Stderr: {stderr[:500] if stderr else '(none)'}\n"
        f"Stdout: {stdout[:200] if stdout else '(none)'}\n\nFix this."
    )

    for attempt in range(1, max_attempts + 1):
        print(f"\n{CYAN}🔧 Consulting Ollama (attempt {attempt}/{max_attempts})...{RESET}", flush=True)
        logger.log_mx_event("CONSULTING_OLLAMA", f"attempt {attempt}")

        raw = call_ollama(model, HEAL_SYSTEM, user_prompt, config["ollama"]["timeout"])
        if not raw:
            print(f"{RED}  Ollama unavailable.{RESET}")
            return False

        data = parse_json_response(raw)
        if not data:
            print(f"{RED}  Could not parse Ollama response.{RESET}")
            return False

        action = data.get("action", "EXPLAIN")
        reasoning = data.get("reasoning", "")
        if reasoning:
            print(f"  {DIM}{reasoning}{RESET}")

        if action in ("FIX", "FIX_SEQUENCE"):
            commands = data.get("commands", [])
            if not commands:
                return False

            all_ok = True
            for i, cmd in enumerate(commands):
                logger.log_fix_attempt(cmd, attempt)
                if len(commands) > 1:
                    print(f"\n  {DIM}Step {i+1}/{len(commands)}:{RESET}")
                if countdown_run(cmd, countdown, is_dangerous(cmd, dangerous_list)):
                    ec, so, se = run_command(cmd)
                    if so.strip(): print(so.rstrip())
                    if se.strip(): print(f"{DIM}{se.rstrip()}{RESET}", file=sys.stderr)
                    logger.log_result(ec, so, se)
                    if ec != 0:
                        all_ok = False
                        user_prompt = (
                            f"Previous fix failed:\nOriginal: {failed_cmd}\n"
                            f"Fix tried: {cmd}\nExit: {ec}\nStderr: {se[:400]}\n\nTry differently."
                        )
                        break
                else:
                    return False

            if all_ok:
                print(f"{GREEN}✓ Fixed.{RESET}")
                logger.log_fix_outcome(True, commands[0], failed_cmd, stderr, reasoning)
                return True

        elif action == "ASK":
            q = data.get("question", "I need more information.")
            print(f"\n{YELLOW}❓ {q}{RESET}")
            logger.log_mx_event("ASK", q)
            answer = input(f"  {CYAN}>{RESET} ").strip()
            if not answer:
                return False
            user_prompt += f"\n\nUser clarification: {answer}\n\nNow fix it."

        elif action == "EXPLAIN":
            print(f"\n{YELLOW}ℹ  {data.get('explanation', 'Cannot determine a fix.')}{RESET}")
            logger.log_mx_event("EXPLAIN", data.get("explanation", ""))
            return False

    print(f"\n{RED}  Max heal attempts reached.{RESET}")
    return False


# ── Ollama intent resolution ──────────────────────────────────────────────────

def resolve_via_ollama(user_input: str, model: str, config: dict, intent_resolver) -> str | None:
    prompt = f'Translate this to a shell command on the Mythos/Arcturus system: "{user_input}"'
    raw = call_ollama(model, INTENT_SYSTEM, prompt, config["ollama"]["timeout"])
    if not raw:
        return None

    data = parse_json_response(raw)
    if not data:
        return None

    action = data.get("action")
    if action == "COMMAND":
        cmd = data.get("command", "").strip()
        if cmd:
            reasoning = data.get("reasoning", "")
            phrase = data.get("phrase", user_input)
            if reasoning:
                print(f"  {DIM}{reasoning}{RESET}")
            intent_resolver.add_intent(phrase, cmd, source="ollama")
            return cmd
    elif action == "ASK":
        q = data.get("question", "")
        print(f"\n{YELLOW}❓ {q}{RESET}")
        answer = input(f"  {CYAN}>{RESET} ").strip()
        if answer:
            return resolve_via_ollama(f"{user_input}. Context: {answer}", model, config, intent_resolver)

    return None


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    model_override = None
    heal_enabled = True
    args = sys.argv[1:]

    for i, arg in enumerate(args):
        if arg == "--version":
            print(f"mx {VERSION} ({PATCH})")
            sys.exit(0)
        if arg == "--no-heal":
            heal_enabled = False
        if arg == "--model" and i + 1 < len(args):
            model_override = args[i + 1]

    config = load_config()
    model = model_override or get_active_model(config)

    sys.path.insert(0, "/opt/mythos/mx")
    from mx_intent import IntentResolver
    from mx_logger import MxLogger
    from mx_journal import MxJournal
    from mx_hooks import is_significant, pre_flight, post_flight

    logger = MxLogger(config)
    resolver = IntentResolver(config)
    buffer: deque = deque(maxlen=config["session"]["buffer_size"])

    # Session journal
    session_id = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    journal = MxJournal(session_id)

    # Declare intent
    try:
        intent_raw = input(f"  {DIM}What are you working on? (Enter to skip){RESET} ").strip()
        if intent_raw:
            journal.declare_intent(intent_raw)
            print(f"  {DIM}✓ Intent recorded: {intent_raw}{RESET}\n")
        else:
            print()
    except (EOFError, KeyboardInterrupt):
        print()


    print(f"\n{CYAN}{BOLD}⬡ mx{RESET}  {DIM}v{VERSION} · {PATCH} · model:{model} · heal:{'on' if heal_enabled else 'off'}{RESET}")
    print(f"{DIM}  Ctrl+D or 'exit' to end  ·  intents: /opt/mythos/mx/mx_intents.yaml{RESET}\n")

    # Readline history
    history_file = Path("~/.mx/.readline_history").expanduser()
    history_file.parent.mkdir(parents=True, exist_ok=True)
    readline.parse_and_bind("tab: complete")
    if history_file.exists():
        try:
            readline.read_history_file(str(history_file))
        except Exception:
            pass

    while True:
        try:
            cwd = os.getcwd().replace(str(Path.home()), "~")
            raw = input(f"{CYAN}mx{RESET} {DIM}{cwd}{RESET} {BOLD}❯{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not raw:
            continue
        if raw in ("exit", "quit", "bye"):
            break

        # cd must affect current process
        if raw.startswith("cd") and (len(raw) == 2 or raw[2] == " "):
            target = os.path.expanduser(raw[3:].strip() or "~")
            try:
                os.chdir(target)
            except FileNotFoundError:
                print(f"{RED}cd: {target}: No such file or directory{RESET}")
            continue

        # ── Intent resolution ──────────────────────────────────────────────
        resolved = raw
        intent_key = None

        if not resolver.is_valid_bash(raw):
            cmd, phrase, _ = resolver.resolve(raw)
            if cmd:
                resolved = cmd
                intent_key = phrase
                print(f"  {DIM}→ {resolved}{RESET}")
            else:
                print(f"  {DIM}Resolving...{RESET}", flush=True)
                logger.log_mx_event("INTENT_LOOKUP", raw)
                ollama_cmd = resolve_via_ollama(raw, model, config, resolver)
                if ollama_cmd:
                    resolved = ollama_cmd
                    intent_key = f"ollama:{raw}"
                    print(f"  {DIM}→ {resolved}{RESET}")

        logger.log_command(raw, resolved, intent_key)

        # ── Execute (with pre/post hooks for significant operations) ───────
        pre_snap_path = None
        pre_snap_data = None
        if is_significant(resolved):
            try:
                pre_snap_path, pre_snap_data = pre_flight(resolved, journal)
            except Exception as _hook_err:
                print(f"{YELLOW}  ⚠ Pre-flight warning: {_hook_err}{RESET}")

        ec, stdout, stderr = run_command(resolved)
        logger.log_result(ec, stdout, stderr)

        if stdout.strip():
            print(stdout.rstrip())
        if stderr.strip():
            print(f"{DIM}{stderr.rstrip()}{RESET}", file=sys.stderr)

        buffer.append({
            "command": resolved, "raw_input": raw,
            "exit_code": ec, "stdout": stdout[:300], "stderr": stderr[:300],
        })
        journal.record_command()
        # Track patch deploys and service restarts
        if 'patch-install' in resolved or resolved.startswith('pi '):
            parts = resolved.split()
            if len(parts) > 1:
                journal.record_patch_deploy(parts[-1])
        if 'systemctl restart' in resolved:
            for tok in resolved.split():
                if tok.endswith('.service') or 'mythos-' in tok:
                    journal.record_service_restart(tok)

        # ── Heal on failure ────────────────────────────────────────────────
        if ec != 0 and heal_enabled and not should_suppress(resolved, config.get("suppress_heal", [])):
            healed = heal(resolved, ec, stdout, stderr, buffer, model, config, logger)
            journal.record_heal(healed)

        # Post-flight for significant operations
        if pre_snap_path and pre_snap_data:
            try:
                post_flight(resolved, pre_snap_path, pre_snap_data, journal)
            except Exception as _hook_err:
                print(f"{YELLOW}  ⚠ Post-flight warning: {_hook_err}{RESET}")

    readline.write_history_file(str(history_file))
    logger.log_session_end()
    # Write session journal entry to TODO.md
    if journal.write_todo_entry():
        print(f"{DIM}  ✓ Session logged to TODO.md{RESET}")
    print(f"\n{DIM}mx session ended.{RESET}\n")


if __name__ == "__main__":
    main()
