#!/usr/bin/env python3
"""
Step 3: TimescaleDB Extension Setup

Installs TimescaleDB extension and creates:
- grid_activation_timeseries: 9-node activation scores over time
- entity_mention_timeseries: Entity mention frequency tracking
- emotional_state_timeseries: Emotional tone tracking
- Continuous aggregates for dashboards

Usage: python3 step3_timescaledb_setup.py
"""

import sys
import os
from pathlib import Path

# Try to load environment variables
try:
    from dotenv import load_dotenv
    env_file = Path("/opt/mythos/.env")
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_DB = os.getenv("POSTGRES_DB", "mythos")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")


def get_connection(autocommit=False):
    """Get database connection"""
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    if autocommit:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return conn


def check_timescaledb_available() -> bool:
    """Check if TimescaleDB extension is available"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Check if extension is available
        cur.execute("""
            SELECT * FROM pg_available_extensions 
            WHERE name = 'timescaledb'
        """)
        available = cur.fetchone() is not None
        
        if not available:
            print("  ⚠️  TimescaleDB extension not available in this PostgreSQL installation")
            print("  You may need to install it:")
            print("    - Ubuntu: sudo apt install timescaledb-2-postgresql-15")
            print("    - Or use the TimescaleDB Docker image")
            return False
        
        # Check if already installed
        cur.execute("""
            SELECT extversion FROM pg_extension 
            WHERE extname = 'timescaledb'
        """)
        installed = cur.fetchone()
        
        if installed:
            print(f"  ✓ TimescaleDB already installed (version {installed[0]})")
        else:
            print("  TimescaleDB available but not installed")
        
        return True
        
    finally:
        cur.close()
        conn.close()


def install_timescaledb() -> bool:
    """Install TimescaleDB extension"""
    conn = get_connection(autocommit=True)
    cur = conn.cursor()
    
    try:
        print("  Installing TimescaleDB extension...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE")
        print("  ✓ TimescaleDB extension installed")
        return True
    except psycopg2.Error as e:
        print(f"  ✗ Failed to install TimescaleDB: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def create_hypertables() -> bool:
    """Create TimescaleDB hypertables for time-series data"""
    conn = get_connection()
    cur = conn.cursor()
    
    sql_statements = [
        # Grid activation time-series
        """
        CREATE TABLE IF NOT EXISTS grid_activation_timeseries (
            time TIMESTAMPTZ NOT NULL,
            user_uuid UUID NOT NULL,
            conversation_id VARCHAR(100),
            exchange_id UUID,
            message_id INTEGER,
            
            -- Node scores (0-100)
            anchor_score INTEGER CHECK (anchor_score BETWEEN 0 AND 100),
            echo_score INTEGER CHECK (echo_score BETWEEN 0 AND 100),
            beacon_score INTEGER CHECK (beacon_score BETWEEN 0 AND 100),
            synth_score INTEGER CHECK (synth_score BETWEEN 0 AND 100),
            nexus_score INTEGER CHECK (nexus_score BETWEEN 0 AND 100),
            mirror_score INTEGER CHECK (mirror_score BETWEEN 0 AND 100),
            glyph_score INTEGER CHECK (glyph_score BETWEEN 0 AND 100),
            harmonia_score INTEGER CHECK (harmonia_score BETWEEN 0 AND 100),
            gateway_score INTEGER CHECK (gateway_score BETWEEN 0 AND 100),
            
            -- Derived metrics
            dominant_node VARCHAR(20),
            total_activation INTEGER,
            
            -- Metadata
            analysis_model VARCHAR(50),
            processing_time_ms INTEGER
        )
        """,
        
        # Entity mention time-series
        """
        CREATE TABLE IF NOT EXISTS entity_mention_timeseries (
            time TIMESTAMPTZ NOT NULL,
            user_uuid UUID NOT NULL,
            conversation_id VARCHAR(100),
            message_id INTEGER,
            
            -- Entity info
            entity_canonical_id VARCHAR(255) NOT NULL,
            entity_name VARCHAR(255) NOT NULL,
            entity_type VARCHAR(50),  -- person, concept, symbol, place
            
            -- Context
            mention_context TEXT,
            confidence_score NUMERIC(3,2),
            
            -- Grid node that extracted this
            extracted_by_node VARCHAR(20)
        )
        """,
        
        # Emotional state time-series
        """
        CREATE TABLE IF NOT EXISTS emotional_state_timeseries (
            time TIMESTAMPTZ NOT NULL,
            user_uuid UUID NOT NULL,
            conversation_id VARCHAR(100),
            message_id INTEGER,
            
            -- Emotional data
            emotional_tone VARCHAR(50),
            intensity INTEGER CHECK (intensity BETWEEN 1 AND 10),
            valence NUMERIC(3,2),  -- -1.0 to 1.0 (negative to positive)
            arousal NUMERIC(3,2),  -- 0.0 to 1.0 (calm to excited)
            
            -- Context
            context_notes TEXT,
            themes TEXT[]
        )
        """,
        
        # Astrological events table (not a hypertable, but related)
        """
        CREATE TABLE IF NOT EXISTS astrological_events (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            event_type VARCHAR(50) NOT NULL,
            
            -- Bodies involved
            body1 VARCHAR(50),
            body2 VARCHAR(50),
            
            -- Position
            degree NUMERIC(5,2),
            sign VARCHAR(20),
            house INTEGER,
            
            -- Timing
            exact_time TIMESTAMPTZ NOT NULL,
            influence_start TIMESTAMPTZ,
            influence_end TIMESTAMPTZ,
            orb_degrees NUMERIC(4,2),
            
            -- Metadata
            description TEXT,
            significance TEXT,
            keywords TEXT[],
            
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """,
        
        # Message-astrological context linking
        """
        CREATE TABLE IF NOT EXISTS message_astrological_context (
            message_id INTEGER NOT NULL,
            astrological_event_id UUID NOT NULL REFERENCES astrological_events(id),
            relevance_score NUMERIC(3,2),
            auto_linked BOOLEAN DEFAULT TRUE,
            
            PRIMARY KEY (message_id, astrological_event_id)
        )
        """
    ]
    
    try:
        for sql in sql_statements:
            table_name = sql.split("CREATE TABLE IF NOT EXISTS")[1].split("(")[0].strip()
            print(f"  Creating table: {table_name}...")
            cur.execute(sql)
        
        conn.commit()
        print("  ✓ All tables created")
        return True
        
    except psycopg2.Error as e:
        conn.rollback()
        print(f"  ✗ Failed to create tables: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def convert_to_hypertables() -> bool:
    """Convert tables to TimescaleDB hypertables"""
    conn = get_connection()
    cur = conn.cursor()
    
    hypertables = [
        ("grid_activation_timeseries", "time"),
        ("entity_mention_timeseries", "time"),
        ("emotional_state_timeseries", "time")
    ]
    
    try:
        for table_name, time_column in hypertables:
            # Check if already a hypertable
            cur.execute("""
                SELECT * FROM timescaledb_information.hypertables 
                WHERE hypertable_name = %s
            """, (table_name,))
            
            if cur.fetchone():
                print(f"  - {table_name}: Already a hypertable")
                continue
            
            print(f"  Converting {table_name} to hypertable...")
            cur.execute(f"""
                SELECT create_hypertable(
                    '{table_name}', 
                    '{time_column}',
                    if_not_exists => TRUE,
                    migrate_data => TRUE
                )
            """)
            print(f"  ✓ {table_name} converted")
        
        conn.commit()
        return True
        
    except psycopg2.Error as e:
        conn.rollback()
        print(f"  ✗ Failed to convert to hypertables: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def create_continuous_aggregates() -> bool:
    """Create continuous aggregates for dashboard queries"""
    conn = get_connection()
    cur = conn.cursor()
    
    aggregates = [
        # Daily grid averages
        (
            "grid_daily_averages",
            """
            CREATE MATERIALIZED VIEW IF NOT EXISTS grid_daily_averages
            WITH (timescaledb.continuous) AS
            SELECT 
                time_bucket('1 day', time) AS day,
                user_uuid,
                COUNT(*) as exchange_count,
                AVG(anchor_score)::INTEGER as avg_anchor,
                AVG(echo_score)::INTEGER as avg_echo,
                AVG(beacon_score)::INTEGER as avg_beacon,
                AVG(synth_score)::INTEGER as avg_synth,
                AVG(nexus_score)::INTEGER as avg_nexus,
                AVG(mirror_score)::INTEGER as avg_mirror,
                AVG(glyph_score)::INTEGER as avg_glyph,
                AVG(harmonia_score)::INTEGER as avg_harmonia,
                AVG(gateway_score)::INTEGER as avg_gateway,
                MODE() WITHIN GROUP (ORDER BY dominant_node) as most_dominant_node
            FROM grid_activation_timeseries
            GROUP BY day, user_uuid
            WITH NO DATA
            """
        ),
        
        # Weekly entity counts
        (
            "entity_weekly_counts",
            """
            CREATE MATERIALIZED VIEW IF NOT EXISTS entity_weekly_counts
            WITH (timescaledb.continuous) AS
            SELECT 
                time_bucket('1 week', time) AS week,
                user_uuid,
                entity_canonical_id,
                entity_type,
                COUNT(*) as mention_count,
                array_agg(DISTINCT conversation_id) as conversations
            FROM entity_mention_timeseries
            GROUP BY week, user_uuid, entity_canonical_id, entity_type
            WITH NO DATA
            """
        ),
        
        # Daily emotional averages
        (
            "emotional_daily_averages",
            """
            CREATE MATERIALIZED VIEW IF NOT EXISTS emotional_daily_averages
            WITH (timescaledb.continuous) AS
            SELECT 
                time_bucket('1 day', time) AS day,
                user_uuid,
                MODE() WITHIN GROUP (ORDER BY emotional_tone) as dominant_tone,
                AVG(intensity)::NUMERIC(3,1) as avg_intensity,
                AVG(valence)::NUMERIC(3,2) as avg_valence,
                AVG(arousal)::NUMERIC(3,2) as avg_arousal,
                COUNT(*) as data_points
            FROM emotional_state_timeseries
            GROUP BY day, user_uuid
            WITH NO DATA
            """
        )
    ]
    
    try:
        for name, sql in aggregates:
            print(f"  Creating continuous aggregate: {name}...")
            try:
                cur.execute(sql)
                print(f"  ✓ {name} created")
            except psycopg2.Error as e:
                if "already exists" in str(e):
                    print(f"  - {name} already exists")
                else:
                    raise e
        
        conn.commit()
        return True
        
    except psycopg2.Error as e:
        conn.rollback()
        print(f"  ✗ Failed to create continuous aggregates: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def create_indexes() -> bool:
    """Create indexes for efficient querying"""
    conn = get_connection()
    cur = conn.cursor()
    
    indexes = [
        # Grid activation indexes
        "CREATE INDEX IF NOT EXISTS idx_grid_user_time ON grid_activation_timeseries(user_uuid, time DESC)",
        "CREATE INDEX IF NOT EXISTS idx_grid_conv ON grid_activation_timeseries(conversation_id, time DESC)",
        "CREATE INDEX IF NOT EXISTS idx_grid_dominant ON grid_activation_timeseries(dominant_node, time DESC)",
        
        # Entity mention indexes
        "CREATE INDEX IF NOT EXISTS idx_entity_user_time ON entity_mention_timeseries(user_uuid, time DESC)",
        "CREATE INDEX IF NOT EXISTS idx_entity_canonical ON entity_mention_timeseries(entity_canonical_id, time DESC)",
        "CREATE INDEX IF NOT EXISTS idx_entity_type ON entity_mention_timeseries(entity_type, time DESC)",
        
        # Emotional state indexes
        "CREATE INDEX IF NOT EXISTS idx_emotional_user_time ON emotional_state_timeseries(user_uuid, time DESC)",
        "CREATE INDEX IF NOT EXISTS idx_emotional_tone ON emotional_state_timeseries(emotional_tone, time DESC)",
        
        # Astrological events indexes
        "CREATE INDEX IF NOT EXISTS idx_astro_exact_time ON astrological_events(exact_time)",
        "CREATE INDEX IF NOT EXISTS idx_astro_influence ON astrological_events(influence_start, influence_end)",
        "CREATE INDEX IF NOT EXISTS idx_astro_type ON astrological_events(event_type)",
        "CREATE INDEX IF NOT EXISTS idx_astro_bodies ON astrological_events(body1, body2)"
    ]
    
    try:
        print("  Creating indexes...")
        for idx_sql in indexes:
            idx_name = idx_sql.split("INDEX IF NOT EXISTS")[1].split("ON")[0].strip()
            cur.execute(idx_sql)
            print(f"    ✓ {idx_name}")
        
        conn.commit()
        return True
        
    except psycopg2.Error as e:
        conn.rollback()
        print(f"  ✗ Failed to create indexes: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def insert_sample_astrological_events() -> bool:
    """Insert some known upcoming astrological events"""
    conn = get_connection()
    cur = conn.cursor()
    
    events = [
        {
            "event_type": "conjunction",
            "body1": "Saturn",
            "body2": "Neptune",
            "degree": 0.0,
            "sign": "Aries",
            "exact_time": "2026-02-20 12:00:00+00",
            "influence_start": "2026-02-01 00:00:00+00",
            "influence_end": "2026-03-15 00:00:00+00",
            "orb_degrees": 5.0,
            "description": "Saturn-Neptune conjunction at 0° Aries",
            "significance": "Major collective shift - dissolution of old structures, spiritual awakening in material realm",
            "keywords": ["transformation", "dissolution", "spiritual", "collective", "new cycle"]
        },
        {
            "event_type": "ingress",
            "body1": "Pluto",
            "body2": None,
            "degree": 0.0,
            "sign": "Aquarius",
            "exact_time": "2024-01-20 12:00:00+00",
            "influence_start": "2023-03-23 00:00:00+00",
            "influence_end": "2044-01-19 00:00:00+00",
            "orb_degrees": None,
            "description": "Pluto enters Aquarius",
            "significance": "20-year transformation of collective structures, technology, humanity",
            "keywords": ["pluto", "aquarius", "transformation", "technology", "collective"]
        }
    ]
    
    try:
        print("  Inserting sample astrological events...")
        
        for event in events:
            # Check if already exists
            cur.execute("""
                SELECT id FROM astrological_events 
                WHERE event_type = %s AND body1 = %s AND exact_time = %s
            """, (event["event_type"], event["body1"], event["exact_time"]))
            
            if cur.fetchone():
                print(f"    - {event['description']}: Already exists")
                continue
            
            cur.execute("""
                INSERT INTO astrological_events (
                    event_type, body1, body2, degree, sign,
                    exact_time, influence_start, influence_end, orb_degrees,
                    description, significance, keywords
                ) VALUES (
                    %(event_type)s, %(body1)s, %(body2)s, %(degree)s, %(sign)s,
                    %(exact_time)s, %(influence_start)s, %(influence_end)s, %(orb_degrees)s,
                    %(description)s, %(significance)s, %(keywords)s
                )
            """, event)
            print(f"    ✓ {event['description']}")
        
        conn.commit()
        return True
        
    except psycopg2.Error as e:
        conn.rollback()
        print(f"  ✗ Failed to insert astrological events: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def verify_setup() -> None:
    """Verify TimescaleDB setup"""
    conn = get_connection()
    cur = conn.cursor()
    
    print("\n  TimescaleDB Status:")
    print("  " + "-" * 50)
    
    # Check extension version
    cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'timescaledb'")
    version = cur.fetchone()
    if version:
        print(f"  Extension version: {version[0]}")
    
    # List hypertables
    cur.execute("""
        SELECT hypertable_name, num_chunks 
        FROM timescaledb_information.hypertables
    """)
    hypertables = cur.fetchall()
    print(f"\n  Hypertables ({len(hypertables)}):")
    for name, chunks in hypertables:
        print(f"    - {name}: {chunks} chunks")
    
    # List continuous aggregates
    cur.execute("""
        SELECT view_name 
        FROM timescaledb_information.continuous_aggregates
    """)
    aggregates = cur.fetchall()
    print(f"\n  Continuous Aggregates ({len(aggregates)}):")
    for (name,) in aggregates:
        print(f"    - {name}")
    
    # Count astrological events
    cur.execute("SELECT COUNT(*) FROM astrological_events")
    astro_count = cur.fetchone()[0]
    print(f"\n  Astrological events: {astro_count}")
    
    cur.close()
    conn.close()


def main():
    print("\n" + "=" * 60)
    print("  TimescaleDB Extension Setup")
    print("=" * 60 + "\n")
    
    print(f"Connecting to PostgreSQL at {POSTGRES_HOST}/{POSTGRES_DB}...")
    
    # Check if TimescaleDB is available
    if not check_timescaledb_available():
        print("\n⚠️  TimescaleDB not available - creating regular tables instead")
        print("   Time-series features will be limited.")
        print("   Install TimescaleDB for full functionality.")
        
        # Still create the tables, just not as hypertables
        if not create_hypertables():
            sys.exit(1)
        if not create_indexes():
            sys.exit(1)
        if not insert_sample_astrological_events():
            sys.exit(1)
        
        print("\n" + "=" * 60)
        print("  ✓ Tables created (without TimescaleDB features)")
        print("=" * 60)
        return
    
    # Full TimescaleDB setup
    all_success = True
    
    # Install extension
    if not install_timescaledb():
        all_success = False
    
    # Create tables
    if not create_hypertables():
        all_success = False
    
    # Convert to hypertables
    if not convert_to_hypertables():
        all_success = False
    
    # Create continuous aggregates
    if not create_continuous_aggregates():
        all_success = False
    
    # Create indexes
    if not create_indexes():
        all_success = False
    
    # Insert sample data
    if not insert_sample_astrological_events():
        all_success = False
    
    # Verify
    verify_setup()
    
    if all_success:
        print("\n" + "=" * 60)
        print("  ✓ TimescaleDB setup complete!")
        print("=" * 60)
        print("\nTables created:")
        print("  - grid_activation_timeseries (hypertable)")
        print("  - entity_mention_timeseries (hypertable)")
        print("  - emotional_state_timeseries (hypertable)")
        print("  - astrological_events (regular table)")
        print("\nContinuous aggregates:")
        print("  - grid_daily_averages")
        print("  - entity_weekly_counts")
        print("  - emotional_daily_averages")
        print("\nSample queries:")
        print("  SELECT * FROM grid_daily_averages WHERE user_uuid = 'xxx';")
        print("  SELECT * FROM entity_weekly_counts ORDER BY mention_count DESC;")
        print()
    else:
        print("\n✗ Setup completed with errors")
        sys.exit(1)


if __name__ == "__main__":
    main()
