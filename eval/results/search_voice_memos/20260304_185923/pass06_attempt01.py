#!/opt/mythos/.venv/bin/python3
"""
Search Voice Memos Skill

This skill enables full-text search across voice memo transcripts
using PostgreSQL's text search capabilities.
"""

import os
import logging
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

from engine.base import SkillBase, SkillRequest, SkillResponse

# Load environment variables
load_dotenv('/opt/mythos/.env')

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
        conn = None
        try:
            terms = self._extract_search_terms(request.message)
            
            if not terms:
                # Query for total count
                conn = _get_conn()
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM voice_memos WHERE status = 'completed'")
                count = cursor.fetchone()[0]
                cursor.close()
                
                guidance = "Try asking something like 'search voice memos about project updates' or 'find recordings about the meeting'"
                return SkillResponse(
                    data={'count': count},
                    summary=f"Found {count} completed voice memos. {guidance}",
                    confidence=0.95,
                    sources=['mythos.voice_memos']
                )
            
            # Search with terms
            rows = self._search_transcripts(terms)
            results = self._format_results(rows)
            summary = self._build_summary(results, terms)
            
            return SkillResponse(
                data={'matches': results, 'search_terms': terms, 'count': len(results)},
                summary=summary,
                confidence=0.95,
                sources=['mythos.voice_memos']
            )
            
        except Exception as e:
            logging.error(f"Error in execute: {e}")
            return SkillResponse(
                data=None,
                summary=f"Error searching voice memos: {str(e)}",
                confidence=0.0,
                sources=['mythos.voice_memos']
            )
        finally:
            if conn:
                conn.close()

    def _extract_search_terms(self, message: str) -> str:
        # Remove trigger phrases, return cleaned search string
        # Must return at least 2 chars or empty string
        message = message.lower().strip()
        
        # Define trigger phrases to remove
        trigger_phrases = [
            'voice memo', 'voice memos', 'recording', 'what did i say', 
            'what did we say', 'we talked about', 'i said', 'we discussed', 
            'remember when i said', 'transcript', 'memo search', 'search', 'find'
        ]
        
        # Remove each trigger phrase
        for phrase in trigger_phrases:
            message = message.replace(phrase, '')
        
        # Remove punctuation and extra whitespace
        cleaned = ''.join(char for char in message if char.isalnum() or char.isspace())
        cleaned = ' '.join(cleaned.split())
        
        # Return cleaned string if length >= 2, else empty string
        return cleaned if len(cleaned) >= 2 else ''

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
            
            # Convert to list of dicts
            result = [dict(row) for row in rows]
            return result
            
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
        formatted_rows = []
        for row in rows:
            # Truncate transcript preview to 200 characters
            transcript_preview = row.get('transcript_preview', '')
            if len(transcript_preview) > 200:
                transcript_preview = transcript_preview[:200] + '...'
            
            # Format duration as minutes:seconds
            duration_seconds = row.get('duration_seconds', 0)
            minutes = int(duration_seconds // 60)
            seconds = int(duration_seconds % 60)
            duration_formatted = f"{minutes}:{seconds:02d}"
            
            formatted_row = {
                'id': row.get('id'),
                'filename': row.get('filename'),
                'duration': duration_formatted,
                'transcript_preview': transcript_preview,
                'rank': row.get('rank'),
                'created_at': row.get('created_at')
            }
            formatted_rows.append(formatted_row)
        
        return formatted_rows

    def _build_summary(self, results: list, search_terms: str) -> str:
        # 'Found N voice memo(s) matching "X": filename1 (duration, date), filename2...'
        # Include brief transcript snippet from top result
        if not results:
            return f"No voice memos found matching \"{search_terms}\"."
        
        count = len(results)
        if count == 1:
            summary = f"Found 1 voice memo matching \"{search_terms}\": "
        else:
            summary = f"Found {count} voice memos matching \"{search_terms}\": "
        
        # Add filenames and durations
        file_list = []
        for i, result in enumerate(results[:3]):  # Show up to 3 results
            filename = result.get('filename', 'Unknown')
            duration = result.get('duration', 'Unknown')
            file_list.append(f"{filename} ({duration})")
        
        summary += ", ".join(file_list)
        
        # Add snippet from top result if available
        if results:
            top_result = results[0]
            transcript_preview = top_result.get('transcript_preview', '')
            if transcript_preview:
                # Truncate snippet to 100 characters for summary
                if len(transcript_preview) > 100:
                    transcript_preview = transcript_preview[:100] + '...'
                summary += f". First result snippet: {transcript_preview}"
        
        return summary

def _get_conn():
    conn = psycopg2.connect(
        database=os.getenv("DB_NAME", "mythos"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )
    return conn