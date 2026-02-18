#!/usr/bin/env python3
"""
Routines Engine
===============
Core logic for the recurring routines system.
Spawns daily task instances, tracks completions,
and assembles the daily briefing for Iris checkin.

This is the backbone of Iris as life operating system.
"""

import os
import logging
from datetime import date, datetime, time, timedelta
from decimal import Decimal

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


def _is_nth_weekday(target_date, day_of_week, week_of_month):
    """
    Check if target_date is the Nth occurrence of a weekday in its month.
    day_of_week: 0=Mon..6=Sun
    week_of_month: 1-5 for 1st-5th, -1 for last
    """
    if target_date.weekday() != day_of_week:
        return False
    
    if week_of_month == -1:
        # Last occurrence: check if adding 7 days would leave the month
        next_week = target_date + timedelta(days=7)
        return next_week.month != target_date.month
    else:
        # Nth occurrence: which occurrence of this weekday is this date?
        day = target_date.day
        occurrence = (day - 1) // 7 + 1
        return occurrence == week_of_month


def get_db_connection():
    from dotenv import load_dotenv
    load_dotenv('/opt/mythos/.env')
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', '/var/run/postgresql'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor,
    )


def get_routines_due_today(conn=None):
    """
    Get all routines that are due today based on their frequency.
    Returns routines with their completion status for today.
    """
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    try:
        cur = conn.cursor()
        today = date.today()
        dow = today.weekday()  # 0=Mon..6=Sun
        dom = today.day
        is_weekend = dow >= 5

        week_num = (today.day - 1) // 7 + 1
        # Check if this is the last occurrence of this weekday
        next_week = today + timedelta(days=7)
        is_last = next_week.month != today.month

        cur.execute("""
            SELECT r.*,
                   rc.status as completion_status,
                   rc.completed_at,
                   rc.notes as completion_notes
            FROM routines r
            LEFT JOIN routine_completions rc 
                ON rc.routine_id = r.id AND rc.due_date = %s
            WHERE r.is_active = true
              AND r.auto_create = true
              AND (
                  r.frequency = 'daily'
                  OR (r.frequency = 'weekdays' AND %s < 5)
                  OR (r.frequency = 'weekends' AND %s >= 5)
                  OR (r.frequency = 'weekly' AND r.day_of_week = %s)
                  OR (r.frequency = 'monthly' AND r.day_of_month IS NOT NULL AND r.day_of_month = %s)
                  OR (r.frequency = 'monthly' AND r.week_of_month IS NOT NULL AND r.day_of_week = %s 
                      AND (r.week_of_month = %s OR (r.week_of_month = -1 AND %s = true)))
              )
            ORDER BY r.sort_order, r.time_due NULLS LAST
        """, (today, dow, dow, dow, dom, dow, week_num, is_last))

        routines = cur.fetchall()
        return routines
    finally:
        if close_conn:
            conn.close()


def get_overdue_routines(conn=None):
    """
    Get routines from previous days that were never completed.
    Only looks back 7 days to avoid noise.
    """
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    try:
        cur = conn.cursor()
        today = date.today()
        week_ago = today - timedelta(days=7)

        # Find routines that should have had completions but don't
        # This is approximate — checks daily routines for the past week
        cur.execute("""
            SELECT r.id, r.title, r.domain, r.priority, r.frequency,
                   rc.due_date, rc.status
            FROM routines r
            JOIN routine_completions rc ON rc.routine_id = r.id
            WHERE r.is_active = true
              AND rc.due_date >= %s
              AND rc.due_date < %s
              AND rc.status = 'pending'
            ORDER BY rc.due_date DESC, r.sort_order
        """, (week_ago, today))

        return cur.fetchall()
    finally:
        if close_conn:
            conn.close()


