#!/usr/bin/env python3
"""
SEN-0003: Earthquake Ingestion Service
Pulls from USGS Earthquake API (GeoJSON), detects clusters, finds antipodal pairs.
"""

import json
import logging
import math
import os
import signal
import sys
import time
from datetime import datetime, timezone, timedelta

import psycopg2
import psycopg2.extras
import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DB_NAME = os.getenv("MYTHOS_DB", "mythos")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "/var/run/postgresql")
DB_PORT = os.getenv("MYTHOS_DB_PORT", "5432")

# USGS endpoints (no auth needed)
USGS_FEED_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
USGS_SIGNIFICANT_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.geojson"

# Polling
POLL_INTERVAL = 600          # 10 minutes
SIGNIFICANT_INTERVAL = 3600  # 1 hour

# Cluster detection
CLUSTER_DISTANCE_KM = 400
CLUSTER_TIME_HOURS = 24

# Antipodal search
ANTIPODAL_RADIUS_KM = 200
ANTIPODAL_TIME_HOURS = 48

LOG_DIR = "/opt/mythos/logs"
LOG_FILE = os.path.join(LOG_DIR, "seismic_ingest.log")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("seismic_ingest")


# ---------------------------------------------------------------------------
# Geo Math
# ---------------------------------------------------------------------------

def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance between two points in km."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def get_db():
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, host=DB_HOST, port=DB_PORT
    )


def upsert_earthquakes(conn, quakes):
    """Bulk upsert earthquake events. Returns count of new inserts."""
    if not quakes:
        return 0
    sql = """
        INSERT INTO earthquakes 
            (usgs_id, timestamp, latitude, longitude, depth, magnitude, mag_type,
             place, status, tsunami, felt, alert, significance, source)
        VALUES (%(usgs_id)s, %(timestamp)s, %(latitude)s, %(longitude)s, %(depth)s,
                %(magnitude)s, %(mag_type)s, %(place)s, %(status)s, %(tsunami)s,
                %(felt)s, %(alert)s, %(significance)s, %(source)s)
        ON CONFLICT (usgs_id) DO UPDATE SET
            magnitude = EXCLUDED.magnitude,
            status = EXCLUDED.status,
            felt = EXCLUDED.felt,
            alert = EXCLUDED.alert,
            significance = EXCLUDED.significance
    """
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(cur, sql, quakes, page_size=200)
    conn.commit()
    return len(quakes)


# ---------------------------------------------------------------------------
# USGS Fetcher
# ---------------------------------------------------------------------------

def fetch_earthquakes(url=USGS_FEED_URL):
    """Fetch earthquake data from USGS GeoJSON feed."""
    quakes = []
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        features = data.get('features', [])
        for f in features:
            props = f.get('properties', {})
            geom = f.get('geometry', {})
            coords = geom.get('coordinates', [None, None, None])

            # USGS uses milliseconds since epoch
            ts_ms = props.get('time')
            ts = None
            if ts_ms:
                ts = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)

            mag = props.get('mag')
            if not ts or mag is None:
                continue

            quakes.append({
                'usgs_id': f.get('id', ''),
                'timestamp': ts,
                'longitude': coords[0],
                'latitude': coords[1],
                'depth': coords[2],
                'magnitude': mag,
                'mag_type': props.get('magType'),
                'place': props.get('place', '')[:200],
                'status': props.get('status'),
                'tsunami': bool(props.get('tsunami', 0)),
                'felt': props.get('felt'),
                'alert': props.get('alert'),
                'significance': props.get('sig'),
                'source': 'USGS',
            })

        log.info(f"Fetched {len(quakes)} earthquakes from USGS")
    except Exception as e:
        log.error(f"USGS fetch failed: {e}")

    return quakes


# ---------------------------------------------------------------------------
# Cluster Detection
# ---------------------------------------------------------------------------

