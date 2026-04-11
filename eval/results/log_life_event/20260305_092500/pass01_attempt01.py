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
        # 2. Detect domain and person
        # 3. INSERT into life_events
        # 4. Return confirmation
        pass

    def _extract_description(self, message) -> str:
        # Remove trigger phrases, return the event description
        pass

    def _detect_domain(self, message) -> str:
        # Check for domain keywords, default 'personal'
        pass

    def _detect_person(self, message) -> str:
        # Check for person names, default 'adge'
        pass

    def _insert_event(self, description, domain, person, source_message) -> int:
        # INSERT and return the new id
        pass

def _get_conn():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'mythos'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
        cursor_factory=RealDictCursor
    )
    return conn