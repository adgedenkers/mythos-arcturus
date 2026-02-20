#!/usr/bin/env python3
"""
Patch 0106: Add 'thinking' model class (qwen3:30b-a3b) and make it default.

Standalone Python script — no bash heredocs, no escaping issues.
Run with: /opt/mythos/.venv/bin/python3 apply_patch.py
"""

import shutil
import subprocess
import sys
import py_compile
from datetime import datetime

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

CHAT_MODE = "/opt/mythos/telegram_bot/handlers/chat_mode.py"
BOT_MAIN = "/opt/mythos/telegram_bot/mythos_bot.py"
ENV_FILE = "/opt/mythos/.env"


def backup(path):
    dest = f"{path}.bak.{TIMESTAMP}"
    shutil.copy2(path, dest)
    print(f"  backup: {dest}")


def patch_file(path, replacements):
    with open(path, "r") as f:
        content = f.read()
    for old, new in replacements:
        if old not in content:
            print(f"  ✗ FAILED: Could not find expected text in {path}")
            print(f"    Looking for: {repr(old[:80])}...")
            sys.exit(1)
        count = content.count(old)
        content = content.replace(old, new)
        print(f"  replaced {count} occurrence(s)")
    with open(path, "w") as f:
        f.write(content)


def verify(path, must_contain):
    with open(path, "r") as f:
        content = f.read()
    for check in must_contain:
        if check not in content:
            print(f"  ✗ VERIFY FAILED: '{check}' not found in {path}")
            sys.exit(1)
    print(f"  ✓ {path} verified")


def syntax_check(path):
    try:
        py_compile.compile(path, doraise=True)
        print(f"  ✓ {path} syntax OK")
    except py_compile.PyCompileError as e:
        print(f"  ✗ SYNTAX ERROR in {path}: {e}")
        sys.exit(1)


def main():
    print("=== Patch 0106: Thinking Model Class ===\n")

    # ── Backups ──
    print("1. Creating backups...")
    backup(CHAT_MODE)
    backup(BOT_MAIN)

    # ── Patch chat_mode.py ──
    print("\n2. Patching chat_mode.py...")
    patch_file(CHAT_MODE, [
        (
            "OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5:32b')",
            "OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen3:30b-a3b')",
        ),
        (
            "MODEL_MAP = {\n"
            "    'auto': 'qwen2.5:32b',\n"
            "    'fast': 'llama3.2:3b',\n"
            "    'deep': 'qwen2.5:32b',\n"
            "}",
            "MODEL_MAP = {\n"
            "    'auto': 'qwen2.5:32b',\n"
            "    'fast': 'llama3.2:3b',\n"
            "    'deep': 'qwen2.5:32b',\n"
            "    'thinking': 'qwen3:30b-a3b',\n"
            "}",
        ),
        (
            "model_preference: 'auto', 'fast', or 'deep'",
            "model_preference: 'auto', 'fast', 'deep', or 'thinking'",
        ),
    ])
    verify(CHAT_MODE, ["'thinking': 'qwen3:30b-a3b'", "qwen3:30b-a3b"])
    syntax_check(CHAT_MODE)

    # ── Patch mythos_bot.py ──
    print("\n3. Patching mythos_bot.py...")
    patch_file(BOT_MAIN, [
        (
            '"current_model": "auto",',
            '"current_model": "thinking",',
        ),
        (
            'session.get("current_model", "auto")',
            'session.get("current_model", "thinking")',
        ),
        (
            'if new_model in ["auto", "fast", "deep"]:',
            'if new_model in ["auto", "fast", "deep", "thinking"]:',
        ),
        (
            '            descriptions = {\n'
            '                "auto": "qwen2.5:32b",\n'
            '                "fast": "llama3.2:3b (~5s)",\n'
            '                "deep": "qwen2.5:32b (~30s)"\n'
            '            }',
            '            descriptions = {\n'
            '                "auto": "qwen2.5:32b",\n'
            '                "fast": "llama3.2:3b (~5s)",\n'
            '                "deep": "qwen2.5:32b (~30s)",\n'
            '                "thinking": "qwen3:30b-a3b (deep reasoning)",\n'
            '            }',
        ),
        (
            '"Use: auto, fast, deep"',
            '"Use: auto, fast, deep, thinking"',
        ),
        (
            '            "`/model auto` - qwen2.5:32b\\n"\n'
            '            "`/model fast` - llama3.2:3b\\n"\n'
            '            "`/model deep` - qwen2.5:32b",',
            '            "`/model thinking` - qwen3:30b-a3b (DEFAULT)\\n"\n'
            '            "`/model auto` - qwen2.5:32b\\n"\n'
            '            "`/model fast` - llama3.2:3b\\n"\n'
            '            "`/model deep` - qwen2.5:32b",',
        ),
    ])
    verify(BOT_MAIN, [
        '"current_model": "thinking"',
        '"thinking": "qwen3:30b-a3b (deep reasoning)"',
        "auto, fast, deep, thinking",
    ])
    syntax_check(BOT_MAIN)

    # ── Patch .env ──
    print("\n4. Patching .env...")
    patch_file(ENV_FILE, [
        (
            "OLLAMA_MODEL=qwen2.5:32b",
            "OLLAMA_MODEL=qwen3:30b-a3b",
        ),
    ])
    verify(ENV_FILE, ["OLLAMA_MODEL=qwen3:30b-a3b"])

    # ── Restart ──
    print("\n5. Restarting bot...")
    result = subprocess.run(
        ["sudo", "systemctl", "restart", "mythos-bot.service"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  ✗ Restart failed: {result.stderr}")
        sys.exit(1)

    import time
    time.sleep(3)

    result = subprocess.run(
        ["systemctl", "is-active", "mythos-bot.service"],
        capture_output=True, text=True
    )
    if result.stdout.strip() == "active":
        print("  ✓ Bot restarted successfully")
    else:
        print("  ✗ Bot not active! Rolling back...")
        shutil.copy2(f"{CHAT_MODE}.bak.{TIMESTAMP}", CHAT_MODE)
        shutil.copy2(f"{BOT_MAIN}.bak.{TIMESTAMP}", BOT_MAIN)
        subprocess.run(["sudo", "systemctl", "restart", "mythos-bot.service"])
        print("  Rolled back. Check: journalctl -u mythos-bot -n 20")
        sys.exit(1)

    print("\n=== Patch 0106 Complete ===")
    print("Default model: qwen3:30b-a3b (thinking)")
    print()
    print("Test with:")
    print("  /model          → should show thinking as DEFAULT")
    print("  /model thinking → should confirm qwen3:30b-a3b")
    print("  /status         → should show thinking")


if __name__ == "__main__":
    main()
