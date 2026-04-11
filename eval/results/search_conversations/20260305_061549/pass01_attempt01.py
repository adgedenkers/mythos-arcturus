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
        pass

    def _extract_search_terms(self, message: str) -> str:
        # Remove trigger phrases (longest first), normalize whitespace between each removal
        # Return cleaned string if len >= 2, else empty string
        pass

    def _search_turns(self, search_terms: str, limit: int = 15) -> list:
        # Use ILIKE '%search_terms%' on content column (NO tsvector on this table)
        # SELECT conversation_id, turn_idx, speaker_type, LEFT(content, 300) as content_preview, created_at
        # FROM conversation_turns
        # WHERE content ILIKE %s
        # ORDER BY created_at DESC
        # LIMIT %s
        # Return list of row dicts
        pass

    def _format_results(self, rows: list) -> list:
        # Convert rows to clean dicts
        # Truncate content preview to 200 chars
        # Format created_at as readable date string
        # Include speaker_type label
        pass

    def _build_summary(self, results: list, search_terms: str) -> str:
        # If no results: 'No conversations found mentioning "X".'
        # If results: 'Found N conversation turn(s) mentioning "X": [speaker] said "preview..." (date), ...'
        # Show top 3 previews max
        pass