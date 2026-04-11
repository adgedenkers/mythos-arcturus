#!/usr/bin/env python3
"""
Iris Memory Layer

Handles persistence of conversation history to PostgreSQL and retrieval
of past context so Iris remembers across restarts.

Three levels:
1. Immediate context — in-memory messages from current session (ChatAssistant.contexts)
2. Recent memory — last N messages from chat_messages table (loaded on first interaction)
3. Summary memory — compressed summaries of older conversations (future: Redis worker)

Usage in ChatAssistant:
    from iris_memory import IrisMemory
    memory = IrisMemory()
    
    # Load past context for a user (call once per session)
    past_messages = memory.load_recent(user_uuid, limit=30)
    
    # Save an exchange
    memory.save_message(user_uuid, telegram_id, 'user', message, mode='chat')
    memory.save_message(user_uuid, telegram_id, 'assistant', response, mode='chat', model_used='qwen2.5:32b')
    
    # Build memory context block for system prompt
    context_block = memory.build_memory_context(user_uuid, limit=20)
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

# DB config from environment
DB_HOST = os.getenv('POSTGRES_HOST', '/var/run/postgresql')
DB_NAME = os.getenv('POSTGRES_DB', 'mythos')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASS = os.getenv('POSTGRES_PASSWORD', '')


class IrisMemory:
    """
    Persistent memory layer for Iris conversations.
    
    Reads/writes chat_messages in PostgreSQL.
    Provides context injection for system prompts.
    """
    
    def __init__(self):
        self._conn = None
        logger.info("IrisMemory initialized")
    
    def _get_conn(self):
        """Get or create a database connection"""
        try:
            if self._conn is None or self._conn.closed:
                self._conn = psycopg2.connect(
                    host=DB_HOST,
                    database=DB_NAME,
                    user=DB_USER,
                    password=DB_PASS
                )
                self._conn.autocommit = True
            return self._conn
        except Exception as e:
            logger.error(f"IrisMemory DB connection failed: {e}")
            self._conn = None
            return None
    
    def save_message(
        self,
        user_uuid: str,
        telegram_id: int,
        role: str,
        content: str,
        mode: str = 'chat',
        model_used: str = None,
        conversation_id: str = None,
        response_time_ms: int = None
    ) -> Optional[int]:
        """
        Save a message to chat_messages.
        Returns the message_id if successful.
        """
        conn = self._get_conn()
        if not conn:
            logger.warning("IrisMemory: Could not save message — no DB connection")
            return None
        
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO chat_messages 
                (user_uuid, telegram_user_id, conversation_id, role, content, mode, model_used, response_time_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING message_id
            """, (
                user_uuid,
                telegram_id,
                conversation_id,
                role,
                content,
                mode,
                model_used,
                response_time_ms
            ))
            message_id = cur.fetchone()[0]
            cur.close()
            logger.debug(f"IrisMemory: Saved {role} message #{message_id}")
            return message_id
        except Exception as e:
            logger.error(f"IrisMemory: Failed to save message: {e}")
            return None
    
    def load_recent(
        self,
        user_uuid: str,
        limit: int = 30,
        mode: str = None,
        since_hours: int = None
    ) -> List[Dict]:
        """
        Load recent messages from chat_messages for a user.
        
        Returns list of dicts with role, content, created_at, mode, model_used.
        Ordered oldest-first so they can be injected into context in order.
        """
        conn = self._get_conn()
        if not conn:
            return []
        
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT role, content, mode, model_used, created_at
                FROM chat_messages
                WHERE user_uuid = %s
            """
            params = [user_uuid]
            
            if mode:
                query += " AND mode = %s"
                params.append(mode)
            
            if since_hours:
                query += " AND created_at > NOW() - INTERVAL '%s hours'"
                params.append(since_hours)
            
            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)
            
            cur.execute(query, params)
            rows = cur.fetchall()
            cur.close()
            
            # Reverse so oldest first (for context injection order)
            rows.reverse()
            
            logger.info(f"IrisMemory: Loaded {len(rows)} recent messages for user {user_uuid[:8]}")
            return [dict(r) for r in rows]
            
        except Exception as e:
            logger.error(f"IrisMemory: Failed to load recent: {e}")
            return []
    
    def build_memory_context(
        self,
        user_uuid: str,
        limit: int = 20,
        since_hours: int = 72
    ) -> str:
        """
        Build a memory context block to inject into Iris's system prompt.
        
        Pulls recent conversation history and formats it as a readable summary
        that Iris can reference naturally.
        """
        messages = self.load_recent(
            user_uuid=user_uuid,
            limit=limit,
            since_hours=since_hours
        )
        
        if not messages:
            return ""
        
        # Group by day
        days = {}
        for msg in messages:
            day_key = msg['created_at'].strftime('%A, %B %d') if msg.get('created_at') else 'Unknown'
            if day_key not in days:
                days[day_key] = []
            days[day_key].append(msg)
        
        lines = ["\n\nYOUR MEMORY — Recent conversations with this person:"]
        
        for day, day_msgs in days.items():
            lines.append(f"\n[{day}]")
            for msg in day_msgs:
                role_label = "They said" if msg['role'] == 'user' else "You said"
                # Truncate long messages for context efficiency
                content = msg['content']
                if len(content) > 200:
                    content = content[:197] + "..."
                lines.append(f"  {role_label}: {content}")
        
        lines.append("\nUse these memories naturally — don't announce that you're remembering, just know.")
        
        return "\n".join(lines)
    
    def get_conversation_stats(self, user_uuid: str) -> Dict[str, Any]:
        """Get stats about a user's conversation history"""
        conn = self._get_conn()
        if not conn:
            return {'total_messages': 0, 'first_message': None, 'last_message': None}
        
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT 
                    COUNT(*) as total_messages,
                    MIN(created_at) as first_message,
                    MAX(created_at) as last_message,
                    COUNT(DISTINCT DATE(created_at)) as active_days
                FROM chat_messages
                WHERE user_uuid = %s
            """, (user_uuid,))
            row = cur.fetchone()
            cur.close()
            return dict(row) if row else {'total_messages': 0}
        except Exception as e:
            logger.error(f"IrisMemory: Stats query failed: {e}")
            return {'total_messages': 0}
    
    def close(self):
        """Close the database connection"""
        if self._conn and not self._conn.closed:
            self._conn.close()
            self._conn = None
