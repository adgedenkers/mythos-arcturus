"""MNE-0010 — Meditation Renderer"""
import sys, os
sys.path.insert(0, "/opt/mythos/patches/scripts")
from patch_base import PatchBase

patch = PatchBase(
    stream="MNE",
    number=10,
    description="meditation renderer",
    patch_type="MINOR",
)
patch.begin()

BASE = os.path.dirname(os.path.abspath(__file__))

patch.deploy_file(f"{BASE}/opt/mythos/voice/meditation.py",
                  "/opt/mythos/voice/meditation.py")
patch.deploy_file(f"{BASE}/opt/mythos/telegram_bot/handlers/meditation_handler.py",
                  "/opt/mythos/telegram_bot/handlers/meditation_handler.py")
patch.deploy_file(f"{BASE}/opt/mythos/bin/iris-meditate",
                  "/opt/mythos/bin/iris-meditate")
patch.deploy_file(f"{BASE}/opt/mythos/public/meditations/.gitkeep",
                  "/opt/mythos/public/meditations/.gitkeep")

os.makedirs("/opt/mythos/public/meditations", exist_ok=True)
os.chmod("/opt/mythos/bin/iris-meditate", 0o755)

patch.finish()

print("""
╔══════════════════════════════════════════════════════════════════╗
║  MANUAL STEPS — wire up Telegram commands                        ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  1. telegram_bot/handlers/__init__.py — add:                     ║
║                                                                  ║
║     from .meditation_handler import (                            ║
║         meditate_command,                                        ║
║         meditations_command,                                     ║
║         handle_meditation_document,                              ║
║         handle_pending_meditation_text,                          ║
║     )                                                            ║
║                                                                  ║
║  2. telegram_bot/bot.py — add in setup section:                  ║
║                                                                  ║
║     app.add_handler(CommandHandler(                              ║
║         "meditate", meditate_command))                           ║
║     app.add_handler(CommandHandler(                              ║
║         "meditations", meditations_command))                     ║
║                                                                  ║
║  3. sudo systemctl restart mythos-bot.service                    ║
║                                                                  ║
║  Test via CLI first:                                             ║
║     echo -e "Breathe.\\n[pause:5]\\nSettle." > /tmp/test.txt      ║
║     iris-meditate --estimate /tmp/test.txt                       ║
║     iris-meditate /tmp/test.txt --title "Quick Test"             ║
╚══════════════════════════════════════════════════════════════════╝
""")
