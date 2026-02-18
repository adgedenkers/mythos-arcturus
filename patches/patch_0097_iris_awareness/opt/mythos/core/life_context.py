#!/usr/bin/env python3
"""
Life Context Builder
====================
Assembles Ka'tuar'el's current life state into a compact context block
for injection into Iris's system prompt.

This is what makes Iris aware of:
- What day/time it is (precisely)
- What routines are due and what's been done
- Open tasks and overdue items
- Financial pulse (balances, bills due soon)
- Calendar events today
- Last checkin info

The output is a concise text block appended to the system prompt.
It must be TIGHT — local models have limited context windows.
Target: under 500 tokens for the life context block.
"""

import os
import logging
from datetime import date, datetime, time, timedelta
from decimal import Decimal

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

logger = logging.getLogger(__name__)


def _get_conn():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', '/var/run/postgresql'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor,
    )


def build_life_context() -> str:
    """
    Build a compact life-state context block for Iris.
    Returns a string to append to the system prompt.
    """
    try:
        conn = _get_conn()
        cur = conn.cursor()
        now = datetime.now()
        today = date.today()
        dow = today.weekday()
        dom = today.day

        sections = []

        # === DATE/TIME (Iris must always know exactly when it is) ===
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        time_str = now.strftime('%-I:%M %p')
        date_str = f"{day_names[dow]}, {now.strftime('%B')} {dom}, {now.year}"
        sections.append(f"RIGHT NOW: {date_str} at {time_str} EST.")

        # === TODAY'S ROUTINES ===
        cur.execute("""
            SELECT r.title, r.domain, r.time_due,
                   rc.status as completion_status
            FROM routines r
            LEFT JOIN routine_completions rc
                ON rc.routine_id = r.id AND rc.due_date = %s
            WHERE r.is_active = true AND r.auto_create = true
              AND (
                  r.frequency = 'daily'
                  OR (r.frequency = 'weekdays' AND %s < 5)
                  OR (r.frequency = 'weekends' AND %s >= 5)
                  OR (r.frequency = 'weekly' AND r.day_of_week = %s)
                  OR (r.frequency = 'monthly' AND r.day_of_month = %s)
              )
            ORDER BY r.sort_order
        """, (today, dow, dow, dow, dom))
        routines = cur.fetchall()

        if routines:
            done = [r for r in routines if r['completion_status'] == 'done']
            pending = [r for r in routines if r['completion_status'] != 'done']

            routine_parts = []
            if pending:
                names = ", ".join(r['title'] for r in pending)
                routine_parts.append(f"Still to do: {names}")
            if done:
                names = ", ".join(r['title'] for r in done)
                routine_parts.append(f"Done: {names}")
            sections.append(f"ROUTINES ({len(done)}/{len(routines)} complete): {'. '.join(routine_parts)}.")

        # === OVERDUE ROUTINES (past days) ===
        cur.execute("""
            SELECT r.title, rc.due_date
            FROM routines r
            JOIN routine_completions rc ON rc.routine_id = r.id
            WHERE r.is_active = true
              AND rc.due_date >= %s AND rc.due_date < %s
              AND rc.status = 'pending'
            ORDER BY rc.due_date DESC
            LIMIT 5
        """, (today - timedelta(days=7), today))
        overdue = cur.fetchall()
        if overdue:
            names = ", ".join(f"{o['title']} ({o['due_date']})" for o in overdue)
            sections.append(f"OVERDUE: {names}.")

        # === OPEN TASKS ===
        cur.execute("""
            SELECT idea, priority
            FROM idea_backlog
            WHERE (domain = 'task' OR idea_type = 'task')
              AND status IN ('open', 'in_progress')
              AND is_archived = false
            ORDER BY
                CASE priority WHEN 'critical' THEN 0 WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2 WHEN 'low' THEN 3 END
            LIMIT 5
        """)
        tasks = cur.fetchall()
        if tasks:
            names = ", ".join(t['idea'] for t in tasks)
            sections.append(f"OPEN TASKS ({len(tasks)}): {names}.")

        # === CALENDAR EVENTS TODAY ===
        cur.execute("""
            SELECT title, start_time, person
            FROM calendar_events
            WHERE event_date = %s AND is_active = true
            ORDER BY start_time NULLS LAST
        """, (today,))
        events = cur.fetchall()
        if events:
            parts = []
            for e in events:
                t = ""
                if e['start_time']:
                    if hasattr(e['start_time'], 'strftime'):
                        t = e['start_time'].strftime('%-I:%M %p') + " "
                    else:
                        t = str(e['start_time']) + " "
                person = f" ({e['person']})" if e.get('person') and e['person'] != 'adge' else ""
                parts.append(f"{t}{e['title']}{person}")
            sections.append(f"CALENDAR TODAY: {'; '.join(parts)}.")

        # === FINANCIAL PULSE ===
        cur.execute("""
            SELECT abbreviation, current_balance
            FROM accounts
            WHERE is_active = true AND abbreviation IN ('USAA', 'SUN')
        """)
        balances = cur.fetchall()
        if balances:
            bal_parts = [f"{b['abbreviation']}: ${float(b['current_balance']):,.2f}" for b in balances]
            sections.append(f"BALANCES: {', '.join(bal_parts)}.")

        # Bills due in next 5 days
        month_str = today.strftime('%Y-%m')
        cur.execute("""
            SELECT rb.merchant_name, rb.expected_amount, rb.expected_day
            FROM recurring_bills rb
            LEFT JOIN bill_overrides bo ON bo.bill_id = rb.id AND bo.month = %s
            WHERE rb.is_active = true
              AND rb.expected_day IS NOT NULL
              AND rb.expected_day >= %s AND rb.expected_day <= %s
              AND (bo.is_paid IS NULL OR bo.is_paid = false)
            ORDER BY rb.expected_day
            LIMIT 5
        """, (month_str, dom, dom + 5))
        bills = cur.fetchall()
        if bills:
            bill_parts = [f"{b['merchant_name']} ${float(b['expected_amount'] or 0):,.0f} (day {b['expected_day']})" for b in bills]
            sections.append(f"BILLS DUE SOON: {', '.join(bill_parts)}.")

        # === LAST CHECKIN ===
        cur.execute("""
            SELECT checkin_date, checkin_time, checkin_type
            FROM checkin_log
            ORDER BY checkin_time DESC LIMIT 1
        """)
        last = cur.fetchone()
        if last:
            if last['checkin_date'] == today:
                t = last['checkin_time']
                if hasattr(t, 'strftime'):
                    sections.append(f"Last checkin: today at {t.strftime('%-I:%M %p')}.")
                else:
                    sections.append(f"Last checkin: today.")
            else:
                days_ago = (today - last['checkin_date']).days
                if days_ago == 1:
                    sections.append("Last checkin: yesterday.")
                else:
                    sections.append(f"Last checkin: {days_ago} days ago. He hasn't checked in recently — note this.")
        else:
            sections.append("No checkin recorded yet. This is new.")

        cur.close()
        conn.close()

        # Assemble
        context = "\n\nLIFE STATE — Ka'tuar'el's current situation (use naturally, don't recite):\n"
        context += "\n".join(sections)
        context += "\n\nUse this awareness naturally. If he asks 'what do I have today,' you know. If he seems stressed, you know what's on his plate. If routines aren't done, you can gently note it. Don't dump all this information — let it inform how you respond."

        return context

    except Exception as e:
        logger.error(f"Life context build failed: {e}", exc_info=True)
        return ""


if __name__ == "__main__":
    print(build_life_context())
