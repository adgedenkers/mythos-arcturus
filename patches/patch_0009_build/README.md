# Patch 0009: Qdrant Vector Collections

## Overview

This patch creates the vector collections in Qdrant required for semantic search across the Mythos system. It establishes three primary collections for message embeddings, photo embeddings, and entity embeddings.

## What This Patch Does

### Creates

- `/opt/mythos/qdrant/` - Qdrant management module
  - `collections.py` - Collection creation and management utilities
  - `__init__.py` - Module initialization
- `/opt/mythos/config/qdrant_config.yaml` - Collection configuration

### Collections Created

| Collection | Vector Size | Distance | Purpose |
|------------|-------------|----------|---------|
| `mythos_messages` | 384 | Cosine | Semantic search of conversation content |
| `mythos_photos` | 512 | Cosine | Visual similarity search of images |
| `mythos_entities` | 384 | Cosine | Semantic entity matching and deduplication |

### Features

- **Automatic collection creation** with proper schemas
- **Payload indexes** for efficient filtering by user, room, timestamp
- **Idempotent setup** - safe to run multiple times
- **Health verification** - confirms collections are accessible
- **Python utilities** for collection management

## Prerequisites

- Patch 0008 applied (Qdrant container running)
- Qdrant accessible at `localhost:6333`
- Docker running

## Installation

```bash
# Extract and install
cd ~/Downloads
unzip patch_0009_qdrant_collections.zip
cd patch_0009_build
./install.sh
```

## Verification

```bash
# Check collections exist
curl -s http://localhost:6333/collections | python3 -m json.tool

# Expected output includes:
# - mythos_messages
# - mythos_photos  
# - mythos_entities

# Or use the Python utility
cd /opt/mythos
source .venv/bin/activate
python3 -c "from qdrant.collections import list_collections; print(list_collections())"
```

## Configuration

Edit `/opt/mythos/config/qdrant_config.yaml` to adjust:

```yaml
collections:
  messages:
    name: mythos_messages
    vector_size: 384
    distance: Cosine
    
  photos:
    name: mythos_photos
    vector_size: 512
    distance: Cosine
    
  entities:
    name: mythos_entities
    vector_size: 384
    distance: Cosine

connection:
  host: localhost
  port: 6333
  timeout: 30
```

## Rollback

```bash
./rollback.sh
```

This will:
- Delete the created collections from Qdrant
- Remove the `/opt/mythos/qdrant/` directory
- Remove the configuration file

## Collection Schemas

### mythos_messages

Stores embeddings of conversation messages for semantic search.

**Vector**: 384 dimensions (sentence-transformers/all-MiniLM-L6-v2)

**Payload fields**:
| Field | Type | Indexed | Description |
|-------|------|---------|-------------|
| `message_id` | integer | Yes | PostgreSQL message ID |
| `user_uuid` | keyword | Yes | User identifier |
| `room_id` | keyword | Yes | Room identifier |
| `conversation_id` | keyword | Yes | Legacy conversation ID |
| `content` | text | No | Original message text |
| `role` | keyword | Yes | user/assistant |
| `timestamp` | datetime | Yes | Message timestamp |
| `spiral_day` | float | Yes | Spiral time day |

### mythos_photos

Stores embeddings of photos for visual similarity search.

**Vector**: 512 dimensions (CLIP or similar vision model)

**Payload fields**:
| Field | Type | Indexed | Description |
|-------|------|---------|-------------|
| `photo_id` | keyword | Yes | Media file identifier |
| `user_uuid` | keyword | Yes | User who uploaded |
| `room_id` | keyword | Yes | Room where shared |
| `file_path` | text | No | Path to file |
| `timestamp` | datetime | Yes | Upload timestamp |
| `location_lat` | float | No | GPS latitude |
| `location_lon` | float | No | GPS longitude |
| `analysis` | text | No | Vision analysis result |

### mythos_entities

Stores embeddings of entities for semantic matching and deduplication.

**Vector**: 384 dimensions (sentence-transformers/all-MiniLM-L6-v2)

**Payload fields**:
| Field | Type | Indexed | Description |
|-------|------|---------|-------------|
| `entity_id` | keyword | Yes | Neo4j node ID |
| `canonical_id` | keyword | Yes | Canonical entity ID |
| `name` | text | Yes | Entity name |
| `entity_type` | keyword | Yes | person/place/concept/etc |
| `aliases` | text[] | No | Alternative names |
| `first_seen` | datetime | Yes | First mention timestamp |

## Usage Examples

### Search for similar messages

```python
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

client = QdrantClient(host="localhost", port=6333)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Encode query
query = "spiral time and consciousness"
query_vector = model.encode(query).tolist()

# Search
results = client.search(
    collection_name="mythos_messages",
    query_vector=query_vector,
    limit=5,
    query_filter={
        "must": [
            {"key": "user_uuid", "match": {"value": "user-uuid-here"}}
        ]
    }
)
```

### Add a message embedding

```python
from qdrant_client.models import PointStruct

client.upsert(
    collection_name="mythos_messages",
    points=[
        PointStruct(
            id=message_id,  # Use PostgreSQL message_id
            vector=embedding,
            payload={
                "message_id": message_id,
                "user_uuid": "uuid",
                "room_id": "room-uuid",
                "content": "original text",
                "role": "user",
                "timestamp": "2026-01-21T12:00:00Z"
            }
        )
    ]
)
```

## Troubleshooting

### Collections not created

```bash
# Check Qdrant is running
curl http://localhost:6333/healthz

# Check Docker container
docker ps | grep qdrant

# Check logs
docker logs mythos-qdrant
```

### Collection already exists error

The install script is idempotent - it will skip existing collections. If you need to recreate:

```bash
# Delete and recreate
curl -X DELETE http://localhost:6333/collections/mythos_messages
./install.sh
```

### Vector dimension mismatch

Ensure your embedding model produces vectors of the correct dimension:
- Messages/Entities: 384 (all-MiniLM-L6-v2)
- Photos: 512 (CLIP)

## Files Created

```
/opt/mythos/
├── qdrant/
│   ├── __init__.py
│   └── collections.py
└── config/
    └── qdrant_config.yaml
```

## Next Steps

After this patch:
- Patch 0010: Embedding worker implementation (generates embeddings)
- Messages will be automatically embedded on receipt
- Semantic search will be available in context assembly

## Performance Notes

- **Initial creation**: < 1 second per collection
- **Storage**: ~1KB per vector (before payload)
- **Search latency**: < 10ms for 100K vectors
- **Recommended**: Enable HNSW indexing for collections > 10K vectors (automatic)
