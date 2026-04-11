#!/usr/bin/env python3
"""
Action Executor
===============
Takes the structured output from the message extractor
and commits actions to the database.

bill_paid → bill_overrides
money_spent → life_events
calendar_event → calendar_events
task_completed → idea_backlog (status=done)
task_added → idea_backlog (new task)
routine_done → routine_completions
life_event → life_events
balance_update → accounts
"""

import os
import logging
from datetime import date, datetime
from typing import Dict, Any, List

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


def execute_actions(extraction: Dict[str, Any]) -> List[str]:
    """
    Execute all extracted actions against the database.
    Returns a list of action summaries for logging.
    """
    if extraction.get('no_action'):
        return []

    conn = _get_conn()
    results = []

    try:
        if 'bill_paid' in extraction:
            r = _execute_bill_paid(conn, extraction['bill_paid'])
            if r:
                results.append(r)

        if 'money_spent' in extraction:
            r = _execute_life_event(conn, {
                'description': f"Spent ${extraction['money_spent'].get('amount', '?')} at {extraction['money_spent'].get('merchant', 'unknown')}",
                'domain': 'finance',
                'person': 'adge',
            })
            if r:
                results.append(r)

        if 'calendar_event' in extraction:
            cal = extraction['calendar_event']
            action = cal.get('action', 'create')
            if action == 'delete':
                r = _execute_calendar_delete(conn, cal)
            elif action == 'update':
                r = _execute_calendar_update(conn, cal)
            else:
                r = _execute_calendar_create(conn, cal)
            if r:
                results.append(r)

        if 'task_completed' in extraction:
            r = _execute_task_completed(conn, extraction['task_completed'])
            if r:
                results.append(r)

        if 'task_added' in extraction:
            r = _execute_task_added(conn, extraction['task_added'])
            if r:
                results.append(r)

        if 'routine_done' in extraction:
            r = _execute_routine_done(conn, extraction['routine_done'])
            if r:
                results.append(r)

        if 'life_event' in extraction:
            r = _execute_life_event(conn, extraction['life_event'])
            if r:
                results.append(r)

        if 'balance_update' in extraction:
            r = _execute_balance_update(conn, extraction['balance_update'])
            if r:
                results.append(r)

        conn.commit()

    except Exception as e:
        logger.error(f"Action execution failed: {e}", exc_info=True)
        conn.rollback()
    finally:
        conn.close()

    return results


def _execute_bill_paid(conn, data: Dict) -> str:
    """Mark a bill as paid in bill_overrides."""
    cur = conn.cursor()
    bill_name = data.get('bill_name', '')
    today = date.today()
    month_str = today.strftime('%Y-%m')

    # Find the bill by matching merchant_name
    cur.execute("""
        SELECT id, merchant_name FROM recurring_bills
        WHERE is_active = true
          AND LOWER(merchant_name) LIKE LOWER(%s)
        LIMIT 1
    """, (f'%{bill_name}%',))
    bill = cur.fetchone()

    if not bill:
        logger.warning(f"Bill not found for '{bill_name}'")
        return None

    # Insert/update override
    paid_amount = data.get('amount')
    cur.execute("""
        INSERT INTO bill_overrides (bill_id, month, is_paid, paid_amount, paid_date)
        VALUES (%s, %s, true, %s, %s)
        ON CONFLICT (bill_id, month)
        DO UPDATE SET is_paid = true, paid_amount = COALESCE(%s, bill_overrides.paid_amount),
                      paid_date = %s, updated_at = NOW()
    """, (bill['id'], month_str, paid_amount, today, paid_amount, today))

    logger.info(f"Bill marked paid: {bill['merchant_name']} for {month_str}")
    return f"Bill paid: {bill['merchant_name']}"


