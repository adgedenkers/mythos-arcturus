#!/bin/bash
# Install script for Triad Memory System
# Knowledge (Grid) / Wisdom (Akashic) / Vision (Prophetic)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MYTHOS_DIR="/opt/mythos"
VENV_PYTHON="${MYTHOS_DIR}/.venv/bin/python3"

echo "=========================================="
echo "Installing Triad Memory System"
echo "=========================================="

# Copy triad module
echo "[1/4] Copying triad module..."
cp -r "${SCRIPT_DIR}/opt/mythos/triad" "${MYTHOS_DIR}/"
chown -R claude:claude "${MYTHOS_DIR}/triad"
echo "  ✓ Module installed to ${MYTHOS_DIR}/triad"

# Run PostgreSQL schema
echo "[2/4] Running PostgreSQL schema..."
sudo -u postgres psql -d mythos -f "${MYTHOS_DIR}/triad/schema.sql"
echo "  ✓ PostgreSQL tables created"

# Run Neo4j schema (if neo4j is available)
echo "[3/4] Running Neo4j schema..."
if command -v cypher-shell &> /dev/null; then
    NEO4J_USER="${NEO4J_USER:-neo4j}"
    NEO4J_PASS="${NEO4J_PASS:-password}"
    cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASS" -f "${MYTHOS_DIR}/triad/schema_neo4j.cypher" 2>/dev/null || {
        echo "  ⚠ Neo4j schema skipped (connection failed - run manually if needed)"
    }
else
    echo "  ⚠ cypher-shell not found, skipping Neo4j schema"
    echo "    Run manually: cypher-shell -f ${MYTHOS_DIR}/triad/schema_neo4j.cypher"
fi

# Install Python dependencies
echo "[4/4] Checking Python dependencies..."
"${VENV_PYTHON}" -c "import httpx" 2>/dev/null || {
    echo "  Installing httpx..."
    "${MYTHOS_DIR}/.venv/bin/pip" install httpx
}
echo "  ✓ Dependencies verified"

echo ""
echo "=========================================="
echo "Triad Memory System Installed Successfully"
echo "=========================================="
echo ""
echo "Usage:"
echo "  from triad import TriadExtractor"
echo "  extractor = TriadExtractor()"
echo "  record = await extractor.extract_all(prompt, response)"
echo ""
echo "CLI test:"
echo "  cd ${MYTHOS_DIR}"
echo "  ${VENV_PYTHON} -m triad.extractor --help"
echo ""
echo "Configuration (env vars):"
echo "  TRIAD_LLM_BACKEND=ollama|anthropic"
echo "  TRIAD_OLLAMA_MODEL=llama3.2"
echo "  TRIAD_EMBEDDING_MODEL=nomic-embed-text"
echo "  OLLAMA_URL=http://localhost:11434"
echo ""
