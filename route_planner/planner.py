"""
Mythos Route Planner — Daily schedule assembly and errand optimization.

Assembles today's recurring commitments, merges one-off errands,
looks up known drive times, and optimizes float placement using
nearest-neighbor within time gaps. Applies the Reality Tax.

Usage:
    from route_planner.planner import RoutePlanner
    planner = RoutePlanner()
    schedule = planner.get_today()
    optimized = planner.optimize_today()
"""

import math
import logging
from datetime import date, time, datetime, timedelta
from typing import List, Dict, Optional, Tuple

import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)

# Reality Tax: buffer per leg
REALITY_TAX = {
    'short': 10,   # under 30 min drive
    'medium': 15,  # 30-60 min drive
    'long': 20,    # over 60 min drive
}

# Norwich corridor bounding box — stores within this box are ~5 min apart
NORWICH_CORRIDOR = {
    'lat_min': 42.530, 'lat_max': 42.550,
    'lon_min': -75.530, 'lon_max': -75.520,
}


def get_db():
    """Get a psycopg2 connection to the mythos database."""
    return psycopg2.connect(
        dbname='mythos',
        user='postgres',
        host='localhost'
    )


def reality_tax(drive_minutes: int) -> int:
    """Calculate buffer time for a leg."""
    if drive_minutes < 30:
        return REALITY_TAX['short']
    elif drive_minutes <= 60:
        return REALITY_TAX['medium']
    else:
        return REALITY_TAX['long']


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    """Great-circle distance between two points in km."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def estimate_drive_minutes(lat1, lon1, lat2, lon2) -> int:
    """Rough drive time estimate: ~2 min per km for rural NY roads."""
    km = haversine_km(lat1, lon1, lat2, lon2)
    return max(3, int(km * 2.0))


def in_norwich_corridor(lat, lon) -> bool:
    """Check if a location is in the Norwich Rt 12 cluster."""
    return (NORWICH_CORRIDOR['lat_min'] <= float(lat) <= NORWICH_CORRIDOR['lat_max'] and
            NORWICH_CORRIDOR['lon_min'] <= float(lon) <= NORWICH_CORRIDOR['lon_max'])


def time_to_minutes(t: time) -> int:
    """Convert a time object to minutes since midnight."""
    return t.hour * 60 + t.minute


def minutes_to_time_str(m: int) -> str:
    """Convert minutes since midnight to human-readable time string."""
    if m < 0:
        m = 0
    h = m // 60
    mins = m % 60
    period = 'AM' if h < 12 else 'PM'
    display_h = h % 12
    if display_h == 0:
        display_h = 12
    return f"{display_h}:{mins:02d} {period}"


class RoutePlanner:
    """Assembles and optimizes a daily schedule from Mythos data."""

    def __init__(self):
        self._known_routes_cache = None

    def _load_known_routes(self, conn) -> Dict[Tuple[str, str], dict]:
        """Load all known routes into a lookup dict."""
        if self._known_routes_cache is not None:
            return self._known_routes_cache
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM known_routes")
        routes = {}
        for row in cur.fetchall():
            key = (row['from_name'], row['to_name'])
            routes[key] = dict(row)
        self._known_routes_cache = routes
        return routes

    def _get_drive_time(self, conn, from_stop: dict, to_stop: dict) -> int:
        """
        Look up drive time between two stops.
        Priority: known_routes exact match → Norwich corridor shortcut → haversine estimate.
        """
        routes = self._load_known_routes(conn)

        from_name = from_stop.get('location_name', from_stop.get('name', ''))
        to_name = to_stop.get('location_name', to_stop.get('name', ''))

        # Exact match
        key = (from_name, to_name)
        if key in routes:
            return routes[key]['drive_minutes']

        # Check if both are in Norwich corridor — ~5 min between stores
        from_lat = float(from_stop.get('latitude', 0))
        from_lon = float(from_stop.get('longitude', 0))
        to_lat = float(to_stop.get('latitude', 0))
        to_lon = float(to_stop.get('longitude', 0))

        if in_norwich_corridor(from_lat, from_lon) and in_norwich_corridor(to_lat, to_lon):
            return 5

        # Check partial matches — if either stop name starts with a known route endpoint
        for (rk_from, rk_to), route in routes.items():
            if (from_name.startswith(rk_from) or rk_from.startswith(from_name)) and \
               (to_name.startswith(rk_to) or rk_to.startswith(to_name)):
                return route['drive_minutes']

        # Fallback to haversine estimate
        if from_lat and from_lon and to_lat and to_lon:
            return estimate_drive_minutes(from_lat, from_lon, to_lat, to_lon)

        return 15  # safe default for rural NY

    def get_todays_recurring(self, target_date: date = None) -> List[dict]:
        """Get recurring schedule items for today (or a given date)."""
        if target_date is None:
            target_date = date.today()

        # Python weekday: Mon=0 .. Sun=6 (matches our schema)
        dow = target_date.weekday()

        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("""
                SELECT rs.*, kl.name as loc_resolved_name, kl.phone as loc_phone,
                       kl.latitude as loc_lat, kl.longitude as loc_lon,
                       kl.default_dwell_minutes as loc_dwell
                FROM recurring_schedules rs
                LEFT JOIN known_locations kl ON rs.location_id = kl.id
                WHERE rs.active = TRUE
                  AND (
                    rs.schedule_type = 'daily'
                    OR (rs.schedule_type = 'weekday' AND %s BETWEEN 0 AND 4)
                    OR (rs.schedule_type = 'specific_days' AND %s = ANY(rs.days_of_week))
                  )
                ORDER BY rs.time_at
            """, (dow, dow))
            rows = cur.fetchall()

            results = []
            for row in rows:
                stop = dict(row)
                # Resolve location details from join
                if stop.get('loc_lat') and not stop.get('latitude'):
                    stop['latitude'] = stop['loc_lat']
                    stop['longitude'] = stop['loc_lon']
                if not stop.get('location_name') and stop.get('loc_resolved_name'):
                    stop['location_name'] = stop['loc_resolved_name']
                if not stop.get('phone') and stop.get('loc_phone'):
                    stop['phone'] = stop['loc_phone']
                stop['source'] = 'recurring'
                stop['is_anchor'] = stop.get('is_anchor', True)
                results.append(stop)
            return results
        finally:
            conn.close()

    def get_todays_tasks(self, target_date: date = None) -> List[dict]:
        """Get one-off daily tasks for today."""
        if target_date is None:
            target_date = date.today()

        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("""
                SELECT dt.*, kl.name as loc_resolved_name, kl.phone as loc_phone,
                       kl.latitude as loc_lat, kl.longitude as loc_lon,
                       kl.default_dwell_minutes as loc_dwell
                FROM daily_tasks dt
                LEFT JOIN known_locations kl ON dt.location_id = kl.id
                WHERE dt.date = %s AND dt.completed = FALSE
                ORDER BY COALESCE(dt.hard_deadline, dt.preferred_time, '23:59')
            """, (target_date,))
            rows = cur.fetchall()

            results = []
            for row in rows:
                stop = dict(row)
                if stop.get('loc_lat') and not stop.get('latitude'):
                    stop['latitude'] = stop['loc_lat']
                    stop['longitude'] = stop['loc_lon']
                if not stop.get('location_name') and stop.get('loc_resolved_name'):
                    stop['location_name'] = stop['loc_resolved_name']
                if not stop.get('phone') and stop.get('loc_phone'):
                    stop['phone'] = stop['loc_phone']
                stop['source'] = 'errand'
                stop['time_at'] = stop.get('hard_deadline') or stop.get('preferred_time')
                results.append(stop)
            return results
        finally:
            conn.close()

    def get_today(self, target_date: date = None) -> dict:
        """
        Assemble today's full schedule: recurring + errands, sorted by time.
        Returns { 'date': ..., 'day_name': ..., 'stops': [...], 'errands_pending': int }
        """
        if target_date is None:
            target_date = date.today()

        recurring = self.get_todays_recurring(target_date)
        tasks = self.get_todays_tasks(target_date)

        # Merge and sort by time
        all_stops = []
        for s in recurring:
            all_stops.append({
                'name': s['name'],
                'location': s.get('location_name', ''),
                'time': s['time_at'].strftime('%I:%M %p').lstrip('0') if s.get('time_at') else None,
                'time_minutes': time_to_minutes(s['time_at']) if s.get('time_at') else 9999,
                'duration': s.get('duration_minutes', 10),
                'is_anchor': s.get('is_anchor', True),
                'source': 'recurring',
                'phone': s.get('phone'),
                'notes': s.get('notes'),
                'latitude': float(s['latitude']) if s.get('latitude') else None,
                'longitude': float(s['longitude']) if s.get('longitude') else None,
            })

        errands_pending = 0
        for s in tasks:
            t = s.get('hard_deadline') or s.get('preferred_time')
            all_stops.append({
                'name': s['name'],
                'location': s.get('location_name', ''),
                'time': t.strftime('%I:%M %p').lstrip('0') if t else 'Flexible',
                'time_minutes': time_to_minutes(t) if t else 9999,
                'duration': s.get('duration_minutes', 15),
                'is_anchor': s.get('is_anchor', False),
                'source': 'errand',
                'phone': s.get('phone'),
                'notes': s.get('notes'),
                'latitude': float(s['latitude']) if s.get('latitude') else None,
                'longitude': float(s['longitude']) if s.get('longitude') else None,
                'completed': s.get('completed', False),
            })
            if not s.get('completed', False):
                errands_pending += 1

        all_stops.sort(key=lambda x: x['time_minutes'])

        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        return {
            'date': target_date.isoformat(),
            'day_name': day_names[target_date.weekday()],
            'stops': all_stops,
            'errands_pending': errands_pending,
        }

    def optimize_today(self, target_date: date = None) -> dict:
        """
        Optimize today's errands around the recurring anchors.

        Strategy:
        1. Get anchors (recurring schedule) in time order
        2. Get float errands (daily_tasks with no hard_deadline)
        3. Identify time gaps between anchors
        4. Place floats into gaps using nearest-neighbor from previous stop
        5. Apply reality tax to each leg
        6. Return the optimized schedule
        """
        if target_date is None:
            target_date = date.today()

        recurring = self.get_todays_recurring(target_date)
        tasks = self.get_todays_tasks(target_date)

        if not tasks:
            # Nothing to optimize
            return self.get_today(target_date)

        conn = get_db()
        try:
            # Build anchor timeline
            home = self._get_home_location(conn)
            anchors = []

            # Add implicit "start at home" anchor
            anchors.append({
                'name': 'Home (start)',
                'location_name': 'Home',
                'time_minutes': 7 * 60,  # default 7 AM start
                'latitude': home['latitude'],
                'longitude': home['longitude'],
                'duration': 0,
                'is_anchor': True,
                'source': 'implicit',
            })

            for s in recurring:
                anchors.append({
                    'name': s['name'],
                    'location_name': s.get('location_name', ''),
                    'time_minutes': time_to_minutes(s['time_at']),
                    'latitude': float(s.get('latitude', 0)),
                    'longitude': float(s.get('longitude', 0)),
                    'duration': s.get('duration_minutes', 10),
                    'is_anchor': True,
                    'source': 'recurring',
                    'phone': s.get('phone'),
                    'notes': s.get('notes'),
                })

            # Add implicit "return home" anchor at end
            last_anchor_end = max(a['time_minutes'] + a['duration'] for a in anchors) if anchors else 17 * 60
            anchors.append({
                'name': 'Home (return)',
                'location_name': 'Home',
                'time_minutes': last_anchor_end + 30,  # 30 min after last thing
                'latitude': home['latitude'],
                'longitude': home['longitude'],
                'duration': 0,
                'is_anchor': True,
                'source': 'implicit',
            })

            anchors.sort(key=lambda x: x['time_minutes'])

            # Separate tasks into hard-deadline (treat as anchors) and floats
            hard_tasks = []
            float_tasks = []
            for t in tasks:
                task_stop = {
                    'name': t['name'],
                    'location_name': t.get('location_name', ''),
                    'latitude': float(t.get('latitude', 0)) if t.get('latitude') else None,
                    'longitude': float(t.get('longitude', 0)) if t.get('longitude') else None,
                    'duration': t.get('duration_minutes', 15),
                    'is_anchor': bool(t.get('is_anchor', False)),
                    'source': 'errand',
                    'phone': t.get('phone'),
                    'notes': t.get('notes'),
                    'hard_deadline': t.get('hard_deadline'),
                    'preferred_time': t.get('preferred_time'),
                }
                if t.get('hard_deadline'):
                    task_stop['time_minutes'] = time_to_minutes(t['hard_deadline'])
                    task_stop['is_anchor'] = True
                    hard_tasks.append(task_stop)
                else:
                    float_tasks.append(task_stop)

            # Merge hard-deadline tasks into anchors
            for ht in hard_tasks:
                anchors.append(ht)
            anchors.sort(key=lambda x: x['time_minutes'])

            # Identify gaps between anchors
            gaps = []
            for i in range(len(anchors) - 1):
                a_end = anchors[i]['time_minutes'] + anchors[i]['duration']
                b_start = anchors[i + 1]['time_minutes']
                # Need drive time from a to b
                drive = self._get_drive_time(conn, anchors[i], anchors[i + 1])
                tax = reality_tax(drive)
                available = b_start - a_end - drive - tax
                gaps.append({
                    'index': i,
                    'after': anchors[i],
                    'before': anchors[i + 1],
                    'available_minutes': max(0, available),
                    'start_minutes': a_end,
                    'end_minutes': b_start,
                    'assigned': [],
                })

            # Place floats into gaps using nearest-neighbor
            remaining = list(float_tasks)
            for gap in gaps:
                if not remaining:
                    break
                if gap['available_minutes'] < 20:  # need at least 20 min for any errand
                    continue

                # Score each remaining task for this gap
                ref_lat = float(gap['after'].get('latitude', 0))
                ref_lon = float(gap['after'].get('longitude', 0))
                available = gap['available_minutes']

                placed_in_gap = []
                while remaining and available >= 20:
                    best_idx = None
                    best_dist = float('inf')
                    for idx, task in enumerate(remaining):
                        if task.get('latitude') and task.get('longitude'):
                            d = haversine_km(ref_lat, ref_lon,
                                             task['latitude'], task['longitude'])
                        else:
                            d = 999
                        if d < best_dist:
                            best_dist = d
                            best_idx = idx

                    if best_idx is None:
                        break

                    task = remaining[best_idx]
                    # Estimate time cost: drive + dwell + tax
                    drive_to = self._get_drive_time(conn,
                                                     {'latitude': ref_lat, 'longitude': ref_lon,
                                                      'location_name': gap['after'].get('location_name', '')},
                                                     task)
                    cost = drive_to + task['duration'] + reality_tax(drive_to)
                    if cost <= available:
                        placed_in_gap.append(task)
                        remaining.pop(best_idx)
                        available -= cost
                        # Update ref point to this task's location
                        if task.get('latitude'):
                            ref_lat = task['latitude']
                            ref_lon = task['longitude']
                    else:
                        break  # gap is full

                gap['assigned'] = placed_in_gap

            # Build the optimized timeline
            schedule = []
            current_time = anchors[0]['time_minutes']

            for i, gap in enumerate(gaps):
                anchor = anchors[i]
                # Add the anchor
                schedule.append({
                    'name': anchor['name'],
                    'location': anchor.get('location_name', ''),
                    'time': minutes_to_time_str(anchor['time_minutes']),
                    'time_minutes': anchor['time_minutes'],
                    'duration': anchor['duration'],
                    'is_anchor': True,
                    'source': anchor.get('source', 'recurring'),
                    'phone': anchor.get('phone'),
                    'notes': anchor.get('notes'),
                    'latitude': anchor.get('latitude'),
                    'longitude': anchor.get('longitude'),
                })

                # Add errands assigned to this gap
                prev = anchor
                gap_time = anchor['time_minutes'] + anchor['duration']
                for errand in gap['assigned']:
                    drive = self._get_drive_time(conn, prev, errand)
                    tax = reality_tax(drive)
                    arrival = gap_time + drive + tax
                    schedule.append({
                        'name': errand['name'],
                        'location': errand.get('location_name', ''),
                        'time': minutes_to_time_str(arrival),
                        'time_minutes': arrival,
                        'duration': errand['duration'],
                        'is_anchor': False,
                        'source': 'errand',
                        'phone': errand.get('phone'),
                        'notes': errand.get('notes'),
                        'drive_from_prev': drive,
                        'reality_tax': tax,
                        'latitude': errand.get('latitude'),
                        'longitude': errand.get('longitude'),
                    })
                    gap_time = arrival + errand['duration']
                    prev = errand

            # Add final anchor
            if anchors:
                final = anchors[-1]
                schedule.append({
                    'name': final['name'],
                    'location': final.get('location_name', ''),
                    'time': minutes_to_time_str(final['time_minutes']),
                    'time_minutes': final['time_minutes'],
                    'duration': final['duration'],
                    'is_anchor': True,
                    'source': final.get('source', 'recurring'),
                    'latitude': final.get('latitude'),
                    'longitude': final.get('longitude'),
                })

            # Anything that didn't fit
            overflow = [{'name': t['name'], 'location': t.get('location_name', '')} for t in remaining]

            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            return {
                'date': target_date.isoformat(),
                'day_name': day_names[target_date.weekday()],
                'stops': schedule,
                'errands_pending': len(float_tasks),
                'errands_placed': len(float_tasks) - len(remaining),
                'overflow': overflow,
                'optimized': True,
            }
        finally:
            conn.close()

    def _get_home_location(self, conn) -> dict:
        """Get the Home location from known_locations."""
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM known_locations WHERE name = 'Home' AND active = TRUE LIMIT 1")
        row = cur.fetchone()
        if row:
            return dict(row)
        return {'latitude': 42.442, 'longitude': -75.5975, 'name': 'Home'}

    def add_errand(self, name: str, location_name: str = None,
                   duration: int = 15, hard_deadline: time = None,
                   preferred_time: time = None, notes: str = None,
                   target_date: date = None) -> dict:
        """Add a one-off errand for today (or a given date)."""
        if target_date is None:
            target_date = date.today()

        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            # Try to resolve location
            location_id = None
            lat = None
            lon = None
            resolved_name = location_name

            if location_name:
                cur.execute("""
                    SELECT * FROM known_locations
                    WHERE active = TRUE
                      AND (LOWER(name) LIKE LOWER(%s) OR LOWER(category) LIKE LOWER(%s))
                    ORDER BY
                        CASE WHEN LOWER(name) = LOWER(%s) THEN 0
                             WHEN LOWER(name) LIKE LOWER(%s) THEN 1
                             ELSE 2 END
                    LIMIT 1
                """, (f'%{location_name}%', f'%{location_name}%',
                      location_name, f'%{location_name}%'))
                loc = cur.fetchone()
                if loc:
                    location_id = loc['id']
                    lat = loc['latitude']
                    lon = loc['longitude']
                    resolved_name = loc['name']
                    if not duration or duration == 15:
                        duration = loc.get('default_dwell_minutes', 15)

            cur.execute("""
                INSERT INTO daily_tasks
                    (date, name, location_name, location_id, latitude, longitude,
                     duration_minutes, hard_deadline, preferred_time, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (target_date, name, resolved_name, location_id, lat, lon,
                  duration, hard_deadline, preferred_time, notes))
            conn.commit()
            result = dict(cur.fetchone())
            result['resolved_location'] = resolved_name
            return result
        finally:
            conn.close()

    def complete_errand(self, errand_id: int) -> bool:
        """Mark an errand as completed."""
        conn = get_db()
        try:
            cur = conn.cursor()
            cur.execute("UPDATE daily_tasks SET completed = TRUE WHERE id = %s", (errand_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    def get_known_routes(self) -> List[dict]:
        """Return all known routes."""
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT * FROM known_routes ORDER BY from_name, to_name")
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def add_route(self, from_name: str, to_name: str, drive_minutes: int,
                  notes: str = None, bidirectional: bool = True) -> dict:
        """Add or update a known route. Bidirectional by default."""
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            # Resolve coordinates from known_locations
            from_loc = self._resolve_location(cur, from_name)
            to_loc = self._resolve_location(cur, to_name)

            cur.execute("""
                INSERT INTO known_routes (from_name, from_lat, from_lon, to_name, to_lat, to_lon, drive_minutes, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (from_name, to_name)
                DO UPDATE SET drive_minutes = EXCLUDED.drive_minutes,
                              notes = COALESCE(EXCLUDED.notes, known_routes.notes),
                              updated_at = NOW()
                RETURNING *
            """, (from_name, from_loc.get('latitude'), from_loc.get('longitude'),
                  to_name, to_loc.get('latitude'), to_loc.get('longitude'),
                  drive_minutes, notes))

            result = dict(cur.fetchone())

            if bidirectional:
                cur.execute("""
                    INSERT INTO known_routes (from_name, from_lat, from_lon, to_name, to_lat, to_lon, drive_minutes, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (from_name, to_name)
                    DO UPDATE SET drive_minutes = EXCLUDED.drive_minutes,
                                  notes = COALESCE(EXCLUDED.notes, known_routes.notes),
                                  updated_at = NOW()
                """, (to_name, to_loc.get('latitude'), to_loc.get('longitude'),
                      from_name, from_loc.get('latitude'), from_loc.get('longitude'),
                      drive_minutes, notes))

            conn.commit()
            self._known_routes_cache = None  # bust cache
            return result
        finally:
            conn.close()

    def _resolve_location(self, cur, name: str) -> dict:
        """Try to find coordinates for a location name."""
        cur.execute("""
            SELECT latitude, longitude FROM known_locations
            WHERE active = TRUE AND LOWER(name) LIKE LOWER(%s)
            LIMIT 1
        """, (f'%{name}%',))
        row = cur.fetchone()
        if row:
            return {'latitude': row['latitude'], 'longitude': row['longitude']}
        return {}

    def add_recurring(self, name: str, schedule_type: str, time_at: str,
                      location_name: str = None, days_of_week: list = None,
                      duration: int = 10, is_anchor: bool = True,
                      notes: str = None) -> dict:
        """Add a new recurring schedule item."""
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            location_id = None
            lat = None
            lon = None
            if location_name:
                cur.execute("""
                    SELECT id, latitude, longitude FROM known_locations
                    WHERE active = TRUE AND LOWER(name) LIKE LOWER(%s)
                    LIMIT 1
                """, (f'%{location_name}%',))
                loc = cur.fetchone()
                if loc:
                    location_id = loc['id']
                    lat = loc['latitude']
                    lon = loc['longitude']

            cur.execute("""
                INSERT INTO recurring_schedules
                    (name, schedule_type, days_of_week, time_at, location_id,
                     location_name, latitude, longitude, duration_minutes,
                     is_anchor, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (name, schedule_type, days_of_week, time_at, location_id,
                  location_name, lat, lon, duration, is_anchor, notes))
            conn.commit()
            return dict(cur.fetchone())
        finally:
            conn.close()

    def get_known_locations(self) -> List[dict]:
        """Return all active known locations."""
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT * FROM known_locations WHERE active = TRUE ORDER BY category, name")
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()


def format_schedule_telegram(schedule: dict) -> str:
    """Format a schedule dict into a nice Telegram message."""
    lines = []
    lines.append(f"📅 **{schedule['day_name']}, {schedule['date']}**")
    lines.append("")

    for stop in schedule['stops']:
        icon = '📌' if stop.get('is_anchor') else '🔸'
        source_tag = '' if stop['source'] == 'recurring' else ' _(errand)_'
        time_str = stop.get('time', 'Flexible')

        line = f"{icon} **{time_str}** — {stop['name']}{source_tag}"
        if stop.get('location') and stop['location'] != stop['name']:
            line += f"\n    📍 {stop['location']}"
        if stop.get('phone'):
            line += f"\n    📞 {stop['phone']}"
        if stop.get('drive_from_prev'):
            line += f"\n    🚗 {stop['drive_from_prev']} min drive (+{stop.get('reality_tax', 0)} buffer)"
        if stop.get('notes'):
            line += f"\n    ℹ️ {stop['notes']}"
        lines.append(line)

    if schedule.get('overflow'):
        lines.append("")
        lines.append("⚠️ **Couldn't fit today:**")
        for item in schedule['overflow']:
            lines.append(f"  • {item['name']} ({item.get('location', 'no location')})")

    if schedule.get('errands_pending', 0) > 0 and not schedule.get('optimized'):
        lines.append("")
        lines.append(f"💡 {schedule['errands_pending']} errand(s) pending — use /optimize to plan them")

    return '\n'.join(lines)
