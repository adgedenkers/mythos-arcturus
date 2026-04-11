"""
NEU-0005: Iris Integrity Awareness
- Deploys iris/integrity/ package
- Registers /iris_integrity Telegram command via SYS bot registration pattern
- Patches life_context.py to inject system health into Iris's awareness
"""

import subprocess
import sys
import py_compile
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='NEU',
    number=5,
    description='iris integrity awareness - self-model health injection',
    patch_type='MINOR',
)
patch.begin()

PATCH_DIR = Path(__file__).parent

# ── 1. Deploy iris/integrity package ─────────────────────────────────────────

integrity_dir = Path('/opt/mythos/iris/integrity')
integrity_dir.mkdir(parents=True, exist_ok=True)

for filename in ['iris_integrity.py', '__init__.py', 'iris_integrity_handler.py']:
    patch.deploy_file(
        str(PATCH_DIR / 'opt/mythos/iris/integrity' / filename),
        str(integrity_dir / filename),
    )
    if filename.endswith('.py'):
        py_compile.compile(str(integrity_dir / filename), doraise=True)
    print(f"  ✓ {filename} deployed and validated")

# ── 2. Register /iris_integrity command in bot handler __init__.py ────────────

init_path = Path('/opt/mythos/telegram_bot/handlers/__init__.py')
init_content = init_path.read_text()

# Only patch if not already registered
if 'iris_integrity_handler' not in init_content:
    # Find the import block to append to
    old_import_anchor = "from telegram_bot.handlers.iris_handler import iris_handler"
    new_import = (
        "from telegram_bot.handlers.iris_handler import iris_handler\n"
        "from iris.integrity.iris_integrity_handler import iris_integrity_handler"
    )
    if old_import_anchor in init_content:
        init_content = init_content.replace(old_import_anchor, new_import)
        print("  ✓ Added iris_integrity_handler import")
    else:
        print("  ⚠ Could not find import anchor — adding at end of imports")
        # Fallback: add before first application.add_handler
        init_content = init_content.replace(
            "# Register handlers",
            "from iris.integrity.iris_integrity_handler import iris_integrity_handler\n# Register handlers",
        )

    # Register the command handler
    # Find where other iris commands are registered
    old_handler_anchor = 'application.add_handler(CommandHandler("iris_reflect"'
    if old_handler_anchor in init_content:
        init_content = init_content.replace(
            old_handler_anchor,
            'application.add_handler(CommandHandler("iris_integrity", iris_integrity_handler))\n    '
            + old_handler_anchor
        )
        print("  ✓ Registered /iris_integrity command handler")
    else:
        # Generic fallback anchor
        fallback = 'application.add_handler(CommandHandler("help"'
        if fallback in init_content:
            init_content = init_content.replace(
                fallback,
                'application.add_handler(CommandHandler("iris_integrity", iris_integrity_handler))\n    '
                + fallback
            )
            print("  ✓ Registered /iris_integrity command handler (fallback anchor)")

    init_path.write_text(init_content)
    py_compile.compile(str(init_path), doraise=True)
    print("  ✓ handlers/__init__.py updated and validated")
else:
    print("  ℹ /iris_integrity already registered — skipping")

# ── 3. Patch life_context.py to inject system health into Iris's prompt ───────

life_context_path = Path('/opt/mythos/core/life_context.py')
if life_context_path.exists():
    lc_content = life_context_path.read_text()

    if 'iris_integrity' not in lc_content:
        # Add health context injection at end of get_life_context() or equivalent
        # Find the return statement of the main context builder
        inject_code = '''

def get_system_health_context() -> str:
    """Get Iris's system health awareness for prompt injection."""
    try:
        import sys
        sys.path.insert(0, '/opt/mythos/iris/integrity')
        from iris_integrity import build_health_summary, format_iris_context
        health = build_health_summary()
        # Only inject if scan has been run and there's something to say
        if health.get("scan_age") != "never":
            return format_iris_context(health)
    except Exception:
        pass
    return ""
'''
        lc_content += inject_code
        life_context_path.write_text(lc_content)
        py_compile.compile(str(life_context_path), doraise=True)
        print("  ✓ life_context.py — added get_system_health_context()")
    else:
        print("  ℹ life_context.py already has integrity awareness — skipping")
else:
    print("  ⚠ life_context.py not found — skipping prompt injection")

# ── 4. Restart bot to pick up new handler ────────────────────────────────────

patch.restart_service('mythos-bot.service')
print("  ✓ mythos-bot.service restarted")

# ── Done ──────────────────────────────────────────────────────────────────────

patch.finish()

print()
print("╔══════════════════════════════════════════════════╗")
print("║  NEU-0005: Iris Integrity Awareness ready.       ║")
print("║                                                  ║")
print("║  /iris_integrity         Status from last scan   ║")
print("║  /iris_integrity scan    Run fresh fast scan     ║")
print("║  /iris_integrity full    Run full scan (~60s)    ║")
print("║  /iris_integrity context What Iris carries       ║")
print("║                                                  ║")
print("║  Iris now knows when she is healthy or broken.   ║")
print("║  The immune system is online.                    ║")
print("╚══════════════════════════════════════════════════╝")
