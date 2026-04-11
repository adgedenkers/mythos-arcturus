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
    triggers = ['backlog', 'idea backlog', 'pending ideas', 'triage ideas', 'manage ideas', 'idea pipeline', 'backlog status', 'what ideas are pending']
    cache_ttl = 300

    async def execute(self, request: SkillRequest) -> SkillResponse:
        pass

    def _get_pending_count(self):
        try:
            conn = _get_conn()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT COUNT(*) as cnt FROM idea_inbox WHERE disposition = %s", ('pending',))
            row = cur.fetchone()
            return row['cnt']
        except Exception as e:
            logging.error(f"Error getting pending count: {e}")
            return 0
        finally:
            if conn:
                conn.close()

    def _get_backlog_status(self):
        try:
            conn = _get_conn()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT stream, priority, status, COUNT(*) as cnt FROM idea_backlog GROUP BY stream, priority, status ORDER BY stream, priority")
            rows = cur.fetchall()
            return rows
        except Exception as e:
            logging.error(f"Error getting backlog status: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def _get_stream_breakdown(self):
        pass

    def _build_summary(self):
        pass

def _get_conn():
    db_host = os.getenv("DB_HOST", "localhost")
    db_name = os.getenv("DB_NAME", "mythos")
    db_user = os.getenv("DB_USER", "mythos")
    db_password = os.getenv("DB_PASSWORD", "mythos")

    try:
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password
        )
        return conn
    except psycopg2.Error as e:
        logging.error(f"Database connection error: {e}")
        return None