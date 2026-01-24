# Mythos Project TODO & Roadmap

> **Last Updated:** 2026-01-24 08:45 EST
> **Current Focus:** Finance System + Patch Infrastructure

---

## 📖 About This Document

**TODO.md is the living work journal.** It is updated constantly during work sessions.

| Document | Purpose | Update Frequency |
|----------|---------|------------------|
| `TODO.md` | What we're trying to do | Every work session |
| `ARCHITECTURE.md` | What actually exists and works | Only at stable milestones |

**Rules:**
- Update Active Work section as status changes
- Move items to Completed when done (never delete)
- Add new ideas to Backlog or Ideas section
- Only update ARCHITECTURE.md when a feature is stable and deployed

---

## 🔥 Active Work

### Finance System (patch_0015)
- **Status:** Patch installed, testing in progress
- **Files:** `/opt/mythos/finance/`
- **What:** Bank CSV import system (USAA + Sunmark), category mapping, reports CLI
- **Next:** Test imports, verify category mappings, add Telegram commands

### Patch System Telegram Commands
- **Status:** Fixed - switched from Markdown to HTML formatting
- **Files:** `/opt/mythos/telegram_bot/handlers/patch_handlers.py`
- **What:** `/patch_status` was failing due to underscore characters breaking Markdown parsing
- **Resolution:** Changed all `parse_mode='Markdown'` to `parse_mode='HTML'`, converted `**bold**` to `<b>bold</b>`, converted `` `code` `` to `<code>code</code>`
- **Next:** Verify all patch commands work with HTML formatting

### Project Documentation (patch_0016)
- **Status:** In progress
- **Files:** `/opt/mythos/docs/TODO.md`, `/opt/mythos/docs/ARCHITECTURE.md`
- **What:** Persistent project tracking that travels with git
- **Next:** Deploy patch, verify docs are committed to GitHub

---

## 📋 Backlog (Not Started)

### Finance - Telegram Integration
- Add `/finance` command group to bot
- `/finance summary` - quick balance overview
- `/finance recent` - last 10 transactions
- `/finance search <term>` - find transactions

### Finance - Recurring Detection
- Auto-detect recurring transactions (subscriptions, bills)
- Flag new recurring patterns
- Monthly recurring summary

### Finance - Budget Alerts
- Set category budgets
- Alert when approaching/exceeding limits
- Weekly spending digest

### Sales Intake System
- Photo analysis via Ollama for item identification
- Marketplace listing generation
- Inventory tracking

### Improved Error Reporting
- Global error handler should capture full stack traces
- Log errors to file with context
- `/error_log` command to view recent errors

### Bot Service Logging
- Redirect stdout/stderr to log file
- Add log rotation
- `/bot_log` command for recent logs

---

## ✅ Completed

### 2026-01-24
- [x] Diagnosed `/patch_status` Markdown parsing failure
- [x] Root cause: underscores in filenames interpreted as italic markers
- [x] Fix: Switched all patch handlers to HTML parse mode
- [x] Created project documentation system (TODO.md, ARCHITECTURE.md)
- [x] Documented diagnostic workflow pattern

### 2026-01-23
- [x] Patch system installed (patch_0010 through patch_0015)
- [x] Auto-detect and install patches from ~/Downloads
- [x] Git versioning with pre/post tags
- [x] GitHub push on each patch
- [x] Telegram commands for patch management
- [x] Finance system schema with 100+ category mappings
- [x] USAA and Sunmark CSV parsers
- [x] Import script with duplicate detection

---

## 💡 Ideas (Unplanned)

- Web dashboard for finance data
- Scheduled reports via Telegram
- Integration with actual bank APIs (Plaid?)
- Receipt photo scanning and matching to transactions
- Voice commands via Telegram voice messages
- Local LLM for transaction categorization suggestions

---

## 🔧 Workflows & Patterns

### Diagnostic Dump Pattern

When Claude needs information from Arcturus, it provides a single copy-paste command block that:
1. Clears `~/diag.txt`
2. Runs diagnostic commands, appending output with headers
3. Copies result to clipboard via `xclip`

**Standard format:**
```bash
D=~/diag.txt; > "$D"
echo "=== SECTION HEADER ===" >> "$D"
<command> >> "$D" 2>&1
echo -e "\n\n=== NEXT SECTION ===" >> "$D"
<command> >> "$D" 2>&1
cat "$D" | xclip -selection clipboard && echo "✓ Copied to clipboard"
```

**Key points:**
- `D=~/diag.txt; > "$D"` - Sets variable and truncates file (creates if doesn't exist)
- Each section has a clear header
- `2>&1` captures both stdout and stderr
- Final line copies to clipboard for easy paste back to Claude
- User can also `cat ~/diag.txt` or open in VS Code if preferred

**Example diagnostic block:**
```bash
D=~/diag.txt; > "$D"
echo "=== SERVICE STATUS ===" >> "$D"
sudo systemctl status mythos-bot.service >> "$D" 2>&1
echo -e "\n\n=== RECENT LOGS ===" >> "$D"
journalctl -u mythos-bot.service -n 50 --no-pager >> "$D" 2>&1
echo -e "\n\n=== PROCESS CHECK ===" >> "$D"
pgrep -af mythos >> "$D" 2>&1
cat "$D" | xclip -selection clipboard && echo "✓ Copied to clipboard"
```

### Patch Deployment Pattern

1. Claude creates patch files in `/home/claude/patch_NNNN_description/`
2. Claude zips and copies to `/mnt/user-data/outputs/`
3. User downloads zip to local machine
4. User copies zip to `~/Downloads` on Arcturus
5. Patch monitor auto-detects, extracts, versions, installs, pushes to GitHub
6. User verifies via `/patch_status` in Telegram

### Manual File Deployment (Non-Patch)

For quick fixes that don't need full patch versioning:
```bash
# Download file from Claude to local machine
# Copy to Arcturus
scp ~/Downloads/file.py arcturus:/opt/mythos/path/

# Or if already on Arcturus
cp ~/Downloads/file.py /opt/mythos/path/

# Restart relevant service
sudo systemctl restart mythos-bot.service
```

### Conversation Continuity Pattern

When starting a new Claude conversation about Mythos:
1. Claude should check for `/opt/mythos/docs/TODO.md` to see current state
2. Claude should check for `/opt/mythos/docs/ARCHITECTURE.md` to understand system
3. User provides context: "continuing work on [topic]" or "let's pick up where we left off"
4. Claude can request diagnostic dump if needed to verify current state

---

## 📝 Notes

- Bot runs as systemd service: `mythos-bot.service`
- Patch monitor runs as systemd service: `mythos-patch-monitor.service`
- All patches should be named: `patch_NNNN_description.zip`
- Finance CSVs go in: `/opt/mythos/finance/accounts/`
- Diagnostic file: `~/diag.txt` (overwritten each diagnostic run)
- Never delete TODO items - mark completed or move to "Dropped" section

---

## ❌ Dropped (Abandoned Ideas)

*Nothing dropped yet - this section holds ideas we explicitly decided not to pursue*

---

*This file is auto-committed with each patch. Never delete items - mark as completed or move to Dropped section if abandoned.*