def ensure_today_instances(conn=None):
    """
    Create completion records for today's routines if they don't exist yet.
    Called at checkin time or by a cron/service.
    """
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    try:
        cur = conn.cursor()
        today = date.today()
        dow = today.weekday()
        dom = today.day
        week_num = (today.day - 1) // 7 + 1
        next_week = today + timedelta(days=7)
        is_last = next_week.month != today.month

        # Get all routines due today that don't have a completion record yet
        cur.execute("""
            INSERT INTO routine_completions (routine_id, due_date, status)
            SELECT r.id, %s, 'pending'
            FROM routines r
            WHERE r.is_active = true
              AND r.auto_create = true
              AND (
                  r.frequency = 'daily'
                  OR (r.frequency = 'weekdays' AND %s < 5)
                  OR (r.frequency = 'weekends' AND %s >= 5)
                  OR (r.frequency = 'weekly' AND r.day_of_week = %s)
                  OR (r.frequency = 'monthly' AND r.day_of_month IS NOT NULL AND r.day_of_month = %s)
                  OR (r.frequency = 'monthly' AND r.week_of_month IS NOT NULL AND r.day_of_week = %s 
                      AND (r.week_of_month = %s OR (r.week_of_month = -1 AND %s = true)))
              )
            ON CONFLICT (routine_id, due_date) DO NOTHING
            RETURNING routine_id
        """, (today, dow, dow, dow, dom, dow, week_num, is_last))

        created = cur.fetchall()
        conn.commit()

        if created:
            logger.info(f"Created {len(created)} routine instances for {today}")
        return len(created)
    finally:
        if close_conn:
            conn.close()


def complete_routine(routine_id, notes=None, completed_by='adge', conn=None):
    """Mark a routine as done for today."""
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    try:
        cur = conn.cursor()
        today = date.today()

        # Ensure the instance exists
        cur.execute("""
            INSERT INTO routine_completions (routine_id, due_date, status)
            VALUES (%s, %s, 'pending')
            ON CONFLICT (routine_id, due_date) DO NOTHING
        """, (routine_id, today))

        # Mark as done
        cur.execute("""
            UPDATE routine_completions
            SET status = 'done', completed_at = NOW(), completed_by = %s, notes = %s
            WHERE routine_id = %s AND due_date = %s
            RETURNING id
        """, (completed_by, notes, routine_id, today))

        result = cur.fetchone()
        conn.commit()

        # Get the routine title for confirmation
        cur.execute("SELECT title FROM routines WHERE id = %s", (routine_id,))
        routine = cur.fetchone()

        return routine['title'] if routine else None
    finally:
        if close_conn:
            conn.close()


def skip_routine(routine_id, reason=None, conn=None):
    """Mark a routine as skipped for today."""
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    try:
        cur = conn.cursor()
        today = date.today()

        cur.execute("""
            INSERT INTO routine_completions (routine_id, due_date, status, notes)
            VALUES (%s, %s, 'skipped', %s)
            ON CONFLICT (routine_id, due_date) 
            DO UPDATE SET status = 'skipped', notes = %s, completed_at = NOW()
        """, (routine_id, today, reason, reason))

        conn.commit()
        return True
    finally:
        if close_conn:
            conn.close()


def get_open_tasks(conn=None, limit=10):
    """Get open one-off tasks from idea_backlog."""
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, idea, priority, status, next_review, created_at
            FROM idea_backlog
            WHERE (domain = 'task' OR idea_type = 'task')
              AND status IN ('open', 'in_progress')
              AND is_archived = false
            ORDER BY
                CASE WHEN next_review IS NOT NULL AND next_review < NOW() THEN 0 ELSE 1 END,
                CASE priority
                    WHEN 'critical' THEN 0
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                END,
                created_at ASC
            LIMIT %s
        """, (limit,))
        return cur.fetchall()
    finally:
        if close_conn:
            conn.close()


def get_upcoming_bills(conn=None, days_ahead=7):
    """Get bills due in the next N days with payment status."""
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    try:
        cur = conn.cursor()
        today = date.today()
        target_day = today.day + days_ahead
        month_str = today.strftime('%Y-%m')

        cur.execute("""
            SELECT rb.id, rb.merchant_name, rb.expected_amount,
                   rb.expected_day, rb.category_primary,
                   a.abbreviation as account_abbr,
                   bo.is_paid as override_paid
            FROM recurring_bills rb
            LEFT JOIN accounts a ON rb.account_id = a.id
            LEFT JOIN bill_overrides bo ON bo.bill_id = rb.id AND bo.month = %s
            WHERE rb.is_active = true
              AND rb.expected_day IS NOT NULL
              AND rb.expected_day >= %s
              AND rb.expected_day <= %s
            ORDER BY rb.expected_day
        """, (month_str, today.day, target_day))

        return cur.fetchall()
    finally:
        if close_conn:
            conn.close()


def get_calendar_events_today(conn=None):
    """Get today's calendar events."""
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    try:
        cur = conn.cursor()
        today = date.today()

        cur.execute("""
            SELECT id, title, description, start_time, end_time,
                   location, person
            FROM calendar_events
            WHERE event_date = %s AND is_active = true
            ORDER BY start_time NULLS LAST
        """, (today,))

        return cur.fetchall()
    finally:
        if close_conn:
            conn.close()