def detect_clusters(conn):
    """Find earthquake clusters: events within 400km and 24h of each other."""
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # Get recent unclustered quakes (last 48h)
            cur.execute("""
                SELECT id, timestamp, latitude, longitude, magnitude
                FROM earthquakes
                WHERE timestamp > NOW() - INTERVAL '48 hours'
                  AND cluster_id IS NULL
                ORDER BY timestamp ASC
            """)
            quakes = cur.fetchall()

            if len(quakes) < 2:
                return

            # Simple greedy clustering
            assigned = set()
            clusters_formed = 0

            for i, q1 in enumerate(quakes):
                if q1['id'] in assigned:
                    continue

                members = [q1]
                for j, q2 in enumerate(quakes):
                    if i == j or q2['id'] in assigned:
                        continue

                    dist = haversine_km(
                        q1['latitude'], q1['longitude'],
                        q2['latitude'], q2['longitude']
                    )
                    time_diff = abs((q2['timestamp'] - q1['timestamp']).total_seconds()) / 3600

                    if dist < CLUSTER_DISTANCE_KM and time_diff < CLUSTER_TIME_HOURS:
                        members.append(q2)

                if len(members) >= 3:
                    # Create cluster
                    center_lat = sum(m['latitude'] for m in members) / len(members)
                    center_lon = sum(m['longitude'] for m in members) / len(members)
                    max_mag = max(m['magnitude'] for m in members)
                    start = min(m['timestamp'] for m in members)
                    end = max(m['timestamp'] for m in members)
                    region = members[0].get('place', 'Unknown') if hasattr(members[0], 'get') else 'Unknown'

                    # Check place field
                    cur.execute("""
                        SELECT place FROM earthquakes WHERE id = %s
                    """, (members[0]['id'],))
                    row = cur.fetchone()
                    region = row['place'] if row else 'Unknown'

                    cur.execute("""
                        INSERT INTO seismic_clusters 
                            (start_time, end_time, center_lat, center_lon, 
                             event_count, max_magnitude, region)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (start, end, center_lat, center_lon,
                          len(members), max_mag, region))
                    cluster_id = cur.fetchone()['id']

                    # Assign members
                    member_ids = [m['id'] for m in members]
                    cur.execute("""
                        UPDATE earthquakes SET cluster_id = %s
                        WHERE id = ANY(%s)
                    """, (cluster_id, member_ids))

                    assigned.update(member_ids)
                    clusters_formed += 1

                    log.info(
                        f"Cluster #{cluster_id}: {len(members)} events, "
                        f"M{max_mag:.1f} max, near {region}"
                    )

            conn.commit()
            if clusters_formed:
                log.info(f"Formed {clusters_formed} new clusters")

    except Exception as e:
        log.error(f"Cluster detection failed: {e}")
        conn.rollback()


# ---------------------------------------------------------------------------
# Antipodal Detection
# ---------------------------------------------------------------------------

def find_antipodal_pairs(conn):
    """Find earthquakes near the antipodal point of other recent quakes."""
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # Get recent quakes with antipodes computed
            cur.execute("""
                SELECT id, timestamp, latitude, longitude, 
                       antipode_lat, antipode_lon, magnitude
                FROM earthquakes
                WHERE timestamp > NOW() - INTERVAL '7 days'
                  AND antipode_lat IS NOT NULL
                ORDER BY timestamp DESC
            """)
            quakes = cur.fetchall()

            pairs_found = 0
            for q1 in quakes:
                # Find quakes near q1's antipode within time window
                cur.execute("""
                    SELECT id, timestamp, latitude, longitude, magnitude
                    FROM earthquakes
                    WHERE id != %s
                      AND timestamp BETWEEN %s AND %s
                      AND ABS(latitude - %s) < 3
                      AND ABS(longitude - %s) < 3
                """, (
                    q1['id'],
                    q1['timestamp'] - timedelta(hours=ANTIPODAL_TIME_HOURS),
                    q1['timestamp'] + timedelta(hours=ANTIPODAL_TIME_HOURS),
                    q1['antipode_lat'],
                    q1['antipode_lon'],
                ))
                candidates = cur.fetchall()

                for q2 in candidates:
                    dist = haversine_km(
                        q2['latitude'], q2['longitude'],
                        q1['antipode_lat'], q1['antipode_lon']
                    )
                    if dist < ANTIPODAL_RADIUS_KM:
                        time_diff = abs(
                            (q2['timestamp'] - q1['timestamp']).total_seconds()
                        ) / 3600

                        # Use consistent ordering (lower id first)
                        a_id = min(q1['id'], q2['id'])
                        b_id = max(q1['id'], q2['id'])

                        cur.execute("""
                            INSERT INTO antipodal_pairs 
                                (earthquake_a_id, earthquake_b_id, distance_km, time_diff_hours)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (earthquake_a_id, earthquake_b_id) DO NOTHING
                        """, (a_id, b_id, dist, time_diff))
                        pairs_found += 1

            conn.commit()
            if pairs_found:
                log.info(f"Found {pairs_found} antipodal pairs")

    except Exception as e:
        log.error(f"Antipodal detection failed: {e}")
        conn.rollback()


# ---------------------------------------------------------------------------
# Telegram Summary
# ---------------------------------------------------------------------------

def get_seismic_summary(conn):
    """Get formatted summary of recent seismic activity."""
    lines = []
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # Recent significant quakes (M5+ in 24h)
            cur.execute("""
                SELECT magnitude, place, depth, timestamp, alert
                FROM earthquakes
                WHERE timestamp > NOW() - INTERVAL '24 hours'
                  AND magnitude >= 5.0
                ORDER BY magnitude DESC LIMIT 10
            """)
            big = cur.fetchall()

            if big:
                lines.append("🔴 **Significant (M5+, 24h)**")
                for q in big:
                    alert_icon = {'green': '🟢', 'yellow': '🟡', 'orange': '🟠', 'red': '🔴'}.get(q['alert'], '')
                    lines.append(
                        f"  M{q['magnitude']:.1f} — {q['place']} "
                        f"({q['depth']:.0f}km deep) {alert_icon}"
                    )
                lines.append("")

            # Count by magnitude range (24h)
            cur.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE magnitude >= 6) as m6plus,
                    COUNT(*) FILTER (WHERE magnitude >= 5 AND magnitude < 6) as m5,
                    COUNT(*) FILTER (WHERE magnitude >= 4 AND magnitude < 5) as m4,
                    COUNT(*) FILTER (WHERE magnitude >= 2.5 AND magnitude < 4) as m2_5
                FROM earthquakes
                WHERE timestamp > NOW() - INTERVAL '24 hours'
            """)
            counts = cur.fetchone()
            lines.append("📊 **Last 24h Summary**")
            lines.append(f"  M6+: {counts['m6plus']} | M5: {counts['m5']} | M4: {counts['m4']} | M2.5: {counts['m2_5']}")
            lines.append("")

            # Active clusters
            cur.execute("""
                SELECT event_count, max_magnitude, region, start_time
                FROM seismic_clusters
                WHERE is_active = TRUE
                  AND start_time > NOW() - INTERVAL '48 hours'
                ORDER BY max_magnitude DESC LIMIT 5
            """)
            clusters = cur.fetchall()
            if clusters:
                lines.append("📍 **Active Clusters**")
                for c in clusters:
                    lines.append(
                        f"  {c['event_count']} events (M{c['max_magnitude']:.1f} max) — "
                        f"{c['region']}"
                    )
                lines.append("")

            # Antipodal pairs (last 7 days)
            cur.execute("""
                SELECT COUNT(*) as cnt FROM antipodal_pairs
                WHERE created_at > NOW() - INTERVAL '7 days'
            """)
            ap = cur.fetchone()
            if ap['cnt'] > 0:
                lines.append(f"🔄 **Antipodal Pairs (7d):** {ap['cnt']} detected")

            # Total in database
            cur.execute("SELECT COUNT(*) as total FROM earthquakes")
            total = cur.fetchone()
            lines.append(f"\n_Total earthquakes tracked: {total['total']:,}_")

    except Exception as e:
        log.error(f"Seismic summary failed: {e}")
        lines.append("Error reading seismic data")

    return "\n".join(lines) if lines else "No seismic data available yet."


