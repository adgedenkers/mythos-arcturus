#!/usr/bin/env python3
"""
SEN-0002: Solar & Space Weather Ingestion Service
Pulls real-time data from NOAA DSCOVR, SWPC, and NASA DONKI APIs.
Runs as a systemd service polling on configurable intervals.
"""

import json
import logging
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
DB_USER = os.getenv("MYTHOS_DB_USER", "adge")
DB_HOST = os.getenv("MYTHOS_DB_HOST", "localhost")
DB_PORT = os.getenv("MYTHOS_DB_PORT", "5432")

NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")

# NOAA SWPC endpoints (no auth needed)
DSCOVR_PLASMA_URL = "https://services.swpc.noaa.gov/products/solar-wind/plasma-7-day.json"
DSCOVR_MAG_URL = "https://services.swpc.noaa.gov/products/solar-wind/mag-7-day.json"
KP_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
DST_URL = "https://services.swpc.noaa.gov/products/kyoto-dst.json"

# NASA DONKI endpoints
DONKI_CME_URL = "https://api.nasa.gov/DONKI/CME"
DONKI_FLR_URL = "https://api.nasa.gov/DONKI/FLR"

# Polling intervals (seconds)
SOLAR_WIND_INTERVAL = 300    # 5 minutes
GEOMAG_INTERVAL = 600        # 10 minutes
DONKI_INTERVAL = 3600        # 1 hour (CMEs/flares don't change fast)

# Event detection thresholds
HIGH_SPEED_THRESHOLD = 600   # km/s
SHOCK_SPEED_JUMP = 150       # km/s in 30 minutes
SHOCK_WINDOW = 1800          # 30 minutes in seconds

LOG_DIR = "/opt/mythos/logs"
LOG_FILE = os.path.join(LOG_DIR, "solar_ingest.log")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("solar_ingest")

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def get_db():
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, host=DB_HOST, port=DB_PORT
    )


def upsert_solar_wind(conn, rows):
    """Bulk upsert solar wind readings."""
    if not rows:
        return 0
    sql = """
        INSERT INTO solar_wind_readings 
            (timestamp, speed, density, temperature, bx, by, bz, bt, source)
        VALUES (%(timestamp)s, %(speed)s, %(density)s, %(temperature)s, 
                %(bx)s, %(by)s, %(bz)s, %(bt)s, %(source)s)
        ON CONFLICT (source, timestamp) DO NOTHING
    """
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(cur, sql, rows, page_size=500)
    conn.commit()
    return len(rows)


def upsert_geomag(conn, rows):
    """Bulk upsert geomagnetic index readings."""
    if not rows:
        return 0
    sql = """
        INSERT INTO geomagnetic_indices 
            (timestamp, index_type, value, storm_level, source)
        VALUES (%(timestamp)s, %(index_type)s, %(value)s, %(storm_level)s, %(source)s)
        ON CONFLICT (index_type, timestamp, source) DO NOTHING
    """
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(cur, sql, rows, page_size=500)
    conn.commit()
    return len(rows)


def upsert_flares(conn, rows):
    """Bulk upsert solar flare events."""
    if not rows:
        return 0
    sql = """
        INSERT INTO solar_flares 
            (flare_id, begin_time, peak_time, end_time, class_type, class_value,
             source_location, active_region, linked_events, source)
        VALUES (%(flare_id)s, %(begin_time)s, %(peak_time)s, %(end_time)s, 
                %(class_type)s, %(class_value)s, %(source_location)s, 
                %(active_region)s, %(linked_events)s, %(source)s)
        ON CONFLICT (flare_id) DO UPDATE SET
            end_time = EXCLUDED.end_time,
            linked_events = EXCLUDED.linked_events
    """
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(cur, sql, rows)
    conn.commit()
    return len(rows)


def upsert_cmes(conn, rows):
    """Bulk upsert CME events."""
    if not rows:
        return 0
    sql = """
        INSERT INTO cme_events 
            (cme_id, start_time, latitude, longitude, half_angle, speed, type,
             is_earth_directed, predicted_arrival, note, linked_events, source)
        VALUES (%(cme_id)s, %(start_time)s, %(latitude)s, %(longitude)s, 
                %(half_angle)s, %(speed)s, %(type)s, %(is_earth_directed)s,
                %(predicted_arrival)s, %(note)s, %(linked_events)s, %(source)s)
        ON CONFLICT (cme_id) DO UPDATE SET
            predicted_arrival = EXCLUDED.predicted_arrival,
            is_earth_directed = EXCLUDED.is_earth_directed,
            linked_events = EXCLUDED.linked_events
    """
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(cur, sql, rows)
    conn.commit()
    return len(rows)


