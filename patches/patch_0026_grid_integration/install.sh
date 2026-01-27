#!/bin/bash
# patch_0026_grid_integration install script
# Wires up grid analysis to run after every chat exchange

set -e

echo "📦 Installing patch_0026: Grid Analysis Integration"

# Copy files
cp -v opt/mythos/assistants/chat_assistant.py /opt/mythos/assistants/chat_assistant.py
cp -v opt/mythos/workers/grid_worker.py /opt/mythos/workers/grid_worker.py

# Set permissions
chmod 644 /opt/mythos/assistants/chat_assistant.py
chmod 644 /opt/mythos/workers/grid_worker.py

# Reload systemd (worker service file may have changed)
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Restart services
echo "🔄 Restarting mythos-api service..."
sudo systemctl restart mythos-api.service

sleep 2
if systemctl is-active --quiet mythos-api.service; then
    echo "✅ mythos-api.service is running"
else
    echo "❌ mythos-api.service failed to start"
    journalctl -u mythos-api.service -n 20 --no-pager
    exit 1
fi

echo "🔄 Restarting mythos-worker-grid service..."
sudo systemctl restart mythos-worker-grid.service

sleep 2
if systemctl is-active --quiet mythos-worker-grid.service; then
    echo "✅ mythos-worker-grid.service is running"
else
    echo "❌ mythos-worker-grid.service failed to start"
    journalctl -u mythos-worker-grid.service -n 20 --no-pager
    exit 1
fi

# Check Redis stream
echo ""
echo "🔍 Checking Redis grid stream..."
STREAM_LEN=$(redis-cli XLEN mythos:assignments:grid_analysis 2>/dev/null || echo "0")
echo "   Grid queue length: $STREAM_LEN"

echo ""
echo "✅ patch_0026 installed successfully!"
echo ""
echo "What's new:"
echo "  - ChatAssistant now dispatches to grid analysis after each exchange"
echo "  - Grid worker analyzes user message + assistant response as a pair"
echo "  - Results stored in PostgreSQL (grid_activation_timeseries)"
echo "  - Results stored in Neo4j:"
echo "      (Exchange)-[:ACTIVATED]->(GridNode)"
echo "      (Exchange)-[:MENTIONED]->(Entity:Person)"
echo "      (Exchange)-[:DISCUSSED]->(Entity:Concept)"
echo "      (Exchange)-[:INVOLVES]->(Entity:System)"
echo "      (Exchange)-[:HAS_THEME]->(Theme)"
echo "      (Soul)-[:HAD_EXCHANGE]->(Exchange)"
echo ""
echo "Test: Send a message in chat mode, then check:"
echo "  redis-cli XLEN mythos:assignments:grid_analysis"
echo "  sudo -u postgres psql -d mythos -c 'SELECT * FROM grid_activation_timeseries ORDER BY time DESC LIMIT 1'"
