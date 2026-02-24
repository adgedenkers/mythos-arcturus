#!/bin/bash
set -e
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
sudo /opt/mythos/.venv/bin/python3 "$PATCH_DIR/apply_patch.py"
