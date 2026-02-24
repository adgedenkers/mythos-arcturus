#!/usr/bin/env python3
"""
Mythos People API Routes
/opt/mythos/api/routes/people.py

Endpoints:
    GET    /api/people/            - List all people (with optional search)
    GET    /api/people/{id}        - Get person by ID
    POST   /api/people/            - Create a new person
    PATCH  /api/people/{id}        - Update a person
    DELETE /api/people/{id}        - Delete a person
    GET    /api/people/stats       - Summary stats
"""

import os
import psycopg2
import psycopg2.extras
from datetime import datetime, date
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

router = APIRouter(prefix="/api/people", tags=["people"])


def get_conn():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', '')
    )


def row_to_dict(row, cursor):
    """Convert a DB row to dict using cursor description."""
    if row is None:
        return None
    cols = [desc[0] for desc in cursor.description]
    d = {}
    for col, val in zip(cols, row):
        if isinstance(val, (datetime, date)):
            d[col] = val.isoformat()
        else:
            d[col] = val
    return d


# ── Models ──

class PersonCreate(BaseModel):
    prefix: Optional[str] = None
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    suffix: Optional[str] = None
    known_as: Optional[str] = None
    date_of_birth: Optional[str] = None
    time_of_birth: Optional[str] = None
    birth_city: Optional[str] = None
    birth_state: Optional[str] = None
    birth_zip: Optional[str] = None
    birth_country: Optional[str] = None
    date_of_death: Optional[str] = None
    notes: Optional[str] = None


class PersonUpdate(BaseModel):
    prefix: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    suffix: Optional[str] = None
    known_as: Optional[str] = None
    date_of_birth: Optional[str] = None
    time_of_birth: Optional[str] = None
    birth_city: Optional[str] = None
    birth_state: Optional[str] = None
    birth_zip: Optional[str] = None
    birth_country: Optional[str] = None
    date_of_death: Optional[str] = None
    notes: Optional[str] = None


# ── Helpers ──

def build_display_text(known_as, first_name, middle_name, last_name):
    full = ' '.join(filter(None, [first_name, middle_name, last_name]))
    if known_as:
        return f"{known_as} ({full})"
    return full


def build_canonical_id(first_name, middle_name, last_name):
    parts = filter(None, [first_name, middle_name, last_name])
    return '-'.join(p.lower().strip() for p in parts)


def parse_dob_parts(dob_str):
    """Parse date string into year/month/day parts."""
    if not dob_str:
        return None, None, None, None
    try:
        d = datetime.strptime(dob_str, '%Y-%m-%d').date()
        return d, d.year, d.month, d.day
    except ValueError:
        return None, None, None, None


# ── Routes ──

@router.get("/stats")
async def people_stats():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM people")
        total = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM people WHERE date_of_birth IS NOT NULL")
        with_dob = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM people WHERE date_of_death IS NOT NULL")
        deceased = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM people WHERE notes IS NOT NULL AND notes != ''")
        with_notes = cur.fetchone()[0]

        return {
            "total": total,
            "with_dob": with_dob,
            "deceased": deceased,
            "with_notes": with_notes,
            "living": total - deceased
        }
    finally:
        cur.close()
        conn.close()


