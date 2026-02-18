#!/usr/bin/env python3
"""
Patch: Calendar update/delete/dedup support
Modifies message_extractor.py and action_executor.py on Arcturus.
"""

def patch_extractor():
    """Add calendar events to dynamic context and update/delete to schema."""
    with open('/opt/mythos/core/message_extractor.py', 'r') as f:
        c = f.read()

    if 'calendar_update' in c:
        print("Extractor already patched")
        return

    # 1. Add upcoming calendar events to dynamic context
    c = c.replace(
        '''        # Open tasks
        cur.execute("""\n            SELECT id, idea FROM idea_backlog''',
        '''        # Upcoming calendar events (so extractor can match for updates/deletes)
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
            parts.append("UPCOMING CALENDAR EVENTS:\\n" + "\\n".join(e_list))

        # Open tasks
        cur.execute("""\\n            SELECT id, idea FROM idea_backlog''')

    # 2. Add calendar_update and calendar_delete to the JSON schema
    c = c.replace(
        '''    "calendar_event": {{
        "title": "event description",
        "date": "YYYY-MM-DD",
        "time": "HH:MM" or null,
        "person": "adge|rebecca|fitz|family",
        "location": "place or null"
    }},''',
        '''    "calendar_event": {{
        "action": "create|update|delete",
        "event_id": null or number,
        "title": "event description",
        "date": "YYYY-MM-DD",
        "time": "HH:MM" or null,
        "person": "adge|rebecca|fitz|family",
        "location": "place or null"
    }},''')

    # 3. Add instructions about calendar updates/deletes
    old_instructions = '''If NOTHING actionable is found, return: {{"no_action": true}}'''
    new_instructions = '''CALENDAR RULES:
- If the user mentions a NEW event, use action: "create"
- If the user says to CHANGE/MOVE/UPDATE an existing event, use action: "update" with the event_id from UPCOMING CALENDAR EVENTS above
- If the user says to CANCEL/REMOVE/DELETE an event, use action: "delete" with the event_id
- If an event sounds similar to an existing one (same person + similar title), prefer "update" over "create"
- When correcting a date/time ("no, it's Monday not Friday"), use "update" with the correct date/time

If NOTHING actionable is found, return: {{"no_action": true}}'''
    c = c.replace(old_instructions, new_instructions)

    # 4. Update the format_extraction_for_context for calendar updates
    c = c.replace(
        '''    if 'calendar_event' in extraction:
        c = extraction['calendar_event']
        time_str = f" at {c['time']}" if c.get('time') else ""
        parts.append(f"[DETECTED: Calendar event — {c.get('title', 'event')} on {c.get('date', '?')}{time_str} for {c.get('person', 'adge')}]")''',
        '''    if 'calendar_event' in extraction:
        c = extraction['calendar_event']
        action = c.get('action', 'create')
        time_str = f" at {c['time']}" if c.get('time') else ""
        if action == 'delete':
            parts.append(f"[DETECTED: Calendar delete — {c.get('title', 'event')}]")
        elif action == 'update':
            parts.append(f"[DETECTED: Calendar update — {c.get('title', 'event')} → {c.get('date', '?')}{time_str}]")
        else:
            parts.append(f"[DETECTED: Calendar event — {c.get('title', 'event')} on {c.get('date', '?')}{time_str} for {c.get('person', 'adge')}]")''')

    with open('/opt/mythos/core/message_extractor.py', 'w') as f:
        f.write(c)
    print("✅ message_extractor.py patched")


def patch_executor():
    """Add calendar update and delete handling."""
    with open('/opt/mythos/core/action_executor.py', 'r') as f:
        c = f.read()

    if 'calendar_update' in c or '_execute_calendar_update' in c:
        print("Executor already patched")
        return

    # Replace the calendar_event executor call to handle action types
    c = c.replace(
        '''        if 'calendar_event' in extraction:
            r = _execute_calendar_event(conn, extraction['calendar_event'])
            if r:
                results.append(r)''',
        '''        if 'calendar_event' in extraction:
            cal = extraction['calendar_event']
            action = cal.get('action', 'create')
            if action == 'delete':
                r = _execute_calendar_delete(conn, cal)
            elif action == 'update':
                r = _execute_calendar_update(conn, cal)
            else:
                r = _execute_calendar_create(conn, cal)
            if r:
                results.append(r)''')

    # Rename existing _execute_calendar_event to _execute_calendar_create
    c = c.replace(
        'def _execute_calendar_event(conn, data: Dict) -> str:\n    """Create a calendar event."""',
        'def _execute_calendar_create(conn, data: Dict) -> str:\n    """Create a new calendar event, with dedup check."""')

    # Add dedup check at the start of calendar create
    c = c.replace(
        '''def _execute_calendar_create(conn, data: Dict) -> str:
    """Create a new calendar event, with dedup check."""
    cur = conn.cursor()

    event_date = data.get('date')
    if not event_date:
        return None''',
        '''def _execute_calendar_create(conn, data: Dict) -> str:
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
        return _execute_calendar_update(conn, data)''')

    # Remove the duplicate date parsing that's now above the dedup check
    c = c.replace(
        '''    # DEDUP: check if a very similar event already exists
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

    # Parse date if string
    if isinstance(event_date, str):
        try:
            event_date = datetime.strptime(event_date, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Bad date format: {event_date}")
            return None''',
        '''    # DEDUP: check if a very similar event already exists
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
        return _execute_calendar_update(conn, data)''')

    # Add the update and delete functions before the _execute_task_completed function
    new_functions = '''
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


'''

    c = c.replace(
        'def _execute_task_completed(conn, data: Dict) -> str:',
        new_functions + 'def _execute_task_completed(conn, data: Dict) -> str:')

    with open('/opt/mythos/core/action_executor.py', 'w') as f:
        f.write(c)
    print("✅ action_executor.py patched")


if __name__ == '__main__':
    patch_extractor()
    patch_executor()
    print("\nDone. Restart mythos-api.service to activate.")
