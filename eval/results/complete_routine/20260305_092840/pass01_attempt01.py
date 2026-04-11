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
        pass

    def _mark_complete(self, routine_id, routine_title) -> int:
        # INSERT INTO routine_completions ON CONFLICT UPDATE
        pass