#!/bin/bash
# Easy patch application wrapper

set -e

PATCH_TYPE=$1
FILE=$2
shift 2

echo "=========================================="
echo "Applying code patch"
echo "=========================================="
echo ""

# Run the patcher
python3 /opt/mythos/updates/patch_code.py "$PATCH_TYPE" "$FILE" "$@"

# If successful, restart services
if [ $? -eq 0 ]; then
    echo ""
    echo "Restarting services..."
    sudo systemctl restart mythos-api mythos-bot
    sleep 2
    
    echo ""
    echo "Status:"
    sudo systemctl status mythos-api --no-pager -n 3
    echo ""
    echo "✅ Patch applied successfully!"
else
    echo "❌ Patch failed"
    exit 1
fi
