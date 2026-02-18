#!/usr/bin/env python3
"""
Message Extractor
=================
Pre-pass that runs a small model (qwen2.5:7b) on every incoming message
to extract structured data: bill payments, spending, calendar events,
task completions, mood, and life events.

This runs BEFORE the main model, enriching the message context.
After the main model responds, the extracted actions are executed
against the database.

Architecture:
    Message in → Extractor (7b) → enriched context → Main model (32b) → response
                                → Executor commits actions to DB
"""

import os
import json
import logging
from datetime import date, datetime, timedelta
from typing import Optional, Dict, Any, List

from ollama import Client
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

logger = logging.getLogger(__name__)

EXTRACTOR_MODEL = os.getenv('EXTRACTOR_MODEL', 'qwen2.5:7b')
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')

# Load knowledge map once at import time

def _validate_extracted_date(extraction: dict, original_message: str) -> dict:
    """
    Post-process: if the model returned a date that contradicts
    day-of-week references in the original message, fix it.
    """
    from datetime import date, timedelta
    
    cal = extraction.get('calendar_event')
    if not cal or not cal.get('date'):
        return extraction
    
    msg = original_message.lower()
    
    # Map day names to weekday numbers
    day_map = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6,
        'mon': 0, 'tue': 1, 'tues': 1, 'wed': 2, 'thu': 3, 'thur': 3,
        'fri': 4, 'sat': 5, 'sun': 6,
    }
    
    # Find which day name was mentioned
    mentioned_day = None
    for name, dow in day_map.items():
        if name in msg.split():
            mentioned_day = dow
            break
    
    if mentioned_day is None:
        # Check for today/tomorrow
        if 'today' in msg or 'tonight' in msg:
            correct_date = date.today()
            cal['date'] = correct_date.strftime('%Y-%m-%d')
        elif 'tomorrow' in msg:
            correct_date = date.today() + timedelta(days=1)
            cal['date'] = correct_date.strftime('%Y-%m-%d')
        return extraction
    
    # Parse the returned date
    try:
        returned = date.fromisoformat(cal['date'])
    except (ValueError, TypeError):
        return extraction
    
    # Check if returned date matches the mentioned day
    if returned.weekday() == mentioned_day:
        return extraction  # Model got it right
    
    # Model got it wrong — find the next occurrence of that day
    today = date.today()
    if 'next' in msg:
        # "next Friday" = skip this week
        days_ahead = (mentioned_day - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        days_ahead += 7  # next week
        # Actually: next week's occurrence
        days_to_monday = (7 - today.weekday()) % 7
        if days_to_monday == 0:
            days_to_monday = 7
        next_monday = today + timedelta(days=days_to_monday)
        correct_date = next_monday + timedelta(days=mentioned_day)
    else:
        # Next upcoming occurrence
        days_ahead = (mentioned_day - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        correct_date = today + timedelta(days=days_ahead)
    
    import logging
    logging.getLogger(__name__).warning(
        f"Date fix: model returned {returned} ({returned.strftime('%A')}) "
        f"but message said {list(day_map.keys())[list(day_map.values()).index(mentioned_day)]}. "
        f"Corrected to {correct_date} ({correct_date.strftime('%A')})"
    )
    
    cal['date'] = correct_date.strftime('%Y-%m-%d')
    return extraction


KNOWLEDGE_MAP_PATH = '/opt/mythos/docs/KNOWLEDGE_MAP.md'
_knowledge_map_cache = None
_knowledge_map_mtime = 0


def _load_knowledge_map() -> str:
    """Load the knowledge map, caching based on file mtime."""
    global _knowledge_map_cache, _knowledge_map_mtime

    try:
        mtime = os.path.getmtime(KNOWLEDGE_MAP_PATH)
        if _knowledge_map_cache is None or mtime > _knowledge_map_mtime:
            with open(KNOWLEDGE_MAP_PATH, 'r') as f:
                _knowledge_map_cache = f.read()
            _knowledge_map_mtime = mtime
            logger.info("Knowledge map loaded/refreshed")
        return _knowledge_map_cache
    except FileNotFoundError:
        logger.warning("Knowledge map not found at %s", KNOWLEDGE_MAP_PATH)
        return ""


def _build_dynamic_context() -> str:
    """
    Build the dynamic part of the extractor context:
    current routine names, open task names, etc.
    Kept very compact.
    """
    import psycopg2
    from psycopg2.extras import RealDictCursor

    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', '/var/run/postgresql'),
            database=os.getenv('POSTGRES_DB', 'mythos'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', ''),
            port=os.getenv('POSTGRES_PORT', '5432'),
            cursor_factory=RealDictCursor,
        )
        cur = conn.cursor()
        today = date.today()
        dow = today.weekday()
        dom = today.day

        parts = []

        # Today's routines (names + status)
        cur.execute("""
            SELECT r.id, r.title, rc.status as completion_status
            FROM routines r
            LEFT JOIN routine_completions rc ON rc.routine_id = r.id AND rc.due_date = %s
            WHERE r.is_active = true AND r.auto_create = true
              AND (r.frequency = 'daily'
                   OR (r.frequency = 'weekdays' AND %s < 5)
                   OR (r.frequency = 'weekends' AND %s >= 5)
                   OR (r.frequency = 'weekly' AND r.day_of_week = %s)
                   OR (r.frequency = 'monthly' AND r.day_of_month = %s))
            ORDER BY r.sort_order
        """, (today, dow, dow, dow, dom))
        routines = cur.fetchall()
        if routines:
            r_list = [f"- {r['title']} (id:{r['id']}, {'done' if r['completion_status'] == 'done' else 'pending'})" for r in routines]
            parts.append("TODAY'S ROUTINES:\n" + "\n".join(r_list))

        # Upcoming calendar events (so extractor can match for updates/deletes)
        cur.execute("""
            SELECT id, title, event_date, start_time, person, location
            FROM calendar_events
            WHERE event_date >= %s AND event_date < %s AND is_active = true
            ORDER BY event_date, start_time NULLS LAST
        """, (today, today + timedelta(days=30)))
        events = cur.fetchall()
        if events:
            e_list = []
            for e in events:
                t = f" at {e['start_time']}" if e.get('start_time') else ""
                p = f" ({e['person']})" if e.get('person') and e['person'] != 'adge' else ""
                loc = f" @ {e['location']}" if e.get('location') else ""
                e_list.append(f"- {e['title']}{t} on {e['event_date']}{p}{loc} (id:{e['id']})")
            parts.append("UPCOMING CALENDAR EVENTS:\n" + "\n".join(e_list))

        # Open tasks
        cur.execute("""\n            SELECT id, idea FROM idea_backlog
            WHERE (domain = 'task' OR idea_type = 'task')
              AND status IN ('open', 'in_progress') AND is_archived = false
            ORDER BY CASE priority WHEN 'critical' THEN 0 WHEN 'high' THEN 1
                WHEN 'medium' THEN 2 WHEN 'low' THEN 3 END
            LIMIT 10
        """)
        tasks = cur.fetchall()
        if tasks:
            t_list = [f"- {t['idea']} (id:{t['id']})" for t in tasks]
            parts.append("OPEN TASKS:\n" + "\n".join(t_list))

        cur.close()
        conn.close()

        return "\n\n".join(parts)

    except Exception as e:
        logger.error(f"Dynamic context build failed: {e}")
        return ""


def _build_extractor_prompt() -> str:
    """Build the full extractor system prompt."""
    knowledge_map = _load_knowledge_map()
    dynamic_context = _build_dynamic_context()

    today = date.today()
    now = datetime.now()

    # Build full date reference frame so the model never guesses dates
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # This week's remaining days
    this_week = []
    for i in range(1, 7 - today.weekday()):
        d = today + timedelta(days=i)
        this_week.append(f"  {day_names[d.weekday()]} = {d.strftime('%B %d, %Y')}")
    
    # Next week
    days_until_monday = 7 - today.weekday()
    next_week = []
    for i in range(7):
        d = today + timedelta(days=days_until_monday + i)
        next_week.append(f"  {day_names[d.weekday()]} = {d.strftime('%B %d, %Y')}")
    
    # Weekend
    days_until_sat = 5 - today.weekday()
    if days_until_sat <= 0:
        days_until_sat += 7
    this_sat = today + timedelta(days=days_until_sat)
    this_sun = this_sat + timedelta(days=1)
    
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)

    date_frame = f"""DATE REFERENCE — USE THIS FOR ALL DATE RESOLUTION:
TODAY: {day_names[today.weekday()]}, {today.strftime('%B %d, %Y')}
YESTERDAY: {day_names[yesterday.weekday()]}, {yesterday.strftime('%B %d, %Y')}
TOMORROW: {day_names[tomorrow.weekday()]}, {tomorrow.strftime('%B %d, %Y')}
Current time: {now.strftime('%-I:%M %p')}

REST OF THIS WEEK:
{chr(10).join(this_week) if this_week else '  (end of week)'}

NEXT WEEK:
{chr(10).join(next_week)}

THIS WEEKEND: {this_sat.strftime('%B %d')} - {this_sun.strftime('%B %d, %Y')}

RULES FOR DATES:
- "Thursday" with no qualifier = the NEXT upcoming Thursday = {(today + timedelta(days=(3 - today.weekday()) % 7 or 7)).strftime('%B %d, %Y') if today.weekday() != 3 else today.strftime('%B %d, %Y')}
- "next Thursday" = Thursday of NEXT week
- "this weekend" = {this_sat.strftime('%B %d')} - {this_sun.strftime('%B %d')}
- "today", "tonight" = {today.strftime('%B %d, %Y')}
- "tomorrow" = {tomorrow.strftime('%B %d, %Y')}
- "yesterday" = {yesterday.strftime('%B %d, %Y')}
- ALWAYS output dates as YYYY-MM-DD format
- If you CANNOT determine the exact date, set date to null"""

    return f"""You are a message extraction engine for the Mythos life management system.
Your job: analyze the user's message and extract ANY actionable structured data.

{date_frame}

REFERENCE DATA:
{knowledge_map}

CURRENT STATE:
{dynamic_context}

INSTRUCTIONS:
Analyze the message and return ONLY a JSON object. No explanation, no markdown, no backticks.

Extract any of the following if present. Omit keys that don't apply:

{{
    "bill_paid": {{
        "bill_name": "merchant name from recurring_bills",
        "amount": null or number,
        "account": "account abbreviation if mentioned"
    }},
    "money_spent": {{
        "amount": number,
        "merchant": "store/vendor name",
        "category": "best guess category",
        "account": "account abbreviation if mentioned"
    }},
    "calendar_event": {{
        "action": "create|update|delete",
        "event_id": null or number,
        "title": "event description",
        "date": "YYYY-MM-DD",
        "time": "HH:MM" or null,
        "person": "adge|rebecca|fitz|family",
        "location": "place or null"
    }},
    "task_completed": {{
        "task_id": "UUID if identifiable from open tasks",
        "task_name": "description of completed task"
    }},
    "task_added": {{
        "title": "new task description",
        "priority": "high|medium|low",
        "due_date": "YYYY-MM-DD or null"
    }},
    "routine_done": {{
        "routine_id": number,
        "routine_name": "routine title"
    }},
    "life_event": {{
        "description": "what happened",
        "domain": "personal|health|finance|household|work|spiritual",
        "person": "adge|rebecca|fitz|family",
        "mood": "emotional state if expressed"
    }},
    "balance_update": {{
        "account": "account abbreviation",
        "new_balance": number
    }}
}}

CALENDAR TITLE FORMATTING:
- Format titles as the EVENT, not "event with [person]"
- WRONG: "doctor appointment with Rebecca", "Rebecca's dentist appointment"
- RIGHT: "Doctor Appointment", "Dentist - Dr. Nolan"
- The person field handles WHO it's for. Don't put the person's name in the title.
- Capitalize the title properly.

CALENDAR RULES:
- If the user mentions a NEW event, use action: "create"
- If the user says to CHANGE/MOVE/UPDATE an existing event, use action: "update" with the event_id from UPCOMING CALENDAR EVENTS above
- If the user says to CANCEL/REMOVE/DELETE an event, use action: "delete" with the event_id
- If an event sounds similar to an existing one (same person + similar title), prefer "update" over "create"
- When correcting a date/time ("no, it's Monday not Friday"), use "update" with the correct date/time

If NOTHING actionable is found, return: {{"no_action": true}}

Remember: return ONLY valid JSON. No text before or after."""


def extract(message: str) -> Dict[str, Any]:
    """
    Run the extractor on an incoming message.
    Returns a dict of extracted actions, or {"no_action": true}.
    """
    try:
        client = Client(host=OLLAMA_HOST)
        prompt = _build_extractor_prompt()

        response = client.chat(
            model=EXTRACTOR_MODEL,
            messages=[
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': message}
            ],
            options={
                'temperature': 0.1,  # Low temp for structured extraction
                'num_predict': 512,
            }
        )

        raw = response['message']['content'].strip()

        # Clean up common model output issues
        # Remove markdown code fences if present
        if raw.startswith('```'):
            raw = raw.split('\n', 1)[1] if '\n' in raw else raw[3:]
        if raw.endswith('```'):
            raw = raw[:-3]
        if raw.startswith('json'):
            raw = raw[4:]
        raw = raw.strip()

        parsed = json.loads(raw)
        parsed = _validate_extracted_date(parsed, message)
        logger.info(f"Extractor result: {json.dumps(parsed, default=str)[:200]}")
        return parsed

    except json.JSONDecodeError as e:
        logger.warning(f"Extractor JSON parse failed: {e}, raw: {raw[:200]}")
        return {"no_action": True, "parse_error": str(e)}
    except Exception as e:
        logger.error(f"Extractor failed: {e}", exc_info=True)
        return {"no_action": True, "error": str(e)}


def format_extraction_for_context(extraction: Dict) -> str:
    """
    Format the extraction result as a context block to inject
    into the main model's message. This tells Iris what was
    detected so she can respond appropriately.
    """
    if extraction.get('no_action'):
        return ""

    parts = []

    if 'bill_paid' in extraction:
        b = extraction['bill_paid']
        amt = f" (${b['amount']})" if b.get('amount') else ""
        parts.append(f"[DETECTED: Bill payment — {b.get('bill_name', 'unknown')}{amt}]")

    if 'money_spent' in extraction:
        m = extraction['money_spent']
        parts.append(f"[DETECTED: Spending — ${m.get('amount', '?')} at {m.get('merchant', 'unknown')}]")

    if 'calendar_event' in extraction:
        c = extraction['calendar_event']
        action = c.get('action', 'create')
        time_str = f" at {c['time']}" if c.get('time') else ""
        cal_date = c.get('date', '')
        if action == 'delete':
            parts.append(f"[DETECTED: Calendar delete — {c.get('title', 'event')}]")
        elif action == 'update':
            parts.append(f"[DETECTED: Calendar update — {c.get('title', 'event')} → {cal_date}{time_str}]")
        else:
            parts.append(f"[DETECTED: Calendar event — {c.get('title', 'event')} on {cal_date}{time_str} for {c.get('person', 'adge')}]")
        # Get the day view for the affected date
        if cal_date:
            try:
                from datetime import date as date_type
                from calendar_formatter import format_day_view
                affected_date = date_type.fromisoformat(cal_date)
                day_view = format_day_view(affected_date)
                # Strip HTML tags for the model context
                import re
                clean_view = re.sub(r'<[^>]+>', '', day_view)
                parts.append(f"[CALENDAR FOR THAT DAY:\n{clean_view}]")
                parts.append("Include the calendar view for that day in your response, using the box-drawing format shown above.")
            except Exception:
                pass

    if 'task_completed' in extraction:
        t = extraction['task_completed']
        parts.append(f"[DETECTED: Task completed — {t.get('task_name', 'unknown')}]")

    if 'task_added' in extraction:
        t = extraction['task_added']
        parts.append(f"[DETECTED: New task — {t.get('title', 'unknown')}]")

    if 'routine_done' in extraction:
        r = extraction['routine_done']
        parts.append(f"[DETECTED: Routine completed — {r.get('routine_name', 'unknown')}]")

    if 'life_event' in extraction:
        e = extraction['life_event']
        parts.append(f"[DETECTED: Life event — {e.get('description', 'unknown')} (domain: {e.get('domain', 'personal')})]")

    if 'balance_update' in extraction:
        b = extraction['balance_update']
        parts.append(f"[DETECTED: Balance update — {b.get('account', '?')} = ${b.get('new_balance', '?')}]")

    if not parts:
        return ""

    return "\n".join(parts) + "\nAcknowledge these naturally in your response. If a bill was paid or task completed, confirm it. Don't just echo the detection tags."


if __name__ == "__main__":
    """Test the extractor with sample messages."""
    test_messages = [
        "just paid the electric bill",
        "spent $45 at Tractor Supply on chicken feed",
        "Rebecca has a dentist appointment Thursday at 2pm",
        "feeling really stressed about money today",
        "hey what's up",
        "I finished the dishes and the laundry",
        "Fitz has a snow day tomorrow",
        "USAA balance is $2,800",
    ]

    for msg in test_messages:
        print(f"\n{'='*50}")
        print(f"MESSAGE: {msg}")
        result = extract(msg)
        print(f"EXTRACTED: {json.dumps(result, indent=2, default=str)}")
        context = format_extraction_for_context(result)
        if context:
            print(f"CONTEXT: {context}")
