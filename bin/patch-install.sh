#!/bin/bash
# patch-install shell function — source this from .bashrc
# Usage:
#   patch-install MNE-0003              # normal install
#   patch-install MNE-0003 --clip       # install + copy all output to clipboard
#   patch-install MNE-0003 --dry-run    # validate, then prompt to install
#   patch-install MNE-0003 --dry-run --clip  # full capture: dry-run + install
#
# On failure: auto-rollback reverts deployed files, decrements STREAMS.json,
# and calls patch-clean to remove all artifacts.

patch-install() {
    local patch_id="$1"
    shift

    # Parse flags
    local clip=false
    local dry_run=false
    for arg in "$@"; do
        case "$arg" in
            --clip) clip=true ;;
            --dry-run) dry_run=true ;;
            *) echo "Unknown flag: $arg"; return 1 ;;
        esac
    done

    if [ -z "$patch_id" ]; then
        echo "Usage: patch-install <STREAM-NNNN|NNNN> [--clip] [--dry-run]"
        echo ""
        echo "Flags:"
        echo "  --clip      Copy all output to clipboard"
        echo "  --dry-run   Validate first, then prompt to install"
        echo ""
        echo "On install failure, auto-rollback reverts all changes."
        return 1
    fi

    # ── Start continuous capture if --clip ─────────────────────────────────
    local capture_file="/tmp/patch_install_output.txt"
    if $clip; then
        _patch_install_inner "$patch_id" "$dry_run" 2>&1 | tee "$capture_file"
        local exit_code=${PIPESTATUS[0]}

        if command -v xclip &> /dev/null; then
            cat "$capture_file" | xclip -selection clipboard
            echo "📋 Output copied to clipboard"
        elif command -v xsel &> /dev/null; then
            cat "$capture_file" | xsel --clipboard
            echo "📋 Output copied to clipboard"
        else
            echo "⚠ xclip/xsel not found — output saved to $capture_file"
        fi
        return $exit_code
    else
        _patch_install_inner "$patch_id" "$dry_run"
        return $?
    fi
}

_patch_install_inner() {
    local patch_id="$1"
    local dry_run="$2"

    local zip_file=""
    local patch_dir=""
    local archive_dir="/opt/mythos/patches/archive"
    local patches_dir="/opt/mythos/patches"
    local downloads_dir="$HOME/Downloads"

    # Detect format: stream (MNE-0003) or legacy (0150)
    if [[ "$patch_id" =~ ^[A-Z]{3}-[0-9]{4}$ ]]; then
        echo "🔍 Stream patch: $patch_id"
        zip_file=$(find "$downloads_dir" -maxdepth 1 -name "${patch_id}*.zip" -type f 2>/dev/null | head -1)
    elif [[ "$patch_id" =~ ^[0-9]+$ ]]; then
        echo "🔍 Legacy patch: $patch_id"
        local padded=$(printf "%04d" "$patch_id")
        zip_file=$(find "$downloads_dir" -maxdepth 1 -name "patch_${padded}*.zip" -o -name "${padded}*.zip" -type f 2>/dev/null | head -1)
    else
        echo "❌ Invalid patch ID format. Use STREAM-NNNN (e.g., MNE-0003) or legacy NNNN"
        return 1
    fi

    if [ -z "$zip_file" ]; then
        echo "❌ No zip found in $downloads_dir for $patch_id"
        return 1
    fi

    echo "📦 Found in Downloads: $(basename "$zip_file")"

    # Archive the zip
    mkdir -p "$archive_dir"
    cp "$zip_file" "$archive_dir/"
    echo "  → Archived to $archive_dir/"

    # Extract
    echo "📂 Extracting..."
    unzip -o "$zip_file" -d "$patches_dir/"

    # Find the extracted directory
    local base_name=$(basename "$zip_file" .zip)
    patch_dir="$patches_dir/$base_name"

    if [ ! -d "$patch_dir" ]; then
        echo "❌ Expected directory not found: $patch_dir"
        return 1
    fi

    # Make install.sh executable
    chmod +x "$patch_dir/install.sh" 2>/dev/null

    # ── Dry-run phase ─────────────────────────────────────────────────────
    if [ "$dry_run" = "true" ]; then
        echo "🧪 DRY RUN — validating without applying changes"
        export MYTHOS_PATCH_DRY_RUN=1

        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        bash "$patch_dir/install.sh"
        local dry_exit=$?
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        unset MYTHOS_PATCH_DRY_RUN

        if [ $dry_exit -ne 0 ]; then
            echo "❌ DRY RUN FAILED (exit code $dry_exit)"
            echo ""
            echo "🧹 Cleaning up failed dry-run artifacts..."
            _patch_clean_artifacts "$patch_id"
            return $dry_exit
        fi

        echo "🧪 DRY RUN PASSED ✓"
        echo ""

        # Prompt to proceed — read from terminal even when piped through tee
        read -p "Proceed with real install? [Y/n] " answer </dev/tty
        case "${answer:-Y}" in
            [Yy]|[Yy][Ee][Ss]|"")
                echo ""
                echo "🚀 Proceeding with real install..."
                ;;
            *)
                echo "⏹ Aborted — no changes applied"
                return 0
                ;;
        esac
    fi

    # ── Real install phase ────────────────────────────────────────────────
    echo "🚀 Running install.sh..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    bash "$patch_dir/install.sh"
    local exit_code=$?
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if [ $exit_code -eq 0 ]; then
        echo "✅ $patch_id installed"
    else
        echo "❌ $patch_id failed (exit code $exit_code)"
        echo ""
        _patch_auto_rollback "$patch_id"
        return $exit_code
    fi
}

