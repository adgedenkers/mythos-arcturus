# Mythos Patch System - Gold Standard Documentation

**Version:** 1.0  
**Author:** Claude (Anthropic) for Ka'tuar'el  
**Created:** 2026-01-23  
**Last Updated:** 2026-01-23  

---

## Overview

The Mythos Patch System is a fully automated code deployment pipeline that handles patch generation, delivery, extraction, execution, version control, and remote backup with minimal manual intervention.

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Auto-Detection** | File watcher monitors `~/Downloads` for patch zips |
| **Auto-Extraction** | Zips extracted to `/opt/mythos/patches/` |
| **Auto-Execution** | `install.sh` runs automatically after extraction |
| **Git Versioning** | Pre-patch snapshot + post-patch commit + semantic tags |
| **GitHub Sync** | Auto-push to remote repository after each patch |
| **Telegram Control** | `/patch` commands for status, apply, rollback |
| **Rollback** | Revert to any previous state via git tags |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PATCH GENERATION (Claude)                       │
│  Claude creates patch_NNNN_description.zip containing:                  │
│  ├── install.sh           (executable installer script)                 │
│  ├── opt/mythos/...       (files in deployment structure)               │
│  └── README.md            (optional documentation)                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         DELIVERY (User Download)                        │
│  User downloads zip to ~/Downloads on Arcturus                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    AUTO-PROCESSING (mythos_patch_monitor.py)            │
│  1. Detect patch_*.zip in ~/Downloads                                   │
│  2. Validate zip integrity                                              │
│  3. Create git snapshot (pre-patch tag)                                 │
│  4. Extract to /opt/mythos/patches/patch_NNNN_*/                        │
│  5. Execute install.sh (if AUTO_EXECUTE_INSTALL=True)                   │
│  6. Commit changes to git                                               │
│  7. Tag new version (vX.Y.Z)                                            │
│  8. Push to GitHub                                                      │
│  9. Archive zip to /opt/mythos/patches/archive/                         │
│  10. Log to /opt/mythos/patches/logs/                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         VISIBILITY (Telegram Bot)                       │
│  /patch           - Overview and help                                   │
│  /patch_status    - Current version, recent activity                    │
│  /patch_list      - Available patches                                   │
│  /patch_apply     - Manually apply a patch                              │
│  /patch_rollback  - Revert to previous state                            │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
/opt/mythos/
├── mythos_patch_monitor.py      # File watcher service (systemd)
├── .git/                        # Git repository
├── .gitignore                   # Excludes data/, .env, backups, etc.
│
├── patches/
│   ├── archive/                 # Processed zip files
│   ├── logs/                    # JSON logs of patch applications
│   ├── scripts/
│   │   ├── patch_apply.sh       # Manual patch application
│   │   └── patch_rollback.sh    # Rollback to git tag
│   ├── patch_0010_*/            # Extracted patch directories
│   ├── patch_0011_*/
│   └── ...
│
├── telegram_bot/
│   ├── mythos_bot.py            # Main bot
│   └── handlers/
│       ├── __init__.py
│       ├── patch_handlers.py    # /patch command handlers
│       └── ...
│
└── ...
```

---

## Patch Naming Convention

```
patch_NNNN_description.zip
```

| Component | Description |
|-----------|-------------|
| `patch_` | Required prefix for auto-detection |
| `NNNN` | 4-digit sequential number (0001, 0002, ...) |
| `description` | Brief snake_case description |
| `.zip` | Required extension |

**Examples:**
- `patch_0010_github_patch_system.zip`
- `patch_0011_test_patch.zip`
- `patch_0012_telegram_autoexec.zip`

---

## Patch Structure

A patch zip should contain:

```
patch_NNNN_description/
├── install.sh                   # REQUIRED: Executable installer
├── README.md                    # Optional: Documentation
└── opt/
    └── mythos/
        ├── some_file.py         # Files to deploy
        ├── another_dir/
        │   └── config.yaml
        └── ...
```

### install.sh Template

```bash
#!/bin/bash
# ============================================================
# PATCH NNNN: Description
# ============================================================

