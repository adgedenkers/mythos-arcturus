# Mythos System Architecture

> **Version:** 1.0.0
> **Last Updated:** 2026-01-24
> **Host:** arcturus (Ubuntu 24.04)

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ARCTURUS SERVER                                 │
│                          (Ubuntu 24.04 / x86_64)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │  Telegram Bot   │    │  Patch Monitor  │    │   Mythos API    │         │
│  │  (systemd)      │    │  (systemd)      │    │   (FastAPI)     │         │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘         │
│           │                      │                      │                   │
│           └──────────────────────┼──────────────────────┘                   │
│                                  │                                          │
│                    ┌─────────────┴─────────────┐                            │
│                    │                           │                            │
│              ┌─────┴─────┐              ┌──────┴──────┐                     │
│              │ PostgreSQL │              │    Neo4j    │                     │
│              │  (mythos)  │              │  (mythos)   │                     │
│              └───────────┘              └─────────────┘                     │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                                │
│  │     Ollama      │    │     GitHub      │                                │
│  │  (Local LLM)    │    │   (Remote)      │                                │
│  └─────────────────┘    └─────────────────┘                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```yaml
/opt/mythos/
├── .env                      # Environment variables (secrets)
├── .venv/                    # Python virtual environment
├── .git/                     # Git repository
│
├── docs/                     # Documentation
│   ├── TODO.md               # Project roadmap and status
│   └── ARCHITECTURE.md       # This file
│
├── telegram_bot/             # Telegram bot application
│   ├── mythos_bot.py         # Main bot entry point
│   └── handlers/             # Command handlers
│       ├── __init__.py
│       ├── patch_handlers.py # /patch_* commands
│       └── ...
│
├── finance/                  # Finance management system
│   ├── schema.sql            # Database schema
│   ├── parsers.py            # Bank CSV parsers
│   ├── import_transactions.py # Import script
│   ├── reports.py            # CLI reports
│   └── accounts/             # CSV files (gitignored)
│
├── patches/                  # Patch system
│   ├── archive/              # Processed patch zips
│   ├── logs/                 # Patch application logs (JSON)
│   ├── scripts/              # Patch utilities
│   │   ├── patch_apply.sh
│   │   └── patch_rollback.sh
│   └── patch_NNNN_*/         # Extracted patches
│
├── mythos_patch_monitor.py   # File watcher for auto-patching
│
└── backups/                  # Database backups (gitignored)
```

---

## Services

| Service | Type | Port | Description |
|---------|------|------|-------------|
| `mythos-bot.service` | systemd | - | Telegram bot (polling) |
| `mythos-patch-monitor.service` | systemd | - | Watches ~/Downloads for patches |
| `mythos-api.service` | systemd | 8000 | FastAPI REST API |
| `postgresql` | system | 5432 | Primary database |
| `neo4j` | system | 7474/7687 | Graph database |
| `ollama` | system | 11434 | Local LLM inference |

---

## Databases

### PostgreSQL: `mythos`

```yaml
Schemas:
  public:
    Tables:
      - users              # System users
      - conversations      # Chat sessions
      - messages           # Chat messages
      - discoveries        # Knowledge extractions
      
  finance:
    Tables:
      - accounts           # Bank accounts
      - transactions       # All transactions
      - categories         # Category definitions
      - category_patterns  # Auto-categorization rules
      - budgets            # Budget limits (planned)
```

### Neo4j: `mythos`

```yaml
Node Labels:
  - Soul              # Spiritual entities
  - Incarnation       # Physical manifestations
  - Lineage           # Spiritual lineages
  - Discovery         # Knowledge nodes
  - Concept           # Abstract concepts

Relationships:
  - INCARNATED_AS
  - BELONGS_TO_LINEAGE
  - CONNECTED_TO
  - DISCOVERED_IN
```

---

## Environment Variables

```yaml
# /opt/mythos/.env

# Telegram
TELEGRAM_BOT_TOKEN: Bot API token
TELEGRAM_ID_KA: Ka'tuar'el's Telegram ID
TELEGRAM_ID_SERAPHE: Seraphe's Telegram ID

# Database
DATABASE_URL: PostgreSQL connection string
NEO4J_URI: Neo4j bolt connection
NEO4J_USER: Neo4j username
NEO4J_PASSWORD: Neo4j password

# API
API_KEY_TELEGRAM_BOT: Internal API auth key

# LLM
OLLAMA_HOST: Ollama API endpoint
```

---

## Patch System Flow

```
1. User downloads patch_NNNN_description.zip to ~/Downloads
                          │
                          ▼
2. mythos-patch-monitor.service detects file
                          │
                          ▼
3. Create git tag: pre-patch-patch_NNNN-TIMESTAMP
                          │
                          ▼
4. Extract zip to /opt/mythos/patches/patch_NNNN_*/
                          │
                          ▼
5. Git commit extracted files
                          │
                          ▼
6. Create version tag: vX.Y.Z (auto-increment)
                          │
                          ▼
7. Push to GitHub (main branch + tags)
                          │
                          ▼
8. Execute install.sh (if present)
                          │
                          ▼
9. Archive zip to /opt/mythos/patches/archive/
                          │
                          ▼
10. Log result to /opt/mythos/patches/logs/
```

---

## Git Workflow

