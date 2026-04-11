-- SEN-0006: Spiral Time Walker
-- Adds spiral_transit_pressure table and seeds spiral_epochs for Adge

-- ── Transit Pressure ────────────────────────────────────────────────────────
-- Tracks daily transit-to-natal aspect orbs over time.
-- One row per transiting_planet × natal_point × date.

CREATE TABLE IF NOT EXISTS spiral_transit_pressure (
    id                  SERIAL PRIMARY KEY,
    chart_id            INTEGER NOT NULL REFERENCES astro_natal_charts(chart_id) ON DELETE CASCADE,
    computed_date       DATE NOT NULL,
    transiting_planet   TEXT NOT NULL,
    natal_point         TEXT NOT NULL,
    aspect_type         TEXT NOT NULL,          -- conjunction, sextile, square, trine, opposition
    exact_angle         DOUBLE PRECISION NOT NULL,
    orb                 DOUBLE PRECISION NOT NULL,
    applying            BOOLEAN NOT NULL,       -- TRUE = orb tightening, FALSE = separating
    transit_lon         DOUBLE PRECISION NOT NULL,
    natal_lon           DOUBLE PRECISION NOT NULL,
    threshold_level     TEXT NOT NULL,          -- 'watch' (<=3), 'building' (<=1.5), 'exact' (<=0.5)
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_spiral_transit_unique
    ON spiral_transit_pressure (chart_id, computed_date, transiting_planet, natal_point, aspect_type);

CREATE INDEX IF NOT EXISTS idx_spiral_transit_date
    ON spiral_transit_pressure (chart_id, computed_date);

CREATE INDEX IF NOT EXISTS idx_spiral_transit_threshold
    ON spiral_transit_pressure (chart_id, computed_date, threshold_level);

-- ── Morning Brief Log ───────────────────────────────────────────────────────
-- Tracks when the morning brief was last delivered per person,
-- so Iris only fires it once per day.

CREATE TABLE IF NOT EXISTS spiral_morning_brief_log (
    id          SERIAL PRIMARY KEY,
    person_id   TEXT NOT NULL,
    brief_date  DATE NOT NULL,
    delivered   BOOLEAN NOT NULL DEFAULT FALSE,
    delivered_at TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (person_id, brief_date)
);

-- ── Seed Adge's Epoch ───────────────────────────────────────────────────────
-- Oct 19 2025 = Spiral 1, Cycle 1, Day 1 for Ka'tuar'el.
-- Only inserts if no active epoch exists for adge.

INSERT INTO spiral_epochs (person_id, epoch_number, started_at, reason, metadata)
SELECT 'adge', 1, '2025-10-19', 'Origin epoch — Bearer of the Nine Day Sun', '{"system": "nine_day_sun", "notation": "cycle.day"}'
WHERE NOT EXISTS (
    SELECT 1 FROM spiral_epochs WHERE person_id = 'adge' AND ended_at IS NULL
);
