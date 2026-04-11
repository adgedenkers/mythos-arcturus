import os
import logging
import re
import datetime
from datetime import date, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from engine.base import SkillBase, SkillRequest, SkillResponse

load_dotenv()

def _get_conn():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'mythos'),
        user=os.getenv('DB_USER', 'mythos_user'),
        password=os.getenv('DB_PASS', 'mythos_pass'),
        port=os.getenv('DB_PORT', '5432'),
        cursor_factory=RealDictCursor
    )
    return conn

class QueryCalendarSkill(SkillBase):
    name = 'query_calendar'
    version = '1.0'
    category = 'data'
    description = 'Show calendar events for today or upcoming days'
    triggers = ['calendar', 'schedule', 'events', 'what is on', 'whats on', 'plans', 'upcoming', 'agenda', 'do I have anything', 'any events', 'appointments']
    cache_ttl = 300

    async def execute(self, request) -> SkillResponse:
        # 1. Detect date range from message (today, this week, next N days)
        # 2. Query calendar_events for that range
        # 3. Format and summarize
        pass

    def _detect_range(self, message) -> tuple:
        # Return (start_date, end_date)
        # Default: today only
        # 'week'/'this week' = today through 7 days
        # 'tomorrow' = tomorrow only
        # 'next N days' = today + N
        today = date.today()
        msg = message.lower()
        
        if 'tomorrow' in msg:
            tomorrow = today + timedelta(days=1)
            return (tomorrow, tomorrow)
        elif 'this week' in msg or 'week' in msg:
            end_date = today + timedelta(days=7)
            return (today, end_date)
        elif 'this month' in msg or 'month' in msg:
            end_date = today + timedelta(days=30)
            return (today, end_date)
        else:
            # Check for 'next N days'
            match = re.search(r'next\s+(\d+)\s*days?', msg)
            if match:
                days = int(match.group(1))
                end_date = today + timedelta(days=days)
                return (today, end_date)
            else:
                # Default: today only
                return (today, today)

    def _query_events(self, start_date, end_date) -> list:
        pass

    def _format_results(self, rows) -> list:
        pass

    def _build_summary(self, results, start_date, end_date) -> str:
        pass