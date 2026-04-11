"""
SYS-0030: mx Documentation
- Adds `mx` block to mythos-diag (session log, snapshots, patterns, health)
- Adds `mythos-diag mx` shorthand
- Adds HELP_MX to help_handler.py + registers topic aliases
- Updates /help diag to mention mx block
- Updates /help main to mention mx
"""

import py_compile
import sys
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=30,
    description='mx documentation - diag block and telegram help',
    patch_type='MINOR',
)
patch.begin()

# ── 1. Patch mythos-diag ──────────────────────────────────────────────────────

diag_path = Path('/opt/mythos/bin/mythos-diag')
diag = diag_path.read_text()

# A. Add block_mx() function before block_summary()
MX_BLOCK = r'''
block_mx() {
    header "MX SHELL SESSION"

    # Session log — last 5 entries from TODO.md Session Log section
    if grep -q "## 🗂️ Session Log" /opt/mythos/docs/TODO.md 2>/dev/null; then
        echo -e "  ${DIM}Recent sessions (from TODO.md):${RESET}"
        awk '/^## 🗂️ Session Log/{found=1; next} found && /^### /{count++; if(count>5) exit; print "  " $0; next} found && count>0 && /^(Commands|Patches|Services|Delta|⚠)/{print "    " $0}' \
            /opt/mythos/docs/TODO.md 2>/dev/null || echo "    (none yet)"
    else
        warn "No session log in TODO.md yet — run mx and exit a session first"
    fi

    echo ""

    # Snapshot count
    SNAP_DIR="$HOME/.mx/snapshots"
    if [[ -d "$SNAP_DIR" ]]; then
        snap_count=$(ls "$SNAP_DIR"/*.json 2>/dev/null | wc -l)
        latest_snap=$(ls -1t "$SNAP_DIR"/*.json 2>/dev/null | head -1)
        ok "Snapshots: ${snap_count} stored in ~/.mx/snapshots/"
        if [[ -n "$latest_snap" ]]; then
            snap_ts=$(python3 -c "import json; d=json.load(open('$latest_snap')); print(d.get('ts','?')[:19])" 2>/dev/null || echo "?")
            snap_trigger=$(python3 -c "import json; d=json.load(open('$latest_snap')); print(d.get('trigger','?'))" 2>/dev/null || echo "?")
            echo -e "    ${DIM}Latest: ${snap_ts} (${snap_trigger})${RESET}"
        fi
    else
        warn "No snapshots yet — ~/.mx/snapshots/ not found"
    fi

    echo ""

    # Learned error patterns
    ERRORS_FILE="$HOME/.mx/patterns/errors.jsonl"
    if [[ -f "$ERRORS_FILE" ]]; then
        pattern_count=$(wc -l < "$ERRORS_FILE" 2>/dev/null || echo 0)
        ok "Learned error patterns: ${pattern_count}"
        if [[ "$pattern_count" -gt 0 ]]; then
            echo -e "  ${DIM}Most recent fixes:${RESET}"
            python3 -c "
import json
lines = open('$ERRORS_FILE').readlines()
for line in reversed(lines[-3:]):
    try:
        d = json.loads(line)
        cmd = d.get('failed_command','?')[:45]
        fix = d.get('fix_command','?')[:45]
        print(f'    {cmd}')
        print(f'      → {fix}')
    except: pass
" 2>/dev/null || true
        fi
    else
        warn "No learned patterns yet — ~/.mx/patterns/errors.jsonl not found"
    fi

    echo ""

    # Learned intents
    LEARNED_FILE="$HOME/.mx/intents/learned.yaml"
    if [[ -f "$LEARNED_FILE" ]]; then
        intent_count=$(grep -c "command:" "$LEARNED_FILE" 2>/dev/null || echo 0)
        ok "Learned intents: ${intent_count} in ~/.mx/intents/learned.yaml"
    else
        echo -e "  ${DIM}Learned intents: none yet${RESET}"
    fi

    echo ""

    # Latest integrity scan
    INTEGRITY_REPORT="/opt/mythos/docs/live/integrity-scan-latest.json"
    if [[ -f "$INTEGRITY_REPORT" ]]; then
        python3 -c "
import json, os
from datetime import datetime
d = json.load(open('$INTEGRITY_REPORT'))
mtime = os.path.getmtime('$INTEGRITY_REPORT')
age = datetime.now() - datetime.fromtimestamp(mtime)
mins = int(age.total_seconds() / 60)
age_str = f'{mins}min ago' if mins < 60 else f'{int(mins/60)}h ago'
svcs = d.get('services', {})
tables = d.get('tables', {})
files = d.get('files', {})
h = svcs.get('healthy', '?')
u = svcs.get('unhealthy', 0)
t = tables.get('tables_found', '?')
m = files.get('files_missing', 0)
status = '✓' if not u and not m else '⚠'
print(f'  {status} Integrity scan ({age_str}): {h} services healthy, {t} tables, {m} files missing')
if u:
    print(f'    ⚠ {u} services unhealthy')
if m:
    print(f'    ⚠ {m} files missing')
" 2>/dev/null || warn "Could not read integrity report"
    else
        warn "No integrity scan yet — run: /iris_integrity scan"
    fi

    echo ""

    # mx intents file status
    INTENTS="/opt/mythos/mx/mx_intents.yaml"
    if [[ -f "$INTENTS" ]]; then
        intent_count=$(grep -c "command:" "$INTENTS" 2>/dev/null || echo "?")
        ok "Intent registry: ${intent_count} intents in mx_intents.yaml"
    fi

    # Journal count
    JOURNAL_DIR="$HOME/.mx/journal"
    if [[ -d "$JOURNAL_DIR" ]]; then
        journal_count=$(ls "$JOURNAL_DIR"/*.json 2>/dev/null | wc -l)
        ok "Session journals: ${journal_count} in ~/.mx/journal/"
    fi
}

'''

