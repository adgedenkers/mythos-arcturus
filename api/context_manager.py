#!/usr/bin/env python3
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
                    formatted += f"\n\nThemes: {', '.join(themes)}"
                if emotional_tone:
                    formatted += f"\nEmotional tone: {emotional_tone}"
                if context_notes:
                    formatted += f"\nContext: {context_notes}"
                
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
        sections.append("\n" + "=" * 60 + "\n")
        
        # Tier 2 summary (if exists)
        if context.get('tier2_summary'):
            sections.append("[EARLIER CONTEXT (Messages 21-60)]\n")
            sections.append(context['tier2_summary'])
            sections.append("\n" + "-" * 60 + "\n")
        
        # Tier 1 summary (if exists)
        if context.get('tier1_summary'):
            sections.append("[RECENT CONTEXT SUMMARY]\n")
            sections.append(context['tier1_summary'])
            sections.append("\n" + "-" * 60 + "\n")
        
        # Recent exchanges (raw, last 20)
        if context.get('recent_exchanges'):
            sections.append("[LAST 20 EXCHANGES - Full Detail]\n")
            for exchange in context['recent_exchanges']:
                role = exchange['role'].upper()
                timestamp = exchange.get('timestamp', '')[:16] if exchange.get('timestamp') else ''
                sections.append(f"\n{role} ({timestamp}):")
                sections.append(exchange['content'])
                
                for photo in exchange.get('photos', []):
                    sections.append(f"  📸 {photo.get('filename', 'Photo')}")
                    if photo.get('description'):
                        sections.append(f"     {photo['description']}")
            
            sections.append("\n" + "-" * 60 + "\n")
        
        # Retrieved context
        retrieved = context.get('retrieved_context', {})
        
        if retrieved.get('semantic_matches'):
            sections.append("[SEMANTICALLY SIMILAR PAST MESSAGES]\n")
            for i, item in enumerate(retrieved['semantic_matches'][:5], 1):
                sections.append(f"{i}. (score: {item['score']:.2f}) {item['content_preview']}")
            sections.append("")
        
        if retrieved.get('past_conversations'):
            sections.append("[RELEVANT PAST CONVERSATIONS]\n")
            for i, item in enumerate(retrieved['past_conversations'][:5], 1):
                sections.append(f"{i}. ({item.get('timestamp', 'unknown')[:10]}) {item['content']}")
            sections.append("")
        
        if retrieved.get('neo4j_entities'):
            sections.append("[RELATED ENTITIES FROM KNOWLEDGE GRAPH]\n")
            for entity in retrieved['neo4j_entities'][:10]:
                sections.append(f"- {entity['type']}: {entity['name']} (mentioned {entity.get('mentions', 0)} times)")
            sections.append("")
        
        if retrieved.get('related_photos'):
            sections.append("[RELATED PHOTOS]\n")
            for photo in retrieved['related_photos'][:5]:
                sections.append(f"- {photo['filename']}: {photo.get('description', 'No description')}")
            sections.append("")
        
        sections.append("=" * 60 + "\n")
        
        # Current message
        sections.append("[CURRENT MESSAGE]\n")
        sections.append(context['current_message'])
        
        if context.get('current_photos'):
            sections.append("\n[ATTACHED PHOTOS]")
            for photo in context['current_photos']:
                sections.append(f"  📸 {photo.get('filename', 'New photo')}")
        
        return "\n".join(sections)
