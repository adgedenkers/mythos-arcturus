#!/bin/bash
# verify_install.sh - Post-patch installation verification
# /opt/mythos/patches/scripts/verify_install.sh
#
# Usage: verify_install.sh <PATCH_NUM>
# Output: Writes detailed verification to /tmp/patch_NNNN_verify.log
#
# This script runs after patch installation to verify:
# - Database schema changes applied
# - Files in correct locations
# - Services running
# - Bot commands registered
#
# Exit codes:
#   0 = All checks passed
#   1 = Some checks failed (see log)

PATCH_NUM="${1:-0000}"
LOG="/tmp/patch_${PATCH_NUM}_verify.log"
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

# ============================================================
# HELPER FUNCTIONS
# ============================================================

log() {
    echo "$1" | tee -a "$LOG"
}

check_pass() {
    ((PASS_COUNT++))
    log "  ✓ $1"
}

check_fail() {
    ((FAIL_COUNT++))
    log "  ✗ $1"
}

check_warn() {
    ((WARN_COUNT++))
    log "  ⚠ $1"
}

section() {
    log ""
    log "━━━ $1 ━━━"
}

# ============================================================
# START VERIFICATION
# ============================================================

> "$LOG"  # Clear log
log "=== Patch ${PATCH_NUM} Verification ==="
log "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"

# ============================================================
# 1. SERVICE STATUS
# ============================================================
section "SERVICE STATUS"

if sudo systemctl is-active --quiet mythos-bot.service; then
    check_pass "mythos-bot.service is running"
else
    check_fail "mythos-bot.service is NOT running"
fi

if sudo systemctl is-active --quiet mythos-patch-monitor.service; then
    check_pass "mythos-patch-monitor.service is running"
else
    check_warn "mythos-patch-monitor.service is not running (optional)"
fi

# ============================================================
# 2. BOT IMPORTS CHECK
# ============================================================
section "BOT IMPORTS"

BOT_FILE="/opt/mythos/telegram_bot/mythos_bot.py"

if grep -q "from handlers.snapshot_handler import" "$BOT_FILE"; then
    check_pass "snapshot_handler imported"
else
    check_fail "snapshot_handler NOT imported"
fi

if grep -q "from handlers.finance_handler import" "$BOT_FILE"; then
    check_pass "finance_handler imported"
else
    check_fail "finance_handler NOT imported"
fi

if grep -q "from handlers.iris_handler import" "$BOT_FILE"; then
    check_pass "iris_handler imported"
else
    check_warn "iris_handler not imported (may be expected)"
fi

# ============================================================
# 3. COMMAND REGISTRATIONS
# ============================================================
section "COMMAND REGISTRATIONS"

check_command() {
    if grep -q "CommandHandler(\"$1\"" "$BOT_FILE"; then
        check_pass "/$1 registered"
    else
        check_fail "/$1 NOT registered"
    fi
}

check_command "snapshot"
check_command "setbal"
check_command "setbalance"
check_command "balance"
check_command "finance"
check_command "spending"

# ============================================================
# 4. HANDLER FILES EXIST
# ============================================================
section "HANDLER FILES"

HANDLERS_DIR="/opt/mythos/telegram_bot/handlers"

check_handler() {
    if [ -f "$HANDLERS_DIR/$1" ]; then
        SIZE=$(stat -c%s "$HANDLERS_DIR/$1")
        check_pass "$1 exists (${SIZE} bytes)"
    else
        check_fail "$1 NOT FOUND"
    fi
}

check_handler "snapshot_handler.py"
check_handler "finance_handler.py"
check_handler "iris_handler.py"
check_handler "patch_handlers.py"

# ============================================================
# 5. DATABASE SCHEMA
# ============================================================
section "DATABASE SCHEMA"

# Check accounts table has expected columns
COLS=$(sudo -u postgres psql -d mythos -t -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'accounts' ORDER BY column_name;" 2>/dev/null | tr -d ' ' | tr '\n' ',')

check_column() {
    if echo "$COLS" | grep -q "$1"; then
        check_pass "accounts.$1 exists"
    else
        check_fail "accounts.$1 NOT FOUND"
    fi
}

check_column "current_balance"
check_column "balance_updated_at"
check_column "credit_limit"
check_column "min_payment"
check_column "payment_due_day"
check_column "abbreviation"

# ============================================================
# 6. ACCOUNT COUNT
# ============================================================
section "ACCOUNT DATA"

ACCT_COUNT=$(sudo -u postgres psql -d mythos -t -c "SELECT COUNT(*) FROM accounts WHERE is_active = true;" 2>/dev/null | tr -d ' ')

if [ "$ACCT_COUNT" -ge 10 ]; then
    check_pass "$ACCT_COUNT active accounts (expected 10+)"
else
    check_warn "Only $ACCT_COUNT active accounts (expected 10+)"
fi

# Check for credit card accounts
CC_COUNT=$(sudo -u postgres psql -d mythos -t -c "SELECT COUNT(*) FROM accounts WHERE account_type = 'credit' AND is_active = true;" 2>/dev/null | tr -d ' ')

if [ "$CC_COUNT" -ge 5 ]; then
    check_pass "$CC_COUNT credit card accounts"
else
    check_fail "Only $CC_COUNT credit cards (expected 5)"
fi

# ============================================================
# 7. RECENT BOT LOGS
# ============================================================
section "BOT STARTUP (last 10 lines)"

sudo journalctl -u mythos-bot.service -n 10 --no-pager 2>/dev/null | while read line; do
    log "  $line"
done

# ============================================================
# SUMMARY
# ============================================================
section "SUMMARY"

log ""
log "  Passed:   $PASS_COUNT"
log "  Failed:   $FAIL_COUNT"
log "  Warnings: $WARN_COUNT"
log ""

if [ "$FAIL_COUNT" -eq 0 ]; then
    log "✅ All critical checks passed"
    exit 0
else
    log "❌ $FAIL_COUNT check(s) failed - review above"
    exit 1
fi
