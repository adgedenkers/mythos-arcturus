-- ============================================================
-- Mythos Astrology Schema v1.0
-- Normalized schema for natal chart data
-- Supports multiple charts (persons) via chart_id FK
--
-- PRESERVES: astro_events, astrological_events,
--            message_astrological_context
-- DROPS:     old natal chart tables (replaced by richer schema)
-- ============================================================

BEGIN;

-- ============================================================
-- Drop OLD natal chart tables (data will be re-loaded from JSON)
-- These are being replaced by the new, richer schema below.
-- ============================================================

-- Old comparison tables (empty, 0 rows)
DROP TABLE IF EXISTS astro_comparison_aspects CASCADE;
DROP TABLE IF EXISTS astro_chart_comparisons CASCADE;

-- Old natal data tables (cascade from old astro_charts)
DROP TABLE IF EXISTS astro_placements CASCADE;
DROP TABLE IF EXISTS astro_aspects CASCADE;
DROP TABLE IF EXISTS astro_house_cusps CASCADE;
DROP TABLE IF EXISTS astro_charts CASCADE;

-- ============================================================
-- NOT dropping (still in use):
--   astro_events              (53 transit/ingress events)
--   astrological_events       (referenced by message context)
--   message_astrological_context  (conversation linkage)
-- ============================================================

-- ============================================================
-- Drop new tables if re-running this script (idempotent)
-- ============================================================
DROP TABLE IF EXISTS astro_geometry_audit CASCADE;
DROP TABLE IF EXISTS astro_geometric_patterns CASCADE;
DROP TABLE IF EXISTS astro_fixed_star_conjunctions CASCADE;
DROP TABLE IF EXISTS astro_dispositors CASCADE;
DROP TABLE IF EXISTS astro_dignities CASCADE;
DROP TABLE IF EXISTS astro_retrogrades CASCADE;
DROP TABLE IF EXISTS astro_arabic_parts CASCADE;
DROP TABLE IF EXISTS astro_natal_aspects CASCADE;
DROP TABLE IF EXISTS astro_natal_house_cusps CASCADE;
DROP TABLE IF EXISTS astro_chart_points CASCADE;
DROP TABLE IF EXISTS astro_chart_objects CASCADE;
DROP TABLE IF EXISTS astro_balance CASCADE;
DROP TABLE IF EXISTS astro_sect CASCADE;
DROP TABLE IF EXISTS astro_chart_ruler CASCADE;
DROP TABLE IF EXISTS astro_natal_charts CASCADE;

-- ============================================================
-- 1. astro_natal_charts — one row per natal chart
-- ============================================================
CREATE TABLE astro_natal_charts (
    chart_id        SERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    birth_date      DATE NOT NULL,
    birth_time      TIME NOT NULL,
    birth_place     TEXT NOT NULL,
    latitude        DOUBLE PRECISION NOT NULL,
    longitude       DOUBLE PRECISION NOT NULL,
    timezone        TEXT NOT NULL,
    house_system    TEXT NOT NULL DEFAULT 'Placidus',
    zodiac_type     TEXT NOT NULL DEFAULT 'Tropical',
    ephemeris       TEXT,
    ephemeris_path  TEXT,
    engine_version  TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(name, birth_date, birth_time)
);

COMMENT ON TABLE astro_natal_charts IS 'Master chart record — one per person/event. FK target for all natal data tables.';

-- ============================================================
-- 2. astro_chart_objects — planetary positions (14 per chart)
-- ============================================================
CREATE TABLE astro_chart_objects (
    id              SERIAL PRIMARY KEY,
    chart_id        INT NOT NULL REFERENCES astro_natal_charts(chart_id) ON DELETE CASCADE,
    object_name     TEXT NOT NULL,
    longitude       DOUBLE PRECISION NOT NULL,
    latitude        DOUBLE PRECISION,
    distance        DOUBLE PRECISION,
    speed           DOUBLE PRECISION,
    sign            TEXT NOT NULL,
    deg_min         TEXT,
    full_position   TEXT,
    is_retrograde   BOOLEAN NOT NULL DEFAULT false,
    house           INT,
    UNIQUE(chart_id, object_name)
);
CREATE INDEX idx_chart_objects_chart ON astro_chart_objects(chart_id);
CREATE INDEX idx_chart_objects_sign ON astro_chart_objects(sign);

COMMENT ON TABLE astro_chart_objects IS 'Planetary/node positions. ~14 rows per chart.';

-- ============================================================
-- 3. astro_chart_points — angles (ASC, MC, DSC, IC, Vertex, ARMC)
-- ============================================================
CREATE TABLE astro_chart_points (
    id              SERIAL PRIMARY KEY,
    chart_id        INT NOT NULL REFERENCES astro_natal_charts(chart_id) ON DELETE CASCADE,
    point_name      TEXT NOT NULL,
    longitude       DOUBLE PRECISION NOT NULL,
    UNIQUE(chart_id, point_name)
);

