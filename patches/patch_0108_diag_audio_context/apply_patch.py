#!/usr/bin/env python3
"""
Patch 0108: Diagnostics, Audio Upload, Context Command, Task Dispatch
======================================================================
Adds:
  - /diag command (composable diagnostics via Telegram)
  - /context command (dumps system docs for new sessions)
  - POST /api/upload/audio endpoint
  - Redis task dispatch foundation
  - BUILD_PROTOCOL.md
"""

import os
import sys
import shutil
import subprocess
import secrets

PATCH_DIR = os.path.dirname(os.path.abspath(__file__))
MYTHOS = "/opt/mythos"


def run(cmd, check=True):
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  FAILED: {result.stderr}")
        sys.exit(1)
    return result


def copy_file(src_rel, dest):
    src = os.path.join(PATCH_DIR, src_rel)
    print(f"  COPY {src_rel} → {dest}")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(src, dest)


def patch_file(filepath, old_str, new_str, description=""):
    """Replace exact string in file. Fails if old_str not found."""
    with open(filepath) as f:
        content = f.read()

    if old_str not in content:
        # Check if already patched
        if new_str in content:
            print(f"  SKIP (already patched): {description or filepath}")
            return
        print(f"  ERROR: Expected string not found in {filepath}")
        print(f"  Looking for: {old_str[:100]}...")
        sys.exit(1)

    content = content.replace(old_str, new_str, 1)
    with open(filepath, "w") as f:
        f.write(content)
    print(f"  PATCHED: {description or filepath}")


