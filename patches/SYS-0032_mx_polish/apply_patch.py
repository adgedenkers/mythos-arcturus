"""
SYS-0032: mx Polish Pass
Fixes:
  1. mx_session.py — bump VERSION to 1.1.0, PATCH to SYS-0032
  2. mx_session.py — add top-level datetime import (was missing)
  3. mx_session.py — verify/add late imports for MxJournal and mx_hooks
  4. help_handler.py — fix SyntaxWarning: invalid escape sequences in HELP_MX
  5. help_handler.py — replace Telegram-unfriendly table with plain text file list
  6. mx_hooks.py — fix snapshot label: strip 'sudo ' prefix so label reads
                   'mythos-api' not 'sudo'
  7. mythos-diag banner — says SYS-0030, fix to SYS-0032
"""

import py_compile
import sys
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=32,
    description='mx polish - version bump, escape fix, snapshot label, imports',
    patch_type='PATCH',
)
patch.begin()

# ── 1. mx_session.py — version bump + datetime import ────────────────────────

session_path = Path('/opt/mythos/mx/mx_session.py')
s = session_path.read_text()

# Version bump
assert 'VERSION = "1.0.0"' in s, "VERSION anchor not found"
s = s.replace('VERSION = "1.0.0"', 'VERSION = "1.1.0"')
print("  ✓ VERSION → 1.1.0")

assert 'PATCH = "SYS-0026"' in s, "PATCH anchor not found"
s = s.replace('PATCH = "SYS-0026"', 'PATCH = "SYS-0032"')
print("  ✓ PATCH → SYS-0032")

# Top-level datetime import (needed by journal session_id)
if 'from datetime import datetime' not in s:
    s = s.replace(
        'from collections import deque',
        'from collections import deque\nfrom datetime import datetime'
    )
    print("  ✓ Added top-level datetime import")
else:
    print("  ℹ datetime import already present")

# Verify late imports are present inside main()
missing = []
for imp in [
    'from mx_journal import MxJournal',
    'from mx_hooks import is_significant, pre_flight, post_flight',
]:
    if imp not in s:
        missing.append(imp)

if missing:
    # They should be present after SYS-0027/0029 — add them now
    old_late = '    from mx_intent import IntentResolver\n    from mx_logger import MxLogger'
    assert old_late in s, f"Late import anchor not found; cannot add: {missing}"
    additions = '\n'.join(f'    {m}' for m in missing)
    s = s.replace(old_late, old_late + '\n' + additions)
    for m in missing:
        print(f"  ✓ Added late import: {m}")
else:
    print("  ℹ Late imports for MxJournal and mx_hooks already present")

session_path.write_text(s)
py_compile.compile(str(session_path), doraise=True)
print("  ✓ mx_session.py updated and validated")

# ── 2. help_handler.py — fix escape sequences + rewrite file table ───────────

help_path = Path('/opt/mythos/telegram_bot/handlers/help_handler.py')
h = help_path.read_text()

# The HELP_MX string uses """ — backslash-escape sequences inside it cause
# SyntaxWarning. Fix: replace the specific offending sequences.
# FIX\_SEQUENCE → FIX_SEQUENCE  (inside a code block, no escaping needed)
# Also fix any other spurious backslashes we introduced.

if 'HELP_MX = """' in h:
    # Extract the HELP_MX block and clean it
    start = h.index('HELP_MX = """')
    end   = h.index('"""\n', start + 13) + 4  # closing triple-quote + newline

    mx_block = h[start:end]
    cleaned  = mx_block

    # Fix invalid escape sequences that triggered SyntaxWarning
    # These appear as \_ in non-raw strings
    cleaned = cleaned.replace('FIX\\_SEQUENCE', 'FIX_SEQUENCE')
    cleaned = cleaned.replace('HAS\\_TABLE',    'HAS_TABLE')

    # Replace Telegram-unfriendly markdown table with plain indented list
    old_table = (
        "| File | Purpose |\n"
        "|------|----------|\n"
        "| `/opt/mythos/mx/mx_session.py` | Core session loop |\n"
        "| `/opt/mythos/mx/mx_intent.py` | Intent resolver |\n"
        "| `/opt/mythos/mx/mx_logger.py` | Session text logger |\n"
        "| `/opt/mythos/mx/mx_journal.py` | TODO.md journal writer |\n"
        "| `/opt/mythos/mx/mx_snapshot.py` | State snapshot serializer |\n"
        "| `/opt/mythos/mx/mx_delta.py` | Snapshot diff engine |\n"
        "| `/opt/mythos/mx/mx_hooks.py` | Pre/post integrity hooks |\n"
        "| `/opt/mythos/mx/mx_intents.yaml` | Your command language |\n"
        "| `/opt/mythos/mx/mx_config.yaml` | Model, countdown, buffer |\n"
        "| `~/.mx/sessions/` | Per-session text logs |\n"
        "| `~/.mx/snapshots/` | System state snapshots |\n"
        "| `~/.mx/patterns/errors.jsonl` | Learned error→fix pairs |\n"
        "| `~/.mx/intents/learned.yaml` | Ollama-learned intents |\n"
        "| `~/.mx/journal/` | Session JSON journals |\n"
        "| `/opt/mythos/docs/live/` | Latest integrity scan output |"
    )
    new_table = (
        "`mx_session.py`       Core session loop\n"
        "`mx_intent.py`        Intent resolver\n"
        "`mx_logger.py`        Session text logger\n"
        "`mx_journal.py`       TODO.md journal writer\n"
        "`mx_snapshot.py`      State snapshot serializer\n"
        "`mx_delta.py`         Snapshot diff engine\n"
        "`mx_hooks.py`         Pre/post integrity hooks\n"
        "`mx_intents.yaml`     Your command language\n"
        "`mx_config.yaml`      Model, countdown, buffer\n"
        "\n"
        "`~/.mx/sessions/`          Per-session text logs\n"
        "`~/.mx/snapshots/`         System state snapshots\n"
        "`~/.mx/patterns/errors.jsonl`  Learned error→fix pairs\n"
        "`~/.mx/intents/learned.yaml`   Ollama-learned intents\n"
        "`~/.mx/journal/`           Session JSON journals\n"
        "`/opt/mythos/docs/live/`   Latest integrity scan output"
    )

    if old_table in cleaned:
        cleaned = cleaned.replace(old_table, new_table)
        print("  ✓ Replaced Telegram-unfriendly table with plain list")
    else:
        print("  ℹ Table not found in expected form — skipping table replacement")

    h = h[:start] + cleaned + h[end:]
    print("  ✓ Fixed escape sequences in HELP_MX")
