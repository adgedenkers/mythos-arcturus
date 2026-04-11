# Mythos Patch System

**Version:** 2.0  
**Last Updated:** 2026-03-04  

---

## Overview

The Mythos Patch System deploys code changes to Arcturus through numbered, stream-organized patches. Each patch is a zip containing an `install.sh` that calls `apply_patch.py`, which uses `PatchBase` for all operations.

### Key Documents

| Document | Location | Purpose |
|----------|----------|---------|
| STREAMS.json | `/opt/mythos/docs/STREAMS.json` | Live stream counters (machine-readable) |
| STREAMS.md | `/opt/mythos/docs/STREAMS.md` | Stream ownership tables (human-readable) |
| PATCH_HISTORY.md | `/opt/mythos/docs/PATCH_HISTORY.md` | Every patch ever installed |
| ARCHITECTURE.md | `/opt/mythos/docs/ARCHITECTURE.md` | System reference (stable milestones) |
| TODO.md | `/opt/mythos/docs/TODO.md` | Active work and backlog |

---

## Streams

All development is organized into five named streams. Every patch belongs to exactly one.

| Prefix | Stream | Owns |
|--------|--------|------|
| NEU | NEURO | Consciousness, Iris core, Arcturian Grid, perception, memory formation |
| LOG | LOGOS | Skills, LLM orchestration, prompts, preprocessor, ontology |
| MNE | MNEMOS | Memory, documents, voice memos, backlog intelligence, life management |
| SEN | SENSUS | Astrology, calendar, email, weather, people, external integrations |
| SYS | SYSTEM | Finance, bot core, patches, services, infrastructure, routines |

Get live counters: `mythos-diag streams`

---

## Patch Naming

```
{STREAM}-{NNNN}_{description}.zip

Examples:
  SYS-0008_patchbase_logging.zip
  MNE-0003_stream_column.zip
  NEU-0001_awareness_loop.zip
```

Legacy format `patch_NNNN_description.zip` is still recognized (patches 0001-0199+).

---

## Patch Structure

```
MNE-0003_stream_column/
├── install.sh              ← 4 lines, calls apply_patch.py
├── apply_patch.py          ← all logic, uses PatchBase
└── opt/mythos/             ← files mirroring target paths
    ├── migrations/
    │   └── mne_0003_stream_column.sql
    └── telegram_bot/
        └── handlers/
            └── backlog_handler.py
```

### install.sh (always exactly this)

```bash
#!/bin/bash
set -e
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
/opt/mythos/.venv/bin/python3 "$PATCH_DIR/apply_patch.py"
```

### apply_patch.py (standard pattern)

```python
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='MNE',
    number=3,
    description='Stream column + backlog filtering',
    patch_type='MINOR',  # MAJOR, MINOR, PATCH
)
patch.begin()

patch.deploy_file('opt/mythos/some/file.py', '/opt/mythos/some/file.py')
patch.run_sql('opt/mythos/migrations/migration.sql')
patch.restart_service('mythos-bot.service')

patch.finish()  # bumps STREAMS.json, writes PATCH_HISTORY, writes logs
```

---

## PatchBase

Location: `/opt/mythos/patches/scripts/patch_base.py`

### Methods

| Method | What it does |
|--------|-------------|
| `begin()` | Prints header, starts timer, opens log |
| `deploy_file(source_rel, target_abs)` | Copies file from patch dir to target |
| `run_sql(sql_rel)` | Runs SQL file against mythos database |
| `restart_service(service_name)` | Restarts a systemd service |
| `finish()` | Bumps STREAMS.json, writes PATCH_HISTORY.md, writes logs |

### Structured Logging

Every patch writes two log files on `finish()`:

| File | Content |
|------|---------|
| `/tmp/{PATCH_ID}_output.log` | Human-readable (same as terminal output) |
| `/tmp/{PATCH_ID}_result.json` | Structured JSON (for graph ingestion, analysis) |
| `/tmp/last_patch_output.log` | Always points to most recent patch log |
| `/tmp/last_patch_result.json` | Always points to most recent patch JSON |

