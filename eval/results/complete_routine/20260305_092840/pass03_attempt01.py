import os
import logging
from datetime import date, datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

from engine.base import SkillBase, SkillRequest, SkillResponse

load_dotenv()

def _get_conn():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'mythos'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
        port=os.getenv('DB_PORT', '5432'),
        cursor_factory=RealDictCursor
    )
    return conn

class CompleteRoutineSkill(SkillBase):
    name = 'complete_routine'
    version = '1.0'
    category = 'action'
    description = 'Mark a routine as completed for today'
    triggers = ['done with', 'completed', 'finished', 'did my', 'mark complete', 'routine done', 'check off', 'done']
    cache_ttl = 0

    async def execute(self, request) -> SkillResponse:
        # 1. Extract which routine from message
        # 2. Find matching routine by title (fuzzy match)
        # 3. INSERT or UPDATE routine_completions for today
        # 4. Return confirmation
        pass

    def _find_routine(self, message) -> dict | None:
        # Query active routines, find best match by title ILIKE
        cleaned = message.lower()
        
        # Remove trigger phrases
        for trigger in self.triggers:
            cleaned = cleaned.replace(trigger, '')
        
        # Normalize whitespace
        cleaned = ' '.join(cleaned.split())
        
        if not cleaned:
            return None
            
        conn = None
        try:
            conn = _get_conn()
            with conn.cursor() as cursor:
                # First try to match the full cleaned string
                query = "SELECT id, title FROM routines WHERE is_active = true AND LOWER(title) ILIKE %s"
                cursor.execute(query, (f'%{cleaned}%',))
                results = cursor.fetchall()
                
                if len(results) == 1:
                    return dict(results[0])
                elif len(results) > 1:
                    return dict(results[0])
                else:
                    # Try each word individually
                    words = cleaned.split()
                    for word in words:
                        cursor.execute(query, (f'%{word}%',))
                        word_results = cursor.fetchall()
                        if word_results:
                            return dict(word_results[0])
                            
        except Exception as e:
            logging.error(f"Error finding routine: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def _mark_complete(self, routine_id, routine_title) -> int:
        # INSERT INTO routine_completions ON CONFLICT UPDATE
        today = date.today()
        conn = None
        try:
            conn = _get_conn()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO routine_completions (routine_id, due_date, status, completed_at, completed_by) 
                VALUES (%s, %s, 'completed', NOW(), 'adge') 
                ON CONFLICT (routine_id, due_date) 
                DO UPDATE SET status = 'completed', completed_at = NOW(), completed_by = 'adge' 
                RETURNING id
                """
                cursor.execute(query, (routine_id, today))
                result = cursor.fetchone()
                conn.commit()
                return result['id']
        except Exception as e:
            logging.error(f"Error marking routine complete: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()