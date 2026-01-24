#!/bin/bash
# ============================================================
# PATCH 0014: Finance Schema Migration
# ============================================================
# Adds CSV import columns to existing Plaid-based schema
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

log "Installing Finance Schema Migration..."

# Deploy migration SQL
cp "$PATCH_DIR/opt/mythos/finance/migration_add_csv_columns.sql" "$FINANCE_DIR/"
log "✓ Deployed migration SQL"

# Deploy updated import script
cp "$PATCH_DIR/opt/mythos/finance/import_transactions.py" "$FINANCE_DIR/"
chmod +x "$FINANCE_DIR/import_transactions.py"
log "✓ Updated import_transactions.py"

# Run migration
log "Running database migration..."
if psql -d mythos -f "$FINANCE_DIR/migration_add_csv_columns.sql" 2>&1; then
    log "✓ Migration completed"
else
    warn "Migration had issues - check output above"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Finance Migration Complete${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "The transactions table now supports both:"
echo "  • Plaid API imports (existing)"
echo "  • CSV file imports (new)"
echo ""
echo "Test the import:"
echo "  cd /opt/mythos/finance"
echo "  python import_transactions.py accounts/sunmark_2026_01.csv --account-id 1 --dry-run"
echo "  python import_transactions.py accounts/usaa_2026_01.csv --account-id 2 --dry-run"
echo ""
