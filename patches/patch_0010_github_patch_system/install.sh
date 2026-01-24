#!/bin/bash
# ============================================================
# PATCH 0010: GitHub-Integrated Patch System
# ============================================================
# This patch adds:
# - Auto-processing of downloaded patch zips with git versioning
# - GitHub sync for all patches (backup + collaboration)
# - Telegram commands for patch management
# - Rollback capability via git tags
# ============================================================

set -e

PATCH_NAME="patch_0010_github_patch_system"
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
MYTHOS_ROOT="/opt/mythos"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/opt/mythos/patches/logs/install_${PATCH_NAME}_${TIMESTAMP}.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

header() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# ============================================================
# Pre-flight checks
# ============================================================

header "Pre-flight Checks"

mkdir -p /opt/mythos/patches/logs

# Check we're running as the right user
if [[ "$USER" != "adge" ]]; then
    error "Must run as user 'adge', not '$USER'"
fi

# Check git is configured
if ! git config --global user.email &>/dev/null; then
    error "Git not configured. Run: git config --global user.email 'your@email.com'"
fi

# Check if git remote is configured
if git -C "$MYTHOS_ROOT" remote get-url origin &>/dev/null; then
    log "✓ Git remote configured"
else
    warn "No git remote configured - GitHub sync will be skipped"
fi

# Check required files exist in patch
REQUIRED_FILES=(
    "opt/mythos/mythos_patch_monitor.py"
    "opt/mythos/patches/scripts/patch_apply.sh"
    "opt/mythos/patches/scripts/patch_rollback.sh"
    "opt/mythos/telegram_bot/handlers/patch_handlers.py"
)

for f in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "$PATCH_DIR/$f" ]]; then
        error "Missing required file: $f"
    fi
done

log "✓ All required files present"

# ============================================================
# Git Snapshot (Pre-patch state)
# ============================================================

header "Creating Git Snapshot"

cd "$MYTHOS_ROOT"

# Get current version number
LAST_TAG=$(git tag -l "v*" --sort=-v:refname | head -1 2>/dev/null || echo "v0.0.0")
if [[ -z "$LAST_TAG" || "$LAST_TAG" == "v0.0.0" ]]; then
    NEXT_VERSION="v1.0.0"
else
    # Increment patch version
    IFS='.' read -r major minor patch <<< "${LAST_TAG#v}"
    NEXT_VERSION="v${major}.${minor}.$((patch + 1))"
fi

PRE_PATCH_TAG="pre-${PATCH_NAME}-${TIMESTAMP}"

log "Creating pre-patch snapshot: $PRE_PATCH_TAG"

# Stage and commit any uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
    git add -A
    git commit -m "Auto-commit before ${PATCH_NAME}" || true
fi

# Tag current state
git tag -a "$PRE_PATCH_TAG" -m "State before applying ${PATCH_NAME}" 2>/dev/null || true

log "✓ Tagged current state: $PRE_PATCH_TAG"

# ============================================================
# Backup existing files
# ============================================================

header "Backing Up Existing Files"

BACKUP_DIR="$MYTHOS_ROOT/_upgrade_backups/${PATCH_NAME}_${TIMESTAMP}"
mkdir -p "$BACKUP_DIR"

FILES_TO_BACKUP=(
    "mythos_patch_monitor.py"
    "telegram_bot/handlers/__init__.py"
)

for f in "${FILES_TO_BACKUP[@]}"; do
    if [[ -f "$MYTHOS_ROOT/$f" ]]; then
        mkdir -p "$BACKUP_DIR/$(dirname "$f")"
        cp "$MYTHOS_ROOT/$f" "$BACKUP_DIR/$f.bak"
        log "Backed up: $f"
    fi
done

log "✓ Backups stored in: $BACKUP_DIR"

# ============================================================
# Deploy New Files
# ============================================================

header "Deploying Patch Files"

# Copy all files from patch maintaining structure
cp "$PATCH_DIR/opt/mythos/mythos_patch_monitor.py" "$MYTHOS_ROOT/mythos_patch_monitor.py"
log "Updated: mythos_patch_monitor.py"

mkdir -p "$MYTHOS_ROOT/patches/scripts"
cp "$PATCH_DIR/opt/mythos/patches/scripts/"*.sh "$MYTHOS_ROOT/patches/scripts/"
chmod +x "$MYTHOS_ROOT/patches/scripts/"*.sh
log "Deployed: patches/scripts/*.sh"