def get_account_balances_summary(conn=None):
    """Quick balance summary for checkin."""
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT abbreviation, current_balance, account_type
            FROM accounts
            WHERE is_active = true AND abbreviation IN ('USAA', 'SUN')
            ORDER BY id
        """)
        return cur.fetchall()
    finally:
        if close_conn:
            conn.close()


def get_last_checkin(conn=None):
    """Get the most recent checkin."""
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT checkin_date, checkin_time, checkin_type
            FROM checkin_log
            ORDER BY checkin_time DESC
            LIMIT 1
        """)
        return cur.fetchone()
    finally:
        if close_conn:
            conn.close()


def log_checkin(checkin_type='morning', summary=None, conn=None):
    """Record a checkin."""
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    try:
        cur = conn.cursor()
        today = date.today()

        cur.execute("""
            INSERT INTO checkin_log (checkin_date, checkin_type, summary)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (today, checkin_type, summary))

        conn.commit()
        result = cur.fetchone()
        return result['id']
    finally:
        if close_conn:
            conn.close()


def generate_daily_briefing():
    """
    Assemble the complete daily briefing.
    This is what Iris uses when you say good morning.
    """
    conn = get_db_connection()

    try:
        now = datetime.now()
        today = date.today()

        # Ensure today's routine instances exist
        ensure_today_instances(conn)

        # Gather everything
        routines = get_routines_due_today(conn)
        overdue = get_overdue_routines(conn)
        tasks = get_open_tasks(conn)
        bills = get_upcoming_bills(conn, days_ahead=7)
        events = get_calendar_events_today(conn)
        balances = get_account_balances_summary(conn)
        last_checkin = get_last_checkin(conn)

        # Log this checkin
        if now.hour < 12:
            checkin_type = 'morning'
        elif now.hour < 17:
            checkin_type = 'midday'
        else:
            checkin_type = 'evening'

        # Separate done vs pending routines
        pending_routines = [r for r in routines if r.get('completion_status') != 'done']
        done_routines = [r for r in routines if r.get('completion_status') == 'done']

        # Day info
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_name = day_names[today.weekday()]

        briefing = {
            'generated_at': now.isoformat(),
            'date': today.isoformat(),
            'day_name': day_name,
            'day_of_month': today.day,
            'checkin_type': checkin_type,

            # Last checkin info
            'last_checkin': dict(last_checkin) if last_checkin else None,

            # Calendar
            'events': [dict(e) for e in events],

            # Routines
            'routines_pending': [dict(r) for r in pending_routines],
            'routines_done': [dict(r) for r in done_routines],
            'routines_total': len(routines),
            'routines_completed': len(done_routines),

            # Overdue from previous days
            'overdue': [dict(o) for o in overdue],

            # One-off tasks
            'open_tasks': [dict(t) for t in tasks],

            # Bills coming up
            'upcoming_bills': [dict(b) for b in bills],

            # Quick financial pulse
            'balances': [dict(b) for b in balances],
        }

        # Log the checkin
        log_checkin(checkin_type, f"Briefing generated: {len(pending_routines)} pending, {len(events)} events, {len(tasks)} tasks", conn)

        return briefing

    finally:
        conn.close()


def format_briefing_telegram(briefing):
    """Format the daily briefing for Telegram."""
    b = briefing
    now = datetime.fromisoformat(b['generated_at'])
    time_str = now.strftime('%-I:%M %p')

    lines = []

    # Greeting based on time of day
    if b['checkin_type'] == 'morning':
        lines.append(f"☀️ <b>Good morning, Ka'tuar'el.</b>")
    elif b['checkin_type'] == 'midday':
        lines.append(f"🌤 <b>Afternoon check-in.</b>")
    else:
        lines.append(f"🌙 <b>Evening check-in.</b>")

    date_obj = date.fromisoformat(b['date'])
    month_name = date_obj.strftime('%B')
    lines.append(f"It's {b['day_name']}, {month_name} {date_obj.day}, {date_obj.year} at {time_str}.")
    lines.append("")

    # Calendar events
    if b['events']:
        lines.append("📅 <b>Calendar</b>")
        for e in b['events']:
            time_part = ""
            if e.get('start_time'):
                # Format time string
                t = e['start_time']
                if isinstance(t, str):
                    time_part = f"{t} — "
                else:
                    time_part = f"{t.strftime('%-I:%M %p')} — "
            person = ""
            if e.get('person') and e['person'] != 'adge':
                person = f" ({e['person']})"
            lines.append(f"  • {time_part}{e['title']}{person}")
        lines.append("")

    # Overdue items
    if b['overdue']:
        lines.append("⚠️ <b>Overdue</b>")
        for o in b['overdue']:
            lines.append(f"  • {o['title']} (due {o['due_date']})")
        lines.append("")

    # Today's routines
    if b['routines_pending']:
        lines.append(f"📋 <b>Today's Routines</b> ({b['routines_completed']}/{b['routines_total']} done)")
        for idx, r in enumerate(b['routines_pending'], 1):
            domain_emoji = {
                'finance': '💰', 'household': '🏠', 'health': '💊',
                'work': '💼', 'personal': '📌', 'mythos': '🔮',
                'spiritual': '✨'
            }
            emoji = domain_emoji.get(r.get('domain'), '📌')
            time_str = ""
            if r.get('time_due'):
                t = r['time_due']
                if isinstance(t, str):
                    time_str = f" (by {t})"
                else:
                    time_str = f" (by {t.strftime('%-I:%M %p')})"
            lines.append(f"  {idx}. {emoji} {r['title']}{time_str}")
        lines.append("")

    if b['routines_done']:
        lines.append(f"✅ <b>Done today</b>")
        for r in b['routines_done']:
            lines.append(f"  ✓ {r['title']}")
        lines.append("")

    # Open tasks
    if b['open_tasks']:
        overdue_tasks = [t for t in b['open_tasks'] if t.get('next_review') and t['next_review'].replace(tzinfo=None) < datetime.now()]
        regular_tasks = [t for t in b['open_tasks'] if t not in overdue_tasks]

        if overdue_tasks or regular_tasks:
            lines.append(f"📝 <b>Open Tasks</b> ({len(b['open_tasks'])})")
            for t in (overdue_tasks + regular_tasks)[:5]:
                priority_emoji = {'critical': '🔴', 'high': '🔴', 'medium': '🟡', 'low': '🟢'}
                p = priority_emoji.get(t.get('priority'), '🟡')
                idea = t['idea']
                if len(idea) > 40:
                    idea = idea[:37] + "..."
                lines.append(f"  {p} {idea}")
            if len(b['open_tasks']) > 5:
                lines.append(f"  <i>... and {len(b['open_tasks']) - 5} more</i>")
            lines.append("")

    # Bills coming up
    if b['upcoming_bills']:
        unpaid_bills = [bill for bill in b['upcoming_bills'] if not bill.get('override_paid')]
        paid_bills = [bill for bill in b['upcoming_bills'] if bill.get('override_paid')]
        total_remaining = sum(float(bill.get('expected_amount') or 0) for bill in unpaid_bills)
        lines.append(f"💳 <b>Bills next 7 days</b> (${total_remaining:,.2f} remaining)")
        for bill in unpaid_bills[:5]:
            amt = float(bill.get('expected_amount') or 0)
            lines.append(f"  Day {bill['expected_day']}: {bill['merchant_name']} ${amt:,.2f}")
        for bill in paid_bills:
            amt = float(bill.get('expected_amount') or 0)
            lines.append(f"  ✅ <s>Day {bill['expected_day']}: {bill['merchant_name']} ${amt:,.2f}</s>")
        lines.append("")

    # Quick financial pulse
    if b['balances']:
        lines.append("💰 <b>Balances</b>")
        for bal in b['balances']:
            lines.append(f"  {bal['abbreviation']}: ${float(bal['current_balance']):,.2f}")
        lines.append("")

    # Footer
    lines.append("<i>/rdone N to complete a routine • /tasks for full task list</i>")

    return "\n".join(lines)


if __name__ == "__main__":
    """Test: generate and print a briefing."""
    briefing = generate_daily_briefing()
    print(format_briefing_telegram(briefing))
