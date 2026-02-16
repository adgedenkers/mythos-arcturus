#!/bin/bash
# ============================================================
# PATCH 0080: Manifest System
# ============================================================
# The LAST patch using integer-only numbering.
# Implements manifest.json standard for all future patches.
# Future patches use semantic versioning: MAJOR.MINOR.PATCH
# ============================================================

set -e

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
MYTHOS_ROOT="/opt/mythos"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=========================================="
echo "Patch 0080: Manifest System"
echo "=========================================="
echo ""
echo "This is the LAST patch using integer-only numbering."
echo "Future patches will use semantic versioning."
echo ""

# ============================================================
# 1. INSTALL SCRIPTS
# ============================================================
echo "[1/6] Installing patch management scripts..."

cp "$PATCH_DIR/opt/mythos/patches/scripts/get_next_patch_info.sh" \
   "$MYTHOS_ROOT/patches/scripts/"
chmod +x "$MYTHOS_ROOT/patches/scripts/get_next_patch_info.sh"

cp "$PATCH_DIR/opt/mythos/patches/scripts/validate_manifest.sh" \
   "$MYTHOS_ROOT/patches/scripts/"
chmod +x "$MYTHOS_ROOT/patches/scripts/validate_manifest.sh"

cp "$PATCH_DIR/opt/mythos/patches/scripts/mythos-diag" \
   "$MYTHOS_ROOT/patches/scripts/"
chmod +x "$MYTHOS_ROOT/patches/scripts/mythos-diag"

echo "  ✓ get_next_patch_info.sh installed"
echo "  ✓ validate_manifest.sh installed"
echo "  ✓ mythos-diag installed"

# Create symlink for easy access
if [ ! -L /usr/local/bin/mythos-diag ]; then
    sudo ln -sf "$MYTHOS_ROOT/patches/scripts/mythos-diag" /usr/local/bin/mythos-diag 2>/dev/null || true
    echo "  ✓ mythos-diag symlinked to /usr/local/bin/"
fi

# ============================================================
# 2. INSTALL AI HANDOFF GUIDE
# ============================================================
echo ""
echo "[2/6] Installing AI handoff guide..."

mkdir -p "$MYTHOS_ROOT/docs/patch_system"
cp "$PATCH_DIR/AI_PATCH_GENERATION_GUIDE.md" \
   "$MYTHOS_ROOT/docs/patch_system/"

echo "  ✓ AI_PATCH_GENERATION_GUIDE.md → /opt/mythos/docs/patch_system/"

# ============================================================
# 3. CREATE MANIFEST TEMPLATE
# ============================================================
echo ""
echo "[3/6] Creating manifest template..."

cat > "$MYTHOS_ROOT/patches/MANIFEST_TEMPLATE.json" << 'EOF'
{
  "manifest_version": "1.0.0",
  "patch": {
    "number": "NNNN",
    "semantic_version": "MAJOR.MINOR.PATCH",
    "name": "short_name",
    "title": "Patch Title",
    "description": "What this patch does",
    "date": "YYYY-MM-DD",
    "author": "AI_Name"
  },
  "versioning": {
    "current_system_version": "1.15.0",
    "new_system_version": "1.16.0",
    "version_increment": "minor|patch|major",
    "reason": "Why this version increment"
  },
  "dependencies": {
    "required_patches": [],
    "required_services": [],
    "python_packages": [],
    "system_packages": [],
    "minimum_system_version": "1.0.0"
  },
  "changes": {
    "files_added": [],
    "files_modified": [],
    "database_changes": [],
    "services_affected": []
  },
  "installation": {
    "estimated_time_minutes": 5,
    "requires_restart": true,
    "requires_sudo": true,
    "safe_mode": true
  },
  "testing": {
    "verification_steps": [],
    "verification_commands": []
  },
  "rollback": {
    "safe": true,
    "complexity": "low",
    "automated": true,
    "notes": ""
  }
}
EOF

echo "  ✓ MANIFEST_TEMPLATE.json created"

# ============================================================
# 4. UPDATE DOCUMENTATION
# ============================================================
echo ""
echo "[4/6] Updating documentation..."

# Add manifest system to TODO.md
if ! grep -q "Manifest System" "$MYTHOS_ROOT/docs/TODO.md" 2>/dev/null; then
    cat >> "$MYTHOS_ROOT/docs/TODO.md" << 'EOF'

## Manifest System (Patch 0080)

All patches after 0080 MUST include manifest.json with:
- Semantic versioning (MAJOR.MINOR.PATCH)
- Dependencies list
- Change tracking
- Validation before installation

