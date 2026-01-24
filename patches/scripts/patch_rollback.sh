#!/bin/bash
# ============================================================
# patch_rollback.sh - Rollback to a previous state
# ============================================================
# Usage: ./patch_rollback.sh [tag]
#
# Without arguments: shows available rollback points
# With tag: rolls back to that specific tag
# ============================================================

set -e

MYTHOS_ROOT="/opt/mythos"
PATCH_LOG_DIR="$MYTHOS_ROOT/patches/logs"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "${GREEN}[ROLLBACK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ============================================================
# Arguments
# ============================================================

TARGET_TAG="$1"

cd "$MYTHOS_ROOT"

if [[ ! -d ".git" ]]; then
    error "Not a git repository: $MYTHOS_ROOT"
fi

# ============================================================
# No arguments - show available rollback points
# ============================================================

if [[ -z "$TARGET_TAG" ]]; then
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Available Rollback Points${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    echo -e "${CYAN}Pre-patch snapshots:${NC}"
    git tag -l "pre-*" --sort=-v:refname | head -10 | while read tag; do
        date=$(git log -1 --format="%ci" "$tag" 2>/dev/null | cut -d' ' -f1,2)
        echo "  $tag  ($date)"
    done
    
    echo ""
    echo -e "${CYAN}Version tags:${NC}"
    git tag -l "v*" --sort=-v:refname | head -10 | while read tag; do
        date=$(git log -1 --format="%ci" "$tag" 2>/dev/null | cut -d' ' -f1,2)
        msg=$(git tag -l -n1 "$tag" | sed "s/^$tag\s*//")
        echo "  $tag  ($date)  $msg"
    done
    
    echo ""
    echo "Usage: $0 <tag>"
    echo ""
    exit 0
fi

# ============================================================
# Verify tag exists
# ============================================================

if ! git rev-parse "$TARGET_TAG" &>/dev/null; then
    error "Tag not found: $TARGET_TAG"
fi

# ============================================================
# Confirm
# ============================================================

CURRENT_VERSION=$(git tag -l "v*" --sort=-v:refname | head -1)
TARGET_DATE=$(git log -1 --format="%ci" "$TARGET_TAG" 2>/dev/null)

echo ""
echo -e "${YELLOW}════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  WARNING: About to rollback${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "  Current version: $CURRENT_VERSION"
echo "  Rolling back to: $TARGET_TAG"
echo "  Target date:     $TARGET_DATE"
echo ""
echo "  This will:"
echo "  • Restore all files to the state at $TARGET_TAG"
echo "  • Create a new commit recording the rollback"
echo "  • NOT delete any history (you can undo this)"
echo ""
read -p "Continue? [y/N] " confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Aborted."
    exit 0
fi

# ============================================================
# Create snapshot of current state
# ============================================================

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PRE_ROLLBACK_TAG="pre-rollback-${TIMESTAMP}"

log "Saving current state: $PRE_ROLLBACK_TAG"

git add -A
git commit -m "Auto-commit before rollback to $TARGET_TAG" 2>/dev/null || true
git tag -a "$PRE_ROLLBACK_TAG" -m "State before rollback to $TARGET_TAG" 2>/dev/null || true

# ============================================================
# Perform rollback
# ============================================================

log "Rolling back to: $TARGET_TAG"

# Checkout the target state (files only, not HEAD)
git checkout "$TARGET_TAG" -- .

# Commit the rollback
git add -A
git commit -m "Rollback to $TARGET_TAG

Pre-rollback state saved as: $PRE_ROLLBACK_TAG
Target tag date: $TARGET_DATE"

# ============================================================
# Push to GitHub
# ============================================================

if git remote get-url origin &>/dev/null; then
    log "Pushing rollback to GitHub..."
    git push origin main --tags 2>/dev/null || git push origin master --tags 2>/dev/null || warn "Push failed"
fi

# ============================================================
# Log
# ============================================================

mkdir -p "$PATCH_LOG_DIR"
cat > "$PATCH_LOG_DIR/rollback_${TIMESTAMP}.json" <<EOF
{
    "timestamp": "$TIMESTAMP",
    "target_tag": "$TARGET_TAG",
    "pre_rollback_tag": "$PRE_ROLLBACK_TAG",
    "previous_version": "$CURRENT_VERSION",
    "status": "success"
}
EOF

# ============================================================
# Restart services
# ============================================================

log "Restarting services..."
sudo systemctl restart mythos-patch-monitor 2>/dev/null || warn "Could not restart patch monitor"

# ============================================================
# Done
# ============================================================

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Rollback Complete${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "  Rolled back to: $TARGET_TAG"
echo "  Previous state saved as: $PRE_ROLLBACK_TAG"
echo ""
echo "  To undo this rollback:"
echo "  $0 $PRE_ROLLBACK_TAG"
echo ""
