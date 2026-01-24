#!/bin/bash
# ============================================================================
# MYTHOS CODEBASE EXPORT SCRIPT
# Creates a zip of /opt/mythos/ excluding large/sensitive/generated files
# ============================================================================

OUTPUT_DIR="$HOME"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="$OUTPUT_DIR/mythos_codebase_$TIMESTAMP.zip"

echo "============================================"
echo "Mythos Codebase Export"
echo "============================================"
echo ""
echo "Source: /opt/mythos/"
echo "Output: $OUTPUT_FILE"
echo ""
echo "Excluding:"
echo "  - Images (*.jpeg, *.jpg, *.png, *.gif, *.webp, *.heic)"
echo "  - Packages (*.deb, *.rpm)"
echo "  - Archives (*.zip, *.tar, *.gz, *.tar.gz)"
echo "  - Environment files (.env, .env.*)"
echo "  - Python cache (__pycache__/)"
echo "  - Virtual environments (.venv/, venv/, env/)"
echo "  - Git directories (.git/)"
echo "  - Node modules (node_modules/)"
echo "  - Large binaries (*.exe, *.bin, *.so, *.dylib)"
echo "  - Database files (*.db, *.sqlite, *.sqlite3)"
echo "  - Log files (*.log)"
echo ""

# Check if source exists
if [ ! -d "/opt/mythos" ]; then
    echo "ERROR: /opt/mythos/ does not exist"
    exit 1
fi

echo "Creating archive..."
echo ""

cd /opt

zip -r "$OUTPUT_FILE" mythos/ \
    -x "*.jpeg" \
    -x "*.jpg" \
    -x "*.png" \
    -x "*.gif" \
    -x "*.webp" \
    -x "*.heic" \
    -x "*.JPEG" \
    -x "*.JPG" \
    -x "*.PNG" \
    -x "*.deb" \
    -x "*.rpm" \
    -x "*.zip" \
    -x "*.tar" \
    -x "*.gz" \
    -x "*.tar.gz" \
    -x "*.tgz" \
    -x "*.env" \
    -x "*.env.*" \
    -x "*/.env" \
    -x "*/.env.*" \
    -x "*__pycache__/*" \
    -x "*/__pycache__/*" \
    -x "*/.venv/*" \
    -x "*/venv/*" \
    -x "*/env/*" \
    -x "*/.git/*" \
    -x "*.git/*" \
    -x "*/node_modules/*" \
    -x "*node_modules/*" \
    -x "*.exe" \
    -x "*.bin" \
    -x "*.so" \
    -x "*.dylib" \
    -x "*.db" \
    -x "*.sqlite" \
    -x "*.sqlite3" \
    -x "*.log" \
    -x "*.Log" \
    -x "*.LOG" \
    -x "*/assets/images/*" \
    -x "mythos/assets/images/*" \
    -x "*/archive/*.zip" \
    -x "mythos/*/archive/*"

echo ""
echo "============================================"
echo "Export Complete!"
echo "============================================"
echo ""
echo "Output file: $OUTPUT_FILE"
echo "File size: $(du -h "$OUTPUT_FILE" | cut -f1)"
echo ""

# List what's included (top-level structure)
echo "Contents preview (top-level):"
unzip -l "$OUTPUT_FILE" | head -50
echo "..."
echo ""

# Count files by extension
echo "File types included:"
unzip -l "$OUTPUT_FILE" | grep -oE '\.[a-zA-Z0-9]+$' | sort | uniq -c | sort -rn | head -20
echo ""

echo "Upload this file to Claude to review the codebase."
echo ""