mkdir -p "$MYTHOS_ROOT/telegram_bot/handlers"
cp "$PATCH_DIR/opt/mythos/telegram_bot/handlers/patch_handlers.py" "$MYTHOS_ROOT/telegram_bot/handlers/"
log "Deployed: telegram_bot/handlers/patch_handlers.py"

# Update handlers __init__.py to include patch handlers
INIT_FILE="$MYTHOS_ROOT/telegram_bot/handlers/__init__.py"
if [[ -f "$INIT_FILE" ]]; then
    if ! grep -q "patch_handlers" "$INIT_FILE"; then
        echo "" >> "$INIT_FILE"
        echo "# Patch management handlers" >> "$INIT_FILE"
        echo "from .patch_handlers import (" >> "$INIT_FILE"
        echo "    patch_command," >> "$INIT_FILE"
        echo "    patch_status_command," >> "$INIT_FILE"
        echo "    patch_apply_command," >> "$INIT_FILE"
        echo "    patch_rollback_command," >> "$INIT_FILE"
        echo "    patch_list_command" >> "$INIT_FILE"
        echo ")" >> "$INIT_FILE"
        log "Updated: handlers/__init__.py with patch imports"
    else
        log "handlers/__init__.py already has patch imports"
    fi
fi

# ============================================================
# GitHub Repository Setup (via standard git)
# ============================================================

header "GitHub Repository Setup"

cd "$MYTHOS_ROOT"

# Check if remote exists
if git remote get-url origin &>/dev/null; then
    log "Git remote 'origin' already configured"
    REPO_URL=$(git remote get-url origin)
    log "Remote URL: $REPO_URL"
    
    # Push current state
    log "Pushing to GitHub..."
    if git push -u origin main --tags 2>/dev/null; then
        log "✓ Pushed to origin/main"
    elif git push -u origin master --tags 2>/dev/null; then
        log "✓ Pushed to origin/master"
    else
        warn "Push failed - check remote config or SSH keys"
    fi
else
    warn "No git remote configured."
    echo ""
    echo "To enable GitHub sync, run:"
    echo "  cd /opt/mythos"
    echo "  git remote add origin git@github.com:YOUR_USERNAME/mythos.git"
    echo "  git push -u origin main --tags"
    echo ""
fi

# ============================================================
# Git Commit (Post-patch state)
# ============================================================

header "Committing Patch"

cd "$MYTHOS_ROOT"

git add -A
git commit -m "Applied ${PATCH_NAME}: GitHub-integrated patch system

- Extended mythos_patch_monitor.py with git versioning
- Added patch_apply.sh and patch_rollback.sh scripts
- Added Telegram /patch commands
- Auto-snapshot before patch application
- Auto-push to GitHub after changes"

# Tag with new version
git tag -a "$NEXT_VERSION" -m "After ${PATCH_NAME}"
log "✓ Committed and tagged: $NEXT_VERSION"

# Push if remote configured
if git remote get-url origin &>/dev/null; then
    git push origin main --tags 2>/dev/null || git push origin master --tags 2>/dev/null || warn "Push failed"
    log "✓ Pushed to GitHub"
fi

# ============================================================
# Restart Services
# ============================================================

header "Restarting Services"

log "Restarting mythos-patch-monitor service..."
sudo systemctl restart mythos-patch-monitor || warn "Could not restart patch monitor"

log "Checking service status..."
if systemctl is-active --quiet mythos-patch-monitor; then
    log "✓ mythos-patch-monitor is running"
else
    warn "mythos-patch-monitor may not be running - check with: sudo systemctl status mythos-patch-monitor"
fi

# ============================================================
# Summary
# ============================================================

header "Installation Complete"

echo -e "${GREEN}Patch ${PATCH_NAME} installed successfully!${NC}"
echo ""
echo "What's new:"
echo "  • Patch zips now trigger git snapshot before extraction"
echo "  • All changes auto-committed and pushed to GitHub"
echo "  • Rollback available via: /opt/mythos/patches/scripts/patch_rollback.sh"
echo "  • Telegram commands: /patch, /patch_status, /patch_apply, /patch_rollback"
echo ""
echo "Git tags:"
echo "  • Pre-patch:  $PRE_PATCH_TAG"
echo "  • Post-patch: $NEXT_VERSION"
echo ""
if git remote get-url origin &>/dev/null; then
    echo "GitHub: Synced ✓"
else
    echo "GitHub: No remote configured"
    echo "  To enable: git remote add origin git@github.com:USER/mythos.git"
fi
echo ""
echo "Log file: $LOG_FILE"
