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

    async def execute(self, request) -> SkillResponse:
        # 1. Extract mood/status from message
        mood = self._extract_mood(request.message)
        # 2. INSERT into checkin_log
        if not mood or len(mood) < 2:
            return SkillResponse(
                skill_name=self.name,
                data={},
                summary='How are you feeling? Tell me your mood or status.',
                confidence=0.3,
                sources=[]
            )
        
        new_id = self._insert_checkin(mood=mood, notes=request.message, person='adge')
        # 3. Return confirmation
        if new_id == -1:
            return SkillResponse(
                skill_name=self.name,
                data={},
                summary='Failed to log check-in due to database error.',
                confidence=0.1,
                sources=[]
            )
        
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
        trigger_order = [
            'status update', 'im feeling', 'i feel', 'doing well', 
            'doing great', 'doing bad', 'check in', 'checkin', 
            'feeling', 'mood'
        ]
        
        # Remove triggers one by one, longest first
        for trigger in trigger_order:
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
            # Otherwise return the full cleaned text as freeform mood
            return msg

    def _insert_checkin(self, mood, notes, person) -> int:
        conn = None
        try:
            conn = _get_conn()
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO checkin_log (mood, notes, person) VALUES (%s, %s, %s) RETURNING id",
                    (mood, notes, person)
                )
                checkin_id = cursor.fetchone()['id']
                conn.commit()
                return checkin_id
        except psycopg2.IntegrityError as e:
            if conn:
                conn.rollback()
            # Handle column mismatch or other integrity errors
            logging.error(f"Database integrity error in _insert_checkin: {e}")
            return -1
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
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'mythos'),
            user=os.getenv('DB_USER', 'adge'),
            password=os.getenv('DB_PASS', ''),
            port=os.getenv('DB_PORT', '5432'),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        if conn:
            conn.close()
        raise e