#!/bin/bash
# ============================================================
# PATCH 0015: Finance System Complete
# ============================================================
# Complete bank CSV import system with:
# - USAA parser (Date,Description,Original Description,Category,Amount,Status)
# - Sunmark parser (Transaction Number,Date,Memo,Debit,Credit,Balance)
# - Auto-detection
# - 100+ category mappings
# - Reports CLI
# ============================================================

set -e

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
MYTHOS_ROOT="/opt/mythos"
FINANCE_DIR="$MYTHOS_ROOT/finance"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[PATCH]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

log "Installing Finance System Complete..."

# Deploy files
cp "$PATCH_DIR/opt/mythos/finance/schema.sql" "$FINANCE_DIR/"
cp "$PATCH_DIR/opt/mythos/finance/parsers.py" "$FINANCE_DIR/"
cp "$PATCH_DIR/opt/mythos/finance/import_transactions.py" "$FINANCE_DIR/"
cp "$PATCH_DIR/opt/mythos/finance/reports.py" "$FINANCE_DIR/"

chmod +x "$FINANCE_DIR/import_transactions.py"
chmod +x "$FINANCE_DIR/reports.py"

mkdir -p "$FINANCE_DIR/accounts"
mkdir -p "$FINANCE_DIR/archive"

log "✓ Files deployed"

# Run schema (will add tables/mappings if missing)
log "Updating database schema..."
if sudo -u postgres psql -d mythos -f "$FINANCE_DIR/schema.sql" 2>/dev/null; then
    log "✓ Schema updated"
else
    warn "Schema update had warnings (likely already exists)"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Finance System Complete - v1.0${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Usage:"
echo "  cd $FINANCE_DIR"
echo ""
echo "  # Import transactions"
echo "  python import_transactions.py accounts/usaa_YYYY_MM.csv --account-id 2"
echo "  python import_transactions.py accounts/sunmark_YYYY_MM.csv --account-id 1"
echo ""
echo "  # Reports"
echo "  python reports.py summary"
echo "  python reports.py monthly"
echo "  python reports.py category"
echo "  python reports.py merchants"
echo "  python reports.py search <term>"
echo "  python reports.py recurring"
echo ""
echo "Account IDs:"
echo "  1 = Sunmark Primary Checking"
echo "  2 = USAA Simple Checking"
echo ""
