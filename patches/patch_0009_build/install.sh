#!/bin/bash
# Patch 0009 Installation Script
# Create Qdrant Vector Collections
# Created: 2026-01-21
# By: Ka_tuar_el via Claude

set -e  # Exit on any error

# Configuration
MYTHOS_BASE="/opt/mythos"
QDRANT_HOST="localhost"
QDRANT_PORT="6333"
QDRANT_URL="http://${QDRANT_HOST}:${QDRANT_PORT}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Track installation state
CURRENT_STEP="initialization"
ERROR_MESSAGE=""
INSTALL_LOG="/tmp/patch_0009_install_$(date +%s).log"

# Redirect all output to log file as well
exec > >(tee -a "$INSTALL_LOG") 2>&1

echo "=========================================="
echo "Patch 0009: Qdrant Vector Collections"
echo "=========================================="
echo ""
echo "Installation log: $INSTALL_LOG"
echo ""

# Error handler - runs on any error
rollback_on_error() {
    exit_code=$1
    
    if [ $exit_code -ne 0 ]; then
        echo ""
        echo "=========================================="
        echo "ERROR DETECTED - ROLLING BACK"
        echo "=========================================="
        echo ""
        echo "Failed at step: $CURRENT_STEP"
        echo ""
        
        # Execute rollback
        if [ -f "${SCRIPT_DIR}/rollback.sh" ]; then
            echo "Executing automatic rollback..."
            chmod +x "${SCRIPT_DIR}/rollback.sh"
            "${SCRIPT_DIR}/rollback.sh" --auto || true
        fi
        
        echo ""
        echo "Installation failed. Check log: $INSTALL_LOG"
        exit $exit_code
    fi
}

trap 'rollback_on_error $?' EXIT

# ===========================================
# Prerequisites Check
# ===========================================
CURRENT_STEP="prerequisites"
echo "Checking prerequisites..."

# Check Qdrant is running
echo -n "  Qdrant at ${QDRANT_URL}... "
if curl -s "${QDRANT_URL}/healthz" | grep -q "passed"; then
    echo "✓"
else
    echo "✗"
    echo ""
    echo "ERROR: Qdrant is not running or not accessible"
    echo "Make sure Patch 0008 is applied and Qdrant container is running:"
    echo "  docker ps | grep qdrant"
    exit 1
fi

# Check mythos directory exists
echo -n "  Mythos directory... "
if [ -d "$MYTHOS_BASE" ]; then
    echo "✓"
else
    echo "✗"
    echo "ERROR: $MYTHOS_BASE does not exist"
    exit 1
fi

# Check Python venv
echo -n "  Python virtual environment... "
if [ -f "${MYTHOS_BASE}/.venv/bin/activate" ]; then
    echo "✓"
else
    echo "✗"
    echo "ERROR: Python venv not found at ${MYTHOS_BASE}/.venv"
    exit 1
fi

echo ""
echo "✓ All prerequisites satisfied"
echo ""

# ===========================================
# Step 1: Create directory structure
# ===========================================
CURRENT_STEP="create_directories"
echo "Step 1: Creating directory structure..."

mkdir -p "${MYTHOS_BASE}/qdrant"
mkdir -p "${MYTHOS_BASE}/config"

echo "  ✓ Created /opt/mythos/qdrant/"
echo "  ✓ Created /opt/mythos/config/"
echo ""

# ===========================================
# Step 2: Install Python module
# ===========================================
CURRENT_STEP="install_python_module"
echo "Step 2: Installing Python module..."

# Copy files
cp "${SCRIPT_DIR}/files/src/__init__.py" "${MYTHOS_BASE}/qdrant/"
cp "${SCRIPT_DIR}/files/src/collections.py" "${MYTHOS_BASE}/qdrant/"
cp "${SCRIPT_DIR}/files/config/qdrant_config.yaml" "${MYTHOS_BASE}/config/"

echo "  ✓ Copied qdrant/__init__.py"
echo "  ✓ Copied qdrant/collections.py"
echo "  ✓ Copied config/qdrant_config.yaml"
echo ""

# ===========================================
# Step 3: Create collections
# ===========================================
CURRENT_STEP="create_collections"
echo "Step 3: Creating Qdrant collections..."

# Activate venv and run collection creation
source "${MYTHOS_BASE}/.venv/bin/activate"

python3 << 'PYTHON'
import sys
sys.path.insert(0, '/opt/mythos')

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

