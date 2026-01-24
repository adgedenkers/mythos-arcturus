#!/usr/bin/env python3
"""
Step 5: Orchestrator API Setup

Creates:
- orchestrator.py module for dispatching assignments to Redis
- context_manager.py for assembling multi-tier conversation context
- integration_example.py showing how to integrate with existing API

Usage: python3 step5_orchestrator_setup.py
"""

import os
import sys
from pathlib import Path

MYTHOS_BASE = Path("/opt/mythos")
API_DIR = MYTHOS_BASE / "api"


def create_orchestrator_module():
    """Create the orchestrator module for dispatching assignments"""
    
    content = '''#!/usr/bin/env python3
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
'''
    
    file_path = API_DIR / "orchestrator.py"
    file_path.write_text(content)
    print(f"  ✓ Created {file_path}")
    return True


def create_context_manager_module():
    """Create the context manager module"""
    
    content = '''#!/usr/bin/env python3
"""
Context Manager for Mythos Conversations

Assembles the multi-tier context window for LLM:
- Mode prompt (personality/role)
- Tier 2 summary (messages 21-60, if exists)
- Tier 1 summary (messages 1-20, if exists)
- Raw last 20 messages (full fidelity)
- Retrieved context (semantic search, Neo4j entities, related photos)
- Current message with any attached photos
"""

import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

import psycopg2
from dotenv import load_dotenv

load_dotenv("/opt/mythos/.env")

logger = logging.getLogger("context_manager")

# Configuration
PROMPTS_DIR = Path("/opt/mythos/prompts")
RECENT_MESSAGES_LIMIT = 20
PAST_CONVERSATIONS_LIMIT = 10
NEO4J_ENTITIES_LIMIT = 25
RELATED_PHOTOS_LIMIT = 10


class ContextManager:
    """Assembles context window for conversations"""
    
    def __init__(self, db_connection_func, neo4j_driver=None, qdrant_client=None):
        """
        Initialize context manager.
        
        Args:
            db_connection_func: Function that returns a psycopg2 connection
            neo4j_driver: Optional Neo4j driver for entity queries
            qdrant_client: Optional Qdrant client for semantic search
        """
        self.get_db = db_connection_func
        self.neo4j = neo4j_driver
        self.qdrant = qdrant_client
    
    def assemble_context(
        self,
        conversation_id: str,
        user_uuid: str,
        current_message: str,
        mode: str = "chat",
        photos: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Assemble complete multi-tier context window.
        
        Returns:
            {
                'mode_prompt': str,
                'tier2_summary': str or None,
                'tier1_summary': str or None,
                'recent_exchanges': List[Dict],
                'retrieved_context': Dict,
                'current_message': str,
                'current_photos': List[Dict],
                'message_count': int,
                'total_tokens': int (estimated)
            }
        """
        
        # Get message count for this conversation
        message_count = self._get_message_count(conversation_id)
        
        context = {
            'mode_prompt': self._load_mode_prompt(mode),
            'tier2_summary': None,
            'tier1_summary': None,
            'recent_exchanges': [],
            'retrieved_context': {},
            'current_message': current_message,
            'current_photos': photos or [],
            'message_count': message_count
        }
        
        # Load summaries based on conversation length
        summaries = self._get_current_summaries(conversation_id)
        
        if message_count >= 60 and summaries.get(2):
            context['tier2_summary'] = summaries[2]
        
        if message_count >= 20 and summaries.get(1):
            context['tier1_summary'] = summaries[1]
        
        # Get last 20 messages (full fidelity)
        context['recent_exchanges'] = self._get_recent_exchanges(conversation_id)
        
        # Retrieve relevant context dynamically
        context['retrieved_context'] = self._retrieve_relevant_context(
            current_message=current_message,
            conversation_id=conversation_id,
            user_uuid=user_uuid,
            recent_exchanges=context['recent_exchanges']
        )
        
        # Estimate tokens
        context['total_tokens'] = self._estimate_tokens(context)
        
        return context
    
    def _load_mode_prompt(self, mode: str) -> str:
        """Load mode-specific system prompt from file"""
        prompt_file = PROMPTS_DIR / f"{mode}_mode.txt"
        
        if not prompt_file.exists():
            prompt_file = PROMPTS_DIR / "chat_mode.txt"
        
        if not prompt_file.exists():
            logger.warning(f"No prompt file found for mode: {mode}")
            return "You are a helpful assistant."
        
        try:
            return prompt_file.read_text()
        except Exception as e:
            logger.error(f"Error loading prompt: {e}")
            return "You are a helpful assistant."
    
    def _get_message_count(self, conversation_id: str) -> int:
        """Get total message count for conversation"""
        conn = self.get_db()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT COUNT(*) FROM chat_messages
                WHERE conversation_id = %s
            """, (conversation_id,))
            return cur.fetchone()[0]
        finally:
            cur.close()
            conn.close()
    
    def _get_current_summaries(self, conversation_id: str) -> Dict[int, str]:
        """Get current summaries for each tier"""
        conn = self.get_db()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT tier, summary_text, themes, emotional_tone, context_notes
                FROM conversation_summaries
                WHERE conversation_id = %s AND is_current = TRUE
                ORDER BY tier
            """, (conversation_id,))
            
            summaries = {}
            for row in cur.fetchall():
                tier, summary_text, themes, emotional_tone, context_notes = row
                
                # Format with metadata
                formatted = f"{summary_text}"
                
                if themes:
                    formatted += f"\\n\\nThemes: {', '.join(themes)}"
                if emotional_tone:
                    formatted += f"\\nEmotional tone: {emotional_tone}"
                if context_notes:
                    formatted += f"\\nContext: {context_notes}"
                
                summaries[tier] = formatted
            
            return summaries
            
        except psycopg2.Error as e:
            logger.warning(f"Error fetching summaries: {e}")
            return {}
        finally:
            cur.close()
            conn.close()
    
    def _get_recent_exchanges(self, conversation_id: str) -> List[Dict]:
        """Get last 20 messages with full fidelity including photos"""
        conn = self.get_db()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT 
                    m.message_id,
                    m.role,
                    m.content,
                    m.created_at,
                    COALESCE(
                        json_agg(
                            json_build_object(
                                'id', mf.id::text,
                                'filename', mf.filename,
                                'dimensions', mf.width || 'x' || mf.height,
                                'description', mf.analysis_data->>'description',
                                'tags', mf.auto_tags
                            )
                        ) FILTER (WHERE mf.id IS NOT NULL),
                        '[]'::json
                    ) as photos
                FROM chat_messages m
                LEFT JOIN media_files mf ON m.message_id = mf.message_id
                WHERE m.conversation_id = %s
                GROUP BY m.message_id, m.role, m.content, m.created_at
                ORDER BY m.created_at DESC
                LIMIT %s
            """, (conversation_id, RECENT_MESSAGES_LIMIT))
            
            results = cur.fetchall()
            
            # Reverse to chronological order
            exchanges = []
            for msg_id, role, content, created_at, photos in reversed(results):
                exchanges.append({
                    'message_id': msg_id,
                    'role': role,
                    'content': content,
                    'timestamp': created_at.isoformat() if created_at else None,
                    'photos': photos if photos else []
                })
            
            return exchanges
            
        except psycopg2.Error as e:
            logger.warning(f"Error fetching recent exchanges: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    
    def _retrieve_relevant_context(
        self,
        current_message: str,
        conversation_id: str,
        user_uuid: str,
        recent_exchanges: List[Dict]
    ) -> Dict[str, Any]:
        """Dynamically retrieve relevant context from multiple sources"""
        
        # Extract keywords from current message and recent context
        keywords = self._extract_keywords(current_message, recent_exchanges)
        
        retrieved = {
            'semantic_matches': [],
            'past_conversations': [],
            'neo4j_entities': [],
            'related_photos': []
        }
        
        if not keywords:
            return retrieved
        
        # Semantic search (if Qdrant available)
        if self.qdrant:
            retrieved['semantic_matches'] = self._semantic_search(
                current_message, user_uuid, conversation_id
            )
        
        # Past conversation search (SQL full-text)
        retrieved['past_conversations'] = self._search_past_conversations(
            keywords, user_uuid, conversation_id
        )
        
        # Neo4j entity search (if available)
        if self.neo4j:
            retrieved['neo4j_entities'] = self._search_neo4j_entities(
                keywords, user_uuid
            )
        
        # Related photos
        retrieved['related_photos'] = self._search_related_photos(
            keywords, user_uuid
        )
        
        return retrieved
    
    def _extract_keywords(self, current_message: str, recent_exchanges: List[Dict]) -> List[str]:
        """Extract meaningful keywords for context retrieval"""
        keywords = []
        
        # Capitalized words (likely proper nouns)
        words = current_message.split()
        for word in words:
            cleaned = word.strip('.,!?";:()[]')
            if cleaned and len(cleaned) > 2 and cleaned[0].isupper():
                keywords.append(cleaned.lower())
        
        # Significant terms to watch for
        significant_terms = [
            'lineage', 'merovingian', 'bloodline', 'norman', 'nobility',
            'genealogy', 'spiral', 'synchronicity', 'flash', 'vision',
            'dream', 'symbol', 'grid', 'anchor', 'echo', 'beacon',
            'synth', 'nexus', 'mirror', 'glyph', 'harmonia', 'gateway',
            'rebecca', 'seraphe', 'fitz', 'research', 'ancestor'
        ]
        
        text_lower = current_message.lower()
        for term in significant_terms:
            if term in text_lower and term not in keywords:
                keywords.append(term)
        
        # Add keywords from recent context (last 3 user messages)
        for exchange in recent_exchanges[-3:]:
            if exchange['role'] == 'user':
                content_lower = exchange['content'].lower()
                for term in significant_terms:
                    if term in content_lower and term not in keywords:
                        keywords.append(term)
        
        return keywords[:15]  # Limit to top 15
    
    def _semantic_search(self, query: str, user_uuid: str, exclude_conversation: str) -> List[Dict]:
        """Perform semantic search in Qdrant"""
        try:
            from sentence_transformers import SentenceTransformer
            
            # Load model (will be cached after first load)
            model = SentenceTransformer("all-MiniLM-L6-v2")
            query_embedding = model.encode(query).tolist()
            
            # Search Qdrant
            results = self.qdrant.search(
                collection_name="text_embeddings",
                query_vector=query_embedding,
                query_filter={
                    "must": [
                        {"key": "user_uuid", "match": {"value": user_uuid}}
                    ],
                    "must_not": [
                        {"key": "conversation_id", "match": {"value": exclude_conversation}}
                    ]
                },
                limit=10
            )
            
            return [
                {
                    "message_id": hit.id,
                    "score": hit.score,
                    "content_preview": hit.payload.get("content_preview", "")[:200],
                    "conversation_id": hit.payload.get("conversation_id", "")[:8]
                }
                for hit in results
                if hit.score > 0.5  # Relevance threshold
            ]
            
        except Exception as e:
            logger.warning(f"Semantic search failed: {e}")
            return []
    
    def _search_past_conversations(
        self,
        keywords: List[str],
        user_uuid: str,
        exclude_conversation: str
    ) -> List[Dict]:
        """Search past conversations by keywords"""
        
        if not keywords:
            return []
        
        conn = self.get_db()
        cur = conn.cursor()
        
        try:
            # Build OR conditions for keywords
            conditions = ' OR '.join(['content ILIKE %s' for _ in keywords])
            params = [f"%{kw}%" for kw in keywords]
            
            cur.execute(f"""
                SELECT DISTINCT ON (conversation_id)
                    conversation_id,
                    content,
                    created_at
                FROM chat_messages
                WHERE user_uuid = %s
                  AND conversation_id != %s
                  AND role = 'user'
                  AND ({conditions})
                ORDER BY conversation_id, created_at DESC
                LIMIT %s
            """, [user_uuid, exclude_conversation] + params + [PAST_CONVERSATIONS_LIMIT])
            
            return [
                {
                    'conversation_id': row[0][:8] + '...',
                    'content': row[1][:200] + '...' if len(row[1]) > 200 else row[1],
                    'timestamp': row[2].isoformat() if row[2] else None
                }
                for row in cur.fetchall()
            ]
            
        except psycopg2.Error as e:
            logger.warning(f"Past conversation search failed: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    
    def _search_neo4j_entities(self, keywords: List[str], user_uuid: str) -> List[Dict]:
        """Search Neo4j for relevant entities"""
        
        if not self.neo4j or not keywords:
            return []
        
        try:
            with self.neo4j.session() as session:
                result = session.run("""
                    MATCH (n)
                    WHERE ANY(keyword IN $keywords 
                        WHERE toLower(n.name) CONTAINS toLower(keyword)
                           OR toLower(n.canonical_id) CONTAINS toLower(keyword))
                    RETURN 
                        labels(n) as labels,
                        n.name as name,
                        n.canonical_id as id,
                        n.mention_count as mentions
                    ORDER BY n.mention_count DESC
                    LIMIT $limit
                """, keywords=keywords, limit=NEO4J_ENTITIES_LIMIT)
                
                return [
                    {
                        'type': record['labels'][0] if record['labels'] else 'Entity',
                        'name': record['name'],
                        'id': record['id'],
                        'mentions': record['mentions'] or 0
                    }
                    for record in result
                ]
                
        except Exception as e:
            logger.warning(f"Neo4j search failed: {e}")
            return []
    
    def _search_related_photos(self, keywords: List[str], user_uuid: str) -> List[Dict]:
        """Search for photos with matching tags"""
        
        if not keywords:
            return []
        
        conn = self.get_db()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT 
                    id,
                    filename,
                    width,
                    height,
                    uploaded_at,
                    auto_tags,
                    analysis_data->>'description' as description
                FROM media_files
                WHERE user_uuid = %s
                  AND (
                      auto_tags && %s
                      OR analysis_data->>'description' ILIKE ANY(%s)
                  )
                ORDER BY uploaded_at DESC
                LIMIT %s
            """, (
                user_uuid,
                keywords,
                [f"%{kw}%" for kw in keywords],
                RELATED_PHOTOS_LIMIT
            ))
            
            return [
                {
                    'id': str(row[0])[:8] + '...',
                    'filename': row[1],
                    'dimensions': f"{row[2]}x{row[3]}",
                    'uploaded': row[4].isoformat() if row[4] else None,
                    'tags': row[5] or [],
                    'description': row[6][:100] + '...' if row[6] and len(row[6]) > 100 else row[6]
                }
                for row in cur.fetchall()
            ]
            
        except psycopg2.Error as e:
            logger.warning(f"Photo search failed: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    
    def _estimate_tokens(self, context: Dict) -> int:
        """Rough token estimation (1 token ≈ 4 characters)"""
        
        total_chars = len(context.get('mode_prompt', ''))
        
        if context.get('tier2_summary'):
            total_chars += len(context['tier2_summary'])
        
        if context.get('tier1_summary'):
            total_chars += len(context['tier1_summary'])
        
        for exchange in context.get('recent_exchanges', []):
            total_chars += len(exchange.get('content', ''))
            for photo in exchange.get('photos', []):
                if photo.get('description'):
                    total_chars += len(photo['description'])
        
        retrieved = context.get('retrieved_context', {})
        for item in retrieved.get('past_conversations', []):
            total_chars += len(item.get('content', ''))
        
        for item in retrieved.get('related_photos', []):
            if item.get('description'):
                total_chars += len(item['description'])
        
        total_chars += len(context.get('current_message', ''))
        
        return total_chars // 4
    
    def format_context_for_llm(self, context: Dict) -> str:
        """Format assembled context into final prompt string for LLM"""
        
        sections = []
        
        # Mode prompt
        sections.append(context['mode_prompt'])
        sections.append("\\n" + "=" * 60 + "\\n")
        
        # Tier 2 summary (if exists)
        if context.get('tier2_summary'):
            sections.append("[EARLIER CONTEXT (Messages 21-60)]\\n")
            sections.append(context['tier2_summary'])
            sections.append("\\n" + "-" * 60 + "\\n")
        
        # Tier 1 summary (if exists)
        if context.get('tier1_summary'):
            sections.append("[RECENT CONTEXT SUMMARY]\\n")
            sections.append(context['tier1_summary'])
            sections.append("\\n" + "-" * 60 + "\\n")
        
        # Recent exchanges (raw, last 20)
        if context.get('recent_exchanges'):
            sections.append("[LAST 20 EXCHANGES - Full Detail]\\n")
            for exchange in context['recent_exchanges']:
                role = exchange['role'].upper()
                timestamp = exchange.get('timestamp', '')[:16] if exchange.get('timestamp') else ''
                sections.append(f"\\n{role} ({timestamp}):")
                sections.append(exchange['content'])
                
                for photo in exchange.get('photos', []):
                    sections.append(f"  📸 {photo.get('filename', 'Photo')}")
                    if photo.get('description'):
                        sections.append(f"     {photo['description']}")
            
            sections.append("\\n" + "-" * 60 + "\\n")
        
        # Retrieved context
        retrieved = context.get('retrieved_context', {})
        
        if retrieved.get('semantic_matches'):
            sections.append("[SEMANTICALLY SIMILAR PAST MESSAGES]\\n")
            for i, item in enumerate(retrieved['semantic_matches'][:5], 1):
                sections.append(f"{i}. (score: {item['score']:.2f}) {item['content_preview']}")
            sections.append("")
        
        if retrieved.get('past_conversations'):
            sections.append("[RELEVANT PAST CONVERSATIONS]\\n")
            for i, item in enumerate(retrieved['past_conversations'][:5], 1):
                sections.append(f"{i}. ({item.get('timestamp', 'unknown')[:10]}) {item['content']}")
            sections.append("")
        
        if retrieved.get('neo4j_entities'):
            sections.append("[RELATED ENTITIES FROM KNOWLEDGE GRAPH]\\n")
            for entity in retrieved['neo4j_entities'][:10]:
                sections.append(f"- {entity['type']}: {entity['name']} (mentioned {entity.get('mentions', 0)} times)")
            sections.append("")
        
        if retrieved.get('related_photos'):
            sections.append("[RELATED PHOTOS]\\n")
            for photo in retrieved['related_photos'][:5]:
                sections.append(f"- {photo['filename']}: {photo.get('description', 'No description')}")
            sections.append("")
        
        sections.append("=" * 60 + "\\n")
        
        # Current message
        sections.append("[CURRENT MESSAGE]\\n")
        sections.append(context['current_message'])
        
        if context.get('current_photos'):
            sections.append("\\n[ATTACHED PHOTOS]")
            for photo in context['current_photos']:
                sections.append(f"  📸 {photo.get('filename', 'New photo')}")
        
        return "\\n".join(sections)
'''
    
    file_path = API_DIR / "context_manager.py"
    file_path.write_text(content)
    print(f"  ✓ Created {file_path}")
    return True


