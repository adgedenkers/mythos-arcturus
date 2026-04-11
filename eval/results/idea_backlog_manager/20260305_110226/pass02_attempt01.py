import os
import logging
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from engine.base import SkillBase, SkillRequest, SkillResponse

load_dotenv()

class IdeaBacklogManagerSkill(SkillBase):
    name = 'idea_backlog_manager'
    triggers = [
        'backlog', 'idea backlog', 'pending ideas', 'triage ideas',
        'manage ideas', 'idea pipeline', 'backlog status', 'what ideas are pending'
    ]
    cache_ttl = 300

    async def execute(self, request: SkillRequest) -> SkillResponse:
        pass

    def _get_pending_count(self):
        conn = None
        try:
            conn = _get_conn()
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as cnt FROM idea_inbox WHERE disposition = 'pending'")
                row = cursor.fetchone()
                return row['cnt'] if row else 0
        except Exception as e:
            logging.error(f"Error in _get_pending_count: {e}")
            return 0
        finally:
            if conn:
                conn.close()

    def _get_backlog_status(self):
        conn = None
        try:
            conn = _get_conn()
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT stream, priority, status, COUNT(*) as cnt FROM idea_backlog GROUP BY stream, priority, status ORDER BY stream, priority"
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"Error in _get_backlog_status: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def _get_stream_breakdown(self):
        pass

    def _build_summary(self):
        pass

def _get_conn():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'mythos'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        cursor_factory=RealDictCursor
    )
    return conn