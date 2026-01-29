#!/bin/bash
# Patch 0040: Wire up Iris Agency System
# Enables real Docker sandbox execution

set -e

echo "=== Installing Patch 0040: Iris Agency Wiring ==="

# Copy updated files
cp -v opt/mythos/iris/core/src/agency.py /opt/mythos/iris/core/src/agency.py
cp -v opt/mythos/iris/core/Dockerfile /opt/mythos/iris/core/Dockerfile

# Build the sandbox image first (if not exists)
echo "=== Building Sandbox Image ==="
cd /opt/mythos/iris/sandbox
docker build -t iris-sandbox:latest . || echo "Warning: Sandbox build failed, will retry on first use"

# Rebuild iris-core with new dependencies
echo "=== Rebuilding Iris Core ==="
cd /opt/mythos/docker
docker compose -f docker-compose.iris.yml build iris-core

# Restart iris-core
echo "=== Restarting Iris ==="
docker compose -f docker-compose.iris.yml down
docker compose -f docker-compose.iris.yml up -d

# Wait for health check
echo "=== Waiting for Iris to come online ==="
sleep 5
curl -s http://localhost:8100/status || echo "Warning: Health check pending"

echo "=== Patch 0040 Complete ==="
echo "Iris now has hands. She can execute code in sandboxed containers."
echo ""
echo "Test with:"
echo "  curl http://localhost:8100/status"
echo "  docker logs -f iris-core"
