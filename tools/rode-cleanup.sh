#!/bin/bash
# rode-cleanup.sh — One-time dedup of /opt/mythos/voice_memos/incoming
# 
# What it does:
#   1. Removes all zero-byte files (hash d41d8cd98f00b204e9800998ecf8427e)
#   2. For each duplicate group (same MD5), keeps the file WITHOUT a _b/_c/etc 
#      suffix (the original), deletes all collision variants
#   3. Generates a manifest of all surviving files for the updated rode-transfer
#
# Usage:
#   ./rode-cleanup.sh              # Dry run — shows what would be deleted
#   ./rode-cleanup.sh --confirm    # Actually delete duplicates
#
set -euo pipefail

TARGET="/opt/mythos/voice_memos/incoming"
MANIFEST="/opt/mythos/voice_memos/incoming/.rode-manifest.json"
CONFIRM=false
[[ "${1:-}" == "--confirm" ]] && CONFIRM=true

echo "═══════════════════════════════════════════════════════════"
echo "  RØDE Cleanup — Deduplicate incoming voice memos"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  Target:  $TARGET"
echo "  Mode:    $( $CONFIRM && echo 'LIVE — files WILL be deleted' || echo 'DRY RUN — nothing will be changed' )"
echo ""

# ── Phase 1: Find and remove zero-byte files ────────────────────────────────
echo "── Phase 1: Zero-byte files ──────────────────────────────"
ZERO_FILES=()
while IFS= read -r -d '' f; do
    ZERO_FILES+=("$f")
done < <(find "$TARGET" -type f -size 0 -print0)

echo "  Found: ${#ZERO_FILES[@]} zero-byte files"

ZERO_BYTES=0
if [[ ${#ZERO_FILES[@]} -gt 0 ]]; then
    if $CONFIRM; then
        for f in "${ZERO_FILES[@]}"; do
            rm -f "$f"
        done
        echo "  ✓ Deleted ${#ZERO_FILES[@]} zero-byte files"
    else
        echo "  Would delete ${#ZERO_FILES[@]} zero-byte files"
        # Show first 5
        for f in "${ZERO_FILES[@]:0:5}"; do
            echo "    🗑  $(basename "$f")"
        done
        [[ ${#ZERO_FILES[@]} -gt 5 ]] && echo "    ... and $((${#ZERO_FILES[@]} - 5)) more"
    fi
fi
echo ""

# ── Phase 2: MD5-based deduplication ────────────────────────────────────────
echo "── Phase 2: Content-based dedup ──────────────────────────"
echo "  Hashing all remaining WAV files (this takes a while)..."

# Build hash → files mapping
# We need to hash only non-zero files
declare -A HASH_TO_FILES
TOTAL_FILES=0
TOTAL_HASHED=0

while IFS= read -r -d '' f; do
    # Skip zero-byte (already handled in phase 1, but in dry-run they still exist)
    [[ ! -s "$f" ]] && continue
    
    TOTAL_FILES=$((TOTAL_FILES + 1))
    md5=$(md5sum "$f" | awk '{print $1}')
    
    if [[ -n "${HASH_TO_FILES[$md5]:-}" ]]; then
        HASH_TO_FILES[$md5]="${HASH_TO_FILES[$md5]}"$'\n'"$f"
    else
        HASH_TO_FILES[$md5]="$f"
    fi
    TOTAL_HASHED=$((TOTAL_HASHED + 1))
    
    # Progress indicator every 20 files
    if (( TOTAL_HASHED % 20 == 0 )); then
        printf "\r  Hashed %d files..." "$TOTAL_HASHED"
    fi
done < <(find "$TARGET" -type f \( -name "*.WAV" -o -name "*.wav" \) -print0)

printf "\r  Hashed %d files.                    \n" "$TOTAL_HASHED"

# Now find duplicates and decide what to keep
KEEP_COUNT=0
DELETE_COUNT=0
DELETE_BYTES=0
KEEP_FILES=()

for md5 in "${!HASH_TO_FILES[@]}"; do
    # Split files for this hash
    mapfile -t files <<< "${HASH_TO_FILES[$md5]}"
    
    if [[ ${#files[@]} -eq 1 ]]; then
        # Only one file with this hash — keep it
        KEEP_COUNT=$((KEEP_COUNT + 1))
        KEEP_FILES+=("${files[0]}")
        continue
    fi
    
    # Multiple files — pick the one to keep
    # Priority: file WITHOUT _b/_c/_d suffix wins (it's the original import)
    KEEPER=""
    for f in "${files[@]}"; do
        base=$(basename "$f" .WAV)
        # Check if this file has NO collision suffix (_b, _c, _d, etc)
        if [[ ! "$base" =~ _[b-z]$ ]]; then
            KEEPER="$f"
            break
        fi
    done
    
    # If all have suffixes (shouldn't happen), keep the first one
    [[ -z "$KEEPER" ]] && KEEPER="${files[0]}"
    
    KEEP_COUNT=$((KEEP_COUNT + 1))
    KEEP_FILES+=("$KEEPER")
    
    # Delete the rest
    for f in "${files[@]}"; do
        [[ "$f" == "$KEEPER" ]] && continue
        fsize=$(stat -c %s "$f" 2>/dev/null || echo 0)
        DELETE_BYTES=$((DELETE_BYTES + fsize))
        DELETE_COUNT=$((DELETE_COUNT + 1))
        
        if $CONFIRM; then
            rm -f "$f"
        fi
    done
done

DELETE_GB=$(echo "scale=1; $DELETE_BYTES / 1073741824" | bc 2>/dev/null || echo "?")
echo ""
echo "  Results:"
echo "    Unique recordings:  $KEEP_COUNT"
echo "    Duplicate files:    $DELETE_COUNT"
echo "    Space to recover:   ${DELETE_GB} GB"
echo ""

if $CONFIRM; then
    echo "  ✓ Deleted $DELETE_COUNT duplicate files (${DELETE_GB} GB freed)"
else
    echo "  This is a DRY RUN. To actually delete, run:"
    echo "    ./rode-cleanup.sh --confirm"
fi

# ── Phase 3: Generate manifest for rode-transfer ────────────────────────────
echo ""
echo "── Phase 3: Generate manifest ────────────────────────────"

if $CONFIRM; then
    # Build JSON manifest of all surviving files
    echo "{" > "$MANIFEST"
    echo '  "version": 1,' >> "$MANIFEST"
    echo '  "generated": "'$(date -Iseconds)'",' >> "$MANIFEST"
    echo '  "files": {' >> "$MANIFEST"
    
    FIRST=true
    for f in "${KEEP_FILES[@]}"; do
        [[ ! -f "$f" ]] && continue
        md5=$(md5sum "$f" | awk '{print $1}')
        fsize=$(stat -c %s "$f")
        fname=$(basename "$f")
        
        if $FIRST; then
            FIRST=false
        else
            echo ',' >> "$MANIFEST"
        fi
        printf '    "%s": {"file": "%s", "size": %d}' "$md5" "$fname" "$fsize" >> "$MANIFEST"
    done
    
    echo '' >> "$MANIFEST"
    echo '  }' >> "$MANIFEST"
    echo '}' >> "$MANIFEST"
    
    echo "  ✓ Manifest written to $MANIFEST"
    echo "    ${#KEEP_FILES[@]} files indexed"
else
    echo "  Manifest will be generated on --confirm run"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Done."
echo "═══════════════════════════════════════════════════════════"
