#!/usr/bin/env python3
"""
Patch 0116: People Handler + Help Topics (People & Define)
- Adds /people command (add, search, list, view, edit, delete)
- Adds /help people and /help define topics to help_handler.py
- Wires /people into mythos_bot.py
"""
import os
import sys
import shutil
import py_compile

PATCH_DIR = os.path.dirname(os.path.abspath(__file__))
MYTHOS = '/opt/mythos'
BOT_FILE = f'{MYTHOS}/telegram_bot/mythos_bot.py'
HELP_FILE = f'{MYTHOS}/telegram_bot/handlers/help_handler.py'
HANDLERS_DIR = f'{MYTHOS}/telegram_bot/handlers'
PEOPLE_HANDLER_SRC = f'{PATCH_DIR}/opt/mythos/telegram_bot/handlers/people_handler.py'


def backup(path):
    ts = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
    bak = f"{path}.bak.{ts}"
    shutil.copy2(path, bak)
    print(f"  Backed up {path} → {bak}")
    return bak


def patch_file(path, old_str, new_str, desc):
    with open(path, 'r') as f:
        content = f.read()
    if old_str not in content:
        print(f"  ⚠️  Could not find target string for: {desc}")
        print(f"      Looking for: {repr(old_str[:80])}...")
        return False
    if new_str in content:
        print(f"  ✓ Already applied: {desc}")
        return True
    content = content.replace(old_str, new_str, 1)
    with open(path, 'w') as f:
        f.write(content)
    print(f"  ✓ Applied: {desc}")
    return True


