#!/bin/bash
# ============================================================
# patch_apply.sh - Apply a patch with git versioning
# ============================================================
# Usage: ./patch_apply.sh <patch_directory>
#
# This script:
# 1. Creates a git snapshot before applying
# 2. Runs the patch's install.sh if present
# 3. Commits changes and tags new version
# 4. Pushes to GitHub
# ============================================================

set -e

MYTHOS_ROOT="/opt/mythos"
PATCH_LOG_DIR="$MYTHOS_ROOT/patches/logs"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[PATCH]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ============================================================
# Arguments
# ============================================================

PATCH_DIR="$1"

if [[ -z "$PATCH_DIR" ]]; then
    echo "Usage: $0 <patch_directory>"
    echo ""
    echo "Available patches:"
    ls -d "$MYTHOS_ROOT/patches/patch_"* 2>/dev/null | while read d; do
        name=$(basename "$d")
        if [[ -f "$d/install.sh" ]]; then
            echo "  $name (has install.sh)"
        else
            echo "  $name"
        fi
    done
    exit 1
fi

# Resolve to absolute path
if [[ ! "$PATCH_DIR" = /* ]]; then
    # Check if it's just a name like "patch_0010_foo"
    if [[ -d "$MYTHOS_ROOT/patches/$PATCH_DIR" ]]; then
        PATCH_DIR="$MYTHOS_ROOT/patches/$PATCH_DIR"
    else
        PATCH_DIR="$(pwd)/$PATCH_DIR"
    fi
fi

if [[ ! -d "$PATCH_DIR" ]]; then
    error "Patch directory not found: $PATCH_DIR"
fi

PATCH_NAME=$(basename "$PATCH_DIR")
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

log "Applying patch: $PATCH_NAME"

# ============================================================
# Pre-flight
# ============================================================

cd "$MYTHOS_ROOT"

if [[ ! -d ".git" ]]; then
    error "Not a git repository: $MYTHOS_ROOT"
fi

# ============================================================
# Git Snapshot (Pre-patch)
# ============================================================

log "Creating pre-patch snapshot..."

PRE_TAG="pre-${PATCH_NAME}-${TIMESTAMP}"

# Commit any uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
    git add -A
    git commit -m "Auto-commit before $PATCH_NAME" || true
fi

# Tag current state
git tag -a "$PRE_TAG" -m "State before $PATCH_NAME" 2>/dev/null || true
log "Tagged: $PRE_TAG"

# ============================================================
# Apply Patch
# ============================================================

if [[ -f "$PATCH_DIR/install.sh" ]]; then
    log "Running install.sh..."
    chmod +x "$PATCH_DIR/install.sh"
    
    # Run install script
    if ! "$PATCH_DIR/install.sh"; then
        error "Install script failed!"
    fi
else
    log "No install.sh found, copying files..."
    
    # Simple file copy for patches without install script
    if [[ -d "$PATCH_DIR/opt/mythos" ]]; then
        cp -rv "$PATCH_DIR/opt/mythos/"* "$MYTHOS_ROOT/"
    else
        # Assume files are meant for MYTHOS_ROOT directly
        find "$PATCH_DIR" -type f ! -name "*.md" ! -name "README*" -exec cp -v {} "$MYTHOS_ROOT/" \;
    fi
fi

# ============================================================
# Git Commit (Post-patch)
# ============================================================

log "Committing changes..."

cd "$MYTHOS_ROOT"

# Get current version and increment
LAST_TAG=$(git tag -l "v*" --sort=-v:refname | head -1 2>/dev/null || echo "v0.0.0")
if [[ -z "$LAST_TAG" || "$LAST_TAG" == "v0.0.0" ]]; then
    NEW_VERSION="v1.0.0"
else
    IFS='.' read -r major minor patch <<< "${LAST_TAG#v}"
    NEW_VERSION="v${major}.${minor}.$((patch + 1))"
fi

# Commit
git add -A
git commit -m "Applied patch: $PATCH_NAME" || true

# Tag new version
git tag -a "$NEW_VERSION" -m "After $PATCH_NAME" 2>/dev/null || true
log "Tagged: $NEW_VERSION"

# ============================================================
# Push to GitHub
# ============================================================

if git remote get-url origin &>/dev/null; then
    log "Pushing to GitHub..."
    git push origin main --tags 2>/dev/null || git push origin master --tags 2>/dev/null || warn "Push failed"
else
    warn "No remote configured, skipping push"
fi

# ============================================================
# Log
# ============================================================

mkdir -p "$PATCH_LOG_DIR"
cat > "$PATCH_LOG_DIR/apply_${PATCH_NAME}_${TIMESTAMP}.json" <<EOF
{
    "timestamp": "$TIMESTAMP",
    "patch": "$PATCH_NAME",
    "pre_tag": "$PRE_TAG",
    "post_tag": "$NEW_VERSION",
    "status": "success"
}
EOF

# ============================================================
# Done
# ============================================================

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Patch Applied Successfully${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "  Patch:       $PATCH_NAME"
echo "  Pre-tag:     $PRE_TAG"
echo "  New version: $NEW_VERSION"
echo ""
echo "  To rollback: /opt/mythos/patches/scripts/patch_rollback.sh $PRE_TAG"
echo ""
