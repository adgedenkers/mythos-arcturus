#!/bin/bash
# Rollback script for patch_0082
# Removes Phase 1.1 Core Infrastructure

set -e

MYTHOS_ROOT="/opt/mythos"
ORCH_ROOT="${MYTHOS_ROOT}/orchestrator"

echo "=========================================================="
echo "Rollback: patch_0082 - Phase 1.1"
echo "Core Infrastructure"
echo ""
echo "This will remove:"
echo "  • Orchestrator directory"
echo "  • 7 database tables (orch_*)"
echo "  • Documentation"
echo "  • Version file"
echo "=========================================================="
echo ""

# Verify running as correct user
if [ "$EUID" -eq 0 ]; then
    echo "❌ Error: Do not run as root"
    echo "   Run as: adge"
    exit 1
fi

# Confirm rollback
echo "⚠️  WARNING: This will delete all orchestrator data!"
echo ""
echo "Continue with rollback? (yes/no)"
read -r response

if [ "$response" != "yes" ]; then
    echo "Rollback cancelled"
    exit 0
fi

echo ""
echo "Starting rollback..."
echo ""

# Step 1: Drop database tables
echo "[1/5] Dropping database tables..."
sudo -u postgres psql -d mythos << 'EOSQL' 2>&1 | grep -v "NOTICE" || true
DROP TABLE IF EXISTS orch_test_results CASCADE;
DROP TABLE IF EXISTS orch_test_runs CASCADE;
DROP TABLE IF EXISTS orch_test_questions CASCADE;
DROP TABLE IF EXISTS orch_test_suites CASCADE;
DROP TABLE IF EXISTS orch_model_benchmarks CASCADE;
DROP TABLE IF EXISTS orch_model_capabilities CASCADE;
DROP TABLE IF EXISTS orch_models CASCADE;
EOSQL

TABLE_COUNT=$(sudo -u postgres psql -d mythos -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'orch_%';" | tr -d ' ')

if [ "$TABLE_COUNT" -eq 0 ]; then
    echo "        ✓ Database tables removed"
else
    echo "        ⚠️  Warning: $TABLE_COUNT orch_* tables still exist"
fi

# Step 2: Remove orchestrator directory
echo "[2/5] Removing orchestrator directory..."
if [ -d "$ORCH_ROOT" ]; then
    rm -rf "$ORCH_ROOT"
    echo "        ✓ Orchestrator directory removed"
else
    echo "        ✓ Orchestrator directory not found (already removed)"
fi

# Step 3: Remove documentation
echo "[3/5] Removing documentation..."
if [ -d "${MYTHOS_ROOT}/docs/orchestrator" ]; then
    rm -rf "${MYTHOS_ROOT}/docs/orchestrator"
    echo "        ✓ Documentation removed"
else
    echo "        ✓ Documentation not found (already removed)"
fi

# Step 4: Restore version file
echo "[4/5] Restoring version file..."
if [ -f "${MYTHOS_ROOT}/.version" ]; then
    echo "1.0.0" > "${MYTHOS_ROOT}/.version"
    echo "        ✓ Version restored to 1.0.0"
else
    echo "        ✓ Version file not found"
fi

# Step 5: Update git
echo "[5/5] Updating git..."
cd "${MYTHOS_ROOT}"
if git rev-parse --git-dir > /dev/null 2>&1; then
    git add -A 2>/dev/null || true
    
    if ! git diff --cached --quiet; then
        git commit -m "Rollback patch_0082: Removed Phase 1.1 Core Infrastructure" 2>/dev/null || true
        
        # Remove tag if it exists
        if git tag -l | grep -q "^v1.15.1$"; then
            git tag -d v1.15.1 2>/dev/null || true
            echo "        ✓ Git tag v1.15.1 removed"
        fi
        
        echo "        ✓ Git updated"
    else
        echo "        ✓ No git changes to commit"
    fi
fi

echo ""
echo "=========================================================="
echo "Rollback Complete"
echo "=========================================================="
echo ""
echo "Removed:"
echo "  • Orchestrator directory: ${ORCH_ROOT}"
echo "  • Database tables: 7 (orch_*)"
echo "  • Documentation: docs/orchestrator/"
echo "  • Version: 1.15.1 → 1.0.0"
echo ""
echo "System restored to: v1.0.0"
echo ""
echo "To reinstall Phase 1.1:"
echo "  Deploy patch_0082 again"
echo ""
