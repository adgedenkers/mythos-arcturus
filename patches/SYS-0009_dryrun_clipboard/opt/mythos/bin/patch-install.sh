#!/bin/bash
# patch-install shell function — source this from .bashrc
# Usage:
#   patch-install MNE-0003              # normal install
#   patch-install MNE-0003 --clip       # install + copy output to clipboard
#   patch-install MNE-0003 --dry-run    # validate without applying changes
#   patch-install MNE-0003 --dry-run --clip  # validate + copy output

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
        echo "  --clip      Copy install output to clipboard"
        echo "  --dry-run   Validate patch without applying changes"
        return 1
    fi

    local zip_file=""
    local patch_dir=""
    local archive_dir="/opt/mythos/patches/archive"
    local patches_dir="/opt/mythos/patches"
    local downloads_dir="$HOME/Downloads"

    # Detect format: stream (MNE-0003) or legacy (0150)
    if [[ "$patch_id" =~ ^[A-Z]{3}-[0-9]{4}$ ]]; then
        echo "🔍 Stream patch: $patch_id"
        # Find matching zip in Downloads
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

    # Set dry-run environment variable if requested
    if $dry_run; then
        echo "🧪 DRY RUN — validating without applying changes"
        export MYTHOS_PATCH_DRY_RUN=1
    else
        unset MYTHOS_PATCH_DRY_RUN 2>/dev/null
    fi

    # Run install
    echo "🚀 Running install.sh..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if $clip; then
        # Capture output to temp file AND display on terminal
        bash "$patch_dir/install.sh" 2>&1 | tee /tmp/patch_install_output.txt
        local exit_code=${PIPESTATUS[0]}
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        if $dry_run; then
            echo "🧪 DRY RUN complete (no changes applied)"
        fi

        # Copy to clipboard
        if command -v xclip &> /dev/null; then
            cat /tmp/patch_install_output.txt | xclip -selection clipboard
            echo "📋 Output copied to clipboard"
        elif command -v xsel &> /dev/null; then
            cat /tmp/patch_install_output.txt | xsel --clipboard
            echo "📋 Output copied to clipboard"
        else
            echo "⚠ xclip/xsel not found — output saved to /tmp/patch_install_output.txt"
        fi

        if [ $exit_code -eq 0 ]; then
            echo "✅ $patch_id installed"
        else
            echo "❌ $patch_id failed (exit code $exit_code)"
            return $exit_code
        fi
    else
        bash "$patch_dir/install.sh"
        local exit_code=$?
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        if $dry_run; then
            echo "🧪 DRY RUN complete (no changes applied)"
        fi

        if [ $exit_code -eq 0 ]; then
            echo "✅ $patch_id installed"
        else
            echo "❌ $patch_id failed (exit code $exit_code)"
            return $exit_code
        fi
    fi

    # Clean up dry-run env var
    unset MYTHOS_PATCH_DRY_RUN 2>/dev/null
}
