#!/bin/bash
# Patch 0114: Ontology v2 Schema Migration + Moon Data Load
# Migrates existing 71 OntologyTerm nodes to v2 schema, loads 21 moon terms
set -e

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
source /opt/mythos/.env

echo "=== Patch 0114: Ontology v2 + Moon Data ==="

# 1. Run Cypher to migrate schema + load moon terms
echo "[1/4] Running Cypher: schema migration + moon term load..."
cat "$PATCH_DIR/load_moon_terms.cypher" | cypher-shell \
    -u "$NEO4J_USER" \
    -p "$NEO4J_PASSWORD" \
    --format plain 2>&1

echo "[2/4] Verifying node count..."
echo "MATCH (t:OntologyTerm) RETURN count(t) as total, count(CASE WHEN t.category = 'Lunar' THEN 1 END) as lunar;" | \
    cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" --format plain

# 3. Copy reference docs to /opt/mythos/docs/
echo "[3/4] Installing reference documentation..."
if [ -f "$PATCH_DIR/opt/mythos/docs/ONTOLOGY_V2_ARCHITECTURE.md" ]; then
    cp "$PATCH_DIR/opt/mythos/docs/ONTOLOGY_V2_ARCHITECTURE.md" /opt/mythos/docs/
    echo "  ✓ ONTOLOGY_V2_ARCHITECTURE.md"
fi
if [ -f "$PATCH_DIR/opt/mythos/docs/MONTHLY_MOONS_REFERENCE.md" ]; then
    cp "$PATCH_DIR/opt/mythos/docs/MONTHLY_MOONS_REFERENCE.md" /opt/mythos/docs/
    echo "  ✓ MONTHLY_MOONS_REFERENCE.md"
fi

# 4. Copy SQL + JSON reference data
if [ -f "$PATCH_DIR/opt/mythos/data/lunar/monthly_moons_ontology.sql" ]; then
    mkdir -p /opt/mythos/data/lunar
    cp "$PATCH_DIR/opt/mythos/data/lunar/monthly_moons_ontology.sql" /opt/mythos/data/lunar/
    cp "$PATCH_DIR/opt/mythos/data/lunar/monthly_moons_cross_reference.json" /opt/mythos/data/lunar/
    echo "  ✓ Reference data installed to /opt/mythos/data/lunar/"
fi

echo "[4/4] Done."
echo ""
echo "=== Patch 0114 Complete ==="
echo "  • Existing nodes migrated to v2 schema (confidence, source, version, is_active)"
echo "  • 12 monthly moon terms created (category: Lunar)"
echo "  • 8 special moon types created (Blue Moon, Supermoon, etc.)"
echo "  • 1 parent grouping node (Monthly Moon Cycle)"
echo "  • Relationships wired (PART_OF, RELATED_TO)"
echo ""
echo "Test: /define Wolf Moon"
echo "Test: /define list Lunar"