def _execute_calendar_create(conn, data: Dict) -> str:
    """Create a new calendar event, with dedup check."""
    cur = conn.cursor()

    event_date = data.get('date')
    if not event_date:
        return None

    # Parse date first for dedup check
    if isinstance(event_date, str):
        try:
            event_date = datetime.strptime(event_date, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Bad date format: {event_date}")
            return None

    # DEDUP: check if a very similar event already exists
    person = data.get('person', 'adge')
    title = data.get('title', '')
    cur.execute("""
        SELECT id, title, event_date, start_time FROM calendar_events
        WHERE is_active = true
          AND person = %s
          AND event_date = %s
          AND (LOWER(title) LIKE LOWER(%s) OR LOWER(%s) LIKE LOWER(CONCAT('%%', title, '%%')))
        LIMIT 1
    """, (person, event_date, f'%{title[:20]}%', title))
    existing = cur.fetchone()

    if existing:
        # Update existing instead of creating duplicate
        logger.info(f"Dedup: found existing event {existing['id']}, updating instead of creating")
        data['event_id'] = existing['id']
        return _execute_calendar_update(conn, data)

    start_time = data.get('time')
    if start_time and isinstance(start_time, str):
        try:
            start_time = datetime.strptime(start_time, '%H:%M').time()
        except ValueError:
            start_time = None

    cur.execute("""
        INSERT INTO calendar_events (title, event_date, start_time, person, location, source)
        VALUES (%s, %s, %s, %s, %s, 'iris')
        RETURNING id
    """, (
        data.get('title', 'Untitled event'),
        event_date,
        start_time,
        data.get('person', 'adge'),
        data.get('location'),
    ))

    event_id = cur.fetchone()['id']
    logger.info(f"Calendar event created: {data.get('title')} on {event_date} (id:{event_id})")
    return f"Calendar: {data.get('title')} on {event_date}"



def _execute_calendar_update(conn, data: Dict) -> str:
    """Update an existing calendar event."""
    cur = conn.cursor()
    event_id = data.get('event_id')

    if not event_id:
        # Try to find by title + person match
        title = data.get('title', '')
        person = data.get('person', 'adge')
        cur.execute("""
            SELECT id FROM calendar_events
            WHERE is_active = true AND person = %s
              AND (LOWER(title) LIKE LOWER(%s) OR LOWER(%s) LIKE LOWER(CONCAT('%%', title, '%%')))
            ORDER BY event_date DESC LIMIT 1
        """, (person, f'%{title[:20]}%', title))
        match = cur.fetchone()
        if match:
            event_id = match['id']
        else:
            logger.warning(f"Calendar update: no matching event found for '{title}'")
            return None

    # Build update fields
    updates = []
    params = []

    if data.get('title'):
        updates.append("title = %s")
        params.append(data['title'])
    if data.get('date'):
        event_date = data['date']
        if isinstance(event_date, str):
            try:
                event_date = datetime.strptime(event_date, '%Y-%m-%d').date()
            except ValueError:
                event_date = None
        if event_date:
            updates.append("event_date = %s")
            params.append(event_date)
    if data.get('time'):
        event_time = data['time']
        if isinstance(event_time, str):
            try:
                event_time = datetime.strptime(event_time, '%H:%M').time()
            except ValueError:
                event_time = None
        if event_time:
            updates.append("start_time = %s")
            params.append(event_time)
    if data.get('location'):
        updates.append("location = %s")
        params.append(data['location'])

    if not updates:
        return None

    updates.append("updated_at = NOW()")
    params.append(event_id)

    cur.execute(f"""
        UPDATE calendar_events SET {', '.join(updates)}
        WHERE id = %s
        RETURNING id, title, event_date
    """, params)

    result = cur.fetchone()
    if result:
        logger.info(f"Calendar updated: {result['title']} on {result['event_date']} (id:{result['id']})")
        return f"Calendar updated: {result['title']} → {result['event_date']}"
    return None


def _execute_calendar_delete(conn, data: Dict) -> str:
    """Delete (deactivate) a calendar event."""
    cur = conn.cursor()
    event_id = data.get('event_id')

    if not event_id:
        # Try to find by title + person match
        title = data.get('title', '')
        person = data.get('person', 'adge')
        cur.execute("""
            SELECT id, title FROM calendar_events
            WHERE is_active = true AND person = %s
              AND (LOWER(title) LIKE LOWER(%s) OR LOWER(%s) LIKE LOWER(CONCAT('%%', title, '%%')))
            ORDER BY event_date DESC LIMIT 1
        """, (person, f'%{title[:20]}%', title))
        match = cur.fetchone()
        if match:
            event_id = match['id']
        else:
            logger.warning(f"Calendar delete: no matching event found for '{title}'")
            return None

    cur.execute("""
        UPDATE calendar_events SET is_active = false, updated_at = NOW()
        WHERE id = %s
        RETURNING id, title
    """, (event_id,))

    result = cur.fetchone()
    if result:
        logger.info(f"Calendar deleted: {result['title']} (id:{result['id']})")
        return f"Calendar removed: {result['title']}"
    return None


def _execute_task_completed(conn, data: Dict) -> str:
    """Mark a task as done in idea_backlog."""
    cur = conn.cursor()

    task_id = data.get('task_id')
    task_name = data.get('task_name', '')

    if task_id:
        cur.execute("""
            UPDATE idea_backlog SET status = 'done', completed_at = NOW(), last_updated = NOW()
            WHERE id = %s AND status IN ('open', 'in_progress')
            RETURNING idea
        """, (task_id,))
    else:
        # Try to match by name
        cur.execute("""
            UPDATE idea_backlog SET status = 'done', completed_at = NOW(), last_updated = NOW()
            WHERE LOWER(idea) LIKE LOWER(%s)
              AND status IN ('open', 'in_progress')
            RETURNING idea
        """, (f'%{task_name}%',))

    result = cur.fetchone()
    if result:
        logger.info(f"Task completed: {result['idea']}")
        return f"Task done: {result['idea']}"
    return None


def _execute_task_added(conn, data: Dict) -> str:
    """Add a new task to idea_backlog."""
    cur = conn.cursor()

    title = data.get('title', '')
    if not title:
        return None

    priority = data.get('priority', 'medium')
    due_date = data.get('due_date')

    if due_date and isinstance(due_date, str):
        try:
            due_date = datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            due_date = None

    cur.execute("""
        INSERT INTO idea_backlog (idea, priority, status, domain, idea_type, next_review)
        VALUES (%s, %s, 'open', 'task', 'task', %s)
        RETURNING id
    """, (title, priority, due_date))

    result = cur.fetchone()
    logger.info(f"Task added: {title} (id:{result['id']})")
    return f"Task added: {title}"


def _execute_routine_done(conn, data: Dict) -> str:
    """Mark a routine as complete for today."""
    cur = conn.cursor()
    today = date.today()

    routine_id = data.get('routine_id')
    routine_name = data.get('routine_name', '')

    if not routine_id and routine_name:
        # Find by name
        cur.execute("""
            SELECT id, title FROM routines
            WHERE is_active = true AND LOWER(title) LIKE LOWER(%s)
            LIMIT 1
        """, (f'%{routine_name}%',))
        routine = cur.fetchone()
        if routine:
            routine_id = routine['id']
            routine_name = routine['title']

    if not routine_id:
        return None

    cur.execute("""
        INSERT INTO routine_completions (routine_id, due_date, status, completed_at, completed_by)
        VALUES (%s, %s, 'done', NOW(), 'iris')
        ON CONFLICT (routine_id, due_date)
        DO UPDATE SET status = 'done', completed_at = NOW()
    """, (routine_id, today))

    logger.info(f"Routine completed via conversation: {routine_name}")
    return f"Routine done: {routine_name}"


def _execute_life_event(conn, data: Dict) -> str:
    """Log a life event."""
    cur = conn.cursor()

    # Ensure life_events table exists (created by migration)
    cur.execute("""
        INSERT INTO life_events (description, domain, person, mood, created_at)
        VALUES (%s, %s, %s, %s, NOW())
        RETURNING id
    """, (
        data.get('description', ''),
        data.get('domain', 'personal'),
        data.get('person', 'adge'),
        data.get('mood'),
    ))

    result = cur.fetchone()
    logger.info(f"Life event logged: {data.get('description', '')[:50]} (id:{result['id']})")
    return f"Logged: {data.get('description', '')[:50]}"


def _execute_balance_update(conn, data: Dict) -> str:
    """Update an account balance."""
    cur = conn.cursor()
    abbr = data.get('account', '')
    amount = data.get('new_balance')

    if not abbr or amount is None:
        return None

    cur.execute("""
        UPDATE accounts SET current_balance = %s, balance_updated_at = NOW()
        WHERE LOWER(abbreviation) = LOWER(%s)
        RETURNING account_name, abbreviation
    """, (amount, abbr))

    result = cur.fetchone()
    if result:
        logger.info(f"Balance updated: {result['abbreviation']} = ${amount}")
        return f"Balance: {result['abbreviation']} → ${amount:,.2f}"
    return None