def insert_solar_wind_event(conn, event):
    """Insert a detected solar wind event."""
    sql = """
        INSERT INTO solar_wind_events 
            (event_type, start_time, peak_speed, peak_density, peak_bt, min_bz, notes)
        VALUES (%(event_type)s, %(start_time)s, %(peak_speed)s, %(peak_density)s,
                %(peak_bt)s, %(min_bz)s, %(notes)s)
    """
    with conn.cursor() as cur:
        cur.execute(sql, event)
    conn.commit()


# ---------------------------------------------------------------------------
# NOAA Data Fetchers
# ---------------------------------------------------------------------------

def safe_float(val):
    """Convert to float or None."""
    if val is None or val == '' or val == 'null':
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def parse_noaa_timestamp(ts_str):
    """Parse NOAA timestamp format '2026-03-13 14:30:00.000'."""
    if not ts_str:
        return None
    try:
        # Strip milliseconds if present
        ts_str = ts_str.strip()
        for fmt in ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
            try:
                dt = datetime.strptime(ts_str, fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        return None
    except Exception:
        return None


def fetch_solar_wind():
    """Fetch DSCOVR plasma + mag data from NOAA SWPC."""
    rows = []
    try:
        # Fetch plasma (speed, density, temperature)
        plasma_resp = requests.get(DSCOVR_PLASMA_URL, timeout=30)
        plasma_resp.raise_for_status()
        plasma_data = plasma_resp.json()

        # Fetch magnetic field (bx, by, bz, bt)
        mag_resp = requests.get(DSCOVR_MAG_URL, timeout=30)
        mag_resp.raise_for_status()
        mag_data = mag_resp.json()

        # Index mag data by timestamp for joining
        mag_by_ts = {}
        for row in mag_data[1:]:  # skip header
            ts = row[0]
            mag_by_ts[ts] = {
                'bx': safe_float(row[1]),
                'by': safe_float(row[2]),
                'bz': safe_float(row[3]),
                'bt': safe_float(row[6]) if len(row) > 6 else None,
            }

        # Merge plasma + mag
        for row in plasma_data[1:]:  # skip header
            ts_str = row[0]
            ts = parse_noaa_timestamp(ts_str)
            if not ts:
                continue

            mag = mag_by_ts.get(ts_str, {})

            rows.append({
                'timestamp': ts,
                'speed': safe_float(row[1]),
                'density': safe_float(row[2]),
                'temperature': safe_float(row[3]),
                'bx': mag.get('bx'),
                'by': mag.get('by'),
                'bz': mag.get('bz'),
                'bt': mag.get('bt'),
                'source': 'DSCOVR',
            })

        log.info(f"Fetched {len(rows)} solar wind readings from DSCOVR")
    except Exception as e:
        log.error(f"Solar wind fetch failed: {e}")

    return rows


def kp_to_storm_level(kp):
    """Convert Kp to NOAA storm level."""
    if kp is None:
        return None
    kp = float(kp)
    if kp >= 9:
        return 'G5'
    elif kp >= 8:
        return 'G4'
    elif kp >= 7:
        return 'G3'
    elif kp >= 6:
        return 'G2'
    elif kp >= 5:
        return 'G1'
    return None


def fetch_geomagnetic():
    """Fetch Kp and Dst indices from NOAA SWPC."""
    rows = []
    try:
        # Kp index
        kp_resp = requests.get(KP_URL, timeout=30)
        kp_resp.raise_for_status()
        kp_data = kp_resp.json()

        for row in kp_data[1:]:  # skip header
            ts = parse_noaa_timestamp(row[0])
            kp_val = safe_float(row[1])
            if ts and kp_val is not None:
                rows.append({
                    'timestamp': ts,
                    'index_type': 'Kp',
                    'value': kp_val,
                    'storm_level': kp_to_storm_level(kp_val),
                    'source': 'SWPC',
                })

        log.info(f"Fetched {len(rows)} Kp readings")
    except Exception as e:
        log.error(f"Kp fetch failed: {e}")

    try:
        # Dst index
        dst_resp = requests.get(DST_URL, timeout=30)
        dst_resp.raise_for_status()
        dst_data = dst_resp.json()

        dst_count = 0
        for row in dst_data[1:]:  # skip header
            ts = parse_noaa_timestamp(row[0])
            dst_val = safe_float(row[1])
            if ts and dst_val is not None:
                rows.append({
                    'timestamp': ts,
                    'index_type': 'Dst',
                    'value': dst_val,
                    'storm_level': None,
                    'source': 'SWPC',
                })
                dst_count += 1

        log.info(f"Fetched {dst_count} Dst readings")
    except Exception as e:
        log.error(f"Dst fetch failed: {e}")

    return rows


# ---------------------------------------------------------------------------
# NASA DONKI Fetchers
# ---------------------------------------------------------------------------

def fetch_donki_flares():
    """Fetch solar flares from NASA DONKI (last 30 days)."""
    rows = []
    try:
        start = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
        params = {
            'startDate': start,
            'api_key': NASA_API_KEY,
        }
        resp = requests.get(DONKI_FLR_URL, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        for flare in data:
            flare_id = flare.get('flrID', '')
            class_full = flare.get('classType', '')
            class_type = class_full[0] if class_full else None
            class_value = None
            if class_full and len(class_full) > 1:
                try:
                    class_value = float(class_full[1:])
                except ValueError:
                    pass

            linked = flare.get('linkedEvents', [])

            rows.append({
                'flare_id': flare_id,
                'begin_time': flare.get('beginTime'),
                'peak_time': flare.get('peakTime'),
                'end_time': flare.get('endTime'),
                'class_type': class_type,
                'class_value': class_value,
                'source_location': flare.get('sourceLocation'),
                'active_region': flare.get('activeRegionNum'),
                'linked_events': json.dumps(linked) if linked else None,
                'source': 'DONKI',
            })

        log.info(f"Fetched {len(rows)} solar flares from DONKI")
    except Exception as e:
        log.error(f"DONKI flare fetch failed: {e}")

    return rows


def fetch_donki_cmes():
    """Fetch CMEs from NASA DONKI (last 30 days)."""
    rows = []
    try:
        start = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
        params = {
            'startDate': start,
            'api_key': NASA_API_KEY,
        }
        resp = requests.get(DONKI_CME_URL, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        for cme in data:
            cme_id = cme.get('activityID', '')
            
            # Check for Earth-directed analysis
            is_earth_directed = False
            predicted_arrival = None
            analyses = cme.get('cmeAnalyses', [])
            if analyses:
                for analysis in analyses:
                    if analysis.get('isMostAccurate'):
                        is_earth_directed = analysis.get('enlilList') is not None
                        # Check for Earth impact in enlil results
                        enlil = analysis.get('enlilList', [])
                        if enlil:
                            for e in enlil:
                                impacts = e.get('impactList', [])
                                for impact in impacts:
                                    if impact.get('location', '').lower() == 'earth':
                                        is_earth_directed = True
                                        predicted_arrival = impact.get('arrivalTime')
                        break

            linked = cme.get('linkedEvents', [])

            rows.append({
                'cme_id': cme_id,
                'start_time': cme.get('startTime'),
                'latitude': safe_float(cme.get('latitude')),
                'longitude': safe_float(cme.get('longitude')),
                'half_angle': safe_float(cme.get('halfAngle')),
                'speed': safe_float(cme.get('speed')),
                'type': cme.get('type'),
                'is_earth_directed': is_earth_directed,
                'predicted_arrival': predicted_arrival,
                'note': cme.get('note', '')[:500] if cme.get('note') else None,
                'linked_events': json.dumps(linked) if linked else None,
                'source': 'DONKI',
            })

        log.info(f"Fetched {len(rows)} CMEs from DONKI")
    except Exception as e:
        log.error(f"DONKI CME fetch failed: {e}")

    return rows


# ---------------------------------------------------------------------------
# Event Detection
# ---------------------------------------------------------------------------

def detect_solar_wind_events(conn):
    """Check recent solar wind data for high-speed streams and shocks."""
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # Get last 2 hours of readings for event detection
            cur.execute("""
                SELECT timestamp, speed, density, bt, bz
                FROM solar_wind_readings
                WHERE timestamp > NOW() - INTERVAL '2 hours'
                  AND speed IS NOT NULL
                ORDER BY timestamp ASC
            """)
            readings = cur.fetchall()

            if len(readings) < 2:
                return

            latest = readings[-1]

            # High-speed stream detection
            if latest['speed'] and latest['speed'] > HIGH_SPEED_THRESHOLD:
                # Check if we already logged this event recently
                cur.execute("""
                    SELECT id FROM solar_wind_events
                    WHERE event_type = 'high_speed_stream'
                      AND start_time > NOW() - INTERVAL '6 hours'
                """)
                if not cur.fetchone():
                    insert_solar_wind_event(conn, {
                        'event_type': 'high_speed_stream',
                        'start_time': latest['timestamp'],
                        'peak_speed': latest['speed'],
                        'peak_density': latest['density'],
                        'peak_bt': latest['bt'],
                        'min_bz': latest['bz'],
                        'notes': f"Speed {latest['speed']:.0f} km/s exceeded {HIGH_SPEED_THRESHOLD} km/s threshold",
                    })
                    log.warning(f"HIGH-SPEED STREAM detected: {latest['speed']:.0f} km/s")

            # Shock detection (speed jump > 150 km/s in 30 min)
            for i in range(len(readings) - 1):
                r1 = readings[i]
                r2 = readings[i + 1]
                if not (r1['speed'] and r2['speed']):
                    continue
                
                dt = (r2['timestamp'] - r1['timestamp']).total_seconds()
                if dt <= 0 or dt > SHOCK_WINDOW:
                    continue

                speed_jump = r2['speed'] - r1['speed']
                if speed_jump > SHOCK_SPEED_JUMP:
                    cur.execute("""
                        SELECT id FROM solar_wind_events
                        WHERE event_type = 'shock'
                          AND start_time > NOW() - INTERVAL '2 hours'
                    """)
                    if not cur.fetchone():
                        insert_solar_wind_event(conn, {
                            'event_type': 'shock',
                            'start_time': r2['timestamp'],
                            'peak_speed': r2['speed'],
                            'peak_density': r2['density'],
                            'peak_bt': r2['bt'],
                            'min_bz': r2['bz'],
                            'notes': f"Speed jump {speed_jump:.0f} km/s in {dt/60:.0f} min",
                        })
                        log.warning(f"SHOCK detected: +{speed_jump:.0f} km/s in {dt/60:.0f} min")

    except Exception as e:
        log.error(f"Event detection failed: {e}")


# ---------------------------------------------------------------------------
# Telegram Summary Helper
# ---------------------------------------------------------------------------

def get_current_conditions(conn):
    """Get a formatted summary of current solar/space weather conditions."""
    lines = []
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # Latest solar wind
            cur.execute("""
                SELECT speed, density, temperature, bz, bt, timestamp
                FROM solar_wind_readings 
                WHERE speed IS NOT NULL
                ORDER BY timestamp DESC LIMIT 1
            """)
            sw = cur.fetchone()
            if sw:
                lines.append("☀️ **Solar Wind**")
                lines.append(f"  Speed: {sw['speed']:.0f} km/s")
                lines.append(f"  Density: {sw['density']:.1f} p/cm³")
                if sw['bz'] is not None:
                    lines.append(f"  Bz: {sw['bz']:.1f} nT {'⚠️' if sw['bz'] < -10 else ''}")
                if sw['bt'] is not None:
                    lines.append(f"  Bt: {sw['bt']:.1f} nT")
                lines.append(f"  _Updated: {sw['timestamp'].strftime('%H:%M UTC')}_")
                lines.append("")

            # Latest Kp
            cur.execute("""
                SELECT value, storm_level, timestamp
                FROM geomagnetic_indices 
                WHERE index_type = 'Kp'
                ORDER BY timestamp DESC LIMIT 1
            """)
            kp = cur.fetchone()
            if kp:
                storm = f" ({kp['storm_level']})" if kp['storm_level'] else ""
                lines.append(f"🧲 **Kp Index:** {kp['value']:.1f}{storm}")

            # Latest Dst
            cur.execute("""
                SELECT value, timestamp
                FROM geomagnetic_indices 
                WHERE index_type = 'Dst'
                ORDER BY timestamp DESC LIMIT 1
            """)
            dst = cur.fetchone()
            if dst:
                lines.append(f"🧲 **Dst Index:** {dst['value']:.0f} nT")

            lines.append("")

            # Recent flares (last 48h)
            cur.execute("""
                SELECT class_type, class_value, peak_time
                FROM solar_flares
                WHERE peak_time > NOW() - INTERVAL '48 hours'
                ORDER BY peak_time DESC LIMIT 5
            """)
            flares = cur.fetchall()
            if flares:
                lines.append("🔥 **Recent Flares (48h)**")
                for f in flares:
                    cls = f"{f['class_type']}{f['class_value']:.1f}" if f['class_value'] else f['class_type']
                    lines.append(f"  {cls} — {f['peak_time'].strftime('%Y-%m-%d %H:%M UTC')}")
                lines.append("")

            # Recent CMEs (Earth-directed, last 7 days)
            cur.execute("""
                SELECT start_time, speed, is_earth_directed, predicted_arrival
                FROM cme_events
                WHERE start_time > NOW() - INTERVAL '7 days'
                ORDER BY start_time DESC LIMIT 5
            """)
            cmes = cur.fetchall()
            if cmes:
                lines.append("💨 **Recent CMEs (7d)**")
                for c in cmes:
                    earth = " 🎯 EARTH-DIRECTED" if c['is_earth_directed'] else ""
                    spd = f" {c['speed']:.0f} km/s" if c['speed'] else ""
                    arrival = ""
                    if c['predicted_arrival']:
                        arrival = f" → ETA {c['predicted_arrival'].strftime('%m/%d %H:%M UTC')}"
                    lines.append(f"  {c['start_time'].strftime('%m/%d %H:%M')}{spd}{earth}{arrival}")
                lines.append("")

            # Recent events
            cur.execute("""
                SELECT event_type, start_time, peak_speed, notes
                FROM solar_wind_events
                WHERE start_time > NOW() - INTERVAL '24 hours'
                ORDER BY start_time DESC LIMIT 3
            """)
            events = cur.fetchall()
            if events:
                lines.append("⚡ **Detected Events (24h)**")
                for e in events:
                    lines.append(f"  {e['event_type']}: {e['notes']}")

    except Exception as e:
        log.error(f"Conditions summary failed: {e}")
        lines.append("Error reading conditions")

    return "\n".join(lines) if lines else "No solar data available yet."


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
    log.info("Solar & Space Weather Ingestion Service starting")

    last_solar_wind = 0
    last_geomag = 0
    last_donki = 0

    while _running:
        now = time.time()
        conn = None

        try:
            conn = get_db()

            # Solar wind (every 5 min)
            if now - last_solar_wind >= SOLAR_WIND_INTERVAL:
                rows = fetch_solar_wind()
                if rows:
                    count = upsert_solar_wind(conn, rows)
                    log.info(f"Upserted {count} solar wind readings")
                    detect_solar_wind_events(conn)
                last_solar_wind = now

            # Geomagnetic indices (every 10 min)
            if now - last_geomag >= GEOMAG_INTERVAL:
                rows = fetch_geomagnetic()
                if rows:
                    count = upsert_geomag(conn, rows)
                    log.info(f"Upserted {count} geomagnetic readings")
                last_geomag = now

            # DONKI CMEs + flares (every hour)
            if now - last_donki >= DONKI_INTERVAL:
                flares = fetch_donki_flares()
                if flares:
                    count = upsert_flares(conn, flares)
                    log.info(f"Upserted {count} solar flares")

                cmes = fetch_donki_cmes()
                if cmes:
                    count = upsert_cmes(conn, cmes)
                    log.info(f"Upserted {count} CMEs")

                last_donki = now

        except Exception as e:
            log.error(f"Main loop error: {e}")
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

        # Sleep in small increments to catch shutdown signals
        for _ in range(30):
            if not _running:
                break
            time.sleep(1)

    log.info("Solar ingestion service stopped")


if __name__ == "__main__":
    run()
