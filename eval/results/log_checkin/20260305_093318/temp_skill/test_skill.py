import os
import logging
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

from engine.base import SkillBase, SkillRequest, SkillResponse

load_dotenv()

class LogCheckinSkill(SkillBase):
    name = 'log_checkin'
    version = '1.0'
    category = 'action'
    description = 'Record a mood or status check-in'
    triggers = ['check in', 'checkin', 'feeling', 'i feel', 'mood', 'how am i', 'status update', 'im feeling', 'doing well', 'doing great', 'doing bad', 'stressed', 'tired', 'energized', 'happy', 'anxious']
    cache_ttl = 0

    async def execute(self, request) -> SkillResponse:
        # 1. Extract mood/status from message
        mood = self._extract_mood(request.message)
        # 2. Validate mood
        if not mood or len(mood) < 2:
            return SkillResponse(
                skill_name=self.name,
                data={},
                summary='How are you feeling? Tell me your mood or status.',
                confidence=0.3,
                sources=[]
            )
        # 3. INSERT into checkin_log
        try:
            checkin_id = self._insert_checkin(mood_text=mood, person=request.message)
        except Exception as e:
            logging.error(f"Failed to insert checkin: {e}")
            raise
        # 4. Return confirmation
        return SkillResponse(
            skill_name=self.name,
            data={'checkin_id': checkin_id, 'mood': mood},
            summary=f'Check-in recorded: {mood}',
            confidence=0.95,
            sources=['mythos.checkin_log']
        )

    def _extract_mood(self, message) -> str:
        # Lowercase the message
        msg = message.lower().strip()
        
        # Remove triggers in order of longest first
        triggers = ['status update', 'im feeling', 'i feel', 'doing well', 'doing great', 'doing bad', 'check in', 'checkin', 'feeling', 'mood']
        triggers.sort(key=len, reverse=True)
        
        for trigger in triggers:
            if msg.startswith(trigger):
                msg = msg[len(trigger):].strip()
                break
        
        # Normalize whitespace
        msg = ' '.join(msg.split())
        
        # Common moods to recognize
        common_moods = {
            'happy', 'sad', 'tired', 'anxious', 'stressed', 
            'energized', 'grateful', 'frustrated', 'calm', 'excited'
        }
        
        # If the cleaned text is a known mood word, use it directly
        if msg in common_moods:
            return msg
        else:
            # Otherwise use the full cleaned text as a freeform mood
            return msg

    def _insert_checkin(self, mood_text, person) -> int:
        conn = None
        try:
            conn = _get_conn()
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO checkin_log (
                        checkin_date,
                        checkin_time,
                        checkin_type,
                        summary,
                        user_response
                    ) VALUES (
                        CURRENT_DATE,
                        CURRENT_TIMESTAMP,
                        'mood',
                        %s,
                        %s
                    ) RETURNING id
                """, (mood_text, person))
                checkin_id = cursor.fetchone()['id']
                conn.commit()
                return checkin_id
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

def _get_conn():
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'mythos'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        if conn:
            conn.close()
        raise e