# ── Auto-rollback: revert deployed files + undo STREAMS.json bump ─────────
_patch_auto_rollback() {
    local patch_id="$1"
    local mythos_root="/opt/mythos"
    local result_json="/tmp/${patch_id}_result.json"

    echo "🔄 AUTO-ROLLBACK: Reverting $patch_id..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    local rolled_back=0
    local rb_errors=0

    # ── Phase 1: Revert deployed files using git ──────────────────────────
    if [ -f "$result_json" ]; then
        echo "  📄 Reading result manifest: $result_json"

        # Extract files_deployed array from JSON
        local deployed_files
        deployed_files=$(python3 -c "
import json, sys
try:
    data = json.load(open('$result_json'))
    for f in data.get('files_deployed', []):
        print(f)
except Exception as e:
    print(f'ERROR: {e}', file=sys.stderr)
" 2>/dev/null)

        if [ -n "$deployed_files" ]; then
            while IFS= read -r filepath; do
                [ -z "$filepath" ] && continue

                # Check if this file existed before the patch (is it tracked by git?)
                if cd "$mythos_root" 2>/dev/null; then
                    local rel_path="${filepath#/opt/mythos/}"

                    if git ls-files --error-unmatch "$rel_path" &>/dev/null; then
                        # File existed before — restore from git
                        if git checkout HEAD -- "$rel_path" 2>/dev/null; then
                            echo "  ✓ Reverted: $rel_path (restored from git)"
                            ((rolled_back++))
                        else
                            echo "  ✗ Failed to revert: $rel_path"
                            ((rb_errors++))
                        fi
                    else
                        # New file added by patch — remove it
                        if rm -f "$filepath" 2>/dev/null; then
                            echo "  ✓ Removed: $rel_path (new file)"
                            ((rolled_back++))

                            # Clean up empty parent dirs created by patch
                            local parent_dir=$(dirname "$filepath")
                            while [ "$parent_dir" != "$mythos_root" ] && [ -d "$parent_dir" ]; do
                                if [ -z "$(ls -A "$parent_dir" 2>/dev/null)" ]; then
                                    rmdir "$parent_dir" 2>/dev/null
                                    echo "  ✓ Removed empty dir: ${parent_dir#/opt/mythos/}/"
                                    parent_dir=$(dirname "$parent_dir")
                                else
                                    break
                                fi
                            done
                        else
                            echo "  ✗ Failed to remove: $rel_path"
                            ((rb_errors++))
                        fi
                    fi
                    cd - > /dev/null 2>&1
                fi
            done <<< "$deployed_files"
        fi

        # ── Phase 2: Undo STREAMS.json bump ──────────────────────────────
        local stream
        stream=$(python3 -c "
import json
data = json.load(open('$result_json'))
print(data.get('stream', ''))
" 2>/dev/null)

        local number
        number=$(python3 -c "
import json
data = json.load(open('$result_json'))
print(data.get('number', 0))
" 2>/dev/null)

        if [ -n "$stream" ] && [ "$number" -gt 0 ] 2>/dev/null; then
            local streams_json="$mythos_root/docs/STREAMS.json"
            if [ -f "$streams_json" ]; then
                python3 -c "
import json
with open('$streams_json', 'r') as f:
    data = json.load(f)
streams = data.get('streams', {})
for key in streams:
    entry = streams[key]
    if entry.get('prefix', '').upper() == '$stream' or key.upper() == '$stream':
        current = entry.get('next_patch', 0)
        if current == $number + 1:
            entry['next_patch'] = $number
            print(f'  ✓ STREAMS.json: {key} next_patch reverted {current} → {$number}')
        else:
            print(f'  ⚠ STREAMS.json: {key} next_patch is {current}, expected {$number + 1} — skipping')
        break
with open('$streams_json', 'w') as f:
    json.dump(data, f, indent=2)
" 2>/dev/null
            fi
        fi

        # ── Phase 3: Remove PATCH_HISTORY entry ──────────────────────────
        local patch_history="$mythos_root/docs/PATCH_HISTORY.md"
        if [ -f "$patch_history" ]; then
            # Remove the block starting with ### PATCH_ID through the next ### or EOF
            python3 -c "
import re
with open('$patch_history', 'r') as f:
    content = f.read()
# Find and remove the entry block for this patch
pattern = r'\n### ${patch_id}:.*?(?=\n### |\Z)'
new_content = re.sub(pattern, '', content, flags=re.DOTALL)
if new_content != content:
    with open('$patch_history', 'w') as f:
        f.write(new_content)
    print('  ✓ PATCH_HISTORY.md: removed $patch_id entry')
else:
    print('  · PATCH_HISTORY.md: no entry found for $patch_id')
" 2>/dev/null
        fi

        # ── Phase 4: Restart services that were restarted by the patch ────
        local restarted_services
        restarted_services=$(python3 -c "
import json
data = json.load(open('$result_json'))
for s in data.get('services_restarted', []):
    print(s)
" 2>/dev/null)

        if [ -n "$restarted_services" ]; then
            echo "  🔄 Re-restarting services to restore previous state..."
            while IFS= read -r svc; do
                [ -z "$svc" ] && continue
                if sudo systemctl restart "$svc" 2>/dev/null; then
                    echo "  ✓ Restarted $svc (to reload pre-patch code)"
                else
                    echo "  ✗ Failed to restart $svc"
                    ((rb_errors++))
                fi
            done <<< "$restarted_services"
        fi

    else
        echo "  ⚠ No result manifest at $result_json — cannot revert deployed files"
        echo "    (The install may have failed before PatchBase.finish() ran)"
    fi

    # ── Phase 5: Clean artifacts (zip, archive, extracted dir, tags, logs) ─
    echo ""
    echo "🧹 Cleaning patch artifacts..."
    _patch_clean_artifacts "$patch_id"

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [ $rb_errors -eq 0 ]; then
        echo "✅ ROLLBACK COMPLETE: $patch_id fully reverted ($rolled_back files)"
    else
        echo "⚠️  ROLLBACK PARTIAL: $rolled_back reverted, $rb_errors errors"
    fi
    echo "   System is back to pre-patch state."
}

# ── Clean artifacts only (no file revert) — used by rollback and dry-run ──
_patch_clean_artifacts() {
    local patch_id="$1"
    local archive_dir="/opt/mythos/patches/archive"
    local patches_dir="/opt/mythos/patches"
    local downloads_dir="$HOME/Downloads"
    local mythos_root="/opt/mythos"

    # Downloads
    find "$downloads_dir" -maxdepth 1 -name "${patch_id}*.zip" -type f 2>/dev/null | while read -r f; do
        rm -f "$f" && echo "  ✓ Removed download: $(basename "$f")"
    done

    # Archive
    find "$archive_dir" -maxdepth 1 -name "${patch_id}*.zip" -type f 2>/dev/null | while read -r f; do
        rm -f "$f" && echo "  ✓ Removed archive: $(basename "$f")"
    done

    # Extracted directory
    find "$patches_dir" -maxdepth 1 -name "${patch_id}*" -type d 2>/dev/null | while read -r d; do
        rm -rf "$d" && echo "  ✓ Removed extracted: $(basename "$d")/"
    done

    # Git tags
    if cd "$mythos_root" 2>/dev/null; then
        git tag -l "*${patch_id}*" 2>/dev/null | while read -r tag; do
            [ -z "$tag" ] && continue
            git tag -d "$tag" > /dev/null 2>&1 && echo "  ✓ Deleted tag: $tag"
            git push origin ":refs/tags/$tag" > /dev/null 2>&1
        done
        cd - > /dev/null 2>&1
    fi

    # Tmp logs
    find /tmp -maxdepth 1 -name "${patch_id}*" -type f 2>/dev/null | while read -r f; do
        rm -f "$f" && echo "  ✓ Removed log: $(basename "$f")"
    done
}