set -e

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
MYTHOS_ROOT="/opt/mythos"

echo "[PATCH] Installing..."

# Copy files to destinations
cp "$PATCH_DIR/opt/mythos/some_file.py" "$MYTHOS_ROOT/"

# Run any setup commands
# pip install something --break-system-packages

# Restart services if needed
# sudo systemctl restart some-service

echo "[PATCH] Done"
```

---

## Git Versioning

### Tag Types

| Pattern | Purpose | Example |
|---------|---------|---------|
| `pre-patch-*` | State before patch | `pre-patch-patch_0012-20260123_200335` |
| `vX.Y.Z` | Version after patch | `v1.0.2` |
| `pre-rollback-*` | State before rollback | `pre-rollback-20260123_210000` |

### Version Increment Logic

- Patches increment the **patch** number: `v1.0.1` → `v1.0.2`
- Manual version bumps can be done for major/minor releases

### Viewing History

```bash
# Recent commits
git log --oneline -10

# All version tags
git tag -l "v*" --sort=-v:refname

# All pre-patch snapshots
git tag -l "pre-*" --sort=-v:refname
```

---

## Rollback

### Via Command Line

```bash
# Show available rollback points
/opt/mythos/patches/scripts/patch_rollback.sh

# Rollback to specific tag
/opt/mythos/patches/scripts/patch_rollback.sh pre-patch-patch_0012-20260123_200335
```

### Via Telegram

```
/patch_rollback                    # Show options
/patch_rollback <tag>              # Initiate rollback
/patch_rollback_confirm <tag>      # Execute rollback
```

### What Rollback Does

1. Saves current state as `pre-rollback-*` tag
2. Checks out all files from target tag
3. Commits the rollback
4. Pushes to GitHub
5. Restarts affected services

**Rollback is reversible** - you can rollback the rollback using the `pre-rollback-*` tag.

---

## Telegram Commands

| Command | Description |
|---------|-------------|
| `/patch` | Show system overview and available commands |
| `/patch_status` | Current version, GitHub status, recent tags, activity log |
| `/patch_list` | List patches in `/opt/mythos/patches/patch_*/` |
| `/patch_apply <name>` | Manually apply a specific patch |
| `/patch_rollback` | Show available rollback points |
| `/patch_rollback <tag>` | Initiate rollback (requires confirmation) |
| `/patch_rollback_confirm <tag>` | Execute the rollback |

### Authorization

Only authorized Telegram IDs can use patch commands. Set in `/opt/mythos/.env`:

```
TELEGRAM_ID_KA=123456789
TELEGRAM_ID_SERAPHE=987654321
```

---

## Service Management

### mythos-patch-monitor

The file watcher runs as a systemd service:

```bash
# Status
sudo systemctl status mythos-patch-monitor

# Restart
sudo systemctl restart mythos-patch-monitor

# View logs
sudo journalctl -u mythos-patch-monitor -f
tail -f /var/log/mythos_patch_monitor.log
```

**Service file:** `/etc/systemd/system/mythos-patch-monitor.service`

### Telegram Bot

If not running as a service:

```bash
# Kill existing
pkill -f mythos_bot.py

# Start fresh
cd /opt/mythos/telegram_bot
nohup python mythos_bot.py > /dev/null 2>&1 &
```

---

## Configuration

### Monitor Configuration

In `/opt/mythos/mythos_patch_monitor.py`:

```python
# Enable/disable git integration
GIT_ENABLED = True

# Enable/disable GitHub push
GITHUB_PUSH_ENABLED = True

