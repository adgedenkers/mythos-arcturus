"""
SEN-0006: Spiral Time Walker
Applies the Nine Day Sun Cycle engine to Mythos / Iris.

Deploys:
  - astrology/spiral/ (engine, transit pressure, morning brief, __init__)
  - skills/data/spiral_walker.py (auto-discovered Iris skill)
  - telegram_bot/handlers/spiral_handler.py
  - migrations/sen_0006_spiral_transit.sql
  - Registers /spiral command in handlers/__init__.py
"""

import os
import subprocess
import sys

sys.path.insert(0, "/opt/mythos/patches/scripts")
from patch_base import PatchBase

patch = PatchBase(
    stream="SEN",
    number=6,
    description="spiral_time_walker",
    patch_type="MINOR",
)
patch.begin()

PATCH_DIR = os.path.dirname(os.path.abspath(__file__))

# ── 1. Deploy spiral engine module ───────────────────────────────────────────
for fname in ["__init__.py", "spiral_engine.py", "transit_pressure.py", "morning_brief.py"]:
    patch.deploy_file(
        f"opt/mythos/astrology/spiral/{fname}",
        f"/opt/mythos/astrology/spiral/{fname}",
    )

# ── 2. Deploy Iris skill ──────────────────────────────────────────────────────
patch.deploy_file(
    "opt/mythos/skills/data/spiral_walker.py",
    "/opt/mythos/skills/data/spiral_walker.py",
)

# ── 3. Deploy Telegram handler ────────────────────────────────────────────────
patch.deploy_file(
    "opt/mythos/telegram_bot/handlers/spiral_handler.py",
    "/opt/mythos/telegram_bot/handlers/spiral_handler.py",
)

# ── 4. Run SQL migration ──────────────────────────────────────────────────────
patch.run_sql("opt/mythos/migrations/sen_0006_spiral_transit.sql")

# ── 5. Register /spiral command in handlers/__init__.py ──────────────────────
INIT_PATH = "/opt/mythos/telegram_bot/handlers/__init__.py"
with open(INIT_PATH, "r") as f:
    init_content = f.read()

IMPORT_LINE = "from .spiral_handler import register as register_spiral"
REGISTER_CALL = "    register_spiral(application)"

needs_import = IMPORT_LINE not in init_content
needs_register = REGISTER_CALL not in init_content

if needs_import or needs_register:
    new_content = init_content

    # Add import after last existing handler import block
    if needs_import:
        # Find a good insertion point — after the last 'from .' import
        lines = new_content.split("\n")
        last_import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("from .") and "import" in line:
                last_import_idx = i
        lines.insert(last_import_idx + 1, IMPORT_LINE)
        new_content = "\n".join(lines)

    # Add register call inside the setup/register function
    if needs_register:
        # Find the application.run_polling or last register call and insert before it
        if "register_spiral(application)" not in new_content:
            # Insert near other register calls
            if "def setup_handlers(application)" in new_content or "def register_handlers(application)" in new_content:
                # Find the last register_* call and add after it
                lines = new_content.split("\n")
                last_register_idx = 0
                for i, line in enumerate(lines):
                    if "register_" in line and "(application)" in line:
                        last_register_idx = i
                if last_register_idx > 0:
                    lines.insert(last_register_idx + 1, REGISTER_CALL)
                    new_content = "\n".join(lines)

    with open(INIT_PATH, "w") as f:
        f.write(new_content)

    print("✓ Registered /spiral in handlers/__init__.py")
else:
    print("✓ /spiral already registered in handlers/__init__.py")

# ── 6. Verify swisseph is available ──────────────────────────────────────────
try:
    result = subprocess.run(
        ["/opt/mythos/.venv/bin/python3", "-c", "import swisseph; print('swisseph OK')"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"✓ {result.stdout.strip()}")
    else:
        print("⚠️  swisseph not found — installing...")
        subprocess.run(
            ["/opt/mythos/.venv/bin/pip", "install", "pyswisseph"],
            check=True
        )
        print("✓ pyswisseph installed")
except Exception as e:
    print(f"⚠️  swisseph check error: {e}")

# ── 7. Restart services ───────────────────────────────────────────────────────
patch.restart_service("mythos-api.service")
patch.restart_service("mythos-bot.service")

patch.finish()
print("\n✅ SEN-0006 Spiral Time Walker deployed.")
print("   Commands: /spiral  /spiral reset  /spiral history  /spiral brief")
print("   Morning brief fires on first Iris message each day.")
print("   Transit pressure computed fresh daily via Swiss Ephemeris.")