COMMENT ON TABLE astro_chart_points IS 'Chart angles. 6 rows per chart.';

-- ============================================================
-- 4. astro_natal_house_cusps — 12 houses per chart
-- ============================================================
CREATE TABLE astro_natal_house_cusps (
    id              SERIAL PRIMARY KEY,
    chart_id        INT NOT NULL REFERENCES astro_natal_charts(chart_id) ON DELETE CASCADE,
    house_number    INT NOT NULL CHECK (house_number BETWEEN 1 AND 12),
    cusp_longitude  DOUBLE PRECISION NOT NULL,
    sign            TEXT NOT NULL,
    deg_min         TEXT,
    full_position   TEXT,
    UNIQUE(chart_id, house_number)
);

COMMENT ON TABLE astro_natal_house_cusps IS 'House cusp positions. 12 rows per chart.';

-- ============================================================
-- 5. astro_natal_aspects — all aspects (major, minor, harmonic)
-- ============================================================
CREATE TABLE astro_natal_aspects (
    id              SERIAL PRIMARY KEY,
    chart_id        INT NOT NULL REFERENCES astro_natal_charts(chart_id) ON DELETE CASCADE,
    object_1        TEXT NOT NULL,
    object_2        TEXT NOT NULL,
    aspect          TEXT NOT NULL,
    angle           DOUBLE PRECISION NOT NULL,
    exact_diff      DOUBLE PRECISION NOT NULL,
    orb             DOUBLE PRECISION NOT NULL,
    tier            TEXT NOT NULL,
    motion          TEXT,
    description     TEXT
);
CREATE INDEX idx_natal_aspects_chart ON astro_natal_aspects(chart_id);
CREATE INDEX idx_natal_aspects_tier ON astro_natal_aspects(chart_id, tier);
CREATE INDEX idx_natal_aspects_aspect ON astro_natal_aspects(aspect);

COMMENT ON TABLE astro_natal_aspects IS 'All natal aspects (major, minor, harmonic). ~90 rows per chart.';

-- ============================================================
-- 6. astro_arabic_parts — calculated lots
-- ============================================================
CREATE TABLE astro_arabic_parts (
    id              SERIAL PRIMARY KEY,
    chart_id        INT NOT NULL REFERENCES astro_natal_charts(chart_id) ON DELETE CASCADE,
    part_name       TEXT NOT NULL,
    longitude       DOUBLE PRECISION NOT NULL,
    sign            TEXT NOT NULL,
    deg_min         TEXT,
    full_position   TEXT,
    house           INT,
    formula         TEXT,
    UNIQUE(chart_id, part_name)
);

COMMENT ON TABLE astro_arabic_parts IS 'Arabic Parts / Lots. ~9 rows per chart.';

-- ============================================================
-- 7. astro_dignities — essential dignities (traditional planets)
-- ============================================================
CREATE TABLE astro_dignities (
    id              SERIAL PRIMARY KEY,
    chart_id        INT NOT NULL REFERENCES astro_natal_charts(chart_id) ON DELETE CASCADE,
    object_name     TEXT NOT NULL,
    sign            TEXT NOT NULL,
    status          TEXT[] NOT NULL,
    UNIQUE(chart_id, object_name)
);

COMMENT ON TABLE astro_dignities IS 'Essential dignities for traditional planets. 7 rows per chart.';

-- ============================================================
-- 8. astro_retrogrades — retrograde bodies snapshot
-- ============================================================
CREATE TABLE astro_retrogrades (
    id              SERIAL PRIMARY KEY,
    chart_id        INT NOT NULL REFERENCES astro_natal_charts(chart_id) ON DELETE CASCADE,
    object_name     TEXT NOT NULL,
    sign            TEXT NOT NULL,
    house           INT,
    longitude       DOUBLE PRECISION NOT NULL,
    UNIQUE(chart_id, object_name)
);

COMMENT ON TABLE astro_retrogrades IS 'Retrograde bodies at time of chart. Variable rows.';

-- ============================================================
-- 9. astro_fixed_star_conjunctions
-- ============================================================
CREATE TABLE astro_fixed_star_conjunctions (
    id               SERIAL PRIMARY KEY,
    chart_id         INT NOT NULL REFERENCES astro_natal_charts(chart_id) ON DELETE CASCADE,
    object_name      TEXT NOT NULL,
    object_longitude DOUBLE PRECISION NOT NULL,
    star_name        TEXT NOT NULL,
    star_longitude   DOUBLE PRECISION NOT NULL,
    star_j2000       DOUBLE PRECISION,
    magnitude        DOUBLE PRECISION,
    constellation    TEXT,
    orb              DOUBLE PRECISION NOT NULL,
    significance     TEXT
);

COMMENT ON TABLE astro_fixed_star_conjunctions IS 'Natal planets conjunct fixed stars. Variable rows.';

