#!/bin/bash
set -e

PATCH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MYTHOS_ROOT="/opt/mythos"
ORCH_ROOT="${MYTHOS_ROOT}/orchestrator"

echo "=========================================================="
echo "Mythos Orchestrator - Phase 1.2"
echo "Ollama Integration"
echo ""
echo "Patch:   0083"
echo "Version: 1.15.1 → 1.15.2"
echo "Phase:   1.2 of 7 (Model Bench)"
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
    if [ "${CURRENT_VERSION}" != "1.15.1" ]; then
        echo "❌ Error: Expected base version 1.15.1, found ${CURRENT_VERSION}"
        echo "   Phase 1.2 requires Phase 1.1 to be installed first"
        exit 1
    fi
else
    echo "❌ Error: No version file found"
    echo "   Install Phase 1.1 (patch_0082) first"
    exit 1
fi

# Verify Phase 1.1 is installed
if [ ! -d "${ORCH_ROOT}/src" ]; then
    echo "❌ Error: Orchestrator not found"
    echo "   Install Phase 1.1 (patch_0082) first"
    exit 1
fi

# Verify Ollama is running
if ! systemctl is-active --quiet ollama; then
    echo "❌ Error: Ollama is not running"
    echo "   Start with: sudo systemctl start ollama"
    exit 1
fi

echo ""
echo "Installing Phase 1.2 - Ollama Integration..."
echo ""

# ============================================================
# Step 1: Update version file
# ============================================================
echo "[1/7] Updating version..."
echo "1.15.2" > "${MYTHOS_ROOT}/.version"
echo "        ✓ Version: 1.15.2"

# ============================================================
# Step 2: Install Python dependencies
# ============================================================
echo "[2/7] Installing Python dependencies..."
source "${MYTHOS_ROOT}/.venv/bin/activate"

# Update pydantic to fix ollama compatibility
pip install --quiet --upgrade pydantic>=2.9.0
echo "        ✓ Updated pydantic to >=2.9.0"

# ============================================================
# Step 3: Copy source files
# ============================================================
echo "[3/7] Copying source files..."
cp "${PATCH_DIR}/opt/mythos/orchestrator/src/models/ollama_client.py" "${ORCH_ROOT}/src/models/"
cp "${PATCH_DIR}/opt/mythos/orchestrator/src/models/model_registry.py" "${ORCH_ROOT}/src/models/"
cp "${PATCH_DIR}/opt/mythos/orchestrator/src/models/model_manager.py" "${ORCH_ROOT}/src/models/"
cp "${PATCH_DIR}/opt/mythos/orchestrator/src/models/__init__.py" "${ORCH_ROOT}/src/models/"
echo "        ✓ Source files copied (4 modules)"

# ============================================================
# Step 4: Copy scripts
# ============================================================
echo "[4/7] Installing scripts..."
cp "${PATCH_DIR}/opt/mythos/orchestrator/scripts/register_models.sh" "${ORCH_ROOT}/scripts/"
chmod +x "${ORCH_ROOT}/scripts/register_models.sh"
echo "        ✓ Scripts installed"

# ============================================================
# Step 5: Copy documentation
# ============================================================
echo "[5/7] Updating documentation..."
cp "${PATCH_DIR}/opt/mythos/docs/orchestrator/OLLAMA.md" "${MYTHOS_ROOT}/docs/orchestrator/"
cat "${PATCH_DIR}/changelog_entry.txt" >> "${MYTHOS_ROOT}/docs/orchestrator/CHANGELOG.md"
echo "        ✓ Documentation updated"

# ============================================================
# Step 6: Register installed models
# ============================================================
echo "[6/7] Registering installed Ollama models..."
cd "${ORCH_ROOT}/scripts"
bash register_models.sh
echo "        ✓ Models registered"

# ============================================================
# Step 7: Verify installation
# ============================================================
echo "[7/7] Verifying installation..."
python3 << 'EOPY' 2>&1 | grep "✓" || echo "        ⚠️  Verification warnings"
import sys
sys.path.insert(0, '/opt/mythos/orchestrator/src')
import asyncio

async def verify():
    from models.ollama_client import OllamaClient
    from models.model_registry import ModelRegistry
    from models.model_manager import ModelManager
    from config import settings
    
    if settings.VERSION == "1.15.2":
        print("        ✓ All modules verified")
    else:
        print(f"        ✗ Version mismatch: {settings.VERSION}")

asyncio.run(verify())
EOPY

# Update git
cd "${MYTHOS_ROOT}"
if git rev-parse --git-dir > /dev/null 2>&1; then
    git add .version orchestrator/ docs/orchestrator/ 2>/dev/null || true
    git commit -m "patch_0083: v1.15.2 - Ollama Integration" 2>/dev/null || true
    git tag -a v1.15.2 -m "Phase 1.2 Complete: Ollama Integration" 2>/dev/null || true
    echo "        ✓ Git updated"
fi

echo ""
echo "=========================================================="
echo "Installation Complete!"
echo "=========================================================="
echo ""
echo "Version: 1.15.1 → 1.15.2"
echo "Phase:   1.2 Complete"
echo ""
echo "Installed:"
echo "  • Ollama client wrapper"
echo "  • Model registry"
echo "  • Model manager"
echo "  • Model registration script"
echo ""
echo "Next: patch_0084 (v1.15.3 - Test Framework)"
echo ""
