"""
Observatory Graph Builder
SEN-0005 — Mythos SENSUS stream

Builds and maintains Neo4j nodes for the observatory domain:
  - SolarEvent      (flares, CMEs, solar wind spikes, geomagnetic storms)
  - SeismicEvent    (individual earthquakes M4+)
  - SeismicCluster  (USGS-detected earthquake clusters)
  - PlanetaryAlignment (significant aspect configurations)

Temporal relationships:
  PRECEDED_BY / FOLLOWED_BY  (ordered time links between events)
  CONCURRENT_WITH            (within ±6h window)
  HAS_MEMBER                 (cluster → earthquakes)

Runs on startup (3-day backfill) then hourly sync.
"""

import logging
import os
import time
from datetime import datetime, timezone, timedelta

import psycopg2
import psycopg2.extras
from neo4j import GraphDatabase

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
log = logging.getLogger(__name__)

# ─── Config ───────────────────────────────────────────────────────────────────

PG_DSN = os.environ.get('DATABASE_URL', 'postgresql://mythos:mythos@localhost/mythos')
NEO4J_URI = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.environ.get('NEO4J_USER', 'neo4j')
NEO4J_PASS = os.environ.get('NEO4J_PASSWORD', 'mythos')

BACKFILL_DAYS = 3
CONCURRENT_WINDOW_HOURS = 6
SYNC_INTERVAL_SECONDS = 3600  # 1 hour


# ─── Database connections ──────────────────────────────────────────────────────

def pg_connect():
    return psycopg2.connect(PG_DSN)


def neo4j_connect():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))


# ─── Schema bootstrap ─────────────────────────────────────────────────────────

CONSTRAINTS = [
    "CREATE CONSTRAINT obs_solar_event_id IF NOT EXISTS FOR (n:SolarEvent) REQUIRE n.event_id IS UNIQUE",
    "CREATE CONSTRAINT obs_seismic_event_id IF NOT EXISTS FOR (n:SeismicEvent) REQUIRE n.event_id IS UNIQUE",
    "CREATE CONSTRAINT obs_seismic_cluster_id IF NOT EXISTS FOR (n:SeismicCluster) REQUIRE n.cluster_id IS UNIQUE",
    "CREATE CONSTRAINT obs_planetary_align_id IF NOT EXISTS FOR (n:PlanetaryAlignment) REQUIRE n.alignment_id IS UNIQUE",
]

def ensure_schema(driver):
    with driver.session() as session:
        for cypher in CONSTRAINTS:
            try:
                session.run(cypher)
            except Exception as e:
                log.warning(f"Constraint (may already exist): {e}")
    log.info("Neo4j observatory schema verified")


# ─── Solar Events ─────────────────────────────────────────────────────────────

