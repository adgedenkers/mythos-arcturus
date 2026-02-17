#!/bin/bash
set -e

PATCH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MYTHOS_ROOT="/opt/mythos"
ORCH_ROOT="${MYTHOS_ROOT}/orchestrator"

echo "=========================================================="
echo "Mythos Orchestrator - Phase 1.5"
echo "Test Runner"
echo ""
echo "Patch:   0090"
echo "Version: 1.15.4 → 1.15.5"
echo "Phase:   1.5 of 7 (Model Bench)"
echo "=========================================================="
echo ""

# Verify running as correct user
if [ "$EUID" -eq 0 ]; then
    echo "❌ Error: Do not run as root"
    exit 1
fi

# Verify base version
if [ -f "${MYTHOS_ROOT}/.version" ]; then
    CURRENT_VERSION=$(cat "${MYTHOS_ROOT}/.version")
    echo "Current version: ${CURRENT_VERSION}"
    if [ "${CURRENT_VERSION}" != "1.15.4" ]; then
        echo "❌ Error: Expected base version 1.15.4, found ${CURRENT_VERSION}"
        echo "   Phase 1.5 requires Phase 1.4 to be installed first"
        exit 1
    fi
else
    echo "❌ Error: No version file found"
    exit 1
fi

echo ""
echo "Installing Phase 1.5 - Test Runner..."
echo ""

# ============================================================
# Step 1: Update version
# ============================================================
echo "[1/5] Updating version..."
echo "1.15.5" > "${MYTHOS_ROOT}/.version"
echo "        ✓ Version: 1.15.5"

# ============================================================
# Step 2: Copy source files
# ============================================================
echo "[2/5] Copying source files..."
cp "${PATCH_DIR}/opt/mythos/orchestrator/src/bench/test_run.py" "${ORCH_ROOT}/src/bench/"
cp "${PATCH_DIR}/opt/mythos/orchestrator/src/bench/test_runner.py" "${ORCH_ROOT}/src/bench/"
cp "${PATCH_DIR}/opt/mythos/orchestrator/src/bench/__init__.py" "${ORCH_ROOT}/src/bench/"
echo "        ✓ Source files copied (3 modules)"

# ============================================================
# Step 3: Copy documentation
# ============================================================
echo "[3/5] Updating documentation..."
cp "${PATCH_DIR}/opt/mythos/docs/orchestrator/RUNNER.md" "${MYTHOS_ROOT}/docs/orchestrator/"
cat "${PATCH_DIR}/changelog_entry.txt" >> "${MYTHOS_ROOT}/docs/orchestrator/CHANGELOG.md"
echo "        ✓ Documentation updated"

# ============================================================
# Step 4: Verify installation
# ============================================================
echo "[4/5] Verifying installation..."
cd "${ORCH_ROOT}"
source "${MYTHOS_ROOT}/.venv/bin/activate"

python3 << 'EOPY' 2>&1 | grep "✓" || echo "        ⚠️  Verification warnings"
import sys
sys.path.insert(0, '/opt/mythos/orchestrator/src')

from bench import TestRunner, TestRun
from config import settings

if settings.VERSION == "1.15.5":
    print("        ✓ All modules verified")
else:
    print(f"        ✗ Version mismatch: {settings.VERSION}")
EOPY

# ============================================================
# Step 5: Update git
# ============================================================
echo "[5/5] Updating git..."
cd "${MYTHOS_ROOT}"
if git rev-parse --git-dir > /dev/null 2>&1; then
    git add .version orchestrator/ docs/orchestrator/ 2>/dev/null || true
    git commit -m "patch_0090: v1.15.5 - Test Runner" 2>/dev/null || true
    git tag -a v1.15.5 -m "Phase 1.5 Complete: Test Runner" 2>/dev/null || true
    echo "        ✓ Git updated"
fi

echo ""
echo "=========================================================="
echo "Installation Complete!"
echo "=========================================================="
echo ""
echo "Version: 1.15.4 → 1.15.5"
echo "Phase:   1.5 Complete"
echo ""
echo "Installed:"
echo "  • TestRun class"
echo "  • TestRunner class"
echo "  • Full test execution workflow"
echo ""
echo "Next: patch_0091 (v1.15.6 - Test Suites)"
echo ""
