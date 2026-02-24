#!/usr/bin/env python3
"""
Mythos People Handler for Telegram Bot
/opt/mythos/telegram_bot/handlers/people_handler.py

Commands:
    /people                                  - Show usage help
    /people add <first> | <middle> | <last> | <known_as> | <DOB> | <time> | <city> | <state> | <country> | <DOD> | <notes>
    /people search <query>                   - Search by name or known_as
    /people list                             - List all people (summary)
    /people view <id_or_name>                - View full record
    /people edit <id> <field> <value>        - Edit a field
    /people delete <id>                      - Delete a record
"""
import os
import logging
from datetime import datetime
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')
log = logging.getLogger(__name__)


def get_db_connection():
    """Get PostgreSQL connection."""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
    )


USAGE_TEXT = (
    "👤 People Database\n\n"
    "Usage:\n"
    "  /people add <first> | <middle> | <last> | <known_as> | <DOB> | <time> | <city> | <state> | <country> | <DOD> | <notes>\n"
    "  /people search <name>\n"
    "  /people list\n"
    "  /people view <id or name>\n"
    "  /people edit <id> <field> <value>\n"
    "  /people delete <id>\n\n"
    "Empty fields: leave blank between pipes\n"
    "Date format: YYYY-MM-DD\n"
    "Time format: HH:MM (24hr)\n\n"
    "Example:\n"
    "  /people add John | Fitzgerald | Kennedy | JFK | 1917-05-29 | 15:00 | Brookline | Massachusetts | USA | 1963-11-22 | 35th President"
)

EDITABLE_FIELDS = {
    'first_name', 'middle_name', 'last_name', 'known_as', 'prefix', 'suffix',
    'date_of_birth', 'time_of_birth', 'birth_city', 'birth_state',
    'birth_country', 'birth_zip', 'date_of_death', 'notes', 'display_text',
}


def handle_people(text: str) -> str:
    """Route /people subcommands. Returns response string."""
    if not text or not text.strip():
        return USAGE_TEXT

    parts = text.strip()
    cmd = parts.split()[0].lower()
    rest = parts[len(cmd):].strip()

    if cmd == 'add':
        return _add_person(rest)
    elif cmd == 'search':
        return _search_people(rest)
    elif cmd == 'list':
        return _list_people()
    elif cmd == 'view':
        return _view_person(rest)
    elif cmd == 'edit':
        return _edit_person(rest)
    elif cmd == 'delete':
        return _delete_person(rest)
    else:
        # Treat bare text as search
        return _search_people(parts)


def _add_person(text: str) -> str:
    """Add a person. Pipe-delimited: first|middle|last|known_as|DOB|time|city|state|country|DOD|notes"""
    if not text:
        return "Format: /people add <first> | <middle> | <last> | <known_as> | <DOB> | <time> | <city> | <state> | <country> | <DOD> | <notes>"

    fields = [f.strip() for f in text.split('|')]

    # Pad to 11 fields
    while len(fields) < 11:
        fields.append('')

    first_name = fields[0]
    middle_name = fields[1] or None
    last_name = fields[2]
    known_as = fields[3] or None
    dob_str = fields[4] or None
    tob_str = fields[5] or None
    birth_city = fields[6] or None
    birth_state = fields[7] or None
    birth_country = fields[8] or None
    dod_str = fields[9] or None
    notes = fields[10] or None

    if not first_name or not last_name:
        return "First name and last name are required."

    # Parse dates
    date_of_birth = _parse_date(dob_str)
    date_of_death = _parse_date(dod_str)
    time_of_birth = _parse_time(tob_str)

    # Build canonical_id
    canonical = f"person-{first_name.lower()}-{last_name.lower()}"
    if known_as:
        canonical = f"person-{known_as.lower().replace(' ', '-')}"

    # Decompose DOB into parts
    dob_year = date_of_birth.year if date_of_birth else (int(dob_str[:4]) if dob_str and len(dob_str) >= 4 and dob_str[:4].isdigit() else None)
    dob_month = date_of_birth.month if date_of_birth else None
    dob_day = date_of_birth.day if date_of_birth else None
    dod_year = date_of_death.year if date_of_death else None
    dod_month = date_of_death.month if date_of_death else None
    dod_day = date_of_death.day if date_of_death else None

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check for duplicate canonical_id
        cur.execute("SELECT id FROM people WHERE canonical_id = %s", (canonical,))
        if cur.fetchone():
            # Append number to make unique
            cur.execute("SELECT COUNT(*) FROM people WHERE canonical_id LIKE %s", (canonical + '%',))
            count = cur.fetchone()[0]
            canonical = f"{canonical}-{count + 1}"

        cur.execute("""
            INSERT INTO people (
                first_name, middle_name, last_name, known_as,
                date_of_birth, dob_year, dob_month, dob_day,
                time_of_birth,
                birth_city, birth_state, birth_country,
                date_of_death, dod_year, dod_month, dod_day,
                notes, canonical_id, created_by
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s,
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s
            ) RETURNING id
        """, (
            first_name, middle_name, last_name, known_as,
            date_of_birth, dob_year, dob_month, dob_day,
            time_of_birth,
            birth_city, birth_state, birth_country,
            date_of_death, dod_year, dod_month, dod_day,
            notes, canonical, 'telegram'
        ))

        new_id = cur.fetchone()[0]
        conn.commit()

        display = known_as or f"{first_name} {last_name}"
        born = f" b.{dob_str}" if dob_str else ""
        died = f" d.{dod_str}" if dod_str else ""
        loc = ""
        if birth_city:
            loc_parts = [p for p in [birth_city, birth_state, birth_country] if p]
            loc = f" — {', '.join(loc_parts)}"

        return f"✅ Added #{new_id}: {display}{born}{died}{loc}"

    except Exception as e:
        log.error(f"Error adding person: {e}")
        if conn:
            conn.rollback()
        return f"❌ Error: {e}"
    finally:
        if conn:
            conn.close()