def sync_solar_events(pg_conn, driver, since: datetime):
    """
    Upsert SolarEvent nodes from:
      - solar_flares table
      - solar_wind_readings where speed > 500 km/s (fast stream events)
      - geomagnetic_indices where kp >= 4 (storm watch) or dst <= -30 (moderate storm)
    """
    upserted = 0
    cur = pg_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Flares
    cur.execute("""
        SELECT id, timestamp, class_letter, class_scale, peak_flux,
               active_region, source_location
        FROM solar_flares
        WHERE timestamp >= %s
        ORDER BY timestamp
    """, (since,))
    flares = cur.fetchall()

    with driver.session() as session:
        for f in flares:
            event_id = f"flare_{f['id']}"
            session.run("""
                MERGE (e:SolarEvent {event_id: $event_id})
                SET e.type = 'FLARE',
                    e.timestamp = $timestamp,
                    e.class_letter = $class_letter,
                    e.class_scale = $class_scale,
                    e.peak_flux = $peak_flux,
                    e.active_region = $active_region,
                    e.source_location = $source_location,
                    e.label = $label,
                    e.updated_at = datetime()
            """, {
                'event_id': event_id,
                'timestamp': f['timestamp'].isoformat(),
                'class_letter': f['class_letter'],
                'class_scale': f['class_scale'],
                'peak_flux': f['peak_flux'],
                'active_region': f['active_region'],
                'source_location': f['source_location'],
                'label': f"{f['class_letter']}{f['class_scale'] or ''} Flare"
            })
            upserted += 1

    # Solar wind speed spikes (>500 km/s sustained = notable event)
    # Group readings within 2h of each other as one event — use first reading's id
    cur.execute("""
        WITH speed_events AS (
            SELECT id, timestamp, speed, density, bz,
                   LAG(timestamp) OVER (ORDER BY timestamp) AS prev_ts
            FROM solar_wind_readings
            WHERE speed > 500 AND timestamp >= %s
        )
        SELECT id, timestamp, speed, density, bz
        FROM speed_events
        WHERE prev_ts IS NULL OR timestamp - prev_ts > interval '2 hours'
        ORDER BY timestamp
    """, (since,))
    speed_spikes = cur.fetchall()

    with driver.session() as session:
        for s in speed_spikes:
            event_id = f"sw_spike_{s['id']}"
            label = f"Solar Wind Spike {int(s['speed'] or 0)} km/s"
            session.run("""
                MERGE (e:SolarEvent {event_id: $event_id})
                SET e.type = 'SOLAR_WIND_SPIKE',
                    e.timestamp = $timestamp,
                    e.speed_kms = $speed,
                    e.density = $density,
                    e.bz = $bz,
                    e.label = $label,
                    e.updated_at = datetime()
            """, {
                'event_id': event_id,
                'timestamp': s['timestamp'].isoformat(),
                'speed': s['speed'],
                'density': s['density'],
                'bz': s['bz'],
                'label': label,
            })
            upserted += 1

    # Geomagnetic storms (Kp >= 4)
    cur.execute("""
        WITH kp_events AS (
            SELECT id, timestamp, kp_index, dst_index,
                   LAG(timestamp) OVER (ORDER BY timestamp) AS prev_ts
            FROM geomagnetic_indices
            WHERE kp_index >= 4 AND timestamp >= %s
        )
        SELECT id, timestamp, kp_index, dst_index
        FROM kp_events
        WHERE prev_ts IS NULL OR timestamp - prev_ts > interval '3 hours'
        ORDER BY timestamp
    """, (since,))
    storms = cur.fetchall()

    with driver.session() as session:
        for g in storms:
            event_id = f"geomag_{g['id']}"
            kp = g['kp_index'] or 0
            storm_class = 'G1' if kp < 5 else 'G2' if kp < 6 else 'G3' if kp < 7 else 'G4+'
            session.run("""
                MERGE (e:SolarEvent {event_id: $event_id})
                SET e.type = 'GEOMAGNETIC_STORM',
                    e.timestamp = $timestamp,
                    e.kp_index = $kp_index,
                    e.dst_index = $dst_index,
                    e.storm_class = $storm_class,
                    e.label = $label,
                    e.updated_at = datetime()
            """, {
                'event_id': event_id,
                'timestamp': g['timestamp'].isoformat(),
                'kp_index': float(kp),
                'dst_index': float(g['dst_index'] or 0),
                'storm_class': storm_class,
                'label': f"{storm_class} Geomagnetic Storm (Kp={kp:.1f})"
            })
            upserted += 1

    cur.close()
    log.info(f"Solar events upserted: {upserted}")
    return upserted


# ─── Seismic Events ───────────────────────────────────────────────────────────

