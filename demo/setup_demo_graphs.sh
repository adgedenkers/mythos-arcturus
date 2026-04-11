#!/bin/bash
# ============================================================================
# Mythos Demo Graph Setup
# Stands up two isolated Neo4j containers for live + completed demo graphs
# ============================================================================

set -e  # exit on any error

echo "=== Mythos Demo Graph Setup ==="
echo ""

# ----------------------------------------------------------------------------
# 1. Verify Docker is installed and running
# ----------------------------------------------------------------------------
if ! command -v docker &> /dev/null; then
    echo "ERROR: docker is not installed. Install it first:"
    echo "  sudo apt update && sudo apt install -y docker.io"
    echo "  sudo usermod -aG docker \$USER"
    echo "  (then log out and back in)"
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo "ERROR: Cannot talk to Docker daemon. Either:"
    echo "  - The docker service isn't running: sudo systemctl start docker"
    echo "  - Your user isn't in the docker group: sudo usermod -aG docker \$USER"
    exit 1
fi

echo "✓ Docker is available"
echo ""

# ----------------------------------------------------------------------------
# 2. Pull the Neo4j image (matching production version)
# ----------------------------------------------------------------------------
NEO4J_VERSION="2026.01.4-community"
echo "Pulling neo4j:${NEO4J_VERSION}..."

if ! docker pull neo4j:${NEO4J_VERSION}; then
    echo "Exact version not available, falling back to neo4j:2026.01-community"
    NEO4J_VERSION="2026.01-community"
    docker pull neo4j:${NEO4J_VERSION}
fi

echo "✓ Image pulled: neo4j:${NEO4J_VERSION}"
echo ""

# ----------------------------------------------------------------------------
# 3. Stop & remove any existing demo containers (idempotent re-runs)
# ----------------------------------------------------------------------------
for container in demo-live demo-complete; do
    if docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
        echo "Removing existing ${container} container..."
        docker stop ${container} 2>/dev/null || true
        docker rm ${container} 2>/dev/null || true
    fi
done

echo ""

# ----------------------------------------------------------------------------
# 4. Create demo-live container
#    Browser: http://localhost:7475
#    Bolt:    bolt://localhost:7688
# ----------------------------------------------------------------------------
echo "Creating demo-live container..."

docker run -d \
    --name demo-live \
    --restart unless-stopped \
    -p 7475:7474 \
    -p 7688:7687 \
    -v demo-live-data:/data \
    -v demo-live-logs:/logs \
    -e NEO4J_AUTH=neo4j/demo-live-password \
    -e NEO4J_PLUGINS='["apoc"]' \
    -e NEO4J_dbms_security_procedures_unrestricted='apoc.*' \
    -e NEO4J_dbms_memory_heap_initial__size=1G \
    -e NEO4J_dbms_memory_heap_max__size=2G \
    neo4j:${NEO4J_VERSION}

echo "✓ demo-live container started"
echo ""

# ----------------------------------------------------------------------------
# 5. Create demo-complete container
#    Browser: http://localhost:7476
#    Bolt:    bolt://localhost:7689
# ----------------------------------------------------------------------------
echo "Creating demo-complete container..."

docker run -d \
    --name demo-complete \
    --restart unless-stopped \
    -p 7476:7474 \
    -p 7689:7687 \
    -v demo-complete-data:/data \
    -v demo-complete-logs:/logs \
    -e NEO4J_AUTH=neo4j/demo-complete-password \
    -e NEO4J_PLUGINS='["apoc"]' \
    -e NEO4J_dbms_security_procedures_unrestricted='apoc.*' \
    -e NEO4J_dbms_memory_heap_initial__size=1G \
    -e NEO4J_dbms_memory_heap_max__size=2G \
    neo4j:${NEO4J_VERSION}

echo "✓ demo-complete container started"
echo ""

# ----------------------------------------------------------------------------
# 6. Wait for both containers to be ready
# ----------------------------------------------------------------------------
echo "Waiting for Neo4j to come up in both containers (this takes ~30 seconds)..."

wait_for_neo4j() {
    local container=$1
    local port=$2
    local max_attempts=60
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if docker exec ${container} cypher-shell -u neo4j -p ${container}-password "RETURN 1" &>/dev/null; then
            echo "  ✓ ${container} is ready"
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done

    echo "  ✗ ${container} did not become ready in time"
    docker logs --tail 20 ${container}
    return 1
}

wait_for_neo4j demo-live 7688
wait_for_neo4j demo-complete 7689

echo ""

# ----------------------------------------------------------------------------
# 7. Create env files for AutoDoc to source explicitly
# ----------------------------------------------------------------------------
echo "Creating env files for AutoDoc..."

cat > /opt/mythos/.env.demo-live << 'EOF'
# Source this file to point AutoDoc at the LIVE demo graph
# Usage: source /opt/mythos/.env.demo-live && autodoc --target /path/to/repo
NEO4J_URI=bolt://localhost:7688
NEO4J_USER=neo4j
NEO4J_PASSWORD=demo-live-password
EOF

cat > /opt/mythos/.env.demo-complete << 'EOF'
# Source this file to point AutoDoc at the COMPLETED demo graph
# Usage: source /opt/mythos/.env.demo-complete && autodoc --target /path/to/repo
NEO4J_URI=bolt://localhost:7689
NEO4J_USER=neo4j
NEO4J_PASSWORD=demo-complete-password
EOF

chmod 600 /opt/mythos/.env.demo-live /opt/mythos/.env.demo-complete

echo "✓ Created /opt/mythos/.env.demo-live"
echo "✓ Created /opt/mythos/.env.demo-complete"
echo ""

# ----------------------------------------------------------------------------
# 8. Print summary
# ----------------------------------------------------------------------------
cat << 'EOF'
============================================================================
DEMO GRAPHS READY
============================================================================

demo-live (the one Tony watches fill up in real time)
  Browser:  http://localhost:7475
  Bolt:     bolt://localhost:7688
  User:     neo4j
  Password: demo-live-password
  Env file: /opt/mythos/.env.demo-live

demo-complete (the one with the pre-populated graph for the Q&A portion)
  Browser:  http://localhost:7476
  Bolt:     bolt://localhost:7689
  User:     neo4j
  Password: demo-complete-password
  Env file: /opt/mythos/.env.demo-complete

============================================================================
USING THE DEMO GRAPHS WITH AUTODOC
============================================================================

To run AutoDoc against the LIVE demo graph (during the demo):
  source /opt/mythos/.env.demo-live
  autodoc --target /path/to/some/repo

To run AutoDoc against the COMPLETE demo graph (the night before):
  source /opt/mythos/.env.demo-complete
  autodoc --target /path/to/some/repo

To wipe a demo graph and start fresh:
  docker stop demo-live && docker rm demo-live && docker volume rm demo-live-data
  (then re-run this setup script)

To check what's running:
  docker ps | grep demo

To view logs:
  docker logs demo-live
  docker logs demo-complete

To stop both demo graphs (e.g., to free RAM when not demoing):
  docker stop demo-live demo-complete

To start them back up:
  docker start demo-live demo-complete

============================================================================
PRODUCTION NEO4J IS UNTOUCHED
============================================================================
Production Neo4j on port 7474/7687 has not been modified in any way.
Your /opt/mythos/.env file has not been touched.
The demo containers are completely isolated from production.

EOF
