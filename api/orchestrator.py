#!/usr/bin/env python3
"""
Mythos Orchestrator

Dispatches extraction assignments to Redis streams for async processing.
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

import redis
from dotenv import load_dotenv

load_dotenv("/opt/mythos/.env")

logger = logging.getLogger("orchestrator")

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Stream names
STREAMS = {
    "grid": "mythos:assignments:grid_analysis",
    "embedding": "mythos:assignments:embedding",
    "vision": "mythos:assignments:vision",
    "temporal": "mythos:assignments:temporal",
    "entity": "mythos:assignments:entity",
    "summary": "mythos:assignments:summary_rebuild"
}


class Orchestrator:
    """Dispatches extraction assignments to worker queues"""
    
    def __init__(self):
        self.redis = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )
        self._verify_connection()
    
    def _verify_connection(self):
        """Verify Redis connection"""
        try:
            self.redis.ping()
            logger.info("Orchestrator connected to Redis")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def dispatch(self, assignment_type: str, payload: Dict[str, Any]) -> str:
        """
        Dispatch an assignment to the appropriate stream.
        
        Args:
            assignment_type: One of 'grid', 'embedding', 'vision', 'temporal', 'entity', 'summary'
            payload: Assignment payload
            
        Returns:
            Assignment ID
        """
        if assignment_type not in STREAMS:
            raise ValueError(f"Unknown assignment type: {assignment_type}")
        
        stream = STREAMS[assignment_type]
        assignment_id = str(uuid.uuid4())
        
        message = {
            "id": assignment_id,
            "type": assignment_type,
            "payload": payload,
            "dispatched_at": datetime.now().isoformat()
        }
        
        # Add to stream
        self.redis.xadd(stream, {"data": json.dumps(message)})
        
        # Update stats
        self.redis.hincrby("mythos:stats:assignments", "total_dispatched", 1)
        self.redis.hincrby("mythos:stats:assignments", f"{assignment_type}_dispatched", 1)
        
        logger.debug(f"Dispatched {assignment_type} assignment: {assignment_id}")
        
        return assignment_id
    
    def dispatch_message_extraction(
        self,
        message_id: int,
        content: str,
        user_uuid: str,
        conversation_id: str,
        photos: Optional[List[Dict]] = None
    ) -> Dict[str, str]:
        """
        Dispatch all extraction tasks for a message.
        
        Returns dict of assignment_type -> assignment_id
        """
        base_payload = {
            "message_id": message_id,
            "content": content,
            "user_uuid": user_uuid,
            "conversation_id": conversation_id
        }
        
        assignments = {}
        
        # Grid analysis
        assignments["grid"] = self.dispatch("grid", base_payload)
        
        # Embedding generation
        assignments["embedding"] = self.dispatch("embedding", base_payload)
        
        # Temporal extraction
        assignments["temporal"] = self.dispatch("temporal", base_payload)
        
        # Photo analysis (if photos present)
        if photos:
            for photo in photos:
                photo_payload = {
                    **base_payload,
                    "photo_id": photo.get("id"),
                    "file_path": photo.get("file_path")
                }
                assignments[f"vision_{photo.get('id', 'unknown')[:8]}"] = self.dispatch("vision", photo_payload)
        
        logger.info(f"Dispatched {len(assignments)} assignments for message {message_id}")
        
        return assignments
    
    def dispatch_entity_resolution(
        self,
        message_id: int,
        user_uuid: str,
        conversation_id: str,
        entities: Dict[str, List[str]],
        exchange_id: Optional[str] = None
    ) -> str:
        """Dispatch entity resolution task"""
        
        payload = {
            "message_id": message_id,
            "user_uuid": user_uuid,
            "conversation_id": conversation_id,
            "entities": entities,
            "exchange_id": exchange_id
        }
        
        return self.dispatch("entity", payload)
    
    def dispatch_summary_rebuild(
        self,
        conversation_id: str,
        user_uuid: str,
        tier: int,
        start_idx: int,
        end_idx: int
    ) -> str:
        """Dispatch summary rebuild task"""
        
        payload = {
            "conversation_id": conversation_id,
            "user_uuid": user_uuid,
            "tier": tier,
            "start_idx": start_idx,
            "end_idx": end_idx
        }
        
        return self.dispatch("summary", payload)
    
    def check_summary_triggers(self, conversation_id: str, message_count: int) -> List[Dict]:
        """
        Check if summary rebuilds should be triggered.
        
        Uses pre-emptive rebuilding: triggers one message BEFORE the summary is needed.
        
        Returns list of rebuild tasks to dispatch.
        """
        tasks = []
        
        # Tier 1: Rebuild every 5 messages after message 19
        # (So summary is ready before message 20, 25, 30, etc.)
        if message_count >= 19:
            if (message_count - 19) % 5 == 0:
                tasks.append({
                    "tier": 1,
                    "start_idx": 1,
                    "end_idx": min(20, message_count + 1)
                })
        
        # Tier 2: Rebuild every 20 messages after message 59
        # (So summary is ready before message 60, 80, 100, etc.)
        if message_count >= 59:
            if (message_count - 59) % 20 == 0:
                tasks.append({
                    "tier": 2,
                    "start_idx": 21,
                    "end_idx": min(60, message_count - 19)
                })
        
        return tasks
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        
        assignment_stats = self.redis.hgetall("mythos:stats:assignments")
        worker_stats = self.redis.hgetall("mythos:stats:workers")
        
        # Get stream lengths (queue depths)
        stream_lengths = {}
        for name, stream in STREAMS.items():
            try:
                info = self.redis.xinfo_stream(stream)
                stream_lengths[name] = info["length"]
            except redis.ResponseError:
                stream_lengths[name] = 0
        
        return {
            "assignments": assignment_stats,
            "workers": worker_stats,
            "queue_lengths": stream_lengths
        }


# Global orchestrator instance
_orchestrator = None


def get_orchestrator() -> Orchestrator:
    """Get or create global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator
