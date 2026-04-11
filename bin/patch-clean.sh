#!/bin/bash
# patch-clean shell function — source this from .bashrc
# Usage:
#   patch-clean SYS-0011                # interactive clean with confirmation
#   patch-clean SYS-0011 --force        # skip confirmation
#   patch-clean SYS-0011 --dry-run      # show what would be removed

patch-clean() {
    local patch_id="$1"
    shift

    local force=false
    local dry_run=false
    for arg in "$@"; do
        case "$arg" in
            --force) force=true ;;
            --dry-run) dry_run=true ;;
            *) echo "Unknown flag: $arg"; return 1 ;;
        esac
    done

    if [ -z "$patch_id" ]; then
        echo "Usage: patch-clean <STREAM-NNNN|NNNN> [--force] [--dry-run]"
        echo ""
        echo "Removes all traces of a patch:"
        echo "  • Zip(s) from ~/Downloads/"
        echo "  • Archived zip from /opt/mythos/patches/archive/"
        echo "  • Extracted directory from /opt/mythos/patches/"
        echo "  • Git tag(s) matching the patch ID"
        echo ""
        echo "Flags:"
        echo "  --force     Skip confirmation prompt"
        echo "  --dry-run   Show what would be removed without doing it"
        return 1
    fi

    local archive_dir="/opt/mythos/patches/archive"
    local patches_dir="/opt/mythos/patches"
    local downloads_dir="$HOME/Downloads"
    local mythos_root="/opt/mythos"

    # ── Discover what exists ──────────────────────────────────────────────
    local found_items=()

    # 1. Zips in ~/Downloads/ (match patch_id prefix, could be multiple copies)
    while IFS= read -r f; do
        found_items+=("download:$f")
    done < <(find "$downloads_dir" -maxdepth 1 -name "${patch_id}*.zip" -type f 2>/dev/null)

    # 2. Archived zip(s)
    while IFS= read -r f; do
        found_items+=("archive:$f")
    done < <(find "$archive_dir" -maxdepth 1 -name "${patch_id}*.zip" -type f 2>/dev/null)

    # 3. Extracted patch directory
    while IFS= read -r d; do
        found_items+=("extracted:$d")
    done < <(find "$patches_dir" -maxdepth 1 -name "${patch_id}*" -type d 2>/dev/null)

    # 4. Git tags matching this patch
    local git_tags=()
    if cd "$mythos_root" 2>/dev/null; then
        while IFS= read -r tag; do
            [ -n "$tag" ] && git_tags+=("$tag") && found_items+=("git-tag:$tag")
        done < <(git tag -l "*${patch_id}*" 2>/dev/null)
        cd - > /dev/null
    fi

    # 5. Patch log files in /tmp
    while IFS= read -r f; do
        found_items+=("log:$f")
    done < <(find /tmp -maxdepth 1 -name "${patch_id}*" -type f 2>/dev/null)

    # ── Report ────────────────────────────────────────────────────────────
    if [ ${#found_items[@]} -eq 0 ]; then
        echo "🔍 No traces found for $patch_id"
        return 0
    fi

    echo ""
    echo "🧹 patch-clean: $patch_id"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    for item in "${found_items[@]}"; do
        local type="${item%%:*}"
        local path="${item#*:}"
        case "$type" in
            download)   echo "  📥 Download:  $(basename "$path")" ;;
            archive)    echo "  📦 Archive:   $(basename "$path")" ;;
            extracted)  echo "  📂 Extracted: $(basename "$path")/" ;;
            git-tag)    echo "  🏷️  Git tag:   $path" ;;
            log)        echo "  📄 Log:       $(basename "$path")" ;;
        esac
    done

    echo ""
    echo "  Total: ${#found_items[@]} item(s)"
    echo ""

    if $dry_run; then
        echo "🧪 DRY RUN — nothing removed"
        return 0
    fi

    # ── Confirm ───────────────────────────────────────────────────────────
    if ! $force; then
        read -p "Remove all ${#found_items[@]} items? [y/N] " answer </dev/tty
        case "$answer" in
            [Yy]|[Yy][Ee][Ss]) ;;
            *)
                echo "⏹ Aborted"
                return 0
                ;;
        esac
        echo ""
    fi

    # ── Remove ────────────────────────────────────────────────────────────
    local removed=0
    local errors=0

    for item in "${found_items[@]}"; do
        local type="${item%%:*}"
        local path="${item#*:}"

        case "$type" in
            download|archive|log)
                if rm -f "$path" 2>/dev/null; then
                    echo "  ✓ Removed $(basename "$path")"
                    ((removed++))
                else
                    echo "  ✗ Failed to remove $(basename "$path")"
                    ((errors++))
                fi
                ;;
            extracted)
                if rm -rf "$path" 2>/dev/null; then
                    echo "  ✓ Removed $(basename "$path")/"
                    ((removed++))
                else
                    echo "  ✗ Failed to remove $(basename "$path")/"
                    ((errors++))
                fi
                ;;
            git-tag)
                if cd "$mythos_root" 2>/dev/null; then
                    if git tag -d "$path" > /dev/null 2>&1; then
                        echo "  ✓ Deleted local tag: $path"
                        ((removed++))
                        # Also remove remote tag if it exists
                        if git push origin ":refs/tags/$path" > /dev/null 2>&1; then
                            echo "  ✓ Deleted remote tag: $path"
                        fi
                    else
                        echo "  ✗ Failed to delete tag: $path"
                        ((errors++))
                    fi
                    cd - > /dev/null
                fi
                ;;
        esac
    done

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [ $errors -eq 0 ]; then
        echo "✅ $patch_id cleaned ($removed items removed)"
    else
        echo "⚠️  $patch_id partially cleaned ($removed removed, $errors errors)"
    fi
}