def main():
    print("╔══════════════════════════════════════════════════╗")
    print("║  Patch 0108: Diag + Audio + Context + Dispatch   ║")
    print("╚══════════════════════════════════════════════════╝")
    print()

    # ── 1. Create directories ──
    print("→ Creating directories...")
    for d in [
        f"{MYTHOS}/audio/inbox",
        f"{MYTHOS}/audio/processed",
    ]:
        os.makedirs(d, exist_ok=True)
        print(f"  DIR {d}")

    # ── 2. Copy new files ──
    print("\n→ Copying new files...")
    copy_file(
        "opt/mythos/telegram_bot/handlers/diag_handler.py",
        f"{MYTHOS}/telegram_bot/handlers/diag_handler.py"
    )
    copy_file(
        "opt/mythos/telegram_bot/handlers/context_handler.py",
        f"{MYTHOS}/telegram_bot/handlers/context_handler.py"
    )
    copy_file(
        "opt/mythos/api/routes/audio.py",
        f"{MYTHOS}/api/routes/audio.py"
    )
    copy_file(
        "opt/mythos/core/task_dispatch.py",
        f"{MYTHOS}/core/task_dispatch.py"
    )
    copy_file(
        "opt/mythos/docs/BUILD_PROTOCOL.md",
        f"{MYTHOS}/docs/BUILD_PROTOCOL.md"
    )

    # ── 3. Wire diag + context handlers into bot ──
    print("\n→ Wiring handlers into mythos_bot.py...")
    bot_file = f"{MYTHOS}/telegram_bot/mythos_bot.py"

    # Backup
    shutil.copy2(bot_file, bot_file + ".bak.0108")

    # Add imports — insert after the weather_handler import
    patch_file(
        bot_file,
        "from telegram_bot.handlers.weather_handler import cmd_weather",
        "from telegram_bot.handlers.weather_handler import cmd_weather\n"
        "from telegram_bot.handlers.diag_handler import handle_diag\n"
        "from telegram_bot.handlers.context_handler import handle_context",
        "Add diag + context handler imports"
    )

    # Add command registrations — insert after the weather command registration
    # Find the line that registers the weather command. Looking at the bot structure,
    # commands are registered in the main() function. We'll add after the last
    # application.add_handler(CommandHandler(...)) block.
    # The safest anchor is after the forecast/bills/income block.
    patch_file(
        bot_file,
        'application.add_handler(CommandHandler("income", income_command))',
        'application.add_handler(CommandHandler("income", income_command))\n'
        '\n'
        '    # Diagnostic & context commands\n'
        '    application.add_handler(CommandHandler("diag", handle_diag))\n'
        '    application.add_handler(CommandHandler("context", handle_context))',
        "Add /diag and /context command handlers"
    )

    # ── 4. Wire audio route into FastAPI ──
    print("\n→ Wiring audio route into api/main.py...")
    api_file = f"{MYTHOS}/api/main.py"

    # Backup
    shutil.copy2(api_file, api_file + ".bak.0108")

    # Add import
    patch_file(
        api_file,
        "from api.routes.review import router as review_router",
        "from api.routes.review import router as review_router\n"
        "from api.routes.audio import router as audio_router",
        "Add audio router import"
    )

    # Add router inclusion
    patch_file(
        api_file,
        "app.include_router(review_router, prefix='/api/finance', tags=['finance'])",
        "app.include_router(review_router, prefix='/api/finance', tags=['finance'])\n"
        "app.include_router(audio_router)",
        "Include audio router"
    )

    # ── 5. Generate API key for audio uploads ──
    print("\n→ Configuring audio API key...")
    env_file = f"{MYTHOS}/.env"
    with open(env_file) as f:
        env_content = f.read()

    if "MYTHOS_AUDIO_API_KEY" not in env_content:
        key = secrets.token_urlsafe(32)
        with open(env_file, "a") as f:
            f.write(f"\n# Audio upload API key (patch 0108)\n")
            f.write(f"MYTHOS_AUDIO_API_KEY={key}\n")
        print(f"  Generated API key: {key}")
        print(f"  (Use this in your iOS Shortcut X-API-Key header)")
    else:
        print("  API key already exists")

    # ── 6. Set ownership ──
    print("\n→ Setting ownership...")
    run(f"chown -R adge:adge {MYTHOS}/audio")
    run(f"chown adge:adge {MYTHOS}/telegram_bot/handlers/diag_handler.py")
    run(f"chown adge:adge {MYTHOS}/telegram_bot/handlers/context_handler.py")
    run(f"chown adge:adge {MYTHOS}/api/routes/audio.py")
    run(f"chown adge:adge {MYTHOS}/core/task_dispatch.py")
    run(f"chown adge:adge {MYTHOS}/docs/BUILD_PROTOCOL.md")

    # ── 7. Syntax check ──
    print("\n→ Syntax checking...")
    python = f"{MYTHOS}/.venv/bin/python3"
    files_to_check = [
        f"{MYTHOS}/telegram_bot/handlers/diag_handler.py",
        f"{MYTHOS}/telegram_bot/handlers/context_handler.py",
        f"{MYTHOS}/api/routes/audio.py",
        f"{MYTHOS}/core/task_dispatch.py",
        bot_file,
        api_file,
    ]
    for f in files_to_check:
        result = run(f"{python} -m py_compile {f}", check=False)
        if result.returncode != 0:
            print(f"\n  ✗ SYNTAX ERROR in {f}")
            print(f"  {result.stderr}")
            print("\n  Rolling back bot and API files...")
            shutil.copy2(bot_file + ".bak.0108", bot_file)
            shutil.copy2(api_file + ".bak.0108", api_file)
            print("  Rolled back. Fix and retry.")
            sys.exit(1)
        print(f"  ✓ {os.path.basename(f)}")

    # ── 8. Restart services ──
    print("\n→ Restarting services...")
    run("sudo systemctl restart mythos-bot.service")
    run("sudo systemctl restart mythos-api.service")

    # Verify they started
    import time
    time.sleep(3)

    bot_status = run("systemctl is-active mythos-bot.service", check=False)
    api_status = run("systemctl is-active mythos-api.service", check=False)

    if "active" not in bot_status.stdout:
        print("\n  ✗ Bot failed to start! Rolling back...")
        shutil.copy2(bot_file + ".bak.0108", bot_file)
        run("sudo systemctl restart mythos-bot.service")
        print("  Rolled back bot. Check: journalctl -u mythos-bot.service -n 30")
        sys.exit(1)

    if "active" not in api_status.stdout:
        print("\n  ✗ API failed to start! Rolling back...")
        shutil.copy2(api_file + ".bak.0108", api_file)
        run("sudo systemctl restart mythos-api.service")
        print("  Rolled back API. Check: journalctl -u mythos-api.service -n 30")
        sys.exit(1)

    # ── Done ──
    print("\n════════════════════════════════════════════════════")
    print("  ✓ Patch 0108 installed successfully")
    print("")
    print("  Test commands:")
    print("    /diag help        — see available diagnostics")
    print("    /diag hw          — hardware check")
    print("    /diag bot db      — combined diagnostics")
    print("    /diag all         — full dump (sent as file)")
    print("    /context          — dump docs for new session")
    print("    /diag audio       — check audio pipeline")
    print("")
    print("  Audio upload endpoint:")
    print("    POST https://mythos-api.denkers.co/api/upload/audio")
    print("    GET  https://mythos-api.denkers.co/api/upload/audio/status")
    print("════════════════════════════════════════════════════")


if __name__ == "__main__":
    main()
