#!/bin/bash
# patch_0027_worker_import_fix install script
# Fixes Python import path for worker handlers

set -e

echo "📦 Installing patch_0027: Worker Import Path Fix"

# Copy files
cp -v opt/mythos/workers/worker.py /opt/mythos/workers/worker.py
chmod 644 /opt/mythos/workers/worker.py

# Restart all workers that use this framework
echo "🔄 Restarting worker services..."

for worker in grid embedding vision temporal entity summary; do
    service="mythos-worker-${worker}.service"
    if systemctl is-enabled "$service" 2>/dev/null; then
        echo "  Restarting $service..."
        sudo systemctl restart "$service" 2>/dev/null || true
    fi
done

sleep 3

# Check grid worker specifically
echo ""
echo "🔍 Checking grid worker status..."
if systemctl is-active --quiet mythos-worker-grid.service; then
    echo "✅ mythos-worker-grid.service is running"
    
    # Check if handler loaded correctly
    if journalctl -u mythos-worker-grid.service -n 10 --no-pager 2>/dev/null | grep -q "Loaded handler"; then
        echo "✅ Handler loaded successfully"
    else
        echo "⚠️  Check logs: journalctl -u mythos-worker-grid.service -n 20"
    fi
else
    echo "❌ mythos-worker-grid.service failed to start"
    journalctl -u mythos-worker-grid.service -n 20 --no-pager
fi

echo ""
echo "✅ patch_0027 installed!"
echo ""
echo "The fix: Added sys.path.insert(0, '/opt/mythos') so workers can import their handlers"
