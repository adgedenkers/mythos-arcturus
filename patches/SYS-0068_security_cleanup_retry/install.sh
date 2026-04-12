#!/bin/bash
set -e
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
# SYS-0068: self-escalate to root via the existing mythos-monitor sudoers rule
# (adge ALL=(ALL) NOPASSWD: /usr/bin/bash /opt/mythos/patches/*/install.sh).
# The apply_patch.py needs root to write /etc/sudoers.d/mythos-monitor.
if [ "$EUID" -ne 0 ]; then
    exec sudo -n bash "$0" "$@"
fi
/opt/mythos/.venv/bin/python3 "$PATCH_DIR/apply_patch.py"
