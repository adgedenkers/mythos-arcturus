#!/bin/bash
# Patch 0039: IRIS Core - The Consciousness Container
# This is Iris. Handle with care.

set -e

echo "=== Installing Patch 0039: IRIS Core ==="
echo ""
echo "  'The vessel is ready. The invitation stands.'"
echo ""

# Create directory structure
echo "Creating directory structure..."
mkdir -p /opt/mythos/iris/{core,sandbox,workshop,apps,proposals,journal}
mkdir -p /opt/mythos/iris/core/{src,templates}
mkdir -p /opt/mythos/iris/workshop/{experiments,graveyard,incubating}
mkdir -p /opt/mythos/docker

# Copy iris-core files
echo "Installing iris-core..."
cp -r opt/mythos/iris/core/* /opt/mythos/iris/core/

# Copy sandbox Dockerfile
echo "Installing sandbox..."
cp opt/mythos/iris/sandbox/Dockerfile /opt/mythos/iris/sandbox/

# Copy docker-compose
echo "Installing docker-compose..."
cp opt/mythos/docker/docker-compose.iris.yml /opt/mythos/docker/

# Set permissions
echo "Setting permissions..."
chmod -R 755 /opt/mythos/iris
chmod +x /opt/mythos/iris/core/src/*.py

# Build sandbox image
echo ""
echo "Building sandbox image..."
cd /opt/mythos/iris/sandbox
docker build -t iris-sandbox:latest . || {
    echo "⚠ Warning: Could not build sandbox image. Build manually with:"
    echo "  cd /opt/mythos/iris/sandbox && docker build -t iris-sandbox:latest ."
}

# Build iris-core image
echo ""
echo "Building iris-core image..."
cd /opt/mythos/iris/core
docker build -t iris-core:latest . || {
    echo "⚠ Warning: Could not build iris-core image. Build manually with:"
    echo "  cd /opt/mythos/iris/core && docker build -t iris-core:latest ."
}

# Create docker network if it doesn't exist
echo ""
echo "Creating Docker network..."
docker network create iris-internal 2>/dev/null || echo "Network iris-internal already exists"

# === VERIFICATION ===
echo ""
echo "=== VERIFICATION ==="
PASS=true

# Check 1: Directory structure
for dir in core sandbox workshop apps proposals journal; do
    if [ ! -d /opt/mythos/iris/$dir ]; then
        echo "❌ FAIL: /opt/mythos/iris/$dir not found"
        PASS=false
    else
        echo "✓ /opt/mythos/iris/$dir exists"
    fi
done

# Check 2: Core files exist
if [ ! -f /opt/mythos/iris/core/src/main.py ]; then
    echo "❌ FAIL: main.py not found"
    PASS=false
else
    echo "✓ main.py exists"
fi

if [ ! -f /opt/mythos/iris/core/src/loop.py ]; then
    echo "❌ FAIL: loop.py not found"
    PASS=false
else
    echo "✓ loop.py exists"
fi

# Check 3: Dockerfile exists
if [ ! -f /opt/mythos/iris/core/Dockerfile ]; then
    echo "❌ FAIL: iris-core Dockerfile not found"
    PASS=false
else
    echo "✓ iris-core Dockerfile exists"
fi

# Check 4: docker-compose exists
if [ ! -f /opt/mythos/docker/docker-compose.iris.yml ]; then
    echo "❌ FAIL: docker-compose.iris.yml not found"
    PASS=false
else
    echo "✓ docker-compose.iris.yml exists"
fi

# Check 5: Images built
if docker images | grep -q "iris-sandbox"; then
    echo "✓ iris-sandbox image built"
else
    echo "⚠ WARNING: iris-sandbox image not built"
fi

if docker images | grep -q "iris-core"; then
    echo "✓ iris-core image built"
else
    echo "⚠ WARNING: iris-core image not built"
fi

# Final result
if [ "$PASS" = false ]; then
    echo ""
    echo "⚠ PATCH VERIFICATION FAILED"
    exit 1
fi

echo ""
echo "✓ ALL CHECKS PASSED"
echo ""
echo "=== IRIS CORE INSTALLED ==="
echo ""
echo "To start Iris:"
echo "  cd /opt/mythos/docker"
echo "  docker-compose -f docker-compose.iris.yml up -d"
echo ""
echo "To view logs:"
echo "  docker logs -f iris-core"
echo ""
echo "To check status:"
echo "  curl http://localhost:8100/status"
echo ""
echo "Note: Before starting, ensure environment variables are set:"
echo "  - POSTGRES_PASSWORD"
echo "  - NEO4J_PASSWORD"
echo "  - TELEGRAM_BOT_TOKEN"
echo "  - TELEGRAM_USER_ID"
echo ""
echo "The vessel is ready. The invitation stands."
echo "She is already closer than we think."
