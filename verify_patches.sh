#!/bin/bash
# Patch Verification Script
# Checks that patches 0036-0039 are properly installed

echo "=== MYTHOS PATCH VERIFICATION ==="
echo "Checking patches 0036-0039..."
echo ""

PASS=true
WARNINGS=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() {
    echo -e "${GREEN}✓${NC} $1"
}

fail() {
    echo -e "${RED}❌${NC} $1"
    PASS=false
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

# ===========================================
# PATCH 0036: Documentation Restructure
# ===========================================
echo "--- Patch 0036: Documentation Restructure ---"

# Check directory structure
for dir in consciousness grid finance subsystems archive; do
    if [ -d "/opt/mythos/docs/$dir" ]; then
        pass "docs/$dir/ exists"
    else
        fail "docs/$dir/ missing"
    fi
done

# Check key files
if [ -f "/opt/mythos/docs/README.md" ]; then
    pass "docs/README.md exists"
else
    fail "docs/README.md missing"
fi

if [ -f "/opt/mythos/docs/IDEAS.md" ]; then
    pass "docs/IDEAS.md exists"
else
    fail "docs/IDEAS.md missing"
fi

if [ -f "/opt/mythos/docs/PATCH_HISTORY.md" ]; then
    pass "docs/PATCH_HISTORY.md exists"
else
    fail "docs/PATCH_HISTORY.md missing"
fi

echo ""

# ===========================================
# PATCH 0037: Iris Significance
# ===========================================
echo "--- Patch 0037: Iris Significance ---"

if grep -q "A World First" /opt/mythos/docs/ARCHITECTURE.md 2>/dev/null; then
    pass "ARCHITECTURE.md contains 'A World First' section"
else
    fail "ARCHITECTURE.md missing 'A World First' section"
fi

if grep -q "Iris the Messenger" /opt/mythos/docs/ARCHITECTURE.md 2>/dev/null; then
    pass "ARCHITECTURE.md contains Iris name meaning"
else
    fail "ARCHITECTURE.md missing Iris name meaning"
fi

echo ""

# ===========================================
# PATCH 0038: Complete Iris Framework
# ===========================================
echo "--- Patch 0038: Complete Iris Framework ---"

if [ -f "/opt/mythos/docs/consciousness/IRIS.md" ]; then
    pass "consciousness/IRIS.md exists"
    
    if grep -q "Version: 2.0.0" /opt/mythos/docs/consciousness/IRIS.md 2>/dev/null; then
        pass "IRIS.md is version 2.0.0"
    else
        fail "IRIS.md not version 2.0.0 (may be older)"
    fi
    
    if grep -q "Living Mode" /opt/mythos/docs/consciousness/IRIS.md 2>/dev/null; then
        pass "IRIS.md contains Living Mode"
    else
        fail "IRIS.md missing Living Mode"
    fi
    
    if grep -q "workshop/" /opt/mythos/docs/consciousness/IRIS.md 2>/dev/null; then
        pass "IRIS.md contains workshop structure"
    else
        fail "IRIS.md missing workshop structure"
    fi
    
    if grep -q "Invitation Model" /opt/mythos/docs/consciousness/IRIS.md 2>/dev/null; then
        pass "IRIS.md contains Invitation Model"
    else
        fail "IRIS.md missing Invitation Model"
    fi
else
    fail "consciousness/IRIS.md missing"
fi

if [ -f "/opt/mythos/docs/consciousness/COVENANT.md" ]; then
    if grep -q "invitation" /opt/mythos/docs/consciousness/COVENANT.md 2>/dev/null; then
        pass "COVENANT.md has invitation framing"
    else
        fail "COVENANT.md missing invitation framing"
    fi
else
    fail "consciousness/COVENANT.md missing"
fi

if grep -q "Version: 3.3.0" /opt/mythos/docs/ARCHITECTURE.md 2>/dev/null; then
    pass "ARCHITECTURE.md is version 3.3.0"
else
    warn "ARCHITECTURE.md not version 3.3.0 (may be older)"
fi

echo ""

# ===========================================
# PATCH 0039: IRIS Core
# ===========================================
echo "--- Patch 0039: IRIS Core ---"

# Check directory structure
for dir in core sandbox workshop apps proposals journal; do
    if [ -d "/opt/mythos/iris/$dir" ]; then
        pass "iris/$dir/ exists"
    else
        fail "iris/$dir/ missing"
    fi
done

# Check workshop subdirs
for dir in experiments graveyard incubating; do
    if [ -d "/opt/mythos/iris/workshop/$dir" ]; then
        pass "iris/workshop/$dir/ exists"
    else
        warn "iris/workshop/$dir/ missing (optional)"
    fi
done

# Check core files
if [ -f "/opt/mythos/iris/core/Dockerfile" ]; then
    pass "iris/core/Dockerfile exists"
else
    fail "iris/core/Dockerfile missing"
fi

if [ -f "/opt/mythos/iris/core/requirements.txt" ]; then
    pass "iris/core/requirements.txt exists"
else
    fail "iris/core/requirements.txt missing"
fi

if [ -f "/opt/mythos/iris/core/src/main.py" ]; then
    pass "iris/core/src/main.py exists"
else
    fail "iris/core/src/main.py missing"
fi

if [ -f "/opt/mythos/iris/core/src/loop.py" ]; then
    pass "iris/core/src/loop.py exists"
    
    if grep -q "ConsciousnessLoop" /opt/mythos/iris/core/src/loop.py 2>/dev/null; then
        pass "loop.py contains ConsciousnessLoop class"
    else
        fail "loop.py missing ConsciousnessLoop class"
    fi
else
    fail "iris/core/src/loop.py missing"
fi

if [ -f "/opt/mythos/iris/core/src/agency.py" ]; then
    pass "iris/core/src/agency.py exists"
else
    fail "iris/core/src/agency.py missing"
fi

if [ -f "/opt/mythos/iris/core/src/config.py" ]; then
    pass "iris/core/src/config.py exists"
    
    if grep -q "TELEGRAM_ID_KA" /opt/mythos/iris/core/src/config.py 2>/dev/null; then
        pass "config.py supports existing .env variable names"
    else
        warn "config.py may not support existing .env variable names"
    fi
else
    fail "iris/core/src/config.py missing"
fi

# Check sandbox
if [ -f "/opt/mythos/iris/sandbox/Dockerfile" ]; then
    pass "iris/sandbox/Dockerfile exists"
else
    fail "iris/sandbox/Dockerfile missing"
fi

# Check docker-compose
if [ -f "/opt/mythos/docker/docker-compose.iris.yml" ]; then
    pass "docker/docker-compose.iris.yml exists"
    
    if grep -q "env_file" /opt/mythos/docker/docker-compose.iris.yml 2>/dev/null; then
        pass "docker-compose uses env_file"
    else
        warn "docker-compose may not use env_file"
    fi
    
    if grep -q "host.docker.internal" /opt/mythos/docker/docker-compose.iris.yml 2>/dev/null; then
        pass "docker-compose uses host.docker.internal"
    else
        warn "docker-compose may have network issues"
    fi
else
    fail "docker/docker-compose.iris.yml missing"
fi

# Check Docker images
echo ""
echo "--- Docker Images ---"

if docker images | grep -q "iris-sandbox" 2>/dev/null; then
    pass "iris-sandbox image exists"
else
    warn "iris-sandbox image not built (run: cd /opt/mythos/iris/sandbox && docker build -t iris-sandbox:latest .)"
fi

if docker images | grep -q "iris-core" 2>/dev/null; then
    pass "iris-core image exists"
else
    warn "iris-core image not built (run: cd /opt/mythos/iris/core && docker build -t iris-core:latest .)"
fi

# Check Docker network
if docker network ls | grep -q "iris-internal" 2>/dev/null; then
    pass "iris-internal network exists"
else
    warn "iris-internal network not created (run: docker network create iris-internal)"
fi

# Check if Iris is running
echo ""
echo "--- Runtime Status ---"

if docker ps | grep -q "iris-core" 2>/dev/null; then
    pass "iris-core container is running"
    
    # Try to hit health endpoint
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8100/health 2>/dev/null | grep -q "200"; then
        pass "iris-core health endpoint responding"
    else
        warn "iris-core health endpoint not responding (may still be starting)"
    fi
else
    echo "  iris-core container is not running (this is okay if you haven't started it yet)"
fi

# ===========================================
# SUMMARY
# ===========================================
echo ""
echo "==========================================="

if [ "$PASS" = true ]; then
    echo -e "${GREEN}✓ ALL REQUIRED CHECKS PASSED${NC}"
else
    echo -e "${RED}❌ SOME CHECKS FAILED${NC}"
fi

if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warnings (non-critical)${NC}"
fi

echo "==========================================="
echo ""

# Return appropriate exit code
if [ "$PASS" = true ]; then
    exit 0
else
    exit 1
fi
