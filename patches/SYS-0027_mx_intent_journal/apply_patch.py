"""
SYS-0027: mx Session Intent + Auto Journal
- Adds mx_journal.py to /opt/mythos/mx/
- Patches mx_session.py to ask for session intent at startup
- Writes session summary to TODO.md on exit
"""

import subprocess
import sys
import py_compile
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=27,
    description='mx session intent and auto journal',
    patch_type='MINOR',
)
patch.begin()

PATCH_DIR = Path(__file__).parent

# ── 1. Deploy mx_journal.py ───────────────────────────────────────────────────

patch.deploy_file(
    str(PATCH_DIR / 'opt/mythos/mx/mx_journal.py'),
    '/opt/mythos/mx/mx_journal.py',
)
py_compile.compile('/opt/mythos/mx/mx_journal.py', doraise=True)
print("  ✓ mx_journal.py deployed and validated")

# ── 2. Patch mx_session.py — add journal import ───────────────────────────────

session_path = Path('/opt/mythos/mx/mx_session.py')
content = session_path.read_text()

# Add import
old_import = "    from mx_intent import IntentResolver\n    from mx_logger import MxLogger"
new_import = "    from mx_intent import IntentResolver\n    from mx_logger import MxLogger\n    from mx_journal import MxJournal"

if 'from mx_journal import MxJournal' not in content:
    assert old_import in content, "Import anchor not found in mx_session.py"
    content = content.replace(old_import, new_import)
    print("  ✓ Added MxJournal import")

# Add journal init after logger/resolver init
old_init = "    buffer: deque = deque(maxlen=config[\"session\"][\"buffer_size\"])"
new_init = (
    "    buffer: deque = deque(maxlen=config[\"session\"][\"buffer_size\"])\n\n"
    "    # Session journal\n"
    "    session_id = datetime.now().strftime(\"%Y-%m-%d_%H%M%S\")\n"
    "    journal = MxJournal(session_id)\n\n"
    "    # Declare intent\n"
    "    try:\n"
    "        intent_raw = input(f\"  {DIM}What are you working on? (Enter to skip){RESET} \").strip()\n"
    "        if intent_raw:\n"
    "            journal.declare_intent(intent_raw)\n"
    "            print(f\"  {DIM}✓ Intent recorded: {intent_raw}{RESET}\\n\")\n"
    "        else:\n"
    "            print()\n"
    "    except (EOFError, KeyboardInterrupt):\n"
    "        print()\n"
)

if 'journal = MxJournal' not in content:
    assert old_init in content, "Buffer init anchor not found in mx_session.py"
    content = content.replace(old_init, new_init)
    print("  ✓ Added journal init and intent declaration")

# Add datetime import if missing
if 'from datetime import datetime' not in content:
    content = content.replace(
        'from collections import deque',
        'from collections import deque\nfrom datetime import datetime'
    )
    print("  ✓ Added datetime import")

# Hook journal.record_command() after the buffer.append block
old_buffer_append = (
    "        buffer.append({\n"
    "            \"command\": resolved, \"raw_input\": raw,\n"
    "            \"exit_code\": ec, \"stdout\": stdout[:300], \"stderr\": stderr[:300],\n"
    "        })"
)
new_buffer_append = (
    "        buffer.append({\n"
    "            \"command\": resolved, \"raw_input\": raw,\n"
    "            \"exit_code\": ec, \"stdout\": stdout[:300], \"stderr\": stderr[:300],\n"
    "        })\n"
    "        journal.record_command()\n"
    "        # Track patch deploys and service restarts\n"
    "        if 'patch-install' in resolved or resolved.startswith('pi '):\n"
    "            parts = resolved.split()\n"
    "            if len(parts) > 1:\n"
    "                journal.record_patch_deploy(parts[-1])\n"
    "        if 'systemctl restart' in resolved:\n"
    "            for tok in resolved.split():\n"
    "                if tok.endswith('.service') or 'mythos-' in tok:\n"
    "                    journal.record_service_restart(tok)"
)

if 'journal.record_command()' not in content:
    assert old_buffer_append in content, "Buffer append anchor not found"
    content = content.replace(old_buffer_append, new_buffer_append)
    print("  ✓ Hooked journal.record_command()")

# Hook heal outcome into journal
old_heal_call = (
    "        if ec != 0 and heal_enabled and not should_suppress(resolved, config.get(\"suppress_heal\", [])):\n"
    "            heal(resolved, ec, stdout, stderr, buffer, model, config, logger)"
)
new_heal_call = (
    "        if ec != 0 and heal_enabled and not should_suppress(resolved, config.get(\"suppress_heal\", [])):\n"
    "            healed = heal(resolved, ec, stdout, stderr, buffer, model, config, logger)\n"
    "            journal.record_heal(healed)"
)

if 'journal.record_heal' not in content:
    assert old_heal_call in content, "Heal call anchor not found"
    content = content.replace(old_heal_call, new_heal_call)
    print("  ✓ Hooked journal.record_heal()")

# Hook journal write on session end
old_end = (
    "    readline.write_history_file(str(history_file))\n"
    "    logger.log_session_end()\n"
    "    print(f\"\\n{DIM}mx session ended.{RESET}\\n\")"
)
new_end = (
    "    readline.write_history_file(str(history_file))\n"
    "    logger.log_session_end()\n"
    "    # Write session journal entry to TODO.md\n"
    "    if journal.write_todo_entry():\n"
    "        print(f\"{DIM}  ✓ Session logged to TODO.md{RESET}\")\n"
    "    print(f\"\\n{DIM}mx session ended.{RESET}\\n\")"
)

if 'journal.write_todo_entry' not in content:
    assert old_end in content, "Session end anchor not found"
    content = content.replace(old_end, new_end)
    print("  ✓ Hooked journal.write_todo_entry() on exit")

session_path.write_text(content)
py_compile.compile(str(session_path), doraise=True)
print("  ✓ mx_session.py patched and validated")

# ── Done ──────────────────────────────────────────────────────────────────────

patch.finish()

print()
print("╔══════════════════════════════════════════════════╗")
print("║  SYS-0027: mx Journal ready.                     ║")
print("║                                                  ║")
print("║  mx now asks: 'What are you working on?'         ║")
print("║  Sessions auto-logged to TODO.md on exit.        ║")
print("║  Journal files: ~/.mx/journal/                   ║")
print("╚══════════════════════════════════════════════════╝")
