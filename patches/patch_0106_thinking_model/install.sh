#!/bin/bash
# Patch 0106: Add 'thinking' model class
# Delegates to Python script to avoid all bash escaping issues
set -e
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
/opt/mythos/.venv/bin/python3 "$PATCH_DIR/apply_patch.py"
