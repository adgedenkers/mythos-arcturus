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

        # Open tasks
        cur.execute("""
            SELECT id, idea FROM idea_backlog
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

    return f"""You are a message extraction engine for the Mythos life management system.
Your job: analyze the user's message and extract ANY actionable structured data.

Current date: {today.strftime('%A, %B %d, %Y')} at {now.strftime('%-I:%M %p')}

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
        time_str = f" at {c['time']}" if c.get('time') else ""
        parts.append(f"[DETECTED: Calendar event — {c.get('title', 'event')} on {c.get('date', '?')}{time_str} for {c.get('person', 'adge')}]")

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
