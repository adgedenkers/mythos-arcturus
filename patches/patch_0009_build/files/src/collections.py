"""
Mythos Qdrant Collections

Utilities for managing and querying Qdrant vector collections.
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    Range,
    SearchParams,
    Distance,
    VectorParams,
)

# Configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

# Collection names
MESSAGES_COLLECTION = "mythos_messages"
PHOTOS_COLLECTION = "mythos_photos"
ENTITIES_COLLECTION = "mythos_entities"

# Global client instance
_client: Optional[QdrantClient] = None


def get_client() -> QdrantClient:
    """Get or create Qdrant client instance."""
    global _client
    if _client is None:
        _client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    return _client


def list_collections() -> List[str]:
    """List all collection names."""
    client = get_client()
    collections = client.get_collections()
    return [c.name for c in collections.collections]


def get_collection_info(collection_name: str) -> Dict[str, Any]:
    """Get detailed information about a collection."""
    client = get_client()
    info = client.get_collection(collection_name)
    return {
        "name": collection_name,
        "vectors_count": info.vectors_count,
        "points_count": info.points_count,
        "status": info.status.value,
        "config": {
            "vector_size": info.config.params.vectors.size,
            "distance": info.config.params.vectors.distance.value,
        }
    }


# =============================================================================
# Message Embeddings
# =============================================================================

def upsert_message_embedding(
    message_id: int,
    embedding: List[float],
    user_uuid: str,
    room_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    content: str = "",
    role: str = "user",
    timestamp: Optional[datetime] = None,
    spiral_day: Optional[float] = None,
) -> bool:
    """
    Insert or update a message embedding.
    
    Args:
        message_id: PostgreSQL message ID (used as point ID)
        embedding: Vector embedding (384 dimensions)
        user_uuid: User identifier
        room_id: Room identifier (new model)
        conversation_id: Conversation ID (legacy)
        content: Original message text
        role: Message role (user/assistant)
        timestamp: Message timestamp
        spiral_day: Spiral time day
        
    Returns:
        True if successful
    """
    client = get_client()
    
    payload = {
        "message_id": message_id,
        "user_uuid": user_uuid,
        "content": content,
        "role": role,
    }
    
    if room_id:
        payload["room_id"] = room_id
    if conversation_id:
        payload["conversation_id"] = conversation_id
    if timestamp:
        payload["timestamp"] = timestamp.isoformat()
    if spiral_day is not None:
        payload["spiral_day"] = spiral_day
    
    client.upsert(
        collection_name=MESSAGES_COLLECTION,
        points=[
            PointStruct(
                id=message_id,
                vector=embedding,
                payload=payload
            )
        ]
    )
    return True


def search_messages(
    query_vector: List[float],
    limit: int = 5,
    user_uuid: Optional[str] = None,
    room_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    min_score: float = 0.0,
) -> List[Dict[str, Any]]:
    """
    Search for similar messages.
    
    Args:
        query_vector: Query embedding (384 dimensions)
        limit: Maximum results to return
        user_uuid: Filter by user
        room_id: Filter by room
        conversation_id: Filter by conversation (legacy)
        min_score: Minimum similarity score
        
    Returns:
        List of matching messages with scores
    """
    client = get_client()
    
    # Build filter conditions
    conditions = []
    if user_uuid:
        conditions.append(
            FieldCondition(key="user_uuid", match=MatchValue(value=user_uuid))
        )
    if room_id:
        conditions.append(
            FieldCondition(key="room_id", match=MatchValue(value=room_id))
        )
    if conversation_id:
        conditions.append(
            FieldCondition(key="conversation_id", match=MatchValue(value=conversation_id))
        )
    
    query_filter = Filter(must=conditions) if conditions else None
    
    results = client.search(
        collection_name=MESSAGES_COLLECTION,
        query_vector=query_vector,
        limit=limit,
        query_filter=query_filter,
        score_threshold=min_score,
    )
    
    return [
        {
            "id": hit.id,
            "score": hit.score,
            **hit.payload
        }
        for hit in results
    ]


# =============================================================================
# Photo Embeddings
# =============================================================================

def upsert_photo_embedding(
    photo_id: str,
    embedding: List[float],
    user_uuid: str,
    room_id: Optional[str] = None,
    file_path: str = "",
    timestamp: Optional[datetime] = None,
    location_lat: Optional[float] = None,
    location_lon: Optional[float] = None,
    analysis: str = "",
) -> bool:
    """
    Insert or update a photo embedding.
    
    Args:
        photo_id: Unique photo identifier
        embedding: Vector embedding (512 dimensions)
        user_uuid: User who uploaded
        room_id: Room where shared
        file_path: Path to file
        timestamp: Upload timestamp
        location_lat: GPS latitude
        location_lon: GPS longitude
        analysis: Vision analysis result
        
    Returns:
        True if successful
    """
    client = get_client()
    
    payload = {
        "photo_id": photo_id,
        "user_uuid": user_uuid,
        "file_path": file_path,
    }
    
    if room_id:
        payload["room_id"] = room_id
    if timestamp:
        payload["timestamp"] = timestamp.isoformat()
    if location_lat is not None:
        payload["location_lat"] = location_lat
    if location_lon is not None:
        payload["location_lon"] = location_lon
    if analysis:
        payload["analysis"] = analysis
    
    # Use hash of photo_id as numeric ID
    point_id = abs(hash(photo_id)) % (2**63)
    
    client.upsert(
        collection_name=PHOTOS_COLLECTION,
        points=[
            PointStruct(
                id=point_id,
                vector=embedding,
                payload=payload
            )
        ]
    )
    return True


def search_photos(
    query_vector: List[float],
    limit: int = 5,
    user_uuid: Optional[str] = None,
    room_id: Optional[str] = None,
    min_score: float = 0.0,
) -> List[Dict[str, Any]]:
    """
    Search for similar photos.
    
    Args:
        query_vector: Query embedding (512 dimensions)
        limit: Maximum results to return
        user_uuid: Filter by user
        room_id: Filter by room
        min_score: Minimum similarity score
        
    Returns:
        List of matching photos with scores
    """
    client = get_client()
    
    conditions = []
    if user_uuid:
        conditions.append(
            FieldCondition(key="user_uuid", match=MatchValue(value=user_uuid))
        )
    if room_id:
        conditions.append(
            FieldCondition(key="room_id", match=MatchValue(value=room_id))
        )
    
    query_filter = Filter(must=conditions) if conditions else None
    
    results = client.search(
        collection_name=PHOTOS_COLLECTION,
        query_vector=query_vector,
        limit=limit,
        query_filter=query_filter,
        score_threshold=min_score,
    )
    
    return [
        {
            "id": hit.id,
            "score": hit.score,
            **hit.payload
        }
        for hit in results
    ]


# =============================================================================
# Entity Embeddings
# =============================================================================

def upsert_entity_embedding(
    entity_id: str,
    embedding: List[float],
    canonical_id: str,
    name: str,
    entity_type: str,
    aliases: Optional[List[str]] = None,
    first_seen: Optional[datetime] = None,
) -> bool:
    """
    Insert or update an entity embedding.
    
    Args:
        entity_id: Neo4j node ID
        embedding: Vector embedding (384 dimensions)
        canonical_id: Canonical entity identifier
        name: Entity name
        entity_type: Type (person/place/concept/etc)
        aliases: Alternative names
        first_seen: First mention timestamp
        
    Returns:
        True if successful
    """
    client = get_client()
    
    payload = {
        "entity_id": entity_id,
        "canonical_id": canonical_id,
        "name": name,
        "entity_type": entity_type,
    }
    
    if aliases:
        payload["aliases"] = aliases
    if first_seen:
        payload["first_seen"] = first_seen.isoformat()
    
    # Use hash of entity_id as numeric ID
    point_id = abs(hash(entity_id)) % (2**63)
    
    client.upsert(
        collection_name=ENTITIES_COLLECTION,
        points=[
            PointStruct(
                id=point_id,
                vector=embedding,
                payload=payload
            )
        ]
    )
    return True


def search_entities(
    query_vector: List[float],
    limit: int = 5,
    entity_type: Optional[str] = None,
    min_score: float = 0.0,
) -> List[Dict[str, Any]]:
    """
    Search for similar entities.
    
    Args:
        query_vector: Query embedding (384 dimensions)
        limit: Maximum results to return
        entity_type: Filter by type
        min_score: Minimum similarity score
        
    Returns:
        List of matching entities with scores
    """
    client = get_client()
    
    conditions = []
    if entity_type:
        conditions.append(
            FieldCondition(key="entity_type", match=MatchValue(value=entity_type))
        )
    
    query_filter = Filter(must=conditions) if conditions else None
    
    results = client.search(
        collection_name=ENTITIES_COLLECTION,
        query_vector=query_vector,
        limit=limit,
        query_filter=query_filter,
        score_threshold=min_score,
    )
    
    return [
        {
            "id": hit.id,
            "score": hit.score,
            **hit.payload
        }
        for hit in results
    ]


def find_similar_entity(
    name: str,
    embedding: List[float],
    entity_type: Optional[str] = None,
    threshold: float = 0.85,
) -> Optional[Dict[str, Any]]:
    """
    Find an existing entity that matches the given name/embedding.
    
    Used for entity deduplication - checks if an entity already exists
    before creating a new one.
    
    Args:
        name: Entity name to match
        embedding: Vector embedding
        entity_type: Filter by type
        threshold: Minimum similarity to consider a match
        
    Returns:
        Matching entity if found, None otherwise
    """
    results = search_entities(
        query_vector=embedding,
        limit=1,
        entity_type=entity_type,
        min_score=threshold,
    )
    
    if results:
        return results[0]
    return None


# =============================================================================
# Utility Functions
# =============================================================================

def delete_by_user(user_uuid: str) -> Dict[str, int]:
    """
    Delete all vectors for a user (GDPR compliance).
    
    Args:
        user_uuid: User identifier
        
    Returns:
        Count of deleted points per collection
    """
    client = get_client()
    deleted = {}
    
    for collection in [MESSAGES_COLLECTION, PHOTOS_COLLECTION]:
        result = client.delete(
            collection_name=collection,
            points_selector=Filter(
                must=[
                    FieldCondition(key="user_uuid", match=MatchValue(value=user_uuid))
                ]
            )
        )
        deleted[collection] = result.status
    
    return deleted


def get_stats() -> Dict[str, Any]:
    """Get statistics for all Mythos collections."""
    stats = {}
    for name in [MESSAGES_COLLECTION, PHOTOS_COLLECTION, ENTITIES_COLLECTION]:
        try:
            info = get_collection_info(name)
            stats[name] = info
        except Exception as e:
            stats[name] = {"error": str(e)}
    return stats