# Insert block_mx before block_summary
old_anchor = "block_summary() {"
assert old_anchor in diag, "block_summary anchor not found in mythos-diag"
diag = diag.replace(old_anchor, MX_BLOCK + old_anchor)
print("  ✓ Added block_mx() to mythos-diag")

# B. Add 'mx' to the dispatch case statement
old_dispatch = "        redis)     block_redis ;;"
new_dispatch = (
    "        redis)     block_redis ;;\n"
    "        mx)        block_mx ;;"
)
assert old_dispatch in diag, "dispatch anchor not found"
diag = diag.replace(old_dispatch, new_dispatch)
print("  ✓ Added mx) dispatch case")

# C. Add mx to help text
old_help_redis = '  echo "  mythos-diag redis        Redis keyspace detail"'
new_help_redis = (
    '  echo "  mythos-diag redis        Redis keyspace detail"\n'
    '  echo "  mythos-diag mx           mx shell session status"'
)
assert old_help_redis in diag, "help redis anchor not found"
diag = diag.replace(old_help_redis, new_help_redis)
print("  ✓ Added mx to help text")

# D. Add mx block to 'all' output
old_all = "    block_redis"
new_all = "    block_redis\n    block_mx"
# Only replace the one inside the 'all' case
assert old_all in diag, "all block anchor not found"
diag = diag.replace(old_all, new_all, 1)
print("  ✓ Added block_mx to 'all' output")

diag_path.write_text(diag)
print("  ✓ mythos-diag updated")

# ── 2. Patch help_handler.py ──────────────────────────────────────────────────

help_path = Path('/opt/mythos/telegram_bot/handlers/help_handler.py')
help_content = help_path.read_text()

