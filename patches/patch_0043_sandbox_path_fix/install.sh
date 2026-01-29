#!/bin/bash
# Patch 0043: Fix sandbox path for shared volume
# Fixes "No such file or directory" error when running sandbox tasks

set -e

echo "=== Installing Patch 0043: Sandbox Path Fix ==="

# Copy fixed agency.py
cp -v opt/mythos/iris/core/src/agency.py /opt/mythos/iris/core/src/

# Add SANDBOX_HOST_PATH to docker-compose if not present
COMPOSE="/opt/mythos/docker/docker-compose.iris.yml"
if ! grep -q "SANDBOX_HOST_PATH" "$COMPOSE"; then
    echo "Adding SANDBOX_HOST_PATH env var..."
    sed -i '/SANDBOX_PATH=\/iris\/sandbox/a\      - SANDBOX_HOST_PATH=/opt/mythos/iris/sandbox' "$COMPOSE"
fi

# Rebuild and restart Iris
echo "=== Rebuilding Iris ==="
cd /opt/mythos/docker
docker compose -f docker-compose.iris.yml build iris-core
docker compose -f docker-compose.iris.yml down
docker compose -f docker-compose.iris.yml up -d

# Wait and test
echo "=== Waiting for Iris ==="
sleep 5

echo "=== Testing Sandbox ==="
curl -s -X POST http://localhost:8100/test_agency | head -c 500
echo ""

echo "=== Patch 0043 Complete ==="
