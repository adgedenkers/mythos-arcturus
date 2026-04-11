import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from engine.base import SkillBase, SkillRequest, SkillResponse

load_dotenv()

class LogLifeEventSkill(SkillBase):
    name = 'log_life_event'
    version = '1.0'
    category = 'action'
    description = 'Log a new life event'
    triggers = ['log event', 'record event', 'log that', 'note that', 'remember that', 'something happened', 'just happened', 'log life event']
    cache_ttl = 0

    async def execute(self, request) -> SkillResponse:
        # 1. Extract description from message
        description = self._extract_description(request.message)
        # 2. Detect domain and person
        domain = self._detect_domain(request.message)
        person = self._detect_person(request.message)
        # 3. INSERT into life_events
        event_id = self._insert_event(description, domain, person, request.message)
        # 4. Return confirmation
        return SkillResponse(
            message=f"Life event logged successfully with ID {event_id}",
            success=True
        )

    def _extract_description(self, message) -> str:
        # Remove trigger phrases, return the event description
        lower_message = message.lower().strip()
        # Remove triggers LONGEST FIRST
        triggers = ['log life event', 'record event', 'log event', 'something happened', 'just happened', 'remember that', 'note that', 'log that', 'log', 'record']
        for trigger in triggers:
            if lower_message.startswith(trigger):
                lower_message = lower_message[len(trigger):].strip()
                break
        # Normalize whitespace
        import re
        cleaned = re.sub(r'\s+', ' ', lower_message)
        return cleaned

    def _detect_domain(self, message) -> str:
        # Check for domain keywords, default 'personal'
        lower_message = message.lower()
        if 'spiritual' in lower_message:
            return 'spiritual'
        elif 'technical' in lower_message:
            return 'technical'
        elif 'financial' in lower_message:
            return 'financial'
        else:
            return 'personal'

    def _detect_person(self, message) -> str:
        # Check for person names, default 'adge'
        lower_message = message.lower()
        if 'rebecca' in lower_message:
            return 'rebecca'
        elif 'seraphe' in lower_message:
            return 'rebecca'  # Map 'seraphe' to 'rebecca'
        elif 'fitz' in lower_message:
            return 'fitz'
        else:
            return 'adge'

    def _insert_event(self, description, domain, person, source_message) -> int:
        # INSERT and return the new id
        conn = None
        try:
            conn = _get_conn()
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO life_events (description, domain, person, source, source_message)
                    VALUES (%s, %s, %s, 'iris', %s)
                    RETURNING id
                """, (description, domain, person, source_message))
                event_id = cursor.fetchone()[0]
                conn.commit()
                return event_id
        except Exception as e:
            if conn:
                conn.rollback()
            logging.error(f"Error inserting life event: {e}")
            raise
        finally:
            if conn:
                conn.close()

def _get_conn():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'mythos'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
        cursor_factory=RealDictCursor
    )
    return conn