-- ============================================================
-- 10. astro_geometric_patterns — grand trines, kites, etc.
-- ============================================================
CREATE TABLE astro_geometric_patterns (
    id              SERIAL PRIMARY KEY,
    chart_id        INT NOT NULL REFERENCES astro_natal_charts(chart_id) ON DELETE CASCADE,
    pattern_type    TEXT NOT NULL,
    points          TEXT[] NOT NULL,
    aspects         TEXT[] NOT NULL
);
CREATE INDEX idx_patterns_chart ON astro_geometric_patterns(chart_id);
CREATE INDEX idx_patterns_type ON astro_geometric_patterns(pattern_type);

COMMENT ON TABLE astro_geometric_patterns IS 'Geometric patterns (Grand Trine, Kite, T-Square, etc.). Variable rows.';

-- ============================================================
-- 11. astro_geometry_audit — validation results
-- ============================================================
CREATE TABLE astro_geometry_audit (
    id              SERIAL PRIMARY KEY,
    chart_id        INT NOT NULL REFERENCES astro_natal_charts(chart_id) ON DELETE CASCADE,
    pattern_type    TEXT NOT NULL,
    expected_count  INT NOT NULL,
    detected_count  INT NOT NULL,
    status          TEXT NOT NULL,
    missing         JSONB DEFAULT '[]',
    extra           JSONB DEFAULT '[]',
    UNIQUE(chart_id, pattern_type)
);

COMMENT ON TABLE astro_geometry_audit IS 'Pattern detection audit/validation. 8 rows per chart.';

-- ============================================================
-- 12. astro_balance — element/modality/polarity distribution
-- ============================================================
CREATE TABLE astro_balance (
    id              SERIAL PRIMARY KEY,
    chart_id        INT NOT NULL REFERENCES astro_natal_charts(chart_id) ON DELETE CASCADE,
    fire            INT NOT NULL DEFAULT 0,
    earth           INT NOT NULL DEFAULT 0,
    air             INT NOT NULL DEFAULT 0,
    water           INT NOT NULL DEFAULT 0,
    dominant_element TEXT,
    cardinal        INT NOT NULL DEFAULT 0,
    fixed           INT NOT NULL DEFAULT 0,
    mutable         INT NOT NULL DEFAULT 0,
    dominant_modality TEXT,
    positive        INT NOT NULL DEFAULT 0,
    negative        INT NOT NULL DEFAULT 0,
    dominant_polarity TEXT,
    UNIQUE(chart_id)
);

COMMENT ON TABLE astro_balance IS 'Element/modality/polarity distribution. 1 row per chart.';

-- ============================================================
-- 13. astro_sect — day/night sect data
-- ============================================================
CREATE TABLE astro_sect (
    id              SERIAL PRIMARY KEY,
    chart_id        INT NOT NULL REFERENCES astro_natal_charts(chart_id) ON DELETE CASCADE,
    sect            TEXT NOT NULL,
    sect_light      TEXT NOT NULL,
    sect_benefic    TEXT NOT NULL,
    sect_malefic    TEXT NOT NULL,
    contra_light    TEXT NOT NULL,
    contra_benefic  TEXT NOT NULL,
    contra_malefic  TEXT NOT NULL,
    UNIQUE(chart_id)
);

COMMENT ON TABLE astro_sect IS 'Sect assignments. 1 row per chart.';

-- ============================================================
-- 14. astro_chart_ruler — chart ruler info
-- ============================================================
CREATE TABLE astro_chart_ruler (
    id              SERIAL PRIMARY KEY,
    chart_id        INT NOT NULL REFERENCES astro_natal_charts(chart_id) ON DELETE CASCADE,
    ascendant_sign  TEXT NOT NULL,
    traditional_ruler TEXT NOT NULL,
    ruler_sign      TEXT NOT NULL,
    ruler_house     INT NOT NULL,
    UNIQUE(chart_id)
);

COMMENT ON TABLE astro_chart_ruler IS 'Chart ruler. 1 row per chart.';

-- ============================================================
-- 15. astro_dispositors — dispositor chain and receptions
-- ============================================================
CREATE TABLE astro_dispositors (
    id              SERIAL PRIMARY KEY,
    chart_id        INT NOT NULL REFERENCES astro_natal_charts(chart_id) ON DELETE CASCADE,
    chain           JSONB NOT NULL,
    final_dispositors TEXT[] DEFAULT '{}',
    mutual_receptions TEXT[] DEFAULT '{}',
    circular_loops  JSONB DEFAULT '[]',
    classical_mutual_receptions TEXT[] DEFAULT '{}',
    modern_mutual_receptions TEXT[] DEFAULT '{}',
    UNIQUE(chart_id)
);

COMMENT ON TABLE astro_dispositors IS 'Dispositor chain and mutual receptions. 1 row per chart.';

COMMIT;
