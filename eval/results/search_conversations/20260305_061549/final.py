#!/usr/bin/env python3
"""
Search Conversations Skill for Mythos System
"""
import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

from engine.base import SkillBase, SkillRequest, SkillResponse

load_dotenv('/opt/mythos/.env')

def _get_conn():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', '/var/run/postgresql'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor,
    )

class SearchConversationsSkill(SkillBase):
    name = 'search_conversations'
    version = '1.0'
    category = 'data'
    description = 'Search conversation history by keyword'
    triggers = ['conversation', 'conversations', 'chat', 'chat history', 'we talked about', 'you said', 'I asked', 'remember our conversation', 'what did we discuss', 'previous chat', 'earlier conversation', 'discussed']
    cache_ttl = 300

    async def execute(self, request: SkillRequest) -> SkillResponse:
        # 1. Extract search terms using _extract_search_terms()
        # 2. If no terms: return total conversation count with guidance
        # 3. Search using _search_turns() with ILIKE
        # 4. Format results using _format_results()
        # 5. Build human summary using _build_summary()
        # 6. Return SkillResponse with matches in data
        try:
            search_terms = self._extract_search_terms(request.message)
            
            if not search_terms:
                # Get total conversation count
                conn = None
                cursor = None
                try:
                    conn = _get_conn()
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) as total FROM conversation_turns")
                    total = cursor.fetchone()['total']
                    return SkillResponse(
                        skill_name=self.name,
                        data={'total_turns': total},
                        summary=f'Conversation history has {total} turns. Ask about a specific topic to search.',
                        confidence=0.5,
                        sources=['mythos.conversation_turns']
                    )
                finally:
                    if cursor:
                        cursor.close()
                    if conn:
                        conn.close()
            
            # Search for terms
            rows = self._search_turns(search_terms)
            formatted = self._format_results(rows)
            summary = self._build_summary(formatted, search_terms)
            
            return SkillResponse(
                skill_name=self.name,
                data={'matches': formatted, 'search_terms': search_terms, 'count': len(formatted)},
                summary=summary,
                confidence=0.95,
                sources=['mythos.conversation_turns']
            )
        except Exception as e:
            logging.error(f"Error in execute: {e}")
            return SkillResponse(skill_name=self.name, error=str(e))
        finally:
            pass

    def _extract_search_terms(self, message: str) -> str:
        # Lowercase the message
        message = message.lower()
        
        # Define trigger phrases to remove, LONGEST FIRST
        trigger_phrases = [
            'remember our conversation',
            'earlier conversation',
            'what did we discuss',
            'we talked about',
            'previous chat',
            'chat history',
            'conversations',
            'conversation',
            'you said',
            'i asked',
            'discussed',
            'search for',
            'search about',
            'search',
            'find'
        ]
        
        # Remove each trigger phrase and normalize whitespace immediately after
        for phrase in trigger_phrases:
            message = message.replace(phrase, '')
            # Normalize whitespace immediately after each removal
            message = ' '.join(message.split())
        
        # Strip punctuation (keep only alphanumeric and spaces)
        cleaned = ''.join(char for char in message if char.isalnum() or char.isspace())
        
        # Final whitespace normalization
        cleaned = ' '.join(cleaned.split())
        
        # Return cleaned string if len >= 2, else empty string
        return cleaned if len(cleaned) >= 2 else ''

    def _search_turns(self, search_terms: str, limit: int = 15) -> list:
        # Use ILIKE '%search_terms%' on content column (NO tsvector on this table)
        # SELECT conversation_id, turn_idx, speaker_type, LEFT(content, 300) as content_preview, created_at
        # FROM conversation_turns
        # WHERE content ILIKE %s
        # ORDER BY created_at DESC
        # LIMIT %s
        # Return list of row dicts
        conn = None
        cursor = None
        try:
            conn = _get_conn()
            cursor = conn.cursor()
            query = """
                SELECT conversation_id, turn_idx, speaker_type, LEFT(content, 300) as content_preview, created_at
                FROM conversation_turns
                WHERE content ILIKE %s
                ORDER BY created_at DESC
                LIMIT %s
            """
            cursor.execute(query, (f'%{search_terms}%', limit))
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error in _search_turns: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _format_results(self, rows: list) -> list:
        # Convert rows to clean dicts
        # Truncate content preview to 200 chars
        # Format created_at as readable date string
        # Include speaker_type label
        formatted = []
        for row in rows:
            content_preview = row['content_preview']
            if len(content_preview) > 200:
                content_preview = content_preview[:200] + '..'
            
            created_at_str = None
            if row['created_at']:
                created_at_str = row['created_at'].isoformat()
            
            speaker_label = row['speaker_type'].capitalize()
            
            formatted.append({
                'conversation_id': str(row['conversation_id']),
                'turn_idx': row['turn_idx'],
                'speaker_type': speaker_label,
                'content_preview': content_preview,
                'created_at': created_at_str
            })
        return formatted

    def _build_summary(self, results: list, search_terms: str) -> str:
        # If no results: 'No conversations found mentioning "X".'
        # If results: 'Found N conversation turn(s) mentioning "X": [speaker] said "preview..." (date), ...'
        # Show top 3 previews max
        if not results:
            return f'No conversations found mentioning "{search_terms}".'
        
        count = len(results)
        plural = 's' if count != 1 else ''
        summary = f'Found {count} conversation turn{plural} mentioning "{search_terms}":'
        
        preview_list = []
        for result in results[:3]:
            speaker = result['speaker_type']
            preview = result['content_preview']
            date = result['created_at'][:10] if result['created_at'] else 'unknown date'
            preview_list.append(f'{speaker} said "{preview}" ({date})')
        
        summary += ' ' + '; '.join(preview_list)
        return summary