def sync_seismic_events(pg_conn, driver, since: datetime):
    """Upsert SeismicEvent nodes for M4+ earthquakes."""
    cur = pg_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT id, usgs_id, timestamp, latitude, longitude, depth,
               magnitude, mag_type, place, alert, significance,
               tsunami, cluster_id, antipode_lat, antipode_lon
        FROM earthquakes
        WHERE magnitude >= 4.0 AND timestamp >= %s
        ORDER BY timestamp
    """, (since,))
    quakes = cur.fetchall()
    cur.close()

    upserted = 0
    with driver.session() as session:
        for q in quakes:
            event_id = f"eq_{q['usgs_id']}"
            session.run("""
                MERGE (e:SeismicEvent {event_id: $event_id})
                SET e.usgs_id = $usgs_id,
                    e.timestamp = $timestamp,
                    e.latitude = $latitude,
                    e.longitude = $longitude,
                    e.depth_km = $depth,
                    e.magnitude = $magnitude,
                    e.mag_type = $mag_type,
                    e.place = $place,
                    e.alert = $alert,
                    e.significance = $significance,
                    e.tsunami = $tsunami,
                    e.cluster_id = $cluster_id,
                    e.antipode_lat = $antipode_lat,
                    e.antipode_lon = $antipode_lon,
                    e.label = $label,
                    e.updated_at = datetime()
            """, {
                'event_id': event_id,
                'usgs_id': q['usgs_id'],
                'timestamp': q['timestamp'].isoformat(),
                'latitude': q['latitude'],
                'longitude': q['longitude'],
                'depth': q['depth'],
                'magnitude': q['magnitude'],
                'mag_type': q['mag_type'],
                'place': q['place'] or 'Unknown',
                'alert': q['alert'],
                'significance': q['significance'],
                'tsunami': q['tsunami'],
                'cluster_id': q['cluster_id'],
                'antipode_lat': q['antipode_lat'],
                'antipode_lon': q['antipode_lon'],
                'label': f"M{q['magnitude']:.1f} {q['place'] or 'Unknown'}"
            })
            upserted += 1

    log.info(f"Seismic events upserted: {upserted}")
    return upserted


# ─── Seismic Clusters ─────────────────────────────────────────────────────────

def sync_seismic_clusters(pg_conn, driver, since: datetime):
    """Upsert SeismicCluster nodes and HAS_MEMBER rels to SeismicEvents."""
    cur = pg_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Get cluster metadata by aggregating from earthquakes table
    cur.execute("""
        SELECT
            cluster_id,
            COUNT(*) AS event_count,
            MAX(magnitude) AS max_magnitude,
            AVG(latitude) AS center_lat,
            AVG(longitude) AS center_lon,
            MIN(timestamp) AS first_event,
            MAX(timestamp) AS last_event,
            MODE() WITHIN GROUP (ORDER BY place) AS region
        FROM earthquakes
        WHERE cluster_id IS NOT NULL
          AND timestamp >= %s
        GROUP BY cluster_id
        ORDER BY cluster_id
    """, (since,))
    clusters = cur.fetchall()
    cur.close()

    upserted = 0
    with driver.session() as session:
        for c in clusters:
            cluster_node_id = f"cluster_{c['cluster_id']}"
            session.run("""
                MERGE (n:SeismicCluster {cluster_id: $cluster_node_id})
                SET n.pg_cluster_id = $pg_cluster_id,
                    n.event_count = $event_count,
                    n.max_magnitude = $max_magnitude,
                    n.center_lat = $center_lat,
                    n.center_lon = $center_lon,
                    n.first_event = $first_event,
                    n.last_event = $last_event,
                    n.region = $region,
                    n.label = $label,
                    n.updated_at = datetime()
            """, {
                'cluster_node_id': cluster_node_id,
                'pg_cluster_id': c['cluster_id'],
                'event_count': c['event_count'],
                'max_magnitude': c['max_magnitude'],
                'center_lat': float(c['center_lat'] or 0),
                'center_lon': float(c['center_lon'] or 0),
                'first_event': c['first_event'].isoformat(),
                'last_event': c['last_event'].isoformat(),
                'region': c['region'] or 'Unknown',
                'label': f"Cluster {c['cluster_id']}: {c['event_count']} events, M{c['max_magnitude']:.1f} max"
            })

            # Link member seismic events
            session.run("""
                MATCH (cluster:SeismicCluster {cluster_id: $cluster_node_id})
                MATCH (eq:SeismicEvent {cluster_id: $pg_cluster_id})
                MERGE (cluster)-[:HAS_MEMBER]->(eq)
            """, {
                'cluster_node_id': cluster_node_id,
                'pg_cluster_id': c['cluster_id']
            })

            upserted += 1

    log.info(f"Seismic clusters upserted: {upserted}")
    return upserted


# ─── Planetary Alignments ─────────────────────────────────────────────────────

def sync_planetary_alignments(pg_conn, driver, since: datetime):
    """Upsert PlanetaryAlignment nodes from planetary_alignments table."""
    cur = pg_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Check what columns are available
    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'planetary_alignments'
    """)
    cols = {r['column_name'] for r in cur.fetchall()}

    if not cols:
        log.warning("planetary_alignments table not found — skipping")
        cur.close()
        return 0

    # Build query based on available columns
    ts_col = 'timestamp' if 'timestamp' in cols else 'computed_at'
    type_col = 'alignment_type' if 'alignment_type' in cols else 'type'

    cur.execute(f"""
        SELECT * FROM planetary_alignments
        WHERE {ts_col} >= %s
        ORDER BY {ts_col}
    """, (since,))
    alignments = cur.fetchall()
    cur.close()

    upserted = 0
    with driver.session() as session:
        for a in alignments:
            row = dict(a)
            ts = row.get('timestamp') or row.get('computed_at')
            align_type = row.get('alignment_type') or row.get('type') or 'UNKNOWN'
            planets = row.get('planets') or row.get('bodies') or ''
            strength = row.get('strength') or row.get('intensity') or 1.0
            alignment_id = f"align_{row['id']}"

            session.run("""
                MERGE (n:PlanetaryAlignment {alignment_id: $alignment_id})
                SET n.timestamp = $timestamp,
                    n.alignment_type = $alignment_type,
                    n.planets = $planets,
                    n.strength = $strength,
                    n.label = $label,
                    n.updated_at = datetime()
            """, {
                'alignment_id': alignment_id,
                'timestamp': ts.isoformat() if ts else None,
                'alignment_type': align_type,
                'planets': str(planets),
                'strength': float(strength or 1.0),
                'label': f"{align_type}: {planets}"
            })
            upserted += 1

    log.info(f"Planetary alignments upserted: {upserted}")
    return upserted