Tools:
- `/opt/mythos/patches/scripts/get_next_patch_info.sh` - Get next version
- `/opt/mythos/patches/scripts/validate_manifest.sh` - Validate manifest
- `/opt/mythos/docs/patch_system/AI_PATCH_GENERATION_GUIDE.md` - AI handoff

EOF
    echo "  ✓ TODO.md updated"
else
    echo "  → TODO.md already has manifest info"
fi

echo ""
echo "[5/6] Creating standard diagnostic command..."

# Add diagnostic info to documentation
if ! grep -q "mythos-diag" "$MYTHOS_ROOT/docs/TODO.md" 2>/dev/null; then
    cat >> "$MYTHOS_ROOT/docs/TODO.md" << 'EOF'

### Standard Diagnostic Command

Run at session start to get all context:

```bash
mythos-diag            # Full diagnostic (default)
mythos-diag --patch    # Patch-focused (for patch generation)
mythos-diag --quick    # Quick status check
```

Output includes:
- Latest patch info
- Next version options
- System documentation
- Service status
- Git status

EOF
    echo "  ✓ Diagnostic command documented in TODO.md"
fi

# ============================================================
# 6. VERIFY INSTALLATION
# ============================================================
echo ""
echo "[6/6] Verifying installation..."

VERIFY_OK=true

# Check scripts are executable
if [ ! -x "$MYTHOS_ROOT/patches/scripts/get_next_patch_info.sh" ]; then
    echo "  ✗ get_next_patch_info.sh not executable"
    VERIFY_OK=false
else
    echo "  ✓ get_next_patch_info.sh executable"
fi

if [ ! -x "$MYTHOS_ROOT/patches/scripts/validate_manifest.sh" ]; then
    echo "  ✗ validate_manifest.sh not executable"
    VERIFY_OK=false
else
    echo "  ✓ validate_manifest.sh executable"
fi

# Check mythos-diag
if [ ! -x "$MYTHOS_ROOT/patches/scripts/mythos-diag" ]; then
    echo "  ✗ mythos-diag not executable"
    VERIFY_OK=false
else
    echo "  ✓ mythos-diag executable"
fi

# Check symlink
if [ -L /usr/local/bin/mythos-diag ]; then
    echo "  ✓ mythos-diag available in PATH"
fi

# Check template exists
if [ ! -f "$MYTHOS_ROOT/patches/MANIFEST_TEMPLATE.json" ]; then
    echo "  ✗ Template not found"
    VERIFY_OK=false
else
    echo "  ✓ MANIFEST_TEMPLATE.json exists"
fi

# Validate this patch's manifest
if "$MYTHOS_ROOT/patches/scripts/validate_manifest.sh" "$PATCH_DIR/manifest.json" > /dev/null 2>&1; then
    echo "  ✓ This patch's manifest is valid"
else
    echo "  ✗ This patch's manifest failed validation"
    VERIFY_OK=false
fi

echo ""
if [ "$VERIFY_OK" = true ]; then
    echo "✅ Installation verified"
else
    echo "⚠️  Some verification checks failed"
fi

# ============================================================
# SUMMARY
# ============================================================
echo ""
echo "=========================================="
echo "Patch 0080 Complete"
echo "=========================================="
echo ""
echo "Installed:"
echo "  → /opt/mythos/patches/scripts/get_next_patch_info.sh"
echo "  → /opt/mythos/patches/scripts/validate_manifest.sh"
echo "  → /opt/mythos/patches/scripts/mythos-diag"
echo "  → /usr/local/bin/mythos-diag (symlink)"
echo "  → /opt/mythos/patches/MANIFEST_TEMPLATE.json"
echo "  → /opt/mythos/docs/patch_system/AI_PATCH_GENERATION_GUIDE.md"
echo ""
echo "IMPORTANT: This is the LAST integer-only patch number."
echo ""
echo "Future patches use semantic versioning:"
echo "  • MAJOR.MINOR.PATCH format in manifest"
echo "  • Directory names still use patch_NNNN_ for compatibility"
echo "  • All patches MUST include manifest.json"
echo ""
echo "Standard diagnostic command:"
echo "  mythos-diag            # Full system state"
echo "  mythos-diag --patch    # Patch generation context"
echo "  mythos-diag --quick    # Quick status"
echo ""
echo "Get next patch info:"
echo "  /opt/mythos/patches/scripts/get_next_patch_info.sh"
echo ""
echo "Next patch will be: 1.15.1 (or 1.16.0 for new features)"
echo ""
