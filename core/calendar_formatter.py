#!/usr/bin/env python3
"""
Calendar Formatter
==================
Reusable visual formatter for calendar/schedule display in Telegram.
Weaves together calendar events, bills due, and routines into
a unified timeline view.

Usage:
    from calendar_formatter import format_week_view, format_day_view, format_month_view
"""

import os
import logging
from datetime import date, datetime, time, timedelta
from typing import List, Dict, Optional

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


def _get_events(cur, start_date: date, end_date: date) -> List[Dict]:
    """Get calendar events in date range."""
    cur.execute("""
        SELECT id, title, event_date, start_time, end_time, person, location
        FROM calendar_events
        WHERE event_date >= %s AND event_date < %s AND is_active = true
        ORDER BY event_date, start_time NULLS LAST
    """, (start_date, end_date))
    return [dict(r) for r in cur.fetchall()]


def _get_bills(cur, start_date: date, end_date: date) -> List[Dict]:
    """Get bills due in date range with payment status."""
    month_str = start_date.strftime('%Y-%m')
    # Get bills where expected_day falls in our range
    cur.execute("""
        SELECT rb.id, rb.merchant_name, rb.expected_amount, rb.expected_day,
               rb.category_primary, bo.is_paid as override_paid
        FROM recurring_bills rb
        LEFT JOIN bill_overrides bo ON bo.bill_id = rb.id AND bo.month = %s
        WHERE rb.is_active = true AND rb.expected_day IS NOT NULL
        ORDER BY rb.expected_day
    """, (month_str,))
    all_bills = [dict(r) for r in cur.fetchall()]

    # Filter to bills whose day falls in our date range
    result = []
    for b in all_bills:
        try:
            bill_date = start_date.replace(day=b['expected_day'])
            if start_date <= bill_date < end_date:
                b['bill_date'] = bill_date
                result.append(b)
        except ValueError:
            pass  # Day doesn't exist in this month
    return result


def _get_routines_for_day(cur, target_date: date) -> List[Dict]:
    """Get routines scheduled for a specific day."""
    dow = target_date.weekday()
    dom = target_date.day

    cur.execute("""
        SELECT r.id, r.title, r.domain, r.frequency,
               rc.status as completion_status
        FROM routines r
        LEFT JOIN routine_completions rc ON rc.routine_id = r.id AND rc.due_date = %s
        WHERE r.is_active = true AND r.auto_create = true
          AND (
              r.frequency = 'daily'
              OR (r.frequency = 'weekdays' AND %s < 5)
              OR (r.frequency = 'weekends' AND %s >= 5)
              OR (r.frequency = 'weekly' AND r.day_of_week = %s)
              OR (r.frequency = 'monthly' AND r.day_of_month = %s)
          )
          AND r.frequency != 'daily'
        ORDER BY r.sort_order
    """, (target_date, dow, dow, dow, dom))
    return [dict(r) for r in cur.fetchall()]


def _format_time(t) -> str:
    """Format a time object for display."""
    if not t:
        return ""
    if hasattr(t, 'strftime'):
        return t.strftime('%-I:%M %p')
    return str(t)


def _format_event_line(e: Dict) -> str:
    """Format a single event as a line."""
    time_part = ""
    if e.get('start_time'):
        time_part = f"{_format_time(e['start_time'])} — "

    person = ""
    if e.get('person') and e['person'] != 'adge':
        person = f" <i>({e['person']})</i>"

    location = ""
    if e.get('location'):
        location = f" 📍 {e['location']}"

    return f"│  • {time_part}{e['title']}{person}{location}"


def _format_bill_line(b: Dict) -> str:
    """Format a single bill as a line."""
    amt = float(b.get('expected_amount') or 0)
    if b.get('override_paid'):
        return f"│  ✅ <s>💳 {b['merchant_name']} ~${amt:,.0f}</s>"
    else:
        return f"│  💳 {b['merchant_name']} ~${amt:,.0f} due"


