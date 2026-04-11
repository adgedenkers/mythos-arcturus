import os
import logging
from datetime import date, datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from engine.base import SkillBase, SkillRequest, SkillResponse

load_dotenv()

class QueryRoutinesSkill(SkillBase):
    name = 'query_routines'
    version = '1.0'
    category = 'data'
    description = 'Show routines and their completion status for today'
    triggers = ['routine', 'routines', 'daily routine', 'to do', 'todo', 'checklist', 'what should I do', 'what do I need to do', 'tasks', 'have I done']
    cache_ttl = 300

    async def execute(self, request) -> SkillResponse:
        # 1. Query active routines applicable today
        # 2. Check completion status for today
        # 3. Format with done/not-done indicators
        # 4. Summarize: N of M complete, list what remains
        pass

    def _query_routines_today(self) -> list:
        # Get active daily routines + weekly routines for today's day + monthly for today's date
        # LEFT JOIN routine_completions for today's date
        # Return list with routine info + completion status
        today = date.today()
        day_of_week = today.weekday()
        day_of_month = today.day
        
        conn = None
        try:
            conn = _get_conn()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT r.id, r.title, r.description, r.frequency, r.time_due, r.domain, r.priority, r.sort_order,
                           rc.status as completion_status, rc.completed_at
                    FROM routines r
                    LEFT JOIN routine_completions rc ON rc.routine_id = r.id AND rc.due_date = %s
                    WHERE r.is_active = true
                      AND (
                        r.frequency = 'daily'
                        OR (r.frequency = 'weekly' AND r.day_of_week = %s)
                        OR (r.frequency = 'monthly' AND r.day_of_month = %s)
                      )
                    ORDER BY r.sort_order, r.title
                """, (today, day_of_week, day_of_month))
                return cursor.fetchall()
        finally:
            if conn:
                conn.close()

    def _format_results(self, rows) -> list:
        pass

    def _build_summary(self, results) -> str:
        # 'Routines: 2 of 5 complete. Done: X, Y. Still to do: A, B, C.'
        pass

def _get_conn():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'mythos'),
        user=os.getenv('DB_USER', 'adge'),
        password=os.getenv('DB_PASSWORD', ''),
        cursor_factory=RealDictCursor
    )
    return conn