#!/usr/bin/env python3
"""
Patch 0115: Clickable Ontology Terms
Makes /define list [category] return inline buttons that trigger /define lookups.
Adds moon_term_buttons() utility for other handlers to use.

Changes ontology_handler.py only. No bot changes needed — define_cmd already
handles (str, list) tuples with InlineKeyboardButton rendering.
"""

import shutil
import subprocess
import sys
from pathlib import Path

TARGET = Path("/opt/mythos/telegram_bot/handlers/ontology_handler.py")
BACKUP = TARGET.with_suffix(".py.bak.0115")


def patch():
    # --- Backup ---
    print(f"📦 Backing up {TARGET}")
    shutil.copy2(TARGET, BACKUP)

    content = TARGET.read_text()

    # =========================================================================
    # CHANGE 1: Add moon_term_buttons() utility after imports
    # =========================================================================
    old_imports = """from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')"""

    new_imports = """from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv('/opt/mythos/.env')


# Category → emoji prefix for inline buttons
CATEGORY_EMOJI = {
    'lunar': '🌙',
    'astrology': '✦',
    'numerology': '🔢',
    'tarot': '🎴',
    'mythos core': '🔥',
}


def moon_term_buttons(moon_names: list[str], cols: int = 2) -> InlineKeyboardMarkup:
    \"\"\"
    Given a list of moon names, return an InlineKeyboardMarkup
    where each name is a tappable button that triggers /define lookup.

    Usage from any handler:
        from handlers.ontology_handler import moon_term_buttons
        buttons = moon_term_buttons(["Wolf Moon", "Snow Moon"])
        await update.message.reply_text("Current moons:", reply_markup=buttons)
    \"\"\"
    keyboard = []
    row = []
    for name in moon_names:
        row.append(InlineKeyboardButton(
            text=f"🌙 {name}",
            callback_data=f"def:{name}"
        ))
        if len(row) >= cols:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)


def term_buttons(names: list[str], category: str = None, cols: int = 2) -> InlineKeyboardMarkup:
    \"\"\"
    Generic version — picks emoji by category.
    Falls back to '↗' if category unknown.
    \"\"\"
    emoji = CATEGORY_EMOJI.get((category or '').lower(), '↗')
    keyboard = []
    row = []
    for name in names:
        row.append(InlineKeyboardButton(
            text=f"{emoji} {name}",
            callback_data=f"def:{name[:60]}"
        ))
        if len(row) >= cols:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)"""

    if old_imports not in content:
        print("❌ Could not find import block to replace. Aborting.")
        shutil.copy2(BACKUP, TARGET)
        sys.exit(1)

    content = content.replace(old_imports, new_imports, 1)
    print("✅ Added moon_term_buttons() and term_buttons() utilities")

    # =========================================================================
    # CHANGE 2: Replace _list_terms() to return (str, names) tuple
    # =========================================================================
    old_list = """def _list_terms(category: str = None) -> str:
    driver = get_driver()
    try:
        with driver.session() as session:
            if category:
                result = session.run(\"\"\"
                    MATCH (t:OntologyTerm)
                    WHERE toLower(t.category) = toLower($cat)
                    RETURN t.name AS name, t.category AS category
                    ORDER BY t.name
                \"\"\", cat=category)
            else:
                result = session.run(\"\"\"
                    MATCH (t:OntologyTerm)
                    RETURN t.name AS name, t.category AS category
                    ORDER BY t.category, t.name
                \"\"\")

            records = list(result)
            if not records:
                return f"✦ No terms found{' in ' + category if category else ''}."

            lines = [f"✦ Ontology{' — ' + category if category else ''} ({len(records)} terms)\\n"]
            current_cat = None
            for r in records:
                if r['category'] != current_cat:
                    current_cat = r['category']
                    lines.append(f"\\n  [{current_cat}]")
                lines.append(f"  • {r['name']}")

            return '\\n'.join(lines)
    finally:
        driver.close()"""

    new_list = """def _list_terms(category: str = None):
    \"\"\"Returns (str, names_list) tuple so define_cmd renders inline buttons.\"\"\"
    driver = get_driver()
    try:
        with driver.session() as session:
            if category:
                result = session.run(\"\"\"
                    MATCH (t:OntologyTerm)
                    WHERE toLower(t.category) = toLower($cat)
                    RETURN t.name AS name, t.category AS category
                    ORDER BY t.name
                \"\"\", cat=category)
            else:
                result = session.run(\"\"\"
                    MATCH (t:OntologyTerm)
                    RETURN t.name AS name, t.category AS category
                    ORDER BY t.category, t.name
                \"\"\")

            records = list(result)
            if not records:
                return f"✦ No terms found{' in ' + category if category else ''}."

            lines = [f"✦ Ontology{' — ' + category if category else ''} ({len(records)} terms)\\n"]
            names = []
            current_cat = None
            for r in records:
                if r['category'] != current_cat:
                    current_cat = r['category']
                    lines.append(f"\\n  [{current_cat}]")
                lines.append(f"  • {r['name']}")
                names.append(r['name'])

            # Return tuple — define_cmd will render names as inline buttons
            return ('\\n'.join(lines), names[:12])
    finally:
        driver.close()"""

    if old_list not in content:
        print("❌ Could not find _list_terms() to replace. Aborting.")
        shutil.copy2(BACKUP, TARGET)
        sys.exit(1)

    content = content.replace(old_list, new_list, 1)
    print("✅ Enhanced _list_terms() to return (str, names) tuple")

    # --- Write ---
    TARGET.write_text(content)
    print(f"📝 Wrote {TARGET}")

    # --- Syntax check ---
    print("🔍 Syntax check...")
    try:
        import py_compile
        py_compile.compile(str(TARGET), doraise=True)
        print("✅ Syntax OK")
    except py_compile.PyCompileError as e:
        print(f"❌ Syntax error: {e}")
        print("🔄 Rolling back...")
        shutil.copy2(BACKUP, TARGET)
        sys.exit(1)

    # --- Restart bot ---
    print("🔄 Restarting mythos-bot.service...")
    result = subprocess.run(
        ["sudo", "systemctl", "restart", "mythos-bot.service"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ Bot restart failed: {result.stderr}")
        print("🔄 Rolling back...")
        shutil.copy2(BACKUP, TARGET)
        subprocess.run(["sudo", "systemctl", "restart", "mythos-bot.service"])
        sys.exit(1)

    # Verify it's running
    import time
    time.sleep(2)
    status = subprocess.run(
        ["systemctl", "is-active", "mythos-bot.service"],
        capture_output=True, text=True
    )
    if status.stdout.strip() != "active":
        print(f"❌ Bot not active after restart: {status.stdout.strip()}")
        print("🔄 Rolling back...")
        shutil.copy2(BACKUP, TARGET)
        subprocess.run(["sudo", "systemctl", "restart", "mythos-bot.service"])
        sys.exit(1)

    print("✅ Bot running")
    print("✅ Patch 0115 applied successfully")
    print()
    print("Test: /define list Lunar → should show clickable moon buttons")
    print("Test: Tap any moon → should show full definition + related terms")


if __name__ == "__main__":
    patch()
