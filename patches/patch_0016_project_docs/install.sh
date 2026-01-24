#!/bin/bash
# ============================================================
# PATCH 0016: Project Documentation
# ============================================================
# Adds persistent project tracking files:
# - TODO.md - Roadmap, active work, backlog, completed items
# - ARCHITECTURE.md - Machine-readable system architecture
# ============================================================

set -e

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
MYTHOS_ROOT="/opt/mythos"
DOCS_DIR="$MYTHOS_ROOT/docs"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[PATCH]${NC} $1"; }

log "Installing Project Documentation..."

# Create docs directory
mkdir -p "$DOCS_DIR"

# Deploy files
cp "$PATCH_DIR/opt/mythos/docs/TODO.md" "$DOCS_DIR/"
cp "$PATCH_DIR/opt/mythos/docs/ARCHITECTURE.md" "$DOCS_DIR/"

log "✓ Documentation deployed to $DOCS_DIR"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Project Documentation Installed${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Files:"
echo "  $DOCS_DIR/TODO.md          - Project roadmap & status"
echo "  $DOCS_DIR/ARCHITECTURE.md  - System architecture reference"
echo ""
echo "These files are version-controlled and pushed with each patch."
echo "Edit TODO.md to track work progress."
echo ""
