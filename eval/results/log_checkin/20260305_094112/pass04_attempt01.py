import os
import logging
from typing import Optional
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

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def execute(self, request) -> SkillResponse:
        # 1. Extract mood/status from message
        mood = self._extract_mood(request.message)
        
        # 2. Check if mood is valid
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
            new_id = self._insert_checkin(mood_text=mood, original_message=request.message)
        except Exception as e:
            self.logger.error(f"Failed to insert checkin: {e}")
            raise e
        
        # 4. Return confirmation
        return SkillResponse(
            skill_name=self.name,
            data={'checkin_id': new_id, 'mood': mood},
            summary=f'Check-in recorded: {mood}',
            confidence=0.95,
            sources=['mythos.checkin_log']
        )

    def _extract_mood(self, message) -> str:
        # Lowercase the message
        msg = message.lower().strip()
        
        # Define triggers in order of longest first
        trigger_words = [
            'status update', 'im feeling', 'i feel', 'doing well', 
            'doing great', 'doing bad', 'check in', 'checkin', 
            'feeling', 'mood'
        ]
        
        # Remove each trigger from the message, longest first
        for trigger in trigger_words:
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
        
        # If the cleaned message is a known mood word, use it directly
        if msg in common_moods:
            return msg
        else:
            # Otherwise return the full cleaned text as freeform mood
            return msg

    def _insert_checkin(self, mood_text, original_message) -> int:
        conn = None
        try:
            conn = self._get_conn()
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
                """, (mood_text, original_message))
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

    def _get_conn(self):
        conn = None
        try:
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'mythos'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', ''),
                port=os.getenv('DB_PORT', '5432'),
                cursor_factory=RealDictCursor
            )
            return conn
        except Exception as e:
            if conn:
                conn.close()
            raise e