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
        try:
            rows = self._query_routines_today()
            formatted = self._format_results(rows)
            summary = self._build_summary(formatted)
            total = len(formatted)
            completed = sum(1 for r in formatted if r['is_complete'])
            remaining = total - completed
            return SkillResponse(
                skill_name=self.name,
                data={
                    'routines': formatted,
                    'total': total,
                    'completed': completed,
                    'remaining': remaining
                },
                summary=summary,
                confidence=0.95,
                sources=['mythos.routines', 'mythos.routine_completions']
            )
        except Exception as e:
            logging.error(f"Error in execute: {e}")
            raise e

    def _query_routines_today(self) -> list:
        # Get active daily routines + weekly routines for today's day + monthly for today's date
        # LEFT JOIN routine_completions for today's date
        # Return list with routine info + completion status
        conn = None
        try:
            conn = self._get_conn()
            today = date.today()
            day_of_week = today.weekday()
            day_of_month = today.day
            
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
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"Error querying routines: {e}")
            raise e
        finally:
            if conn:
                conn.close()

    def _format_results(self, rows) -> list:
        formatted = []
        for row in rows:
            formatted.append({
                'id': row['id'],
                'title': row['title'],
                'frequency': row['frequency'],
                'time_due': str(row['time_due']) if row['time_due'] else None,
                'domain': row['domain'],
                'priority': row['priority'],
                'is_complete': row['completion_status'] == 'completed',
                'completed_at': row['completed_at'].isoformat() if row['completed_at'] else None
            })
        return formatted

    def _build_summary(self, results) -> str:
        total = len(results)
        completed = sum(1 for r in results if r['is_complete'])
        
        if total == 0:
            return "No routines scheduled for today."
        
        summary = f"Routines: {completed} of {total} complete."
        
        done_titles = [r['title'] for r in results if r['is_complete']]
        remaining_titles = [r['title'] for r in results if not r['is_complete']]
        
        if done_titles:
            summary += f" Done: {', '.join(done_titles)}."
        
        if remaining_titles:
            summary += f" Still to do: {', '.join(remaining_titles)}."
        
        if completed == total:
            summary = "All routines complete for today!"
            
        return summary

    def _get_conn(self):
        conn = None
        try:
            conn = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'mythos'),
                user=os.getenv('DB_USER', 'adge'),
                password=os.getenv('DB_PASSWORD', ''),
                port=os.getenv('DB_PORT', '5432'),
                cursor_factory=RealDictCursor
            )
            return conn
        except Exception as e:
            if conn:
                conn.close()
            raise e