-- ═══════════════════════════════════════════════════════════════════
-- Patch 0120: Harmonic Analysis System
-- Schema: person_dates, harmonic_values, harmonic_resonance
-- ═══════════════════════════════════════════════════════════════════

BEGIN;

-- ───────────────────────────────────────────────────────────────────
-- TABLE: person_dates
-- Any significant date associated with a person
-- ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS person_dates (
    id              SERIAL PRIMARY KEY,
    person_id       INTEGER NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    date_value      DATE NOT NULL,
    date_type       VARCHAR(50) NOT NULL DEFAULT 'birth',
    label           VARCHAR(200),
    date_string     VARCHAR(8) GENERATED ALWAYS AS (
        LPAD(EXTRACT(MONTH FROM date_value)::TEXT, 2, '0') ||
        LPAD(EXTRACT(DAY FROM date_value)::TEXT, 2, '0') ||
        EXTRACT(YEAR FROM date_value)::TEXT
    ) STORED,
    time_value      TIME,
    location_city   VARCHAR(100),
    location_state  VARCHAR(100),
    location_country VARCHAR(100),
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      VARCHAR(100)
);

CREATE INDEX idx_person_dates_person ON person_dates(person_id);
CREATE INDEX idx_person_dates_type ON person_dates(date_type);
CREATE INDEX idx_person_dates_date ON person_dates(date_value);
CREATE UNIQUE INDEX idx_person_dates_unique ON person_dates(person_id, date_type, date_value);

-- ───────────────────────────────────────────────────────────────────
-- TABLE: harmonic_values
-- Every number extracted from any source, fully decomposed
-- This is the universal extraction table — dates, planets, names, anything
-- ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS harmonic_values (
    id              SERIAL PRIMARY KEY,
    person_date_id  INTEGER REFERENCES person_dates(id) ON DELETE CASCADE,
    person_id       INTEGER REFERENCES people(id) ON DELETE CASCADE,
    source_system   VARCHAR(50) NOT NULL DEFAULT 'numerology',
    source_type     VARCHAR(80) NOT NULL,
    source_label    VARCHAR(200),
    source_raw      VARCHAR(100),
    pyramid_row     SMALLINT,
    pyramid_col     SMALLINT,
    raw_value       INTEGER NOT NULL,
    digit_1         SMALLINT,
    digit_2         SMALLINT,
    root            SMALLINT NOT NULL,
    mirror          INTEGER,
    mirror_root     SMALLINT,
    rotation        INTEGER,
    rotation_root   SMALLINT,
    is_master       BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_hv_person_date ON harmonic_values(person_date_id);
CREATE INDEX idx_hv_person ON harmonic_values(person_id);
CREATE INDEX idx_hv_root ON harmonic_values(root);
CREATE INDEX idx_hv_raw ON harmonic_values(raw_value);
CREATE INDEX idx_hv_mirror ON harmonic_values(mirror);
CREATE INDEX idx_hv_rotation ON harmonic_values(rotation) WHERE rotation IS NOT NULL;
CREATE INDEX idx_hv_source_type ON harmonic_values(source_type);
CREATE INDEX idx_hv_pyramid_pos ON harmonic_values(pyramid_row, pyramid_col) WHERE pyramid_row IS NOT NULL;
CREATE INDEX idx_hv_master ON harmonic_values(is_master) WHERE is_master = TRUE;

-- ───────────────────────────────────────────────────────────────────
-- TABLE: harmonic_resonance
-- Match records between two people/dates
-- ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS harmonic_resonance (
    id                  SERIAL PRIMARY KEY,
    person_date_id_a    INTEGER REFERENCES person_dates(id) ON DELETE CASCADE,
    person_date_id_b    INTEGER REFERENCES person_dates(id) ON DELETE CASCADE,
    person_id_a         INTEGER REFERENCES people(id) ON DELETE CASCADE,
    person_id_b         INTEGER REFERENCES people(id) ON DELETE CASCADE,
    harmonic_id_a       INTEGER REFERENCES harmonic_values(id) ON DELETE CASCADE,
    harmonic_id_b       INTEGER REFERENCES harmonic_values(id) ON DELETE CASCADE,
    match_type          VARCHAR(30) NOT NULL,
    source_a            VARCHAR(80),
    source_b            VARCHAR(80),
    value_a             INTEGER,
    value_b             INTEGER,
    pyramid_row_a       SMALLINT,
    pyramid_col_a       SMALLINT,
    pyramid_row_b       SMALLINT,
    pyramid_col_b       SMALLINT,
    notes               TEXT,
    discovered_by       VARCHAR(30) DEFAULT 'auto',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_hr_pair ON harmonic_resonance(person_id_a, person_id_b);
CREATE INDEX idx_hr_date_pair ON harmonic_resonance(person_date_id_a, person_date_id_b);
CREATE INDEX idx_hr_match_type ON harmonic_resonance(match_type);
CREATE INDEX idx_hr_person_a ON harmonic_resonance(person_id_a);
CREATE INDEX idx_hr_person_b ON harmonic_resonance(person_id_b);

-- ───────────────────────────────────────────────────────────────────
-- SEED: Migrate existing DOB/DOD from people table into person_dates
-- ───────────────────────────────────────────────────────────────────
INSERT INTO person_dates (person_id, date_value, date_type, label, time_value, 
                          location_city, location_state, location_country, created_by)
SELECT id, date_of_birth, 'birth', 
       known_as || ' — birth',
       time_of_birth,
       birth_city, birth_state, birth_country,
       'patch_0120'
FROM people 
WHERE date_of_birth IS NOT NULL
ON CONFLICT DO NOTHING;

INSERT INTO person_dates (person_id, date_value, date_type, label, created_by)
SELECT id, date_of_death, 'death',
       known_as || ' — death',
       'patch_0120'
FROM people 
WHERE date_of_death IS NOT NULL
ON CONFLICT DO NOTHING;

-- Add the wedding
INSERT INTO person_dates (person_id, date_value, date_type, label, time_value,
                          location_city, location_state, location_country, created_by)
VALUES 
    (1, '2003-10-04', 'marriage', 'Ka & Seraphe — wedding', '18:20:00',
     'Greene', 'NY', 'USA', 'patch_0120'),
    (2, '2003-10-04', 'marriage', 'Ka & Seraphe — wedding', '18:20:00',
     'Greene', 'NY', 'USA', 'patch_0120')
ON CONFLICT DO NOTHING;

COMMIT;
