#!/usr/bin/env python3
"""
SYS-0006: patch-install stream format support

Updates the patch-install shell function in ~/.bash_adge to handle
both legacy numeric format (118) and stream format (SYS-0005, MNE-0001).

Legacy:  patch-install 118       → looks for patch_0118_*.zip
Stream:  patch-install SYS-0005  → looks for SYS-0005_*.zip
"""

import os
import sys
import shutil
import datetime

BASH_ADGE = os.path.expanduser("~/.bash_adge")

NEW_FUNCTION = '''
patch-install() {
    local arg="$1"
    if [ -z "$arg" ]; then
        echo "Usage:"
        echo "  patch-install <number>       e.g. patch-install 118"
        echo "  patch-install <STREAM-NNNN>  e.g. patch-install SYS-0005"
        return 1
    fi

    local patches_dir="/opt/mythos/patches"
    local archive_dir="${patches_dir}/archive"
    local downloads_dir="$HOME/Downloads"
    local zip_file=""
    local patch_dir=""

    # ── Detect format ────────────────────────────────────────────────────────
    if [[ "$arg" =~ ^[A-Z]{2,5}-[0-9]{4}$ ]]; then
        # Stream format: SYS-0005, MNE-0001, etc.
        local stream_id="$arg"
        echo "🔍 Stream patch: ${stream_id}"

        zip_file=$(command ls -1 ${downloads_dir}/${stream_id}_*.zip 2>/dev/null | head -1)
        if [ -z "$zip_file" ]; then
            zip_file=$(command ls -1 ${archive_dir}/${stream_id}_*.zip 2>/dev/null | head -1)
            if [ -z "$zip_file" ]; then
                echo "❌ No zip found for ${stream_id} in ~/Downloads or archive"
                return 1
            fi
            echo "📦 Found in archive: $(basename $zip_file)"
        else
            echo "📦 Found in Downloads: $(basename $zip_file)"
            mkdir -p "$archive_dir"
            command cp "$zip_file" "$archive_dir/" 2>/dev/null
            echo "  → Archived to ${archive_dir}/"
        fi

        # Extract if not already present
        patch_dir=$(command ls -1d ${patches_dir}/${stream_id}_*/ 2>/dev/null | head -1)
        if [ -z "$patch_dir" ]; then
            echo "📂 Extracting..."
            cd "$patches_dir"
            unzip -o "$zip_file" -d "$patches_dir"
            patch_dir=$(command ls -1d ${patches_dir}/${stream_id}_*/ 2>/dev/null | head -1)
            if [ -z "$patch_dir" ]; then
                echo "❌ Extraction failed — no patch directory found"
                return 1
            fi
        else
            echo "📂 Already extracted: $(basename $patch_dir)"
        fi

    else
        # Legacy numeric format: 118 or 0118
        local padded
        padded=$(printf "%04d" "$arg" 2>/dev/null)
        if [ $? -ne 0 ]; then
            echo "❌ Invalid patch identifier: $arg"
            echo "   Use a number (118) or stream format (SYS-0005)"
            return 1
        fi
        echo "🔍 Legacy patch: ${padded}"

        zip_file=$(command ls -1 ${downloads_dir}/patch_${padded}_*.zip 2>/dev/null | head -1)
        if [ -z "$zip_file" ]; then
            zip_file=$(command ls -1 ${archive_dir}/patch_${padded}_*.zip 2>/dev/null | head -1)
            if [ -z "$zip_file" ]; then
                echo "❌ No zip found for patch ${padded} in ~/Downloads or archive"
                return 1
            fi
            echo "📦 Found in archive: $(basename $zip_file)"
        else
            echo "📦 Found in Downloads: $(basename $zip_file)"
            mkdir -p "$archive_dir"
            command cp "$zip_file" "$archive_dir/" 2>/dev/null
            echo "  → Archived to ${archive_dir}/"
        fi

        patch_dir=$(command ls -1d ${patches_dir}/patch_${padded}_*/ 2>/dev/null | grep -v archive | head -1)
        if [ -z "$patch_dir" ]; then
            echo "📂 Extracting..."
            cd "$patches_dir"
            unzip -o "$zip_file" -d "$patches_dir"
            patch_dir=$(command ls -1d ${patches_dir}/patch_${padded}_*/ 2>/dev/null | grep -v archive | head -1)
            if [ -z "$patch_dir" ]; then
                echo "❌ Extraction failed — no patch directory found"
                return 1
            fi
        else
            echo "📂 Already extracted: $(basename $patch_dir)"
        fi
    fi

    # ── Run install.sh ────────────────────────────────────────────────────────
    local install_sh="${patch_dir}install.sh"
    if [ ! -f "$install_sh" ]; then
        echo "❌ No install.sh in ${patch_dir}"
        return 1
    fi

    chmod +x "$install_sh"
    echo "🚀 Running install.sh..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    cd "$patch_dir"
    ./install.sh
    local rc=$?
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [ $rc -eq 0 ]; then
        echo "✅ ${arg} installed"
    else
        echo "❌ ${arg} failed (exit code $rc)"
    fi
    return $rc
}
'''

print("[SYS-0006] patch-install stream format support")
print("=" * 50)

if not os.path.exists(BASH_ADGE):
    print(f"  ❌ {BASH_ADGE} not found")
    sys.exit(1)

# Backup
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
backup = f"{BASH_ADGE}.bak.{ts}"
shutil.copy2(BASH_ADGE, backup)
print(f"  ✓ Backup: {backup}")

with open(BASH_ADGE, "r") as f:
    content = f.read()

# Find and replace the existing patch-install function
import re

# Match the function from definition to closing brace
# Handles both `patch-install ()` and `patch-install()`
pattern = re.compile(
    r'\npatch-install\s*\(\s*\)\s*\n\{[^}]*(?:\{[^}]*\}[^}]*)*\}',
    re.DOTALL
)

if pattern.search(content):
    new_content = pattern.sub(NEW_FUNCTION, content)
    print("  ✓ Replaced existing patch-install function")
else:
    # Not found with that pattern — append it
    new_content = content + "\n" + NEW_FUNCTION
    print("  ⚠ Function not found via pattern — appended to end of file")

with open(BASH_ADGE, "w") as f:
    f.write(new_content)

print(f"  ✓ Written: {BASH_ADGE}")
print()
print("[SYS-0006] Complete ✓")
print()
print("  Reload with:  source ~/.bashrc")
print("  Then test:    patch-install SYS-0004")
print("                patch-install SYS-0005")