### Dry-Run Mode

When `MYTHOS_PATCH_DRY_RUN=1` is set:

- `deploy_file()` validates source exists, target is writable — does not copy
- `run_sql()` wraps migration in BEGIN/ROLLBACK — tests syntax without changing data
- `restart_service()` checks the systemd unit exists — does not restart
- `finish()` skips STREAMS.json bump and PATCH_HISTORY write

---

## Installing Patches

### patch-install command

```bash
patch-install MNE-0003                    # normal install
patch-install MNE-0003 --clip             # install + copy output to clipboard
patch-install MNE-0003 --dry-run          # validate without changes
patch-install MNE-0003 --dry-run --clip   # validate + copy to clipboard
```

What `patch-install` does:
1. Finds the matching zip in `~/Downloads/`
2. Archives the zip to `/opt/mythos/patches/archive/`
3. Extracts to `/opt/mythos/patches/{PATCH_DIR}/`
4. Runs `install.sh`
5. Reports success/failure

### Auto-Detection (Patch Monitor)

The `mythos-patch-monitor.service` watches `~/Downloads/` for new patch zips and auto-processes them:
1. Detect zip → extract → run install.sh
2. Git commit + semantic version tag
3. Push to GitHub
4. Archive zip

```bash
sudo systemctl status mythos-patch-monitor
sudo journalctl -u mythos-patch-monitor -f
```

---

## Ownership Rules

- `/opt/mythos/` is owned by `adge:adge` — no sudo needed for file operations
- sudo only for: `systemctl`, `/usr/local/bin` symlinks, `psql` as postgres
- Read-only cross-stream access is always fine
- Never write to another stream's tables without declaring it
- Shared table migrations go through SYS only

---

## Directory Reference

```
/opt/mythos/patches/
├── scripts/
│   ├── patch_base.py          ← PatchBase class
│   ├── patch_apply.sh         ← Legacy manual apply
│   └── patch_rollback.sh      ← Rollback to git tag
├── archive/                   ← Processed zip files
├── logs/                      ← Legacy JSON logs
├── MNE-0003_stream_column/    ← Extracted patch directories
├── SYS-0008_patchbase_logging/
└── ...
```

---

## Git & Rollback

### Tags

| Pattern | Purpose |
|---------|---------|
| `pre-patch-*` | State before patch |
| `vX.Y.Z` | Version after patch |
| `pre-rollback-*` | State before rollback |

### Rollback

```bash
# Via script
/opt/mythos/patches/scripts/patch_rollback.sh <tag>

# Via Telegram
/patch_rollback <tag>
/patch_rollback_confirm <tag>
```

Rollback is reversible — a `pre-rollback-*` tag is created first.

---

## Telegram Commands

| Command | Description |
|---------|-------------|
| `/patch` | System overview |
| `/patch_status` | Current version, recent activity |
| `/patch_list` | Available patches |
| `/patch_apply <name>` | Manually apply a patch |
| `/patch_rollback` | Show rollback options |
| `/backlog` | Development backlog by priority |
| `/backlog NEU` | Filter backlog by stream |
| `/backlog streams` | Stream summary with counts |

---

## Session Start Protocol

Before building any patch:

1. Get the diagnostic dump (TODO.md + ARCHITECTURE.md + STREAMS.md)
2. Run `mythos-diag streams` for live patch counters
3. Identify which stream the work belongs to
4. Confirm the plan before writing code
5. **Never build blind or guess patch numbers**

```bash
D=~/diag.txt; > "$D"
echo "=== TODO ===" >> "$D"
cat /opt/mythos/docs/TODO.md >> "$D" 2>&1
echo -e "\n\n=== STREAMS ===" >> "$D"
mythos-diag streams >> "$D" 2>&1
cat "$D" | xclip -selection clipboard && echo "✓ Copied"
```
