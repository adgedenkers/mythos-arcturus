#!/bin/bash
# ============================================================
# PATCH 0013: Finance System - Bank CSV Import
# ============================================================
# Deploys the complete finance import system:
# - PostgreSQL schema
# - Bank parsers (USAA, Sunmark)
# - Import script with deduplication
# - Reports CLI
# ============================================================

set -e

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
MYTHOS_ROOT="/opt/mythos"
FINANCE_DIR="$MYTHOS_ROOT/finance"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[PATCH]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

log "Installing Finance System..."

# ============================================================
# Deploy files
# ============================================================

log "Deploying finance scripts..."

cp "$PATCH_DIR/opt/mythos/finance/schema.sql" "$FINANCE_DIR/"
cp "$PATCH_DIR/opt/mythos/finance/parsers.py" "$FINANCE_DIR/"
cp "$PATCH_DIR/opt/mythos/finance/import_transactions.py" "$FINANCE_DIR/"
cp "$PATCH_DIR/opt/mythos/finance/reports.py" "$FINANCE_DIR/"

chmod +x "$FINANCE_DIR/import_transactions.py"
chmod +x "$FINANCE_DIR/reports.py"

log "✓ Scripts deployed"

# ============================================================
# Create directories
# ============================================================

mkdir -p "$FINANCE_DIR/accounts"
mkdir -p "$FINANCE_DIR/archive"

log "✓ Directories created"

# ============================================================
# Database setup
# ============================================================

log "Setting up database schema..."

# Check if postgres is accessible
if command -v psql &> /dev/null; then
    # Try to run schema
    if psql -h localhost -U postgres -d mythos -f "$FINANCE_DIR/schema.sql" 2>/dev/null; then
        log "✓ Schema applied to database"
    else
        warn "Could not apply schema automatically."
        echo "  Run manually:"
        echo "  psql -d mythos -f $FINANCE_DIR/schema.sql"
    fi
else
    warn "psql not found in PATH"
    echo "  Run manually when available:"
    echo "  psql -d mythos -f $FINANCE_DIR/schema.sql"
fi

# ============================================================
# Done
# ============================================================

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Finance System Installed${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Files deployed to: $FINANCE_DIR"
echo ""
echo "Usage:"
echo "  cd $FINANCE_DIR"
echo ""
echo "  # Import USAA transactions"
echo "  python import_transactions.py accounts/usaa_2026_01.csv --account-id 2"
echo ""
echo "  # Import Sunmark transactions"
echo "  python import_transactions.py accounts/sunmark_2026_01.csv --account-id 1"
echo ""
echo "  # Preview without importing"
echo "  python import_transactions.py <file> --account-id <id> --dry-run"
echo ""
echo "  # Reports"
echo "  python reports.py summary"
echo "  python reports.py monthly"
echo "  python reports.py category"
echo "  python reports.py merchants"
echo "  python reports.py search <term>"
echo "  python reports.py uncategorized"
echo "  python reports.py recurring"
echo ""
echo "Account IDs:"
echo "  1 = Sunmark Primary Checking"
echo "  2 = USAA Simple Checking"
echo ""