def _search_people(query: str) -> str:
    """Search people by name, known_as, or notes."""
    if not query:
        return "Usage: /people search <name>"

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT id, first_name, middle_name, last_name, known_as,
                   date_of_birth, date_of_death, birth_city, birth_country, notes
            FROM people
            WHERE LOWER(first_name) LIKE LOWER(%s)
               OR LOWER(last_name) LIKE LOWER(%s)
               OR LOWER(known_as) LIKE LOWER(%s)
               OR LOWER(notes) LIKE LOWER(%s)
               OR LOWER(first_name || ' ' || last_name) LIKE LOWER(%s)
            ORDER BY last_name, first_name
            LIMIT 20
        """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))

        rows = cur.fetchall()
        if not rows:
            return f"No results for \"{query}\""

        lines = [f"👤 Search: \"{query}\" ({len(rows)} result{'s' if len(rows) != 1 else ''})\n"]
        for r in rows:
            display = r['known_as'] or f"{r['first_name']} {r['last_name']}"
            born = f" b.{r['date_of_birth']}" if r['date_of_birth'] else ""
            died = f" d.{r['date_of_death']}" if r['date_of_death'] else ""
            lines.append(f"  #{r['id']} {display}{born}{died}")

        return '\n'.join(lines)

    except Exception as e:
        log.error(f"Error searching people: {e}")
        return f"❌ Error: {e}"
    finally:
        if conn:
            conn.close()


def _list_people() -> str:
    """List all people in the database."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT id, first_name, last_name, known_as,
                   date_of_birth, date_of_death, birth_country
            FROM people
            ORDER BY last_name, first_name
        """)

        rows = cur.fetchall()
        if not rows:
            return "👤 No people in database yet.\n\nUse /people add to create one."

        lines = [f"👤 People Database ({len(rows)} records)\n"]
        for r in rows:
            display = r['known_as'] or f"{r['first_name']} {r['last_name']}"
            born = f" b.{r['date_of_birth']}" if r['date_of_birth'] else ""
            died = f" d.{r['date_of_death']}" if r['date_of_death'] else ""
            country = f" [{r['birth_country']}]" if r['birth_country'] else ""
            lines.append(f"  #{r['id']} {display}{born}{died}{country}")

        return '\n'.join(lines)

    except Exception as e:
        log.error(f"Error listing people: {e}")
        return f"❌ Error: {e}"
    finally:
        if conn:
            conn.close()


def _view_person(query: str) -> str:
    """View full details for a person by ID or name."""
    if not query:
        return "Usage: /people view <id or name>"

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Try by ID first
        if query.strip().isdigit():
            cur.execute("SELECT * FROM people WHERE id = %s", (int(query),))
        else:
            cur.execute("""
                SELECT * FROM people
                WHERE LOWER(known_as) = LOWER(%s)
                   OR LOWER(first_name || ' ' || last_name) = LOWER(%s)
                   OR LOWER(first_name) = LOWER(%s)
                   OR LOWER(last_name) = LOWER(%s)
                LIMIT 1
            """, (query, query, query, query))

        row = cur.fetchone()
        if not row:
            return f"No person found for \"{query}\""

        lines = []
        full_name_parts = [p for p in [row['prefix'], row['first_name'], row['middle_name'], row['last_name'], row['suffix']] if p]
        full_name = ' '.join(full_name_parts)
        lines.append(f"👤 #{row['id']}: {full_name}")
        if row['known_as']:
            lines.append(f"   aka: {row['known_as']}")

        lines.append("")

        # Birth
        if row['date_of_birth']:
            born_parts = [str(row['date_of_birth'])]
            if row['time_of_birth']:
                born_parts.append(str(row['time_of_birth'])[:5])
            lines.append(f"   Born: {' '.join(born_parts)}")
        elif row['dob_year']:
            lines.append(f"   Born: ~{row['dob_year']}")

        # Location
        loc_parts = [p for p in [row['birth_city'], row['birth_state'], row['birth_country']] if p]
        if loc_parts:
            lines.append(f"   Place: {', '.join(loc_parts)}")

        # Death
        if row['date_of_death']:
            lines.append(f"   Died: {row['date_of_death']}")

        # Notes
        if row['notes']:
            lines.append(f"\n   {row['notes']}")

        return '\n'.join(lines)

    except Exception as e:
        log.error(f"Error viewing person: {e}")
        return f"❌ Error: {e}"
    finally:
        if conn:
            conn.close()


def _edit_person(text: str) -> str:
    """Edit a person's field. Format: <id> <field> <value>"""
    parts = text.split(None, 2)
    if len(parts) < 3:
        fields_list = ', '.join(sorted(EDITABLE_FIELDS))
        return f"Format: /people edit <id> <field> <value>\n\nEditable fields:\n{fields_list}"

    person_id, field, value = parts[0], parts[1].lower(), parts[2]

    if not person_id.isdigit():
        return "First argument must be a person ID (number)."

    if field not in EDITABLE_FIELDS:
        return f"Unknown field: {field}\n\nEditable: {', '.join(sorted(EDITABLE_FIELDS))}"

    # Validate date/time fields
    if field in ('date_of_birth', 'date_of_death'):
        parsed = _parse_date(value)
        if not parsed:
            return f"Invalid date: {value} (use YYYY-MM-DD)"
        value = str(parsed)
    elif field == 'time_of_birth':
        parsed = _parse_time(value)
        if not parsed:
            return f"Invalid time: {value} (use HH:MM)"
        value = str(parsed)

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Verify person exists
        cur.execute("SELECT first_name, last_name, known_as FROM people WHERE id = %s", (int(person_id),))
        row = cur.fetchone()
        if not row:
            return f"No person with ID {person_id}"

        display = row[2] or f"{row[0]} {row[1]}"

        cur.execute(
            f"UPDATE people SET {field} = %s, updated_at = CURRENT_TIMESTAMP, modified_by = 'telegram' WHERE id = %s",
            (value, int(person_id))
        )

        # Update decomposed date fields if needed
        if field == 'date_of_birth':
            d = _parse_date(value)
            if d:
                cur.execute(
                    "UPDATE people SET dob_year=%s, dob_month=%s, dob_day=%s WHERE id=%s",
                    (d.year, d.month, d.day, int(person_id))
                )
        elif field == 'date_of_death':
            d = _parse_date(value)
            if d:
                cur.execute(
                    "UPDATE people SET dod_year=%s, dod_month=%s, dod_day=%s WHERE id=%s",
                    (d.year, d.month, d.day, int(person_id))
                )

        conn.commit()
        return f"✅ Updated #{person_id} ({display}): {field} → {value}"

    except Exception as e:
        log.error(f"Error editing person: {e}")
        if conn:
            conn.rollback()
        return f"❌ Error: {e}"
    finally:
        if conn:
            conn.close()


def _delete_person(text: str) -> str:
    """Delete a person by ID."""
    if not text or not text.strip().isdigit():
        return "Usage: /people delete <id>"

    person_id = int(text.strip())

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT first_name, last_name, known_as FROM people WHERE id = %s", (person_id,))
        row = cur.fetchone()
        if not row:
            return f"No person with ID {person_id}"

        display = row[2] or f"{row[0]} {row[1]}"
        cur.execute("DELETE FROM people WHERE id = %s", (person_id,))
        conn.commit()

        return f"🗑️ Deleted #{person_id}: {display}"

    except Exception as e:
        log.error(f"Error deleting person: {e}")
        if conn:
            conn.rollback()
        return f"❌ Error: {e}"
    finally:
        if conn:
            conn.close()


def _parse_date(s: str) -> Optional[datetime]:
    """Parse YYYY-MM-DD date string."""
    if not s or not s.strip():
        return None
    s = s.strip()
    for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y'):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _parse_time(s: str) -> Optional[str]:
    """Parse HH:MM time string."""
    if not s or not s.strip():
        return None
    s = s.strip()
    try:
        t = datetime.strptime(s, '%H:%M')
        return t.strftime('%H:%M:00')
    except ValueError:
        return None
