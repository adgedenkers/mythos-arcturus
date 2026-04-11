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
        pending = 0
        backlog_rows = []
        stream_rows = []
        summary = ""
        
        try:
            pending = self._get_pending_count()
            backlog_rows = self._get_backlog_status()
            stream_rows = self._get_stream_breakdown()
            summary = self._build_summary(pending, backlog_rows, stream_rows)
        except Exception as e:
            logging.error(f"Error in execute: {e}")
            return SkillResponse(
                response="Error retrieving idea backlog data.",
                skill_name=self.name,
                confidence=0.0,
                sources=[]
            )
        finally:
            pass  # Connection handling is done in individual methods
            
        return SkillResponse(
            skill_name=self.name,
            data={
                'pending_count': pending,
                'backlog': [self._convert_uuids_to_str(row) for row in backlog_rows],
                'streams': [self._convert_uuids_to_str(row) for row in stream_rows]
            },
            summary=summary,
            confidence=0.95,
            sources=['mythos.idea_inbox', 'mythos.idea_backlog']
        )

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
        conn = None
        try:
            conn = _get_conn()
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT stream, COUNT(*) as total, SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as done, SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress, SUM(CASE WHEN status = 'backlog' THEN 1 ELSE 0 END) as backlog FROM idea_backlog GROUP BY stream ORDER BY stream"
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"Error in _get_stream_breakdown: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def _build_summary(self, pending, backlog_rows, stream_rows):
        summary_parts = []
        
        # Idea Pipeline
        summary_parts.append(f"Idea Pipeline: {pending} ideas pending triage.")
        
        # Backlog status
        if backlog_rows:
            streams = set(row['stream'] for row in backlog_rows)
            summary_parts.append(f"Backlog: {len(backlog_rows)} items across {len(streams)} streams.")
            
            # Per stream breakdown
            for stream_row in stream_rows:
                stream = stream_row['stream']
                total = stream_row['total']
                backlog = stream_row['backlog']
                in_progress = stream_row['in_progress']
                done = stream_row['done']
                summary_parts.append(f"{stream}: {total} total ({backlog} backlog, {in_progress} in progress, {done} done)")
        else:
            summary_parts.append("Backlog is empty.")
            
        # Ensure summary is never empty
        if not summary_parts:
            summary_parts.append("No backlog data available.")
            
        # Convert to ASCII only
        ascii_summary = []
        for part in summary_parts:
            ascii_summary.append(part.encode('ascii', 'ignore').decode('ascii'))
            
        return "\n".join(ascii_summary)

    def _convert_uuids_to_str(self, row):
        """Convert all uuid fields in a row to strings"""
        result = {}
        for key, value in row.items():
            if isinstance(value, bytes):
                # Handle binary UUIDs
                result[key] = str(value)
            else:
                result[key] = value
        return result

def _get_conn():
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'mythos'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        cursor_factory=RealDictCursor
    )
    return conn