```yaml
Repository: github.com/adgedenkers/mythos-arcturus
Branch: main
Tags:
  - vX.Y.Z              # Version after patch applied
  - pre-patch-*         # Snapshot before patch
  - pre-rollback-*      # Snapshot before rollback

Ignored:
  - .env
  - .venv/
  - backups/
  - finance/accounts/   # Actual financial data
  - patches/archive/
  - __pycache__/
  - *.pyc
  - *.log
```

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `/opt/mythos/telegram_bot/mythos_bot.py` | Main Telegram bot |
| `/opt/mythos/telegram_bot/handlers/patch_handlers.py` | Patch management commands |
| `/opt/mythos/mythos_patch_monitor.py` | Auto-patch file watcher |
| `/opt/mythos/finance/import_transactions.py` | Bank CSV importer |
| `/opt/mythos/finance/reports.py` | Finance CLI reports |
| `/opt/mythos/.env` | All secrets and config |
| `/etc/systemd/system/mythos-bot.service` | Bot service definition |
| `/etc/systemd/system/mythos-patch-monitor.service` | Patch monitor service |

---

## Common Commands

```bash
# Services
sudo systemctl status mythos-bot.service
sudo systemctl restart mythos-bot.service
sudo systemctl status mythos-patch-monitor.service

# Logs
journalctl -u mythos-bot.service -f
tail -f /var/log/mythos_patch_monitor.log

# Git
cd /opt/mythos && git log --oneline -10
cd /opt/mythos && git tag -l --sort=-v:refname | head -10

# Finance
cd /opt/mythos/finance
python import_transactions.py accounts/file.csv --account-id 1 --dry-run
python reports.py summary

# Database
psql -d mythos -c "SELECT * FROM finance.transactions ORDER BY date DESC LIMIT 10;"
```

---

## Diagnostic Workflow

When troubleshooting with Claude, use the **diagnostic dump pattern**. Claude provides a single copy-paste command block that collects all needed info into `~/diag.txt` and copies to clipboard.

### Diagnostic File
- **Location:** `~/diag.txt`
- **Behavior:** Overwritten each diagnostic run (not appended)
- **Clipboard:** Auto-copied via `xclip -selection clipboard`

### Standard Diagnostic Block Format

```bash
D=~/diag.txt; > "$D"
echo "=== SECTION 1 ===" >> "$D"
<command1> >> "$D" 2>&1
echo -e "\n\n=== SECTION 2 ===" >> "$D"
<command2> >> "$D" 2>&1
cat "$D" | xclip -selection clipboard && echo "✓ Copied to clipboard"
```

### How It Works

| Component | Purpose |
|-----------|---------|
| `D=~/diag.txt` | Set variable for brevity |
| `> "$D"` | Truncate/create file (empty it) |
| `echo "=== HEADER ==="` | Section dividers for readability |
| `>> "$D"` | Append to file |
| `2>&1` | Capture both stdout and stderr |
| `xclip -selection clipboard` | Copy to system clipboard |

### Example: Service Troubleshooting

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

### Example: Patch System Check

```bash
D=~/diag.txt; > "$D"
echo "=== PATCH LOGS ===" >> "$D"
ls -la /opt/mythos/patches/logs/ >> "$D" 2>&1
echo -e "\n\n=== RECENT JSON LOG ===" >> "$D"
cat /opt/mythos/patches/logs/$(ls -t /opt/mythos/patches/logs/*.json | head -1) >> "$D" 2>&1
echo -e "\n\n=== GIT STATUS ===" >> "$D"
cd /opt/mythos && git status >> "$D" 2>&1
cat "$D" | xclip -selection clipboard && echo "✓ Copied to clipboard"
```

### After Running

1. Terminal shows `✓ Copied to clipboard`
2. Paste directly into Claude chat (Ctrl+V)
3. Or view locally: `cat ~/diag.txt` or open in VS Code

---

## Conversation Continuity

When starting a new Claude conversation about Mythos:

1. **Reference this documentation:**
   - Ask Claude to check `/opt/mythos/docs/TODO.md` for current project state
   - Ask Claude to check `/opt/mythos/docs/ARCHITECTURE.md` for system understanding

2. **Provide context:**
   - "Let's continue work on [feature]"
   - "Pick up where we left off with [topic]"
   - "Check the TODO for current status"

3. **If Claude needs verification:**
   - Claude will provide a diagnostic block
   - Run it, paste results
   - Claude will have full current state

### Quick Start for New Conversation

```
"I'm working on Mythos. Check /opt/mythos/docs/TODO.md and 
/opt/mythos/docs/ARCHITECTURE.md to see where we left off."
```

---

## Telegram Commands

### General
| Command | Description |
|---------|-------------|
| `/start` | Initialize session |
| `/help` | Show available commands |

### Patch Management
| Command | Description |
|---------|-------------|
| `/patch` | System overview |
| `/patch_status` | Current version and recent activity |
| `/patch_list` | Available patches |
| `/patch_apply <name>` | Apply a patch |
| `/patch_rollback` | Show rollback options |
| `/patch_rollback <tag>` | Initiate rollback |

### Finance (Planned)
| Command | Description |
|---------|-------------|
| `/finance` | Finance overview |
| `/finance summary` | Account balances |
| `/finance recent` | Recent transactions |

---

*This document is the authoritative architecture reference for the Mythos system.*