# ─── Temporal Relationships ───────────────────────────────────────────────────

def build_temporal_relationships(driver, since: datetime):
    """
    Build PRECEDED_BY / CONCURRENT_WITH relationships between all observatory
    event types within the sync window. Uses timestamp proximity.
    CONCURRENT_WITH = within ±6 hours.
    """
    window_hours = CONCURRENT_WINDOW_HOURS
    log.info(f"Building temporal relationships (±{window_hours}h concurrent window)")

    # Cross-type concurrent relationships
    # Solar ↔ Seismic
    with driver.session() as session:
        result = session.run("""
            MATCH (s:SolarEvent), (e:SeismicEvent)
            WHERE s.timestamp >= $since
              AND e.timestamp >= $since
              AND abs(duration.between(
                    datetime(s.timestamp),
                    datetime(e.timestamp)
                  ).hours) <= $window_hours
              AND NOT (s)-[:CONCURRENT_WITH]-(e)
            MERGE (s)-[:CONCURRENT_WITH {window_hours: $window_hours}]->(e)
            RETURN count(*) as created
        """, {
            'since': since.isoformat(),
            'window_hours': window_hours
        })
        r = result.single()
        if r:
            log.info(f"Solar↔Seismic concurrent rels: {r['created']}")

    # Solar ↔ Planetary
    with driver.session() as session:
        result = session.run("""
            MATCH (s:SolarEvent), (p:PlanetaryAlignment)
            WHERE s.timestamp >= $since
              AND p.timestamp >= $since
              AND abs(duration.between(
                    datetime(s.timestamp),
                    datetime(p.timestamp)
                  ).hours) <= $window_hours
              AND NOT (s)-[:CONCURRENT_WITH]-(p)
            MERGE (s)-[:CONCURRENT_WITH {window_hours: $window_hours}]->(p)
            RETURN count(*) as created
        """, {
            'since': since.isoformat(),
            'window_hours': window_hours
        })
        r = result.single()
        if r:
            log.info(f"Solar↔Planetary concurrent rels: {r['created']}")

    # Seismic ↔ Planetary
    with driver.session() as session:
        result = session.run("""
            MATCH (e:SeismicEvent), (p:PlanetaryAlignment)
            WHERE e.timestamp >= $since
              AND p.timestamp >= $since
              AND abs(duration.between(
                    datetime(e.timestamp),
                    datetime(p.timestamp)
                  ).hours) <= $window_hours
              AND NOT (e)-[:CONCURRENT_WITH]-(p)
            MERGE (e)-[:CONCURRENT_WITH {window_hours: $window_hours}]->(p)
            RETURN count(*) as created
        """, {
            'since': since.isoformat(),
            'window_hours': window_hours
        })
        r = result.single()
        if r:
            log.info(f"Seismic↔Planetary concurrent rels: {r['created']}")

    log.info("Temporal relationships complete")


# ─── Main sync loop ───────────────────────────────────────────────────────────

def run_sync(pg_conn, driver, since: datetime):
    log.info(f"Observatory graph sync — since {since.isoformat()}")
    sync_solar_events(pg_conn, driver, since)
    sync_seismic_events(pg_conn, driver, since)
    sync_seismic_clusters(pg_conn, driver, since)
    sync_planetary_alignments(pg_conn, driver, since)
    build_temporal_relationships(driver, since)
    log.info("Sync complete")


def main():
    log.info("Observatory Graph Builder starting (SEN-0005)")

    pg_conn = pg_connect()
    driver = neo4j_connect()

    ensure_schema(driver)

    # Initial backfill
    backfill_since = datetime.now(timezone.utc) - timedelta(days=BACKFILL_DAYS)
    log.info(f"Running {BACKFILL_DAYS}-day backfill from {backfill_since.isoformat()}")
    run_sync(pg_conn, driver, backfill_since)
    log.info("Backfill complete — entering hourly sync loop")

    while True:
        time.sleep(SYNC_INTERVAL_SECONDS)
        # Sync window = last 2 hours to catch any new data + overlap for safety
        sync_since = datetime.now(timezone.utc) - timedelta(hours=2)
        try:
            run_sync(pg_conn, driver, sync_since)
        except Exception as e:
            log.error(f"Sync error: {e}", exc_info=True)


if __name__ == '__main__':
    main()
