---
name: build_patch
version: "1.0"
category: builder
risk_tier: T2-patch
description: >
  Create and deploy a numbered Mythos patch to Arcturus. Use this skill
  whenever any code, configuration, or infrastructure change needs to be
  deployed to the Mythos system. This is the primary deployment mechanism —
  all builder skills ultimately produce a patch. Triggers on: "build a patch",
  "deploy a fix", "create patch", or whenever Iris determines a change to
  Arcturus infrastructure is needed.
requires:
  services: [mythos-patch-monitor]
  tools: [bash, zip]
  files:
    - /opt/mythos/docs/TODO.md
    - /opt/mythos/docs/ARCHITECTURE.md
  env_vars: []
inputs:
  required:
    - description of what the patch does
    - current patch number (from TODO.md or /patch_status)
  optional:
    - target files to modify (if editing existing code)
    - diagnostic dump of current system state
outputs:
  files:
    - patch_NNNN_description.zip
  formats: [.zip]
  destinations:
    - /mnt/user-data/outputs/ (for download by Ka'tuar'el)
    - Ka'tuar'el copies to ~/Downloads on Arcturus
    - Patch monitor auto-detects and deploys
---

# Build Patch

## Purpose

The patch system is the deployment pipeline for all Mythos infrastructure
changes. Every code change, config update, or new feature ships as a numbered
patch. The patch monitor on Arcturus auto-detects new patches in ~/Downloads,
extracts them, runs install.sh, commits to git with a version tag, and pushes
to GitHub. This skill ensures patches are correctly structured every time.

## Pre-Flight Checks

Before building ANY patch:

1. **Get current state.** Request a diagnostic dump from Ka'tuar'el:
   ```bash
   D=~/diag.txt; > "$D"
   echo "=== TODO ===" >> "$D"
   cat /opt/mythos/docs/TODO.md >> "$D" 2>&1
   echo -e "\n\n=== ARCHITECTURE ===" >> "$D"
   cat /opt/mythos/docs/ARCHITECTURE.md >> "$D" 2>&1
   echo -e "\n\n=== RECENT PATCHES ===" >> "$D"
   ls -lt /opt/mythos/patches/*.zip 2>/dev/null | head -20 >> "$D" 2>&1
   echo -e "\n\n=== GIT LOG ===" >> "$D"
   cd /opt/mythos && git log --oneline -10 >> "$D" 2>&1
   cat "$D" | xclip -selection clipboard && echo "✓ Copied to clipboard"
   ```

2. **Determine the next patch number.** Patches are sequential 4-digit numbers.
   Find the highest existing patch number and increment by 1.

3. **If modifying existing code**, request the current file contents:
   ```bash
   D=~/diag.txt; > "$D"
   echo "=== TARGET FILE ===" >> "$D"
   cat /opt/mythos/path/to/file.py >> "$D" 2>&1
   cat "$D" | xclip -selection clipboard && echo "✓ Copied to clipboard"
   ```

4. **Confirm plan with Ka'tuar'el.** State:
   - Patch number: NNNN
   - What it does (one sentence)
   - What files it creates or modifies
   - Any service restarts needed

   Do NOT proceed until Ka'tuar'el confirms.

## Process

### Step 1: Create Patch Directory Structure

```
/home/claude/patch_NNNN_description/
├── install.sh              # Deployment script (MUST be executable)
└── opt/mythos/             # Files mirror their Arcturus paths
    ├── module/file.py
    └── other/file.conf
```

The directory tree under the patch root mirrors the absolute paths on Arcturus.
Files at `opt/mythos/module/file.py` will be deployed to `/opt/mythos/module/file.py`.

### Step 2: Write the install.sh

The install.sh script handles deployment. It runs as the user who triggers
the patch monitor (typically with sudo access). Structure:

```bash
#!/bin/bash
set -euo pipefail

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
MYTHOS_ROOT="/opt/mythos"

echo "=== Installing patch NNNN: description ==="

# Copy files to their destinations
cp "$PATCH_DIR/opt/mythos/module/file.py" "$MYTHOS_ROOT/module/file.py"

# Set permissions if needed
chmod +x "$MYTHOS_ROOT/module/file.py"

# Run any database migrations
# sudo -u postgres psql -d mythos -f "$PATCH_DIR/opt/mythos/migrations/NNNN.sql"

# Restart affected services
sudo systemctl restart mythos-bot.service
# sudo systemctl restart mythos-gateway.service

# Verify
echo "=== Verifying ==="
systemctl is-active mythos-bot.service && echo "✓ Bot service running"

echo "=== Patch NNNN installed successfully ==="
```

Key rules for install.sh:
- Always use `set -euo pipefail` — fail fast on errors
- Always echo what's happening at each step
- Always verify after deploying
- Restart only the services that are actually affected
- Use `$PATCH_DIR` for paths to files within the patch
- Use absolute paths for Arcturus destinations

### Step 3: Write the Patch Files

Create all files that need to be deployed. These live under the `opt/mythos/`
subtree of the patch directory, mirroring their final paths.

For Python files: use the Mythos venv shebang if the file is executable:
```python
#!/opt/mythos/.venv/bin/python3
```

For SQL migrations: name them with the patch number prefix:
```sql
-- Migration NNNN: description
-- Applied by patch_NNNN install.sh
BEGIN;
-- ... changes ...
COMMIT;
```

### Step 4: Create the Zip

```bash
cd /home/claude
zip -r patch_NNNN_description.zip patch_NNNN_description/
cp patch_NNNN_description.zip /mnt/user-data/outputs/
```

The zip filename MUST match the directory name exactly.

### Step 5: Provide to Ka'tuar'el

Present the zip file for download. Ka'tuar'el will:
1. Download the zip
2. Copy it to `~/Downloads` on Arcturus
3. The patch monitor auto-detects, extracts, runs install.sh
4. Verify via `/patch_status` in Telegram

### Step 6: Update TODO.md

After Ka'tuar'el confirms successful deployment, provide an updated TODO.md
entry moving the relevant item to Completed with the patch number.

## Validation

After deployment, Ka'tuar'el verifies by:
- `/patch_status` in Telegram — shows last deployed patch
- Checking service status: `systemctl status mythos-bot.service`
- Testing the specific feature that was patched
- Checking git log: `cd /opt/mythos && git log --oneline -3`

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| install.sh fails mid-execution | Missing dependency or wrong path | Check error output, fix install.sh, redeploy as NNNN+1 |
| Service won't restart | Code error in deployed file | Check journalctl, fix code, redeploy |
| Patch monitor doesn't detect | Wrong filename or ~/Downloads path | Verify zip is in ~/Downloads with correct naming |
| Git push fails | Auth or remote issue | Manual: `cd /opt/mythos && git push origin main` |
| Wrong patch number | Collision with existing patch | Check /opt/mythos/patches/ for actual latest, renumber |

## Examples

### Example 1: Simple File Update

**Input:** "Fix the timezone handling in the finance module"

**Patch structure:**
```
patch_0142_fix_finance_timezone/
├── install.sh
└── opt/mythos/finance/utils.py
```

**install.sh:**
```bash
#!/bin/bash
set -euo pipefail
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "=== Installing patch 0142: fix finance timezone ==="
cp "$PATCH_DIR/opt/mythos/finance/utils.py" /opt/mythos/finance/utils.py
sudo systemctl restart mythos-bot.service
echo "=== Patch 0142 installed ==="
```

### Example 2: New Feature with Database Migration

**Input:** "Add a new /goals command to the Telegram bot"

**Patch structure:**
```
patch_0143_telegram_goals_command/
├── install.sh
└── opt/mythos/
    ├── telegram_bot/handlers/goals.py
    ├── telegram_bot/commands.py  (updated)
    └── migrations/0143_goals_table.sql
```

**install.sh includes both file copy and SQL migration step.**

---

_Last updated: 2026-02-22_
_Author: Ka'tuar'el_
