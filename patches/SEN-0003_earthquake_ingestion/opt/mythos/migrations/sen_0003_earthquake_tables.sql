-- SEN-0003: Earthquake & Seismic Monitoring Tables

BEGIN;

-- Global earthquake events (USGS feed)
CREATE TABLE IF NOT EXISTS earthquakes (
    id BIGSERIAL PRIMARY KEY,
    usgs_id TEXT UNIQUE NOT NULL,        -- USGS event ID (e.g. us7000abcd)
    timestamp TIMESTAMPTZ NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    depth DOUBLE PRECISION,              -- km
    magnitude DOUBLE PRECISION NOT NULL,
    mag_type TEXT,                        -- ml, mb, mw, etc.
    place TEXT,                           -- human-readable location
    status TEXT,                          -- reviewed, automatic
    tsunami BOOLEAN DEFAULT FALSE,
    felt INTEGER,                         -- number of felt reports
    alert TEXT,                           -- green, yellow, orange, red
    significance INTEGER,                -- 0-1000 composite significance
    -- Antipodal point (computed on insert)
    antipode_lat DOUBLE PRECISION,       -- -latitude
    antipode_lon DOUBLE PRECISION,       -- longitude ± 180
    -- Cluster assignment
    cluster_id INTEGER,
    source TEXT DEFAULT 'USGS',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_eq_timestamp ON earthquakes(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_eq_magnitude ON earthquakes(magnitude DESC);
CREATE INDEX IF NOT EXISTS idx_eq_location ON earthquakes(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_eq_antipode ON earthquakes(antipode_lat, antipode_lon);
CREATE INDEX IF NOT EXISTS idx_eq_cluster ON earthquakes(cluster_id) WHERE cluster_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_eq_alert ON earthquakes(alert) WHERE alert IS NOT NULL;

-- Seismic clusters (groups of nearby quakes within time window)
CREATE TABLE IF NOT EXISTS seismic_clusters (
    id SERIAL PRIMARY KEY,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    center_lat DOUBLE PRECISION,
    center_lon DOUBLE PRECISION,
    event_count INTEGER DEFAULT 0,
    max_magnitude DOUBLE PRECISION,
    region TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cluster_time ON seismic_clusters(start_time DESC);
CREATE INDEX IF NOT EXISTS idx_cluster_active ON seismic_clusters(is_active) WHERE is_active = TRUE;

-- Antipodal earthquake pairs
CREATE TABLE IF NOT EXISTS antipodal_pairs (
    id SERIAL PRIMARY KEY,
    earthquake_a_id BIGINT REFERENCES earthquakes(id),
    earthquake_b_id BIGINT REFERENCES earthquakes(id),
    distance_km DOUBLE PRECISION,        -- distance between B and antipode of A
    time_diff_hours DOUBLE PRECISION,    -- abs time difference
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(earthquake_a_id, earthquake_b_id)
);

CREATE INDEX IF NOT EXISTS idx_antipodal_a ON antipodal_pairs(earthquake_a_id);
CREATE INDEX IF NOT EXISTS idx_antipodal_b ON antipodal_pairs(earthquake_b_id);

-- Function to compute antipodal coordinates on insert
CREATE OR REPLACE FUNCTION compute_antipode()
RETURNS TRIGGER AS $$
BEGIN
    NEW.antipode_lat := -NEW.latitude;
    IF NEW.longitude > 0 THEN
        NEW.antipode_lon := NEW.longitude - 180.0;
    ELSE
        NEW.antipode_lon := NEW.longitude + 180.0;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_compute_antipode ON earthquakes;
CREATE TRIGGER trg_compute_antipode
    BEFORE INSERT OR UPDATE ON earthquakes
    FOR EACH ROW EXECUTE FUNCTION compute_antipode();

COMMIT;