@router.get("/")
async def list_people(
    search: Optional[str] = Query(None, description="Search by name or known_as"),
    sort: str = Query("last_name", description="Sort field"),
    order: str = Query("asc", description="Sort order: asc or desc"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    conn = get_conn()
    cur = conn.cursor()
    try:
        allowed_sorts = {
            'last_name': 'last_name',
            'first_name': 'first_name',
            'known_as': 'known_as',
            'date_of_birth': 'date_of_birth',
            'created_at': 'created_at',
            'id': 'id'
        }
        sort_col = allowed_sorts.get(sort, 'last_name')
        sort_dir = 'DESC' if order.lower() == 'desc' else 'ASC'

        if search:
            cur.execute(f"""
                SELECT * FROM people
                WHERE LOWER(first_name) LIKE LOWER(%s)
                   OR LOWER(last_name) LIKE LOWER(%s)
                   OR LOWER(COALESCE(known_as,'')) LIKE LOWER(%s)
                   OR LOWER(COALESCE(middle_name,'')) LIKE LOWER(%s)
                   OR LOWER(COALESCE(display_text,'')) LIKE LOWER(%s)
                ORDER BY {sort_col} {sort_dir}
                LIMIT %s OFFSET %s
            """, tuple([f'%{search}%'] * 5 + [limit, offset]))
        else:
            cur.execute(f"""
                SELECT * FROM people
                ORDER BY {sort_col} {sort_dir}
                LIMIT %s OFFSET %s
            """, (limit, offset))

        rows = cur.fetchall()
        people = [row_to_dict(r, cur) for r in rows]

        # Total count
        if search:
            cur.execute("""
                SELECT COUNT(*) FROM people
                WHERE LOWER(first_name) LIKE LOWER(%s)
                   OR LOWER(last_name) LIKE LOWER(%s)
                   OR LOWER(COALESCE(known_as,'')) LIKE LOWER(%s)
                   OR LOWER(COALESCE(middle_name,'')) LIKE LOWER(%s)
                   OR LOWER(COALESCE(display_text,'')) LIKE LOWER(%s)
            """, tuple([f'%{search}%'] * 5))
        else:
            cur.execute("SELECT COUNT(*) FROM people")
        total = cur.fetchone()[0]

        return {"people": people, "total": total}
    finally:
        cur.close()
        conn.close()


@router.get("/{person_id}")
async def get_person(person_id: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM people WHERE id = %s", (person_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Person not found")
        return row_to_dict(row, cur)
    finally:
        cur.close()
        conn.close()


@router.post("/")
async def create_person(person: PersonCreate):
    conn = get_conn()
    cur = conn.cursor()
    try:
        display = build_display_text(
            person.known_as, person.first_name,
            person.middle_name, person.last_name
        )
        canonical = build_canonical_id(
            person.first_name, person.middle_name, person.last_name
        )
        dob, dob_y, dob_m, dob_d = parse_dob_parts(person.date_of_birth)

        dod, dod_y, dod_m, dod_d = (None, None, None, None)
        if person.date_of_death:
            dod, dod_y, dod_m, dod_d = parse_dob_parts(person.date_of_death)

        cur.execute("""
            INSERT INTO people (
                prefix, first_name, middle_name, last_name, suffix,
                known_as, display_text, canonical_id,
                date_of_birth, dob_year, dob_month, dob_day,
                time_of_birth, birth_city, birth_state, birth_zip, birth_country,
                date_of_death, dod_year, dod_month, dod_day,
                notes, created_by, modified_by
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, 'mythos-web', 'mythos-web'
            ) RETURNING id
        """, (
            person.prefix, person.first_name, person.middle_name,
            person.last_name, person.suffix,
            person.known_as, display, canonical,
            dob, dob_y, dob_m, dob_d,
            person.time_of_birth, person.birth_city, person.birth_state,
            person.birth_zip, person.birth_country,
            dod, dod_y, dod_m, dod_d,
            person.notes
        ))
        new_id = cur.fetchone()[0]
        conn.commit()

        cur.execute("SELECT * FROM people WHERE id = %s", (new_id,))
        return row_to_dict(cur.fetchone(), cur)
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=409, detail="Person with that canonical ID already exists")
    finally:
        cur.close()
        conn.close()


@router.patch("/{person_id}")
async def update_person(person_id: int, person: PersonUpdate):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Get current record
        cur.execute("SELECT * FROM people WHERE id = %s", (person_id,))
        existing = cur.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Person not found")

        current = row_to_dict(existing, cur)
        updates = person.dict(exclude_unset=True)

        if not updates:
            return current

        # Build SET clause
        set_parts = []
        values = []
        for key, val in updates.items():
            set_parts.append(f"{key} = %s")
            values.append(val)

        # Recompute derived fields if name changed
        fn = updates.get('first_name', current['first_name'])
        mn = updates.get('middle_name', current['middle_name'])
        ln = updates.get('last_name', current['last_name'])
        ka = updates.get('known_as', current['known_as'])

        if any(k in updates for k in ['first_name', 'middle_name', 'last_name', 'known_as']):
            set_parts.append("display_text = %s")
            values.append(build_display_text(ka, fn, mn, ln))
            set_parts.append("canonical_id = %s")
            values.append(build_canonical_id(fn, mn, ln))

        # Parse DOB if changed
        if 'date_of_birth' in updates:
            dob, y, m, d = parse_dob_parts(updates['date_of_birth'])
            set_parts.extend(["date_of_birth = %s", "dob_year = %s", "dob_month = %s", "dob_day = %s"])
            values.extend([dob, y, m, d])

        if 'date_of_death' in updates:
            dod, y, m, d = parse_dob_parts(updates['date_of_death'])
            set_parts.extend(["date_of_death = %s", "dod_year = %s", "dod_month = %s", "dod_day = %s"])
            values.extend([dod, y, m, d])

        set_parts.append("updated_at = NOW()")
        set_parts.append("modified_by = 'mythos-web'")

        values.append(person_id)
        sql = f"UPDATE people SET {', '.join(set_parts)} WHERE id = %s"
        cur.execute(sql, values)
        conn.commit()

        cur.execute("SELECT * FROM people WHERE id = %s", (person_id,))
        return row_to_dict(cur.fetchone(), cur)
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=409, detail="Canonical ID conflict")
    finally:
        cur.close()
        conn.close()


@router.delete("/{person_id}")
async def delete_person(person_id: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT display_text FROM people WHERE id = %s", (person_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Person not found")

        cur.execute("DELETE FROM people WHERE id = %s", (person_id,))
        conn.commit()
        return {"status": "deleted", "display_text": row[0]}
    finally:
        cur.close()
        conn.close()
