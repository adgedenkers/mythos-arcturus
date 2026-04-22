# AutoDoc2 — Next Patch Spec

> This file is rewritten wholesale after every feature patch lands.
> It always describes exactly one patch ahead.
> Run `mythos-handoff autodoc2` to get the full context payload.

---

## Patch: SYS-next — AutoDoc2 Letter F — Telegram `/autodoc` commands

**Letter:** F
**Stream:** SYS
**Patch type:** MINOR
**Blast radius:** Low — new bot commands only, no schema, no services

**Status:** DEFERRED — not blocking anything. The Iris skill (Letter E)
handles natural-language codebase queries from Telegram already. Letter F
adds convenience `/autodoc` slash commands.

---

## Scope

Wire three commands into `mythos_bot.py`:

| Command | Handler | Action |
|---------|---------|--------|
| `/autodoc` | `autodoc_status` | Show last crawl date, file count, language breakdown from Neo4j |
| `/autodoc crawl` | `autodoc_crawl` | Trigger `mythos-autodoc2-crawl.service` via systemctl |
| `/autodoc query <question>` | `autodoc_query` | Run query through `Autodoc2QuerySkill` and return summary |

**Files to modify:**

| File | Change |
|------|--------|
| `/opt/mythos/telegram_bot/handlers/autodoc_handler.py` | New — three command handlers |
| `/opt/mythos/telegram_bot/mythos_bot.py` | Two edits: import + `add_handler` call |

---

## Pre-build diagnostic

Before building this patch, read the live bot handler registration pattern:

```bash
D=~/diag.txt; > "$D"
echo "=== STREAMS ===" >> "$D"
mythos-diag streams >> "$D" 2>&1
echo -e "\n\n=== BOT MAIN ===" >> "$D"
cat /opt/mythos/telegram_bot/mythos_bot.py >> "$D" 2>&1
echo -e "\n\n=== HANDLERS __INIT__ ===" >> "$D"
cat /opt/mythos/telegram_bot/handlers/__init__.py >> "$D" 2>&1
echo -e "\n\n=== SAMPLE HANDLER ===" >> "$D"
head -60 /opt/mythos/telegram_bot/handlers/finance_handler.py >> "$D" 2>&1
cat "$D" | xclip -selection clipboard && echo "✓ Copied"
```

---

## Handler implementation notes

`autodoc_status` — query Neo4j directly (same pattern as `step_verify_graph_coverage`):
```python
MATCH (c:AutodocCrawl) RETURN c.target, c.file_count, c.finished_at, c.status
ORDER BY c.finished_at DESC LIMIT 3
```

`autodoc_crawl` — trigger the systemd service:
```python
subprocess.run(['sudo', '-n', '/usr/local/libexec/mythos/mythos-servicectl',
                'start', 'mythos-autodoc2-crawl.service'], ...)
```

`autodoc_query` — instantiate `Autodoc2QuerySkill` and call `execute()`:
```python
import sys; sys.path.insert(0, '/opt/mythos/skills')
from data.autodoc2_query import Autodoc2QuerySkill
```

---

## Registration pattern (two edits to mythos_bot.py)

Both use `patch.str_replace()`. Get exact anchors from the diagnostic dump
before writing these — never guess.

Edit 1 — import (at top of file, near other handler imports):
```python
from .handlers.autodoc_handler import autodoc_status, autodoc_crawl, autodoc_query
```

Edit 2 — add_handler (inside `main()`, near other command registrations):
```python
application.add_handler(CommandHandler("autodoc", autodoc_status))
application.add_handler(MessageHandler(
    filters.Regex(r'^/autodoc crawl'), autodoc_crawl))
application.add_handler(MessageHandler(
    filters.Regex(r'^/autodoc query'), autodoc_query))
```

---

## Verification

After install:
```bash
# Check handler file exists
ls -la /opt/mythos/telegram_bot/handlers/autodoc_handler.py

# Check bot picked it up (restart and check logs)
sudo systemctl restart mythos-bot.service
journalctl -u mythos-bot.service -n 20 --no-pager

# Test in Telegram
/autodoc
/autodoc query what files import neo4j
```
