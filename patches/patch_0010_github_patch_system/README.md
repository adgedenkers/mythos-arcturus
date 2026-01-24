# Patch 0010: GitHub-Integrated Patch System

## Overview

This patch adds automatic git versioning and GitHub sync to the Mythos patch pipeline. Every patch application now:

1. Creates a tagged snapshot before changes
2. Commits and tags after successful application
3. Pushes to GitHub for backup and collaboration
4. Supports rollback to any previous state

## Prerequisites

If you want GitHub sync, configure a remote first:

```bash
cd /opt/mythos
git remote add origin git@github.com:YOUR_USERNAME/mythos.git
```

Or use HTTPS:
```bash
git remote add origin https://github.com/YOUR_USERNAME/mythos.git
```

The patch works fine without a remote - you just won't get auto-push to GitHub.

## Installation

```bash
cd /opt/mythos/patches/patch_0010_github_patch_system
chmod +x install.sh
./install.sh
```

## What Gets Installed

| File | Purpose |
|------|---------|
| `mythos_patch_monitor.py` | Updated monitor with GitManager class |
| `patches/scripts/patch_apply.sh` | Manual patch application with git |
| `patches/scripts/patch_rollback.sh` | Rollback to any git tag |
| `telegram_bot/handlers/patch_handlers.py` | Telegram commands |

## Usage

### Automatic (Download Detection)

1. Download a patch zip to `~/Downloads`
2. Monitor detects `patch_####_*.zip`
3. Git snapshot created automatically
4. Patch extracted and committed
5. Changes pushed to GitHub

### Manual Application

```bash
# List available patches
ls /opt/mythos/patches/patch_*/

# Apply a patch
/opt/mythos/patches/scripts/patch_apply.sh patch_0011_something

# Or by full path
/opt/mythos/patches/scripts/patch_apply.sh /path/to/patch_dir
```

### Rollback

```bash
# Show available rollback points
/opt/mythos/patches/scripts/patch_rollback.sh

# Rollback to specific tag
/opt/mythos/patches/scripts/patch_rollback.sh pre-patch_0010-20260123_150000
```

### Telegram Commands

| Command | Description |
|---------|-------------|
| `/patch` | Show help and current version |
| `/patch_status` | Version info, recent tags, activity |
| `/patch_list` | Available patches to apply |
| `/patch_apply <n>` | Apply a specific patch |
| `/patch_rollback` | Show rollback options |
| `/patch_rollback <tag>` | Initiate rollback |
| `/patch_rollback_confirm <tag>` | Confirm and execute rollback |

## Git Tags

The system creates two types of tags:

- **`pre-patch_NNNN-TIMESTAMP`** - State before patch application
- **`vX.Y.Z`** - Version after patch (auto-incremented)

## GitHub Repository

On first run with `gh` authenticated, the install script will:

1. Create a private `mythos` repository
2. Configure the origin remote
3. Push all existing content and tags

## Logs

Patch activity is logged to:

- `/var/log/mythos_patch_monitor.log` - Service log
- `/opt/mythos/patches/logs/*.json` - Individual patch records

## Troubleshooting

### GitHub push fails

```bash
# Check remote
cd /opt/mythos && git remote -v

# Add remote if missing
git remote add origin git@github.com:YOUR_USERNAME/mythos.git

# Test SSH connection
ssh -T git@github.com

# Manual push
git push -u origin main --tags
```

### Service not running

```bash
sudo systemctl status mythos-patch-monitor
sudo journalctl -u mythos-patch-monitor -f
```

### Rollback fails

```bash
# Check current state
cd /opt/mythos && git status

# Manual reset to tag
git checkout <tag> -- .
git add -A
git commit -m "Manual rollback to <tag>"
```