def main():
    print("=== Patch 0116: People Handler + Help Topics ===\n")

    # ── 1. Copy people_handler.py ──
    print("[1/4] Installing people_handler.py")
    dest = f'{HANDLERS_DIR}/people_handler.py'
    shutil.copy2(PEOPLE_HANDLER_SRC, dest)
    os.chmod(dest, 0o644)
    print(f"  ✓ Copied to {dest}")

    # ── 2. Wire /people into mythos_bot.py ──
    print("\n[2/4] Wiring /people into mythos_bot.py")
    backup(BOT_FILE)

    # Add import
    IMPORT_ANCHOR = "from handlers.ontology_handler import handle_define"
    IMPORT_NEW = """from handlers.ontology_handler import handle_define
from handlers.people_handler import handle_people"""

    patch_file(BOT_FILE, IMPORT_ANCHOR, IMPORT_NEW, "Add people_handler import")

    # Add command handler — insert after the define callback handler registration
    # We add the people_cmd inline function + handler near the define block
    CMD_ANCHOR = '    application.add_handler(CallbackQueryHandler(define_callback, pattern="^def:"))'
    CMD_NEW = '''    application.add_handler(CallbackQueryHandler(define_callback, pattern="^def:"))

    # People database
    async def people_cmd(update, context):
        text = " ".join(context.args) if context.args else ""
        result = handle_people(text)
        await update.message.reply_text(result)
    application.add_handler(CommandHandler("people", people_cmd))'''

    patch_file(BOT_FILE, CMD_ANCHOR, CMD_NEW, "Add /people command handler")

    # ── 3. Add help topics to help_handler.py ──
    print("\n[3/4] Adding help topics for People and Define")
    backup(HELP_FILE)

    # Add HELP_PEOPLE and HELP_DEFINE text blocks before the HELP_TOPICS dict
    HELP_ANCHOR = "# Topic aliases for flexible matching"
    HELP_NEW = '''HELP_PEOPLE = """👤 **People Database**

Track people for astrology, genealogy, and lineage work.

━━━━━━━━━━━━━━━━━━━━━━━━
**ADDING PEOPLE**
━━━━━━━━━━━━━━━━━━━━━━━━

Fields are pipe-separated. Leave empty between pipes for unknown fields.

`/people add <first> | <middle> | <last> | <known_as> | <DOB> | <time> | <city> | <state> | <country> | <DOD> | <notes>`

**Examples:**
`/people add John | Fitzgerald | Kennedy | JFK | 1917-05-29 | 15:00 | Brookline | Massachusetts | USA | 1963-11-22 | 35th US President`

`/people add Aleister | Edward Alexander | Crowley | The Great Beast | 1875-10-12 | | Royal Leamington Spa | Warwickshire | England | 1947-12-01 | Occultist, founder of Thelema`

**Partial data (no middle, no time, no death):**
`/people add Marie | | Curie | | 1867-11-07 | | Warsaw | | Poland | | Physicist, Nobel laureate`

━━━━━━━━━━━━━━━━━━━━━━━━
**SEARCHING & VIEWING**
━━━━━━━━━━━━━━━━━━━━━━━━

`/people list` — All records (summary)
`/people search <query>` — Search by name, known\\_as, or notes
`/people view <id or name>` — Full detail for one person
`/people Kennedy` — Bare text also searches

━━━━━━━━━━━━━━━━━━━━━━━━
**EDITING**
━━━━━━━━━━━━━━━━━━━━━━━━

`/people edit <id> <field> <value>`

**Fields:** first\\_name, middle\\_name, last\\_name, known\\_as, date\\_of\\_birth, time\\_of\\_birth, birth\\_city, birth\\_state, birth\\_country, date\\_of\\_death, notes

**Examples:**
`/people edit 4 time_of_birth 14:15`
`/people edit 4 notes Eclipse-born, Scorpio rising`

━━━━━━━━━━━━━━━━━━━━━━━━
**DELETING**
━━━━━━━━━━━━━━━━━━━━━━━━

`/people delete <id>`

━━━━━━━━━━━━━━━━━━━━━━━━
**TIPS**
━━━━━━━━━━━━━━━━━━━━━━━━
• Date format: YYYY-MM-DD
• Time format: HH:MM (24hr)
• Use known\\_as for spiritual names, stage names, etc.
• People records feed into /chart for astrology
• Leave fields empty (blank between pipes) for unknowns
"""

HELP_DEFINE = """✦ **Ontology / Glossary**

The living glossary of the Mythos system. Terms stored in Neo4j.

━━━━━━━━━━━━━━━━━━━━━━━━
**LOOKING UP TERMS**
━━━━━━━━━━━━━━━━━━━━━━━━

`/define <term>` — Look up a term by name
`/define chakra` — Exact or fuzzy match
`/define natal` — Partial matches shown as buttons

━━━━━━━━━━━━━━━━━━━━━━━━
**ADDING TERMS**
━━━━━━━━━━━━━━━━━━━━━━━━

`/define add <name> | <definition> | <category>`

**Examples:**
`/define add Thelema | Religious philosophy founded by Aleister Crowley based on The Book of the Law (1904) | Occult`

`/define add Chitra Nakshatra | 14th lunar mansion, ruled by Mars, deity Vishvakarma the celestial architect | Astrology`

━━━━━━━━━━━━━━━━━━━━━━━━
**LISTING TERMS**
━━━━━━━━━━━━━━━━━━━━━━━━

`/define list` — All terms, grouped by category
`/define list Astrology` — Only astrology terms
`/define list Occult` — Only occult terms

━━━━━━━━━━━━━━━━━━━━━━━━
**CATEGORIES**
━━━━━━━━━━━━━━━━━━━━━━━━

Astrology, Numerology, Tarot, Mythos Core, History, Lineage, Theology, Occult, Music, Literature, Science, Philosophy

(New categories are created automatically when you add a term)

━━━━━━━━━━━━━━━━━━━━━━━━
**TIPS**
━━━━━━━━━━━━━━━━━━━━━━━━
• Related terms show as clickable buttons
• The glossary is shared across the whole system
• Use it to build institutional knowledge
"""

# Topic aliases for flexible matching'''

    patch_file(HELP_FILE, HELP_ANCHOR, HELP_NEW, "Add HELP_PEOPLE and HELP_DEFINE text blocks")

    # Add topic aliases into HELP_TOPICS dict
    TOPICS_ANCHOR = """    # System
    'system': HELP_SYSTEM,"""
    TOPICS_NEW = """    # People
    'people': HELP_PEOPLE,
    'person': HELP_PEOPLE,
    'contacts': HELP_PEOPLE,

    # Ontology / Define
    'define': HELP_DEFINE,
    'ontology': HELP_DEFINE,
    'glossary': HELP_DEFINE,
    'terms': HELP_DEFINE,

    # System
    'system': HELP_SYSTEM,"""

    patch_file(HELP_FILE, TOPICS_ANCHOR, TOPICS_NEW, "Add people/define aliases to HELP_TOPICS")

    # Update the main help overview to include People and Define
    MAIN_ANCHOR = '**⚙️ SYSTEM** → `/help system`\nPatches, status, modes'
    MAIN_NEW = '''**👤 PEOPLE** → `/help people`
Track people for astrology & lineage

**✦ GLOSSARY** → `/help define`
Mythos ontology & definitions

**⚙️ SYSTEM** → `/help system`
Patches, status, modes'''

    patch_file(HELP_FILE, MAIN_ANCHOR, MAIN_NEW, "Add People and Glossary to main help overview")

    # Update the unknown-topic hint to include new topics
    OLD_TOPICS_HINT = '"`tasks`, `finance`, `sell`, `chat`, `db`, `system`, `astrology`\\n\\n"'
    NEW_TOPICS_HINT = '"`tasks`, `finance`, `sell`, `chat`, `db`, `people`, `define`, `astrology`, `system`\\n\\n"'

    patch_file(HELP_FILE, OLD_TOPICS_HINT, NEW_TOPICS_HINT, "Update unknown-topic hint list")

    # ── 4. Syntax check ──
    print("\n[4/4] Syntax checking")
    errors = []
    for f in [BOT_FILE, HELP_FILE, f'{HANDLERS_DIR}/people_handler.py']:
        try:
            py_compile.compile(f, doraise=True)
            print(f"  ✓ {os.path.basename(f)}")
        except py_compile.PyCompileError as e:
            print(f"  ✗ {os.path.basename(f)}: {e}")
            errors.append(f)

    if errors:
        print("\n❌ Syntax errors found. NOT restarting bot.")
        sys.exit(1)

    # ── Restart bot ──
    print("\n=== Restarting mythos-bot ===")
    os.system("sudo systemctl restart mythos-bot.service")

    import time
    time.sleep(3)

    rc = os.system("sudo systemctl is-active --quiet mythos-bot.service")
    if rc == 0:
        print("✓ mythos-bot is running")
    else:
        print("✗ mythos-bot failed to start — check journalctl")
        sys.exit(1)

    print("\n=== Patch 0116 complete ===")
    print("Test with:")
    print("  /people list")
    print("  /people add Test | | User | | 2000-01-01 | | | | | | Test record")
    print("  /help people")
    print("  /help define")


if __name__ == '__main__':
    main()