# A. Add HELP_MX constant before HELP_TOPICS
HELP_MX_CONSTANT = '''
# ---------------------------------------------------------------------------
# mx Shell Session
# ---------------------------------------------------------------------------
HELP_MX = """🖥️ **mx — Mythos Shell Session**
Self-healing, intent-aware terminal session for Arcturus.
Installed: SYS-0026 through SYS-0030

━━━━━━━━━━━━━━━━━━━━━━━━
**STARTING A SESSION**
━━━━━━━━━━━━━━━━━━━━━━━━
```
mx                     Start session (asks for intent)
mx --model llama3.2:3b Use specific Ollama model
mx --no-heal           Intent resolution only, no healing
mx --version           Show version
```

━━━━━━━━━━━━━━━━━━━━━━━━
**INTENT RESOLUTION**
━━━━━━━━━━━━━━━━━━━━━━━━
Terse phrases resolve to real commands automatically:
```
api restart       → sudo systemctl restart mythos-api.service
api logs          → journalctl -u mythos-api.service -f -n 50
bot restart       → sudo systemctl restart mythos-bot.service
services          → systemctl list-units | grep mythos
streams           → show stream patch counters
pi SYS-0031       → patch-install SYS-0031
pi SYS-0031 -dry  → patch-install SYS-0031 --dry-run
pi SYS-0031 -c    → patch-install SYS-0031 --clip
db balances       → psql query for account balances
db tables         → psql table listing
seraphe lunar     → seraphe lunar report
adge transits     → adge transit report
diag              → mythos-diag streams
todo              → cat TODO.md (head)
```
Edit: `/opt/mythos/mx/mx_intents.yaml`
Unknown phrases → Ollama resolves → auto-saved for next time

━━━━━━━━━━━━━━━━━━━━━━━━
**SELF-HEALING**
━━━━━━━━━━━━━━━━━━━━━━━━
When a command fails:
1. Checks `~/.mx/patterns/errors.jsonl` for known fix (instant)
2. If unknown → sends last 10 commands + error to Ollama
3. Ollama returns: FIX / FIX\\_SEQUENCE / ASK / EXPLAIN
4. Shows fix with 3s countdown → runs it
5. If fix fails → loops up to 3 attempts with updated context
6. Successful fixes stored → learned instantly

Dangerous commands (`rm -rf`, `DROP TABLE`, etc.) always require explicit `yes` confirmation.

━━━━━━━━━━━━━━━━━━━━━━━━
**PRE/POST INTEGRITY HOOKS**
━━━━━━━━━━━━━━━━━━━━━━━━
Significant operations trigger automatic wrapping:
• `patch-install`, `systemctl restart`, `psql` migrations
• `ALTER TABLE`, `CREATE TABLE`, `DROP TABLE`

Each significant command:
1. 📸 Pre-flight integrity scan (services + tables)
2. 📸 Pre-operation snapshot → `~/.mx/snapshots/`
3. Executes command (healing if needed)
4. 📸 Post-operation integrity scan
5. 📸 Post-operation snapshot
6. Delta report — additions / changes / regressions / neutral
7. ⚠ Rollback offer if regressions detected

━━━━━━━━━━━━━━━━━━━━━━━━
**SESSION JOURNAL**
━━━━━━━━━━━━━━━━━━━━━━━━
On exit, mx writes a summary to `docs/TODO.md`:
• Intent declared at session start
• Commands run, failures healed, duration
• Patches deployed, services restarted
• Delta summary

Journal files: `~/.mx/journal/`

━━━━━━━━━━━━━━━━━━━━━━━━
**IRIS INTEGRITY**
━━━━━━━━━━━━━━━━━━━━━━━━
`/iris_integrity` — Health from last scan
`/iris_integrity scan` — Run fast scan (services + tables)
`/iris_integrity full` — Full scan including files (~60s)
`/iris_integrity context` — What Iris carries in awareness

━━━━━━━━━━━━━━━━━━━━━━━━
**FILES**
━━━━━━━━━━━━━━━━━━━━━━━━
| File | Purpose |
|------|---------|
| `/opt/mythos/mx/mx_session.py` | Core session loop |
| `/opt/mythos/mx/mx_intent.py` | Intent resolver |
| `/opt/mythos/mx/mx_logger.py` | Session text logger |
| `/opt/mythos/mx/mx_journal.py` | TODO.md journal writer |
| `/opt/mythos/mx/mx_snapshot.py` | State snapshot serializer |
| `/opt/mythos/mx/mx_delta.py` | Snapshot diff engine |
| `/opt/mythos/mx/mx_hooks.py` | Pre/post integrity hooks |
| `/opt/mythos/mx/mx_intents.yaml` | Your command language |
| `/opt/mythos/mx/mx_config.yaml` | Model, countdown, buffer |
| `~/.mx/sessions/` | Per-session text logs |
| `~/.mx/snapshots/` | System state snapshots |
| `~/.mx/patterns/errors.jsonl` | Learned error→fix pairs |
| `~/.mx/intents/learned.yaml` | Ollama-learned intents |
| `~/.mx/journal/` | Session JSON journals |
| `/opt/mythos/docs/live/` | Latest integrity scan output |

━━━━━━━━━━━━━━━━━━━━━━━━
**CLI DIAGNOSTICS**
━━━━━━━━━━━━━━━━━━━━━━━━
`mythos-diag mx` — Full mx system status
`mythos-diag mx` shows: recent sessions, snapshots, learned patterns, learned intents, integrity scan age, journal count.
"""

'''

