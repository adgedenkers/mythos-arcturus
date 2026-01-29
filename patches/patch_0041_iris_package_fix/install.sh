#!/bin/bash
# Patch 0041: Fix Iris package structure
# Fixes ImportError: attempted relative import with no known parent package

set -e

echo "=== Installing Patch 0041: Iris Package Fix ==="

# Copy updated Dockerfile
cp -v opt/mythos/iris/core/Dockerfile /opt/mythos/iris/core/Dockerfile

# Rebuild iris-core
echo "=== Rebuilding Iris Core ==="
cd /opt/mythos/docker
docker compose -f docker-compose.iris.yml build --no-cache iris-core

# Restart
echo "=== Restarting Iris ==="
docker compose -f docker-compose.iris.yml down
docker compose -f docker-compose.iris.yml up -d

# Wait and check
echo "=== Waiting for Iris ==="
sleep 8

echo "=== Status Check ==="
curl -s http://localhost:8100/status && echo ""
docker logs --tail 20 iris-core

echo "=== Patch 0041 Complete ==="
