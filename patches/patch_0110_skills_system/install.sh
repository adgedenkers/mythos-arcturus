#!/bin/bash
set -euo pipefail

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
MYTHOS_ROOT="/opt/mythos"

echo "=== Installing patch 0110: Mythos Skills System ==="

# Create skills directory structure
mkdir -p "$MYTHOS_ROOT/skills/analytical"
mkdir -p "$MYTHOS_ROOT/skills/builder"
mkdir -p "$MYTHOS_ROOT/skills/meta"
mkdir -p "$MYTHOS_ROOT/skills/templates"

# Copy all skill files
echo "Deploying skill files..."
cp "$PATCH_DIR/opt/mythos/skills/REGISTRY.yaml" "$MYTHOS_ROOT/skills/REGISTRY.yaml"
cp "$PATCH_DIR/opt/mythos/skills/README.md" "$MYTHOS_ROOT/skills/README.md"

cp "$PATCH_DIR/opt/mythos/skills/analytical/soul_stratigraphy.md" "$MYTHOS_ROOT/skills/analytical/"
cp "$PATCH_DIR/opt/mythos/skills/analytical/western_tropical_natal_chart.md" "$MYTHOS_ROOT/skills/analytical/"

cp "$PATCH_DIR/opt/mythos/skills/builder/build_patch.md" "$MYTHOS_ROOT/skills/builder/"
cp "$PATCH_DIR/opt/mythos/skills/builder/build_feature_api.md" "$MYTHOS_ROOT/skills/builder/"
cp "$PATCH_DIR/opt/mythos/skills/builder/build_feature_self.md" "$MYTHOS_ROOT/skills/builder/"
cp "$PATCH_DIR/opt/mythos/skills/builder/build_feature_telegram_mode.md" "$MYTHOS_ROOT/skills/builder/"
cp "$PATCH_DIR/opt/mythos/skills/builder/build_feature_telegram_tool.md" "$MYTHOS_ROOT/skills/builder/"

cp "$PATCH_DIR/opt/mythos/skills/meta/humandoc_to_skill.md" "$MYTHOS_ROOT/skills/meta/"

cp "$PATCH_DIR/opt/mythos/skills/templates/SKILL_TEMPLATE.md" "$MYTHOS_ROOT/skills/templates/"

# Verify
echo "=== Verifying ==="
FILE_COUNT=$(find "$MYTHOS_ROOT/skills" -name "*.md" -o -name "*.yaml" | wc -l)
echo "✓ Deployed $FILE_COUNT skill files to $MYTHOS_ROOT/skills/"
ls -la "$MYTHOS_ROOT/skills/"
echo ""
echo "=== Skills directory structure ==="
find "$MYTHOS_ROOT/skills" -type f | sort

echo "=== Patch 0110 installed successfully ==="
