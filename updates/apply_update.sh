#!/bin/bash
# Universal code update script

UPDATE_FILE=$1

if [ -z "$UPDATE_FILE" ]; then
    echo "Usage: ./apply_update.sh <update_file.sh>"
    exit 1
fi

if [ ! -f "$UPDATE_FILE" ]; then
    echo "Error: Update file not found: $UPDATE_FILE"
    exit 1
fi

echo "=========================================="
echo "Applying update: $UPDATE_FILE"
echo "=========================================="
echo ""

# Source the update file
source "$UPDATE_FILE"

# Restart services if needed
if [ "$RESTART_SERVICES" = "true" ]; then
    echo ""
    echo "Restarting services..."
    sudo systemctl restart mythos-api
    sudo systemctl restart mythos-bot
    sleep 2
    echo ""
    echo "Service status:"
    sudo systemctl status mythos-api --no-pager -n 3
    sudo systemctl status mythos-bot --no-pager -n 3
fi

echo ""
echo "✅ Update complete!"