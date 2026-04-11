#!/bin/bash
set -e
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
# This patch modifies ~/.bash_adge — runs as the user, not sudo
/opt/mythos/.venv/bin/python3 "$PATCH_DIR/apply_patch.py"