# ---------------------------------------------------------------------------
# Main Loop
# ---------------------------------------------------------------------------

_running = True

def _shutdown(signum, frame):
    global _running
    log.info("Shutdown signal received")
    _running = False

signal.signal(signal.SIGTERM, _shutdown)
signal.signal(signal.SIGINT, _shutdown)


def run():
    global _running
    log.info("Earthquake Ingestion Service starting")

    last_poll = 0
    last_significant = 0

    while _running:
        now = time.time()
        conn = None

        try:
            conn = get_db()

            # Regular feed (every 10 min)
            if now - last_poll >= POLL_INTERVAL:
                quakes = fetch_earthquakes(USGS_FEED_URL)
                if quakes:
                    count = upsert_earthquakes(conn, quakes)
                    log.info(f"Upserted {count} earthquakes")
                    detect_clusters(conn)
                    find_antipodal_pairs(conn)
                last_poll = now

            # Significant events (every hour)
            if now - last_significant >= SIGNIFICANT_INTERVAL:
                sig_quakes = fetch_earthquakes(USGS_SIGNIFICANT_URL)
                if sig_quakes:
                    count = upsert_earthquakes(conn, sig_quakes)
                    log.info(f"Upserted {count} significant earthquakes")
                last_significant = now

        except Exception as e:
            log.error(f"Main loop error: {e}")
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

        for _ in range(30):
            if not _running:
                break
            time.sleep(1)

    log.info("Earthquake ingestion service stopped")


if __name__ == "__main__":
    run()