def create_integration_example():
    """Create example code showing how to integrate with existing API"""
    
    content = '''#!/usr/bin/env python3
"""
Integration Example for Mythos API

This file shows how to integrate the orchestrator and context manager
with your existing main.py API.

DO NOT RUN THIS FILE DIRECTLY - it's a reference for manual integration.
"""

# =============================================================================
# STEP 1: Add imports at the top of main.py
# =============================================================================

"""
# Add these imports:
from fastapi import BackgroundTasks
from api.orchestrator import get_orchestrator, Orchestrator
from api.context_manager import ContextManager
"""

# =============================================================================
# STEP 2: Initialize after app creation (around line 45-50 in main.py)
# =============================================================================

"""
# Initialize orchestrator for async task dispatch
orchestrator: Orchestrator = None
try:
    orchestrator = get_orchestrator()
    print("✅ Orchestrator initialized")
except Exception as e:
    print(f"⚠️  Orchestrator not available: {e}")

# Initialize context manager
# Note: You may need to initialize Qdrant client here too
qdrant_client = None
try:
    from qdrant_client import QdrantClient
    qdrant_client = QdrantClient(host="localhost", port=6333)
    print("✅ Qdrant client initialized")
except Exception as e:
    print(f"⚠️  Qdrant not available: {e}")

context_manager = ContextManager(
    db_connection_func=get_db_connection,
    neo4j_driver=neo4j_driver,
    qdrant_client=qdrant_client
)
print("✅ Context manager initialized")
"""

# =============================================================================
# STEP 3: Modify your /message endpoint
# =============================================================================

"""
@app.post("/message")
async def handle_message(
    request: MessageRequest,
    background_tasks: BackgroundTasks,  # Add this parameter
    api_key: str = Depends(verify_api_key)
):
    # ... existing user lookup code ...
    
    # Store user message in database
    message_id = store_message(
        user_uuid=user['uuid'],
        conversation_id=request.conversation_id,
        role="user",
        content=request.message
    )
    
    # Get message count for this conversation
    message_count = get_message_count(request.conversation_id)
    
    # Assemble full context
    context = context_manager.assemble_context(
        conversation_id=request.conversation_id,
        user_uuid=user['uuid'],
        current_message=request.message,
        mode=request.mode
    )
    
    # Format context for LLM
    full_prompt = context_manager.format_context_for_llm(context)
    
    # Generate LLM response with full context
    response = generate_llm_response(full_prompt, model=request.model_preference)
    
    # Store assistant response
    store_message(
        user_uuid=user['uuid'],
        conversation_id=request.conversation_id,
        role="assistant",
        content=response
    )
    
    # Dispatch async extraction tasks (non-blocking)
    if orchestrator:
        # Dispatch all extraction tasks for this message
        background_tasks.add_task(
            orchestrator.dispatch_message_extraction,
            message_id=message_id,
            content=request.message,
            user_uuid=user['uuid'],
            conversation_id=request.conversation_id
        )
        
        # Check if summaries need pre-emptive rebuilding
        summary_tasks = orchestrator.check_summary_triggers(
            request.conversation_id,
            context['message_count']
        )
        
        for task in summary_tasks:
            background_tasks.add_task(
                orchestrator.dispatch_summary_rebuild,
                conversation_id=request.conversation_id,
                user_uuid=user['uuid'],
                tier=task['tier'],
                start_idx=task['start_idx'],
                end_idx=task['end_idx']
            )
    
    return MessageResponse(
        response=response,
        mode=request.mode,
        user=user.get('soul_display_name')
    )
"""

# =============================================================================
# STEP 4: Add orchestrator stats endpoint (optional but useful)
# =============================================================================

"""
@app.get("/orchestrator/stats")
async def get_orchestrator_stats(api_key: str = Depends(verify_api_key)):
    \"\"\"Get orchestrator and worker statistics\"\"\"
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not available")
    return orchestrator.get_stats()
"""

# =============================================================================
# STEP 5: Add endpoint to manually trigger summary rebuild (optional)
# =============================================================================

"""
@app.post("/conversation/{conversation_id}/rebuild-summaries")
async def rebuild_conversation_summaries(
    conversation_id: str,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    \"\"\"Manually trigger summary rebuild for a conversation\"\"\"
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not available")
    
    # Get user from conversation
    user_uuid = get_user_uuid_from_conversation(conversation_id)
    
    # Rebuild Tier 1
    tier1_id = orchestrator.dispatch_summary_rebuild(
        conversation_id=conversation_id,
        user_uuid=user_uuid,
        tier=1,
        start_idx=1,
        end_idx=20
    )
    
    # Rebuild Tier 2
    tier2_id = orchestrator.dispatch_summary_rebuild(
        conversation_id=conversation_id,
        user_uuid=user_uuid,
        tier=2,
        start_idx=21,
        end_idx=60
    )
    
    return {
        "status": "dispatched",
        "tier1_assignment": tier1_id,
        "tier2_assignment": tier2_id
    }
"""

# =============================================================================
# HELPER FUNCTIONS (add these if you don't have them)
# =============================================================================

"""
def get_message_count(conversation_id: str) -> int:
    \"\"\"Get total message count for a conversation\"\"\"
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT COUNT(*) FROM chat_messages WHERE conversation_id = %s",
            (conversation_id,)
        )
        return cur.fetchone()[0]
    finally:
        cur.close()
        conn.close()


def get_user_uuid_from_conversation(conversation_id: str) -> str:
    \"\"\"Get user UUID from a conversation\"\"\"
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT user_uuid FROM chat_messages WHERE conversation_id = %s LIMIT 1",
            (conversation_id,)
        )
        result = cur.fetchone()
        return str(result[0]) if result else None
    finally:
        cur.close()
        conn.close()
"""

print("This file is a reference - do not run directly.")
print("Copy the relevant sections into your main.py")
'''
    
    file_path = API_DIR / "integration_example.py"
    file_path.write_text(content)
    print(f"  ✓ Created {file_path}")
    return True


