#!/usr/bin/env python3
"""
Embedding Worker

Generates text embeddings and stores them in Qdrant.
"""

import os
import logging
from typing import Dict, Any
from datetime import datetime

from dotenv import load_dotenv

load_dotenv("/opt/mythos/.env")

logger = logging.getLogger("worker.embedding")

# Lazy-loaded globals
_model = None
_qdrant = None


def get_model():
    global _model
    if _model is None:
        logger.info("Loading sentence-transformers model...")
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Model loaded successfully")
    return _model


def get_qdrant():
    global _qdrant
    if _qdrant is None:
        from qdrant_client import QdrantClient
        _qdrant = QdrantClient(
            host=os.getenv("QDRANT_HOST", "localhost"),
            port=int(os.getenv("QDRANT_PORT", 6333))
        )
    return _qdrant


def process_embedding(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate and store text embedding in Qdrant"""
    
    from qdrant_client.models import PointStruct
    
    message_id = payload.get("message_id")
    content = payload.get("content", "")
    user_uuid = payload.get("user_uuid")
    conversation_id = payload.get("conversation_id")
    
    if not content or not content.strip():
        logger.warning(f"Empty content for message {message_id}")
        return {"status": "skipped", "message_id": message_id, "reason": "empty_content"}
    
    logger.info(f"Generating embedding for message {message_id}")
    
    try:
        # Generate embedding
        embedding = get_model().encode(content).tolist()
        
        # Store in Qdrant
        get_qdrant().upsert(
            collection_name="text_embeddings",
            points=[
                PointStruct(
                    id=message_id,
                    vector=embedding,
                    payload={
                        "user_uuid": user_uuid,
                        "conversation_id": conversation_id,
                        "content_preview": content[:500],
                        "content_length": len(content),
                        "message_type": "user_message",
                        "created_at": datetime.now().isoformat()
                    }
                )
            ]
        )
        
        logger.info(f"Stored embedding for message {message_id} (dim={len(embedding)})")
        
        return {
            "status": "success",
            "message_id": message_id,
            "embedding_dim": len(embedding)
        }
        
    except Exception as e:
        logger.exception(f"Failed to generate/store embedding: {e}")
        return {"status": "failed", "message_id": message_id, "error": str(e)}
