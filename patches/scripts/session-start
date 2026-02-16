#!/bin/bash
# ============================================================
# Mythos System Diagnostic - Standard Session Start
# ============================================================
# Run this at the start of any AI session to get full context
# Usage: mythos-diag [--full|--patch|--quick]
# ============================================================

set -e

# Parse arguments
MODE="${1:-full}"

OUTPUT_FILE=~/mythos_diag.txt

# Clear output file
> "$OUTPUT_FILE"

case "$MODE" in
    --full|full)
        echo "Running full diagnostic..."
        ;;
    --patch|patch)
        echo "Running patch-focused diagnostic..."
        ;;
    --quick|quick)
        echo "Running quick diagnostic..."
        ;;
    *)
        echo "Usage: mythos-diag [--full|--patch|--quick]"
        exit 1
        ;;
esac

# ============================================================
# ALWAYS INCLUDED (ALL MODES)
# ============================================================

echo "=== MYTHOS SYSTEM DIAGNOSTIC ===" >> "$OUTPUT_FILE"
echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')" >> "$OUTPUT_FILE"
echo "Mode: $MODE" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# ============================================================
# PATCH INFO (all modes)
# ============================================================

echo "=== LATEST PATCH INFO ===" >> "$OUTPUT_FILE"

if [ -x /opt/mythos/patches/scripts/get_next_patch_info.sh ]; then
    /opt/mythos/patches/scripts/get_next_patch_info.sh >> "$OUTPUT_FILE" 2>&1
