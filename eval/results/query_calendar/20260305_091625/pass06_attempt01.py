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
        host=os.getenv('POSTGRES_HOST', 'localhost'),
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
        try:
            message = request.message
            start_date, end_date = self._detect_range(message)
            rows = self._query_events(start_date, end_date)
            results = self._format_results(rows)
            summary = self._build_summary(results, start_date, end_date)
            return SkillResponse(
                skill_name=self.name,
                data={
                    'events': results,
                    'count': len(results),
                    'start_date': str(start_date),
                    'end_date': str(end_date)
                },
                summary=summary,
                confidence=0.95,
                sources=['mythos.calendar_events']
            )
        except Exception as e:
            logging.error(f"Error in QueryCalendarSkill.execute: {e}")
            raise
        finally:
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
        conn = None
        try:
            conn = _get_conn()
            with conn.cursor() as cursor:
                query = """
                SELECT id, title, description, event_date, start_time, end_time, location, person
                FROM calendar_events
                WHERE is_active = true
                  AND event_date >= %s AND event_date <= %s
                ORDER BY event_date, start_time NULLS LAST
                """
                cursor.execute(query, (start_date, end_date))
                return cursor.fetchall()
        finally:
            if conn:
                conn.close()

    def _format_results(self, rows) -> list:
        formatted = []
        for row in rows:
            start_time_str = 'all day' if row['start_time'] is None else row['start_time'].strftime('%H:%M')
            end_time_str = None if row['end_time'] is None else row['end_time'].strftime('%H:%M')
            formatted.append({
                'id': row['id'],
                'title': row['title'],
                'event_date': row['event_date'].isoformat(),
                'start_time': start_time_str,
                'end_time': end_time_str,
                'location': row['location'],
                'person': row['person']
            })
        return formatted

    def _build_summary(self, results, start_date, end_date) -> str:
        if not results:
            if start_date == end_date:
                return 'No events scheduled for today.'
            else:
                days = (end_date - start_date).days + 1
                return f'No events in the next {days} days.'
        
        # Group events by date
        events_by_date = {}
        for event in results:
            date_key = event['event_date']
            if date_key not in events_by_date:
                events_by_date[date_key] = []
            events_by_date[date_key].append(event)
        
        # Format the summary
        lines = []
        event_count = 0
        for date_key in sorted(events_by_date.keys()):
            date_obj = datetime.datetime.strptime(date_key, '%Y-%m-%d').date()
            date_str = date_obj.strftime('%A, %B %d')
            for event in events_by_date[date_key]:
                if event_count >= 5:
                    break
                event_count += 1
                if event['start_time'] == 'all day':
                    line = f"{date_str}: {event['title']} (all day)"
                else:
                    # Format times cleanly
                    start_time = event['start_time']
                    end_time = event['end_time']
                    if end_time:
                        time_str = f"{start_time} - {end_time}"
                    else:
                        time_str = start_time
                    location_str = f" at {event['location']}" if event['location'] else ""
                    line = f"{date_str}: {event['title']} at {time_str}{location_str}"
                lines.append(line)
            if event_count >= 5:
                break
        
        if event_count < len(results):
            remaining = len(results) - event_count
            lines.append(f"and {remaining} more")
        
        # Ensure ASCII only
        ascii_lines = []
        for line in lines:
            ascii_lines.append(line.encode('ascii', 'ignore').decode('ascii'))
        
        return '\n'.join(ascii_lines)