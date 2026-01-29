#!/bin/bash
# ============================================================================
# MYTHOS ASTROLOGY SYSTEM - Install Script
# ============================================================================
# Creates the astrology schema in PostgreSQL and Neo4j
# Loads reference data into both systems
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCHEMA_DIR="$SCRIPT_DIR/schema"

echo "=============================================="
echo "MYTHOS ASTROLOGY SYSTEM - Installation"
echo "=============================================="

# ============================================================================
# PostgreSQL Setup
# ============================================================================

echo ""
echo "=== PostgreSQL Schema ==="

# Run schema
echo "Creating tables..."
sudo -u postgres psql -d mythos -f "$SCHEMA_DIR/postgres_schema.sql" 2>&1 | grep -v "NOTICE" || true

# Run seed data
echo "Loading reference data..."
sudo -u postgres psql -d mythos -f "$SCHEMA_DIR/postgres_seed.sql" 2>&1 | grep -v "NOTICE" || true

# Verify
echo "Verifying PostgreSQL tables..."
TABLES=$(sudo -u postgres psql -d mythos -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_name LIKE 'astro_%'")
echo "  Created $TABLES astrology tables"

SIGNS=$(sudo -u postgres psql -d mythos -t -c "SELECT COUNT(*) FROM astro_signs")
echo "  Loaded $SIGNS zodiac signs"

BODIES=$(sudo -u postgres psql -d mythos -t -c "SELECT COUNT(*) FROM astro_bodies")
echo "  Loaded $BODIES celestial bodies"

# ============================================================================
# Neo4j Setup
# ============================================================================

echo ""
echo "=== Neo4j Schema ==="

# Load Neo4j credentials from .env
if [ -f /opt/mythos/.env ]; then
    source /opt/mythos/.env
fi

NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-}"
NEO4J_URI="${NEO4J_URI:-bolt://localhost:7687}"

if [ -z "$NEO4J_PASSWORD" ]; then
    echo "Warning: NEO4J_PASSWORD not set in .env"
    echo "Skipping Neo4j setup - run manually with:"
    echo "  cat $SCHEMA_DIR/neo4j_schema.cypher | cypher-shell -u neo4j -p <password>"
else
    echo "Creating constraints and loading data..."
    
    # Split the cypher file into smaller chunks to avoid memory issues
    # Run it through cypher-shell
    cat "$SCHEMA_DIR/neo4j_schema.cypher" | cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" -a "$NEO4J_URI" 2>&1 || {
        echo "Warning: Some Neo4j commands may have failed (constraints may already exist)"
    }
    
    echo "Verifying Neo4j nodes..."
    NODES=$(echo "MATCH (n) RETURN count(n) AS count" | cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" -a "$NEO4J_URI" --format plain 2>/dev/null | tail -1)
    echo "  Total nodes in Neo4j: $NODES"
fi

# ============================================================================
# Copy documentation
# ============================================================================

echo ""
echo "=== Documentation ==="

mkdir -p /opt/mythos/docs/astrology
cp -v "$SCRIPT_DIR/docs/ASTROLOGY.md" /opt/mythos/docs/astrology/

# ============================================================================
# Create astrology module directory
# ============================================================================

echo ""
echo "=== Creating Module Structure ==="

mkdir -p /opt/mythos/astrology/{charts,ephemeris,transits}
cp -r "$SCHEMA_DIR" /opt/mythos/astrology/

echo "  Created /opt/mythos/astrology/"

# ============================================================================
# Summary
# ============================================================================

echo ""
echo "=============================================="
echo "Installation Complete!"
echo "=============================================="
echo ""
echo "PostgreSQL tables: astro_*"
echo "  - astro_signs, astro_bodies, astro_houses"
echo "  - astro_charts, astro_placements, astro_aspects"
echo "  - astro_ephemeris, astro_transits, astro_events"
echo ""
echo "Neo4j nodes:"
echo "  - Sign, Body, House, AspectType"
echo "  - Element, Modality"
echo "  - Chart, Placement (for actual charts)"
echo ""
echo "Next steps:"
echo "  1. Install Swiss Ephemeris: pip install pyswisseph"
echo "  2. Create ephemeris updater script"
echo "  3. Import natal charts for Ka'tuar'el, Seraphe, Fitz, Iris"
echo ""
echo "Documentation: /opt/mythos/docs/astrology/ASTROLOGY.md"
echo ""
