#!/opt/mythos/.venv/bin/python3
"""
SearchVoiceMemoSkill - Full-text search across voice memo transcripts
"""

import os
import logging
import re
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from engine.base import SkillBase, SkillRequest, SkillResponse

load_dotenv('/opt/mythos/.env')

def _get_conn():
    """Get database connection using environment variables"""
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'mythos'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT', '5432'),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        if conn:
            conn.close()
        raise e

class SearchVoiceMemoSkill(SkillBase):
    name = 'search_voice_memos'
    version = '1.0'
    category = 'data'
    description = 'Full-text search across voice memo transcripts'
    triggers = ['voice memo', 'voice memos', 'recording', 'what did I say', 'what did we say', 'we talked about', 'I said', 'we discussed', 'remember when I said', 'transcript', 'memo search']
    cache_ttl = 300

    async def execute(self, request: SkillRequest) -> SkillResponse:
        # 1. Extract search terms using _extract_search_terms()
        # 2. If no terms: return total memo count with guidance
        # 3. Run FTS query using _search_transcripts() with ts_rank
        # 4. Build result list using _format_results()
        # 5. Build human summary using _build_summary()
        # 6. Return SkillResponse with matches in data
        pass

    def _extract_search_terms(self, message: str) -> str:
        # Remove trigger phrases, return cleaned search string
        # Must return at least 2 chars or empty string
        if not message:
            return ""
        
        # Convert to lowercase
        msg = message.lower()
        
        # Define trigger phrases to remove
        trigger_phrases = [
            'voice memo', 'voice memos', 'recording', 'what did i say', 
            'what did we say', 'we talked about', 'i said', 'we discussed', 
            'remember when i said', 'transcript', 'memo search', 'search', 'find'
        ]
        
        # Remove trigger phrases (case insensitive)
        for phrase in trigger_phrases:
            # Use word boundaries to avoid partial matches
            msg = re.sub(r'\b' + re.escape(phrase) + r'\b', '', msg, flags=re.IGNORECASE)
        
        # Remove punctuation and extra whitespace
        msg = re.sub(r'[^\w\s]', '', msg)
        msg = re.sub(r'\s+', ' ', msg).strip()
        
        # Return cleaned string if length >= 2, else empty string
        return msg if len(msg) >= 2 else ""

    def _search_transcripts(self, search_terms: str, limit: int = 10) -> list:
        # Use to_tsquery with plainto_tsquery for safety
        # SELECT with ts_rank for relevance scoring
        # Return rows ordered by rank DESC, then created_at DESC
        # Include: id, filename, duration_seconds, snippet of transcript, rank, created_at
        conn = None
        cursor = None
        try:
            conn = _get_conn()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    id, 
                    filename, 
                    duration_seconds, 
                    LEFT(transcript_full, 300) as transcript_preview, 
                    created_at, 
                    ts_rank(to_tsvector('english', COALESCE(transcript_full, '')), plainto_tsquery('english', %s)) as rank 
                FROM voice_memos 
                WHERE status = 'completed' 
                AND to_tsvector('english', COALESCE(transcript_full, '')) @@ plainto_tsquery('english', %s) 
                ORDER BY rank DESC, created_at DESC 
                LIMIT %s
            """
            
            cursor.execute(query, (search_terms, search_terms, limit))
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"Error in _search_transcripts: {e}")
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _format_results(self, rows: list) -> list:
        # Convert rows to clean dicts
        # Truncate transcript previews to 200 chars
        # Format duration as minutes:seconds
        pass

    def _build_summary(self, results: list, search_terms: str) -> str:
        # 'Found N voice memo(s) matching "X": filename1 (duration, date), filename2...'
        # Include brief transcript snippet from top result
        pass