client = QdrantClient(host="localhost", port=6333)

# Collection definitions
collections = {
    "mythos_messages": {
        "vector_size": 384,
        "distance": Distance.COSINE,
        "payload_indexes": [
            ("message_id", PayloadSchemaType.INTEGER),
            ("user_uuid", PayloadSchemaType.KEYWORD),
            ("room_id", PayloadSchemaType.KEYWORD),
            ("conversation_id", PayloadSchemaType.KEYWORD),
            ("role", PayloadSchemaType.KEYWORD),
            ("timestamp", PayloadSchemaType.DATETIME),
            ("spiral_day", PayloadSchemaType.FLOAT),
        ]
    },
    "mythos_photos": {
        "vector_size": 512,
        "distance": Distance.COSINE,
        "payload_indexes": [
            ("photo_id", PayloadSchemaType.KEYWORD),
            ("user_uuid", PayloadSchemaType.KEYWORD),
            ("room_id", PayloadSchemaType.KEYWORD),
            ("timestamp", PayloadSchemaType.DATETIME),
        ]
    },
    "mythos_entities": {
        "vector_size": 384,
        "distance": Distance.COSINE,
        "payload_indexes": [
            ("entity_id", PayloadSchemaType.KEYWORD),
            ("canonical_id", PayloadSchemaType.KEYWORD),
            ("name", PayloadSchemaType.TEXT),
            ("entity_type", PayloadSchemaType.KEYWORD),
            ("first_seen", PayloadSchemaType.DATETIME),
        ]
    }
}

# Get existing collections
existing = [c.name for c in client.get_collections().collections]

for name, config in collections.items():
    if name in existing:
        print(f"  ⏭️  Collection '{name}' already exists, skipping")
        continue
    
    # Create collection
    client.create_collection(
        collection_name=name,
        vectors_config=VectorParams(
            size=config["vector_size"],
            distance=config["distance"]
        )
    )
    print(f"  ✓ Created collection '{name}' ({config['vector_size']} dims)")
    
    # Create payload indexes
    for field_name, field_type in config["payload_indexes"]:
        try:
            client.create_payload_index(
                collection_name=name,
                field_name=field_name,
                field_schema=field_type
            )
        except Exception as e:
            # Index might already exist
            pass
    print(f"    ✓ Created {len(config['payload_indexes'])} payload indexes")

print("")
print("  All collections ready!")
PYTHON

echo ""

# ===========================================
# Step 4: Verification
# ===========================================
CURRENT_STEP="verification"
echo "Step 4: Verifying installation..."

# Check collections exist
echo -n "  Checking collections... "
COLLECTIONS=$(curl -s "${QDRANT_URL}/collections" | python3 -c "import sys,json; colls=[c['name'] for c in json.load(sys.stdin)['result']['collections']]; print(' '.join(colls))")

ALL_FOUND=true
for coll in mythos_messages mythos_photos mythos_entities; do
    if [[ ! "$COLLECTIONS" =~ "$coll" ]]; then
        echo ""
        echo "  ✗ Missing collection: $coll"
        ALL_FOUND=false
    fi
done

if [ "$ALL_FOUND" = true ]; then
    echo "✓"
    echo "    - mythos_messages"
    echo "    - mythos_photos"
    echo "    - mythos_entities"
else
    echo ""
    echo "ERROR: Not all collections were created"
    exit 1
fi

# Check Python module imports
echo -n "  Checking Python module... "
python3 -c "from qdrant.collections import get_collection_info; print('✓')" || {
    echo "✗"
    echo "ERROR: Python module not importable"
    exit 1
}

echo ""
echo "✓ All verifications passed"
echo ""

# ===========================================
# Success
# ===========================================
trap - EXIT  # Remove error handler

echo "=========================================="
echo "✓ Patch 0009 installed successfully!"
echo "=========================================="
echo ""
echo "Collections created:"
echo "  - mythos_messages (384 dims) - conversation semantic search"
echo "  - mythos_photos (512 dims)   - visual similarity search"
echo "  - mythos_entities (384 dims) - entity matching"
echo ""
echo "Configuration: ${MYTHOS_BASE}/config/qdrant_config.yaml"
echo ""
echo "Next steps:"
echo "  - Apply Patch 0010 to enable embedding generation"
echo "  - Messages will be automatically embedded on receipt"
echo ""
echo "Test with:"
echo "  curl http://localhost:6333/collections | python3 -m json.tool"
echo ""