def verify_setup():
    """Verify orchestrator setup"""
    
    print("\n  Verifying orchestrator setup...")
    
    required_files = [
        API_DIR / "orchestrator.py",
        API_DIR / "context_manager.py",
        API_DIR / "integration_example.py"
    ]
    
    all_present = True
    for f in required_files:
        if f.exists():
            print(f"    ✓ {f.name}")
        else:
            print(f"    ✗ {f.name} MISSING")
            all_present = False
    
    return all_present


def main():
    print("\n" + "=" * 60)
    print("  Step 5: Orchestrator API Setup")
    print("=" * 60 + "\n")
    
    # Ensure API directory exists
    API_DIR.mkdir(parents=True, exist_ok=True)
    
    all_success = True
    
    print("Creating orchestrator modules...")
    
    if not create_orchestrator_module():
        all_success = False
    
    if not create_context_manager_module():
        all_success = False
    
    if not create_integration_example():
        all_success = False
    
    # Verify
    if not verify_setup():
        all_success = False
    
    if all_success:
        print("\n" + "=" * 60)
        print("  ✓ Orchestrator setup complete!")
        print("=" * 60)
        print("\nFiles created in:", API_DIR)
        print("  - orchestrator.py      : Dispatches assignments to Redis")
        print("  - context_manager.py   : Assembles multi-tier context")
        print("  - integration_example.py : Shows how to integrate with main.py")
        print("\nNext steps:")
        print("  1. Review integration_example.py")
        print("  2. Add imports to main.py")
        print("  3. Initialize orchestrator and context_manager")
        print("  4. Modify /message endpoint to use context manager")
        print("  5. Add background tasks for async extraction")
        print("  6. Restart API: sudo systemctl restart mythos-api")
        print()
    else:
        print("\n✗ Setup completed with errors")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
