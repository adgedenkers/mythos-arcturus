#!/usr/bin/env python3
"""
Mythos Astrology & Numerology API Routes
/opt/mythos/api/routes/astrology.py

Endpoints:
    GET  /api/astrology/charts          - List all natal charts
    GET  /api/astrology/charts/{id}     - Get chart with planet positions
    GET  /api/astrology/people          - List people with birth data
    GET  /api/astrology/numerology/{id} - Numerology analysis for a chart
"""
import os
import psycopg2
import psycopg2.extras
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/astrology", tags=["astrology"])


def get_conn():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'adge'),
        password=os.getenv('POSTGRES_PASSWORD', '')
    )


def reduce_to_single(n: int) -> dict:
    """Numerological reduction: returns path and final single digit"""
    current = abs(n)
    path = [current]
    while current > 9:
        current = sum(int(d) for d in str(current))
        path.append(current)
    return {"path": path, "result": current}


def compute_triangles(month: int, day: int, year: int) -> dict:
    """Compute the two numerological triangles for a birthdate"""
    month_r = reduce_to_single(month)
    day_r = reduce_to_single(day)
    two_digit_year = year % 100
    two_digit_r = reduce_to_single(two_digit_year)
    four_digit_r = reduce_to_single(year)

    return {
        "month": month_r,
        "day": day_r,
        "two_digit_year": two_digit_r,
        "four_digit_year": four_digit_r,
        "triangle1": [month_r["result"], day_r["result"], two_digit_r["result"]],
        "triangle2": [month_r["result"], day_r["result"], four_digit_r["result"]],
    }


def generate_birthstring(month: int, day: int, year: int, hour: int = 0, minute: int = 0) -> str:
    """Generate personal birthstring: MMDDYYYYTHHmm"""
    return f"{month:02d}{day:02d}{year:04d}T{hour:02d}{minute:02d}"


# ── Charts ──────────────────────────────────────────────────

@router.get("/charts")
async def list_charts():
    """List all natal charts with basic info"""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT c.chart_id, c.name, c.birth_date, c.birth_time,
                   c.birth_place, c.latitude, c.longitude, c.timezone,
                   c.house_system, c.zodiac_type, c.created_at,
                   COUNT(p.id) as point_count
            FROM astro_natal_charts c
            LEFT JOIN astro_chart_points p ON p.chart_id = c.chart_id
            GROUP BY c.chart_id
            ORDER BY c.name
        """)
        charts = cur.fetchall()

        # Convert dates/times to strings for JSON
        result = []
        for ch in charts:
            r = dict(ch)
            r['birth_date'] = str(r['birth_date'])
            r['birth_time'] = str(r['birth_time'])
            r['created_at'] = str(r['created_at'])

            # Generate birthstring
            bd = ch['birth_date']
            bt = ch['birth_time']
            r['birthstring'] = generate_birthstring(
                bd.month, bd.day, bd.year,
                bt.hour, bt.minute
            )

            # Compute numerology triangles
            tri = compute_triangles(bd.month, bd.day, bd.year)
            r['triangle1'] = tri['triangle1']
            r['triangle2'] = tri['triangle2']

            result.append(r)

        return {"charts": result}
    finally:
        cur.close()
        conn.close()


@router.get("/charts/{chart_id}")
async def get_chart(chart_id: int):
    """Get a single chart with all planet positions"""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        # Chart metadata
        cur.execute("""
            SELECT * FROM astro_natal_charts WHERE chart_id = %s
        """, (chart_id,))
        chart = cur.fetchone()
        if not chart:
            raise HTTPException(status_code=404, detail="Chart not found")

        ch = dict(chart)
        ch['birth_date'] = str(ch['birth_date'])
        ch['birth_time'] = str(ch['birth_time'])
        ch['created_at'] = str(ch['created_at'])

        bd = chart['birth_date']
        bt = chart['birth_time']
        ch['birthstring'] = generate_birthstring(
            bd.month, bd.day, bd.year, bt.hour, bt.minute
        )

        # Planet positions
        cur.execute("""
            SELECT point_name, longitude
            FROM astro_chart_points
            WHERE chart_id = %s
            ORDER BY longitude
        """, (chart_id,))
        ch['points'] = [dict(p) for p in cur.fetchall()]

        # House cusps
        cur.execute("""
            SELECT house_number, cusp_longitude
            FROM astro_natal_house_cusps
            WHERE chart_id = %s
            ORDER BY house_number
        """, (chart_id,))
        ch['houses'] = [dict(h) for h in cur.fetchall()]

        # Aspects
        cur.execute("""
            SELECT point1, point2, aspect_type, orb, exact_angle
            FROM astro_natal_aspects
            WHERE chart_id = %s
            ORDER BY orb
        """, (chart_id,))
        ch['aspects'] = [dict(a) for a in cur.fetchall()]

        # Numerology
        tri = compute_triangles(bd.month, bd.day, bd.year)
        ch['numerology'] = tri

        return ch
    finally:
        cur.close()
        conn.close()


# ── People ──────────────────────────────────────────────────

@router.get("/people")
async def list_people():
    """List all people with birth data for chart/numerology work"""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT p.id, p.first_name, p.middle_name, p.last_name,
                   p.known_as, p.display_text,
                   p.date_of_birth, p.time_of_birth,
                   p.birth_city, p.birth_state, p.birth_country,
                   p.canonical_id,
                   c.chart_id
            FROM people p
            LEFT JOIN astro_natal_charts c
                ON c.name = COALESCE(p.known_as, p.first_name)
                AND c.birth_date = p.date_of_birth
            WHERE p.date_of_birth IS NOT NULL
            ORDER BY p.last_name, p.first_name
        """)
        people = cur.fetchall()

        result = []
        for person in people:
            r = dict(person)
            r['date_of_birth'] = str(r['date_of_birth']) if r['date_of_birth'] else None
            r['time_of_birth'] = str(r['time_of_birth']) if r['time_of_birth'] else None

            # Generate birthstring + numerology if we have DOB
            if person['date_of_birth']:
                dob = person['date_of_birth']
                tob = person['time_of_birth']
                hour = tob.hour if tob else 12
                minute = tob.minute if tob else 0
                r['birthstring'] = generate_birthstring(
                    dob.month, dob.day, dob.year, hour, minute
                )
                tri = compute_triangles(dob.month, dob.day, dob.year)
                r['triangle1'] = tri['triangle1']
                r['triangle2'] = tri['triangle2']

            result.append(r)

        return {"people": result}
    finally:
        cur.close()
        conn.close()


# ── Numerology ──────────────────────────────────────────────

@router.get("/numerology/{chart_id}")
async def get_numerology(chart_id: int):
    """Full numerology breakdown for a chart"""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT name, birth_date, birth_time FROM astro_natal_charts
            WHERE chart_id = %s
        """, (chart_id,))
        chart = cur.fetchone()
        if not chart:
            raise HTTPException(status_code=404, detail="Chart not found")

        bd = chart['birth_date']
        bt = chart['birth_time']

        return {
            "chart_id": chart_id,
            "name": chart['name'],
            "birth_date": str(bd),
            "birth_time": str(bt),
            "birthstring": generate_birthstring(
                bd.month, bd.day, bd.year, bt.hour, bt.minute
            ),
            **compute_triangles(bd.month, bd.day, bd.year)
        }
    finally:
        cur.close()
        conn.close()