def _format_routine_line(r: Dict) -> str:
    """Format a routine as a line."""
    if r.get('completion_status') == 'done':
        return f"│  ✅ <s>📋 {r['title']}</s>"
    else:
        return f"│  📋 {r['title']}"


def format_day_view(target_date: date = None, conn=None) -> str:
    """
    Format a single day's view with events, bills, and routines.
    """
    close_conn = False
    if conn is None:
        conn = _get_conn()
        close_conn = True

    if target_date is None:
        target_date = date.today()

    try:
        cur = conn.cursor()
        today = date.today()

        events = _get_events(cur, target_date, target_date + timedelta(days=1))
        bills = _get_bills(cur, target_date, target_date + timedelta(days=1))
        routines = _get_routines_for_day(cur, target_date)

        # Day header
        day_label = target_date.strftime('%A, %B %d')
        if target_date == today:
            day_label += " (today)"
        elif target_date == today + timedelta(days=1):
            day_label += " (tomorrow)"
        elif target_date == today - timedelta(days=1):
            day_label += " (yesterday)"

        lines = [f"┌─ <b>{day_label}</b>"]

        has_items = False

        # Bills first (they're important)
        for b in bills:
            lines.append(_format_bill_line(b))
            has_items = True

        # Events
        for e in events:
            lines.append(_format_event_line(e))
            has_items = True

        # Non-daily routines (weekly/monthly only — skip daily to reduce noise)
        for r in routines:
            lines.append(_format_routine_line(r))
            has_items = True

        if not has_items:
            lines.append("│  <i>No events</i>")

        return "\n".join(lines)

    finally:
        if close_conn:
            conn.close()


def format_week_view(start_date: date = None) -> str:
    """
    Format a full week view with events, bills, and routines.
    """
    conn = _get_conn()

    if start_date is None:
        start_date = date.today()

    end_date = start_date + timedelta(days=7)

    try:
        lines = [f"📅 <b>This Week</b> — {start_date.strftime('%b %d')} → {(end_date - timedelta(days=1)).strftime('%b %d')}\n"]

        for i in range(7):
            day = start_date + timedelta(days=i)
            day_view = format_day_view(day, conn=conn)
            lines.append(day_view)

        return "\n".join(lines)

    finally:
        conn.close()


def format_month_view(target_date: date = None) -> str:
    """
    Format a month view — only shows days that have something on them.
    """
    conn = _get_conn()

    if target_date is None:
        target_date = date.today()

    month_start = target_date.replace(day=1)
    if target_date.month == 12:
        month_end = target_date.replace(year=target_date.year + 1, month=1, day=1)
    else:
        month_end = target_date.replace(month=target_date.month + 1, day=1)

    try:
        cur = conn.cursor()
        today = date.today()

        events = _get_events(cur, month_start, month_end)
        bills = _get_bills(cur, month_start, month_end)

        # Group events by date
        events_by_date = {}
        for e in events:
            d = e['event_date']
            if d not in events_by_date:
                events_by_date[d] = []
            events_by_date[d].append(e)

        # Group bills by date
        bills_by_date = {}
        for b in bills:
            d = b.get('bill_date')
            if d:
                if d not in bills_by_date:
                    bills_by_date[d] = []
                bills_by_date[d].append(b)

        # All dates that have something
        all_dates = sorted(set(list(events_by_date.keys()) + list(bills_by_date.keys())))

        lines = [f"📅 <b>{target_date.strftime('%B %Y')}</b>\n"]

        if not all_dates:
            lines.append("<i>No events or bills this month</i>")
        else:
            for d in all_dates:
                day_label = d.strftime('%A, %b %d')
                if d == today:
                    day_label += " ← <b>today</b>"
                elif d < today:
                    day_label = f"<i>{day_label}</i>"

                lines.append(f"┌─ {day_label}")

                for b in bills_by_date.get(d, []):
                    lines.append(_format_bill_line(b))

                for e in events_by_date.get(d, []):
                    lines.append(_format_event_line(e))

        return "\n".join(lines)

    finally:
        conn.close()


if __name__ == "__main__":
    print(format_week_view())
    print("\n" + "=" * 50 + "\n")
    print(format_month_view())