old_topics_anchor = "# ---------------------------------------------------------------------------\n# Topic aliases for flexible matching\n# ---------------------------------------------------------------------------"
assert old_topics_anchor in help_content, "HELP_TOPICS anchor not found"
help_content = help_content.replace(old_topics_anchor, HELP_MX_CONSTANT + old_topics_anchor)
print("  ✓ Added HELP_MX constant")

# B. Add mx to HELP_TOPICS dict
old_topics_end = "    # System\n    'system': HELP_SYSTEM,"
new_topics_end = (
    "    # mx shell\n"
    "    'mx': HELP_MX,\n"
    "    'shell': HELP_MX,\n"
    "    'terminal': HELP_MX,\n"
    "    'heal': HELP_MX,\n"
    "    'healing': HELP_MX,\n"
    "    'intent': HELP_MX,\n"
    "    'snapshot': HELP_MX,\n"
    "    'delta': HELP_MX,\n"
    "    # System\n"
    "    'system': HELP_SYSTEM,"
)
assert old_topics_end in help_content, "HELP_TOPICS system anchor not found"
help_content = help_content.replace(old_topics_end, new_topics_end)
print("  ✓ Added mx topic aliases to HELP_TOPICS")

# C. Add mx to TOPIC_LIST
old_topic_list = "    'consciousness',\n]))"
new_topic_list = "    'consciousness',\n    'mx',\n]))"
assert old_topic_list in help_content, "TOPIC_LIST anchor not found"
help_content = help_content.replace(old_topic_list, new_topic_list)
print("  ✓ Added mx to TOPIC_LIST")

# D. Add mx entry to HELP_MAIN overview
old_help_main_system = '**⚙️ SYSTEM** → `/help system`\nModes, models, patches, services'
new_help_main_system = (
    '**⚙️ SYSTEM** → `/help system`\n'
    'Modes, models, patches, services\n'
    '**🖥️ MX SHELL** → `/help mx`\n'
    'Self-healing terminal, intent resolution, integrity hooks'
)
assert old_help_main_system in help_content, "HELP_MAIN system anchor not found"
help_content = help_content.replace(old_help_main_system, new_help_main_system)
print("  ✓ Added mx entry to HELP_MAIN")

# E. Update HELP_DIAG to mention mx block
old_diag_tips = '• Great for quick health checks from your phone\n"""'
new_diag_tips = (
    '• Great for quick health checks from your phone\n'
    '• `mythos-diag mx` — mx session status, snapshots, learned patterns\n'
    '"""'
)
assert old_diag_tips in help_content, "HELP_DIAG tips anchor not found"
help_content = help_content.replace(old_diag_tips, new_diag_tips)
print("  ✓ Updated HELP_DIAG with mx block mention")

# F. Add mx to HELP_DIAG blocks list
old_diag_blocks = '`patches` — Version, tags, patches'
new_diag_blocks = (
    '`patches` — Version, tags, patches\n'
    '`mx` — mx session status, snapshots, patterns, integrity'
)
assert old_diag_blocks in help_content, "HELP_DIAG blocks anchor not found"
help_content = help_content.replace(old_diag_blocks, new_diag_blocks)
print("  ✓ Added mx to HELP_DIAG block list")

help_path.write_text(help_content)
py_compile.compile(str(help_path), doraise=True)
print("  ✓ help_handler.py updated and validated")

# ── 3. Restart bot ────────────────────────────────────────────────────────────

patch.restart_service('mythos-bot.service')
print("  ✓ mythos-bot.service restarted")

# ── Done ──────────────────────────────────────────────────────────────────────

patch.finish()

print()
print("╔══════════════════════════════════════════════════╗")
print("║  SYS-0030: mx Documentation ready.              ║")
print("║                                                  ║")
print("║  CLI:       mythos-diag mx                       ║")
print("║  Telegram:  /help mx                             ║")
print("║             /help shell                          ║")
print("║             /help healing                        ║")
print("║                                                  ║")
print("║  Also added mx block to: mythos-diag all         ║")
print("╚══════════════════════════════════════════════════╝")
