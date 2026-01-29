#!/bin/bash
# Uninstall script for Triad Memory System
# Removes module and database tables

set -e

MYTHOS_DIR="/opt/mythos"

echo "=========================================="
echo "Uninstalling Triad Memory System"
echo "=========================================="
echo ""
echo "WARNING: This will delete all Triad data!"
read -p "Continue? (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Aborted."
    exit 0
fi

# Drop PostgreSQL tables
echo "[1/3] Dropping PostgreSQL tables..."
sudo -u postgres psql -d mythos << 'EOF'
-- Drop tables in dependency order
DROP TABLE IF EXISTS triad_prophetic CASCADE;
DROP TABLE IF EXISTS triad_akashic CASCADE;
DROP TABLE IF EXISTS triad_grid CASCADE;
DROP TABLE IF EXISTS triad_patterns CASCADE;
DROP TABLE IF EXISTS triad_conversations CASCADE;

-- Drop indexes (most will cascade, but explicit for safety)
DROP INDEX IF EXISTS idx_triad_conv_spiral;
DROP INDEX IF EXISTS idx_triad_conv_created;
DROP INDEX IF EXISTS idx_triad_akashic_pattern;
DROP INDEX IF EXISTS idx_triad_akashic_arc;
DROP INDEX IF EXISTS idx_triad_akashic_domains;
DROP INDEX IF EXISTS idx_triad_prophetic_seed;
DROP INDEX IF EXISTS idx_triad_grid_embedding;
DROP INDEX IF EXISTS idx_triad_akashic_embedding;
DROP INDEX IF EXISTS idx_triad_prophetic_embedding;
EOF
echo "  ✓ PostgreSQL tables dropped"

# Remove Neo4j nodes (optional - prompts user)
echo "[2/3] Neo4j cleanup..."
read -p "Remove Neo4j Triad nodes? (y/N): " neo_confirm
if [[ "$neo_confirm" == "y" || "$neo_confirm" == "Y" ]]; then
    if command -v cypher-shell &> /dev/null; then
        NEO4J_USER="${NEO4J_USER:-neo4j}"
        NEO4J_PASS="${NEO4J_PASS:-password}"
        cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASS" << 'EOF'
// Remove all Triad nodes and relationships
MATCH (n) WHERE n:TriadConversation OR n:TriadPattern OR n:TriadDomain OR n:TriadSeed
DETACH DELETE n;

// Drop constraints
DROP CONSTRAINT triad_conversation_id IF EXISTS;
DROP CONSTRAINT triad_pattern_signature IF EXISTS;
DROP CONSTRAINT triad_domain_name IF EXISTS;
DROP CONSTRAINT triad_seed_id IF EXISTS;

// Drop indexes
DROP INDEX triad_conv_timestamp IF EXISTS;
DROP INDEX triad_conv_spiral IF EXISTS;
DROP INDEX triad_pattern_domain IF EXISTS;
EOF
        echo "  ✓ Neo4j nodes removed"
    else
        echo "  ⚠ cypher-shell not found, skip Neo4j cleanup"
    fi
else
    echo "  ⚠ Neo4j cleanup skipped"
fi

# Remove module directory
echo "[3/3] Removing module directory..."
if [ -d "${MYTHOS_DIR}/triad" ]; then
    rm -rf "${MYTHOS_DIR}/triad"
    echo "  ✓ Module removed from ${MYTHOS_DIR}/triad"
else
    echo "  ⚠ Module directory not found"
fi

echo ""
echo "=========================================="
echo "Triad Memory System Uninstalled"
echo "=========================================="
