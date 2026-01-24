#!/usr/bin/env python3
"""
Step 1: Qdrant Vector Database Setup

Creates collections for:
- text_embeddings: Message and conversation embeddings
- image_embeddings: Photo embeddings (CLIP)

Usage: python3 step1_qdrant_setup.py
"""

import sys
import time
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, 
    VectorParams, 
    OptimizersConfigDiff,
    HnswConfigDiff,
    PayloadSchemaType
)

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

# Collection configurations
COLLECTIONS = {
    "text_embeddings": {
        "size": 384,  # all-MiniLM-L6-v2 dimension
        "distance": Distance.COSINE,
        "description": "Text embeddings for messages, summaries, and conversations",
        "payload_indexes": [
            ("user_uuid", PayloadSchemaType.KEYWORD),
            ("conversation_id", PayloadSchemaType.KEYWORD),
            ("message_type", PayloadSchemaType.KEYWORD),
            ("created_at", PayloadSchemaType.DATETIME),
        ]
    },
    "image_embeddings": {
        "size": 512,  # CLIP ViT-B/32 dimension
        "distance": Distance.COSINE,
        "description": "Image embeddings for photos using CLIP",
        "payload_indexes": [
            ("user_uuid", PayloadSchemaType.KEYWORD),
            ("conversation_id", PayloadSchemaType.KEYWORD),
            ("photo_id", PayloadSchemaType.KEYWORD),
            ("created_at", PayloadSchemaType.DATETIME),
            ("has_symbols", PayloadSchemaType.BOOL),
        ]
    }
}


def wait_for_qdrant(client: QdrantClient, max_attempts: int = 30) -> bool:
    """Wait for Qdrant to be ready"""
    for attempt in range(max_attempts):
        try:
            health = client.get_collections()
            print(f"✓ Qdrant is ready (found {len(health.collections)} existing collections)")
            return True
        except Exception as e:
            if attempt < max_attempts - 1:
                print(f"  Waiting for Qdrant... (attempt {attempt + 1}/{max_attempts})")
                time.sleep(2)
            else:
                print(f"✗ Qdrant not responding after {max_attempts} attempts: {e}")
                return False
    return False


def create_collection(client: QdrantClient, name: str, config: dict) -> bool:
    """Create a Qdrant collection with optimized settings"""
    
    # Check if collection exists
    collections = client.get_collections().collections
    existing_names = [c.name for c in collections]
    
    if name in existing_names:
        print(f"  Collection '{name}' already exists - skipping creation")
        
        # Verify configuration matches
        collection_info = client.get_collection(name)
        current_size = collection_info.config.params.vectors.size
        if current_size != config["size"]:
            print(f"  ⚠️  Warning: Existing collection has size {current_size}, expected {config['size']}")
            print(f"     You may need to recreate this collection if dimensions changed")
        
        return True
    
    print(f"  Creating collection: {name}")
    print(f"    - Vector size: {config['size']}")
    print(f"    - Distance: {config['distance']}")
    print(f"    - Description: {config['description']}")
    
    try:
        # Create collection with optimized settings
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=config["size"],
                distance=config["distance"]
            ),
            # Optimize for search performance
            hnsw_config=HnswConfigDiff(
                m=16,  # Number of edges per node
                ef_construct=100,  # Construction time/quality tradeoff
            ),
            optimizers_config=OptimizersConfigDiff(
                indexing_threshold=20000,  # Start indexing after this many vectors
            )
        )
        
        # Create payload indexes for filtering
        for field_name, field_type in config.get("payload_indexes", []):
            print(f"    - Creating index: {field_name} ({field_type})")
            client.create_payload_index(
                collection_name=name,
                field_name=field_name,
                field_schema=field_type
            )
        
        print(f"  ✓ Collection '{name}' created successfully")
        return True
        
    except Exception as e:
        print(f"  ✗ Failed to create collection '{name}': {e}")
        return False


def verify_collections(client: QdrantClient) -> None:
    """Print collection statistics"""
    print("\n  Collection Status:")
    print("  " + "-" * 50)
    
    for name in COLLECTIONS.keys():
        try:
            info = client.get_collection(name)
            print(f"  {name}:")
            print(f"    - Points: {info.points_count}")
            print(f"    - Vectors: {info.vectors_count}")
            print(f"    - Status: {info.status}")
        except Exception as e:
            print(f"  {name}: ✗ Error - {e}")


def main():
    print("\n" + "=" * 60)
    print("  Qdrant Vector Database Setup")
    print("=" * 60 + "\n")
    
    # Connect to Qdrant
    print(f"Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}...")
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    # Wait for Qdrant to be ready
    if not wait_for_qdrant(client):
        print("\n✗ Setup failed: Qdrant not available")
        sys.exit(1)
    
    # Create collections
    print("\nCreating collections...")
    all_success = True
    
    for name, config in COLLECTIONS.items():
        if not create_collection(client, name, config):
            all_success = False
    
    # Verify setup
    verify_collections(client)
    
    if all_success:
        print("\n" + "=" * 60)
        print("  ✓ Qdrant setup complete!")
        print("=" * 60)
        print("\nCollections ready:")
        print("  - text_embeddings: For message/conversation semantic search")
        print("  - image_embeddings: For photo similarity search")
        print("\nAPI endpoints:")
        print(f"  - REST: http://{QDRANT_HOST}:{QDRANT_PORT}")
        print(f"  - gRPC: {QDRANT_HOST}:6334")
        print(f"  - Dashboard: http://{QDRANT_HOST}:{QDRANT_PORT}/dashboard")
        print()
    else:
        print("\n✗ Setup completed with errors")
        sys.exit(1)


if __name__ == "__main__":
    main()
