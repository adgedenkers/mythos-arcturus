#!/bin/bash
set -euo pipefail

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
MYTHOS_ROOT="/opt/mythos"
VENV_PY="/opt/mythos/.venv/bin/python3"

echo "=== Installing patch 0111: Skills awareness + patch status fix ==="

# --- Fix 1: Patch status numbering ---
echo "Deploying fixed patch_handlers.py..."
cp "$PATCH_DIR/opt/mythos/telegram_bot/handlers/patch_handlers.py" \
   "$MYTHOS_ROOT/telegram_bot/handlers/patch_handlers.py"
echo "✓ patch_handlers.py updated"

# --- Fix 2: Skills context builder ---
echo "Deploying skills_context.py..."
cp "$PATCH_DIR/opt/mythos/core/skills_context.py" \
   "$MYTHOS_ROOT/core/skills_context.py"
echo "✓ skills_context.py deployed"

# Ensure PyYAML is available in venv (needed for REGISTRY.yaml parsing)
echo "Checking PyYAML..."
$VENV_PY -c "import yaml" 2>/dev/null || {
    echo "Installing PyYAML..."
    $VENV_PY -m pip install pyyaml --quiet
}
echo "✓ PyYAML available"

# --- Fix 3: Inject skills awareness into chat_mode.py ---
echo "Backing up chat_mode.py..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp "$MYTHOS_ROOT/telegram_bot/handlers/chat_mode.py" \
   "$MYTHOS_ROOT/telegram_bot/handlers/chat_mode.py.bak.${TIMESTAMP}"

echo "Injecting skills + life context into Iris system prompt..."
cp "$PATCH_DIR/opt/mythos/patches/patch_0111_inject_skills.py" \
   "$MYTHOS_ROOT/patches/patch_0111_inject_skills.py"
$VENV_PY "$MYTHOS_ROOT/patches/patch_0111_inject_skills.py"
echo "✓ chat_mode.py patched"

# --- Restart affected services ---
echo "Restarting bot service..."
sudo systemctl restart mythos-bot.service

# --- Verify ---
echo ""
echo "=== Verifying ==="
systemctl is-active mythos-bot.service && echo "✓ Bot service running" || echo "✗ Bot service failed"

# Test skills context output
echo ""
echo "Testing skills context builder:"
cd "$MYTHOS_ROOT" && $VENV_PY -c "
import sys
sys.path.insert(0, '$MYTHOS_ROOT')
from core.skills_context import build_skills_context
ctx = build_skills_context()
if ctx:
    print(f'✓ Skills context: {len(ctx)} chars, {len(ctx.split(chr(10)))} lines')
    # Show first 3 lines
    for line in ctx.strip().split(chr(10))[:3]:
        print(f'  {line}')
else:
    print('✗ Skills context returned empty')
"

echo ""
echo "=== Patch 0111 installed successfully ==="
echo "Changes:"
echo "  1. /patch_status now shows highest real patch # (ignores #9999 test patches)"
echo "  2. Iris now has skills awareness via REGISTRY.yaml injection"
echo "  3. Life context + skills context injected into system prompt builder"