else
    # Fallback if patch 0080 not installed yet
    LATEST_PATCH=$(ls -1d /opt/mythos/patches/patch_* 2>/dev/null | sort -V | tail -1)
    if [ -n "$LATEST_PATCH" ]; then
        echo "Latest patch: $(basename $LATEST_PATCH)" >> "$OUTPUT_FILE"
        LATEST_NUM=$(basename "$LATEST_PATCH" | grep -oP 'patch_\K\d+')
        NEXT_NUM=$(printf "%04d" $((10#$LATEST_NUM + 1)))
        echo "Next patch number: patch_${NEXT_NUM}_description" >> "$OUTPUT_FILE"
        
        if [ -f "$LATEST_PATCH/manifest.json" ]; then
            echo "" >> "$OUTPUT_FILE"
            echo "Latest manifest:" >> "$OUTPUT_FILE"
            cat "$LATEST_PATCH/manifest.json" >> "$OUTPUT_FILE" 2>&1
        fi
    else
        echo "No patches found" >> "$OUTPUT_FILE"
    fi
fi

# ============================================================
# QUICK MODE - Stop here
# ============================================================

if [ "$MODE" = "quick" ] || [ "$MODE" = "--quick" ]; then
    echo "" >> "$OUTPUT_FILE"
    echo "=== QUICK SYSTEM STATUS ===" >> "$OUTPUT_FILE"
    
    # Service status
    echo "" >> "$OUTPUT_FILE"
    echo "Services:" >> "$OUTPUT_FILE"
    for service in mythos-api mythos-bot mythos-patch-monitor; do
        if systemctl is-active --quiet ${service}.service 2>/dev/null; then
            echo "  ✓ ${service}" >> "$OUTPUT_FILE"
        else
            echo "  ✗ ${service}" >> "$OUTPUT_FILE"
        fi
    done
    
    cat "$OUTPUT_FILE" | clip && echo "✓ Copied to clipboard"
    exit 0
fi

# ============================================================
# PATCH MODE - Patch-specific info
# ============================================================

if [ "$MODE" = "patch" ] || [ "$MODE" = "--patch" ]; then
    echo "" >> "$OUTPUT_FILE"
    echo "=== PATCH GENERATION CONTEXT ===" >> "$OUTPUT_FILE"
    
    # Recent patches
    echo "" >> "$OUTPUT_FILE"
    echo "Recent patches (last 5):" >> "$OUTPUT_FILE"
    ls -1d /opt/mythos/patches/patch_* 2>/dev/null | sort -V | tail -5 | while read patch; do
        PATCH_NAME=$(basename "$patch")
        if [ -f "$patch/manifest.json" ]; then
            TITLE=$(python3 -c "import json; print(json.load(open('$patch/manifest.json'))['patch']['title'])" 2>/dev/null || echo "No title")
            echo "  $PATCH_NAME - $TITLE" >> "$OUTPUT_FILE"
        else
            echo "  $PATCH_NAME" >> "$OUTPUT_FILE"
        fi
    done
    
    # Manifest template location
    echo "" >> "$OUTPUT_FILE"
    if [ -f /opt/mythos/patches/MANIFEST_TEMPLATE.json ]; then
        echo "Manifest template: /opt/mythos/patches/MANIFEST_TEMPLATE.json" >> "$OUTPUT_FILE"
    else
        echo "⚠️  Manifest template not found (install patch 0080)" >> "$OUTPUT_FILE"
    fi
    
    # AI handoff guide
    if [ -f /opt/mythos/docs/patch_system/AI_PATCH_GENERATION_GUIDE.md ]; then
        echo "AI Guide: /opt/mythos/docs/patch_system/AI_PATCH_GENERATION_GUIDE.md" >> "$OUTPUT_FILE"
    else
        echo "⚠️  AI guide not found (install patch 0080)" >> "$OUTPUT_FILE"
    fi
fi

# ============================================================
# FULL MODE - Complete system state
# ============================================================

if [ "$MODE" = "full" ] || [ "$MODE" = "--full" ]; then
    echo "" >> "$OUTPUT_FILE"
    echo "=== TODO ===" >> "$OUTPUT_FILE"
    if [ -f /opt/mythos/docs/TODO.md ]; then
        cat /opt/mythos/docs/TODO.md >> "$OUTPUT_FILE" 2>&1
    else
        echo "TODO.md not found" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "=== ARCHITECTURE ===" >> "$OUTPUT_FILE"
    if [ -f /opt/mythos/docs/ARCHITECTURE.md ]; then
        cat /opt/mythos/docs/ARCHITECTURE.md >> "$OUTPUT_FILE" 2>&1
    else
        echo "ARCHITECTURE.md not found" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "=== SYSTEM STATUS ===" >> "$OUTPUT_FILE"
    
    # Services
    echo "" >> "$OUTPUT_FILE"
    echo "Services:" >> "$OUTPUT_FILE"
    for service in mythos-api mythos-bot mythos-patch-monitor mythos-worker-grid; do
        if systemctl is-active --quiet ${service}.service 2>/dev/null; then
            echo "  ✓ ${service}" >> "$OUTPUT_FILE"
        else
            echo "  ✗ ${service}" >> "$OUTPUT_FILE"
        fi
    done
    
    # Database
    echo "" >> "$OUTPUT_FILE"
    echo "Database:" >> "$OUTPUT_FILE"
    if sudo -u postgres psql -d mythos -c "SELECT 1" >/dev/null 2>&1; then
        TABLE_COUNT=$(sudo -u postgres psql -d mythos -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'" 2>/dev/null | tr -d ' ')
        echo "  ✓ PostgreSQL ($TABLE_COUNT tables)" >> "$OUTPUT_FILE"
    else
        echo "  ✗ PostgreSQL" >> "$OUTPUT_FILE"
    fi
    
    # Git status
    echo "" >> "$OUTPUT_FILE"
    echo "Git:" >> "$OUTPUT_FILE"
    if [ -d /opt/mythos/.git ]; then
        cd /opt/mythos
        echo "  Branch: $(git branch --show-current)" >> "$OUTPUT_FILE"
        echo "  Last commit: $(git log -1 --format='%h - %s' 2>/dev/null)" >> "$OUTPUT_FILE"
        
        if git remote get-url origin >/dev/null 2>&1; then
            echo "  Remote: $(git remote get-url origin)" >> "$OUTPUT_FILE"
        else
            echo "  Remote: Not configured" >> "$OUTPUT_FILE"
        fi
    else
        echo "  Not a git repository" >> "$OUTPUT_FILE"
    fi
fi

# ============================================================
# COPY TO CLIPBOARD
# ============================================================

cat "$OUTPUT_FILE" | clip && echo "✓ Diagnostic copied to clipboard"

echo ""
echo "Diagnostic saved to: $OUTPUT_FILE"
echo "Content copied to clipboard"
echo ""
echo "Mode: $MODE"
case "$MODE" in
    quick|--quick)
        echo "  (Patch info + service status only)"
        ;;
    patch|--patch)
        echo "  (Patch info + generation context)"
        ;;
    full|--full)
        echo "  (Complete system state)"
        ;;
esac