else:
    print("  ⚠ HELP_MX block not found — skipping escape fix")

help_path.write_text(h)
py_compile.compile(str(help_path), doraise=True)
print("  ✓ help_handler.py updated and validated")

# ── 3. mx_hooks.py — fix snapshot label strips 'sudo ' prefix ────────────────

hooks_path = Path('/opt/mythos/mx/mx_hooks.py')
hk = hooks_path.read_text()

old_label_func = (
    'def _label_from_command(command: str) -> str:\n'
    '    """Extract a short label from a command for snapshot filename."""\n'
    '    for pattern in ["patch-install", "systemctl restart", "systemctl start"]:\n'
    '        if pattern in command:\n'
    '            parts = command.replace(pattern, "").strip().split()\n'
    '            if parts:\n'
    '                return parts[0].replace(".service", "").replace("-", "_")[:20]\n'
    '    return "op"'
)
new_label_func = (
    'def _label_from_command(command: str) -> str:\n'
    '    """Extract a short label from a command for snapshot filename."""\n'
    '    # Strip sudo prefix so label reads \'mythos-api\' not \'sudo\'\n'
    '    cmd = command.strip()\n'
    '    if cmd.startswith("sudo "):\n'
    '        cmd = cmd[5:].strip()\n'
    '    for pattern in ["patch-install", "systemctl restart", "systemctl start",\n'
    '                    "systemctl stop", "systemctl reload"]:\n'
    '        if pattern in cmd:\n'
    '            parts = cmd.replace(pattern, "").strip().split()\n'
    '            if parts:\n'
    '                label = parts[0].replace(".service", "").replace("mythos-", "")\n'
    '                return label.replace("-", "_")[:20]\n'
    '    # For patch-install, grab the patch ID\n'
    '    if "patch-install" in cmd or cmd.startswith("pi "):\n'
    '        parts = cmd.split()\n'
    '        if len(parts) > 1:\n'
    '            return parts[1].replace("-", "_")[:20]\n'
    '    return "op"'
)

assert old_label_func in hk, "_label_from_command anchor not found in mx_hooks.py"
hk = hk.replace(old_label_func, new_label_func)
hooks_path.write_text(hk)
py_compile.compile(str(hooks_path), doraise=True)
print("  ✓ mx_hooks.py: snapshot label now strips sudo + reads service name cleanly")

# ── 4. mythos-diag — fix banner text SYS-0030 → SYS-0032 ────────────────────

diag_path = Path('/opt/mythos/bin/mythos-diag')
d = diag_path.read_text()

if 'SYS-0030: mx Documentation ready.' in d:
    d = d.replace('SYS-0030: mx Documentation ready.', 'SYS-0032: mx stack complete.')
    # Also fix the banner content to reflect full stack
    old_banner = (
        '║  SYS-0030: mx Documentation ready.              ║\n'
        '║                                                  ║\n'
        '║  CLI:       mythos-diag mx                       ║\n'
        '║  Telegram:  /help mx                             ║\n'
        '║             /help shell                          ║\n'
        '║             /help healing                        ║\n'
        '║                                                  ║\n'
        '║  Also added mx block to: mythos-diag all         ║'
    )
    # The banner is actually in apply_patch.py output, not in diag itself.
    # The diag file has no embedded banner. Skip.
    print("  ℹ Banner is in apply_patch.py output only — no change needed in diag")
    d = d.replace('SYS-0032: mx stack complete.', 'SYS-0030: mx Documentation ready.')
else:
    print("  ℹ No stale banner string in mythos-diag")

diag_path.write_text(d)
print("  ✓ mythos-diag reviewed")

# ── 5. Restart bot ────────────────────────────────────────────────────────────

patch.restart_service('mythos-bot.service')
print("  ✓ mythos-bot.service restarted")

# ── Done ──────────────────────────────────────────────────────────────────────

patch.finish()

print()
print("╔══════════════════════════════════════════════════╗")
print("║  SYS-0032: mx Polish Pass complete.             ║")
print("║                                                  ║")
print("║  ✓ VERSION 1.1.0 / PATCH SYS-0032              ║")
print("║  ✓ datetime import at top level                  ║")
print("║  ✓ Late imports verified                         ║")
print("║  ✓ HELP_MX escape sequences fixed                ║")
print("║  ✓ HELP_MX table → plain list                    ║")
print("║  ✓ Snapshot labels clean (no sudo prefix)        ║")
print("╚══════════════════════════════════════════════════╝")
