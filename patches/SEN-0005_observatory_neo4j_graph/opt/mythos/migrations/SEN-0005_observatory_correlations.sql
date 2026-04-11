-- SEN-0005: Observatory Correlations Table
-- Created by the SEN stream for NEU-0011 to write into
-- Stores detected cross-domain correlations with scoring

CREATE TABLE IF NOT EXISTS observatory_correlations (
    id              BIGSERIAL PRIMARY KEY,
    detected_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    domain_a        TEXT NOT NULL,          -- 'solar', 'seismic', 'planetary'
    domain_b        TEXT NOT NULL,
    event_a_id      TEXT,                   -- neo4j event_id
    event_b_id      TEXT,
    time_delta_h    DOUBLE PRECISION,       -- hours between events (signed)
    correlation_type TEXT NOT NULL,         -- 'CONCURRENT', 'PRECEDED', 'FOLLOWED'
    score           DOUBLE PRECISION,       -- 0.0–1.0
    description     TEXT,
    details         JSONB,
    notified        BOOLEAN DEFAULT false,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_obs_corr_detected  ON observatory_correlations (detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_obs_corr_score      ON observatory_correlations (score DESC);
CREATE INDEX IF NOT EXISTS idx_obs_corr_domains    ON observatory_correlations (domain_a, domain_b);
CREATE INDEX IF NOT EXISTS idx_obs_corr_notified   ON observatory_correlations (notified) WHERE notified = false;