# Auto-run install.sh after extraction
AUTO_EXECUTE_INSTALL = True
```

### .gitignore

The repository excludes:

- `data/` - Runtime state (Redis, Qdrant)
- `.env` - Secrets
- `_backups/`, `backups/` - Large backup directories
- `patches/archive/` - Processed zips
- `patches/logs/` - Patch logs
- `media/` - User uploads
- `.venv/` - Python virtual environment
- `__pycache__/` - Python bytecode

---

## GitHub Integration

### Initial Setup

```bash
cd /opt/mythos
git remote add origin git@github.com:USERNAME/REPO.git
git branch -M main
git push -u origin main --tags
```

### Verify

```bash
git remote -v
# origin  git@github.com:adgedenkers/mythos-arcturus.git (fetch)
# origin  git@github.com:adgedenkers/mythos-arcturus.git (push)
```

### Manual Push

If auto-push fails:

```bash
cd /opt/mythos
git push origin main --tags
```

---

## Workflow: Claude Generates a Patch

1. **User requests feature/fix** in Claude conversation
2. **Claude generates patch zip** with proper structure
3. **User downloads** to `~/Downloads` on Arcturus
4. **Monitor detects** the zip file
5. **System automatically:**
   - Creates pre-patch git snapshot
   - Extracts zip to patches directory
   - Runs `install.sh`
   - Commits changes
   - Tags new version
   - Pushes to GitHub
6. **User verifies** via `/patch_status` in Telegram

---

## Workflow: Manual Patch Application

```bash
# List available patches
/opt/mythos/patches/scripts/patch_apply.sh

# Apply specific patch
/opt/mythos/patches/scripts/patch_apply.sh patch_0015_new_feature

# Or via Telegram
/patch_list
/patch_apply patch_0015_new_feature
```

---

## Troubleshooting

### Patch not detected

```bash
# Check service is running
sudo systemctl status mythos-patch-monitor

# Check logs
tail -50 /var/log/mythos_patch_monitor.log

# Verify naming convention
ls ~/Downloads/patch_*.zip
```

### install.sh permission denied

```bash
# Make executable
chmod +x /opt/mythos/patches/patch_NNNN_*/install.sh
```

### Git push fails

```bash
# Check remote
git remote -v

# Test SSH connection
ssh -T git@github.com

# Manual push
git push origin main --tags
```

### Telegram commands not working

```bash
# Check bot has patch imports
grep "patch_command" /opt/mythos/telegram_bot/mythos_bot.py

# Restart bot
pkill -f mythos_bot.py
cd /opt/mythos/telegram_bot && nohup python mythos_bot.py > /dev/null 2>&1 &
```

---

## File Reference

| File | Purpose |
|------|---------|
| `/opt/mythos/mythos_patch_monitor.py` | Main file watcher service |
| `/opt/mythos/patches/scripts/patch_apply.sh` | Manual patch application |
| `/opt/mythos/patches/scripts/patch_rollback.sh` | Rollback to git tag |
| `/opt/mythos/telegram_bot/handlers/patch_handlers.py` | Telegram command handlers |
| `/etc/systemd/system/mythos-patch-monitor.service` | Systemd service definition |
| `/var/log/mythos_patch_monitor.log` | Service log file |
| `/opt/mythos/patches/logs/*.json` | Individual patch application logs |
| `/opt/mythos/.gitignore` | Git exclusions |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0.0 | 2026-01-23 | Initial patch system (patch 0010) |
| v1.0.1 | 2026-01-23 | Test patch (patch 0011) |
| v1.0.2 | 2026-01-23 | Telegram commands + auto-execute (patch 0012) |

---

## Quick Reference Card

```
PATCH NAMING:     patch_NNNN_description.zip
DOWNLOAD TO:      ~/Downloads (auto-detected)
EXTRACT TO:       /opt/mythos/patches/patch_NNNN_*/
ARCHIVE TO:       /opt/mythos/patches/archive/

TELEGRAM:
  /patch              Overview
  /patch_status       Current state
  /patch_list         Available patches
  /patch_apply <n>    Apply patch
  /patch_rollback     Revert options

COMMAND LINE:
  patch_apply.sh <dir>       Apply patch
  patch_rollback.sh          Show tags
  patch_rollback.sh <tag>    Revert

LOGS:
  /var/log/mythos_patch_monitor.log
  /opt/mythos/patches/logs/*.json

SERVICE:
  sudo systemctl status mythos-patch-monitor
  sudo systemctl restart mythos-patch-monitor
```

---

*This document is the authoritative reference for the Mythos Patch System. Keep it updated as the system evolves.*
