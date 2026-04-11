-- SEN-0004: Planetary Geometry Engine Tables

BEGIN;

-- Hourly planetary positions (geocentric ecliptic)
CREATE TABLE IF NOT EXISTS planetary_positions (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    planet TEXT NOT NULL,              -- Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto
    ecliptic_lon DOUBLE PRECISION,    -- degrees (0-360)
    ecliptic_lat DOUBLE PRECISION,    -- degrees
    distance_au DOUBLE PRECISION,     -- AU from Earth
    speed_deg_day DOUBLE PRECISION,   -- daily motion in degrees
    is_retrograde BOOLEAN DEFAULT FALSE,
    zodiac_sign TEXT,                  -- Aries, Taurus, etc.
    zodiac_degree DOUBLE PRECISION,   -- degree within sign (0-30)
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_planet_pos_dedup 
    ON planetary_positions(timestamp, planet);
CREATE INDEX IF NOT EXISTS idx_planet_pos_time ON planetary_positions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_planet_pos_planet ON planetary_positions(planet);

-- Planetary aspects (continuous strength, not binary)
CREATE TABLE IF NOT EXISTS planetary_aspects (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    planet_a TEXT NOT NULL,
    planet_b TEXT NOT NULL,
    aspect_type TEXT NOT NULL,         -- conjunction, opposition, square, trine, sextile
    exact_angle DOUBLE PRECISION,     -- the target angle (0, 180, 90, 120, 60)
    actual_angle DOUBLE PRECISION,    -- measured angle between planets
    orb DOUBLE PRECISION,             -- difference from exact
    strength DOUBLE PRECISION,        -- gaussian: exp(-(orb²)/(2σ²)), 0.0-1.0
    is_applying BOOLEAN,              -- getting tighter?
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_aspect_dedup 
    ON planetary_aspects(timestamp, planet_a, planet_b, aspect_type);
CREATE INDEX IF NOT EXISTS idx_aspect_time ON planetary_aspects(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_aspect_strength ON planetary_aspects(strength DESC);

-- Major planetary alignment events (detected configurations)
CREATE TABLE IF NOT EXISTS planetary_alignments (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    alignment_type TEXT NOT NULL,      -- conjunction, opposition, grand_trine, t_square, stellium, compression
    planets TEXT[] NOT NULL,           -- array of involved planets
    description TEXT,
    strength DOUBLE PRECISION,        -- composite strength
    ecliptic_center DOUBLE PRECISION, -- center longitude of the pattern
    span_degrees DOUBLE PRECISION,    -- angular span of involved planets
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alignment_time ON planetary_alignments(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_alignment_type ON planetary_alignments(alignment_type);

-- Planetary gravitational forcing vectors (geocentric)
CREATE TABLE IF NOT EXISTS planetary_forcing (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    -- Per-planet vectors stored as JSONB for flexibility
    planet_vectors JSONB,             -- {planet: {fx, fy, magnitude, direction_deg}}
    -- Net vector (sum of all planets)
    net_fx DOUBLE PRECISION,
    net_fy DOUBLE PRECISION,
    net_magnitude DOUBLE PRECISION,
    net_direction_deg DOUBLE PRECISION,
    -- Alignment metrics
    total_reinforcement DOUBLE PRECISION,  -- how aligned the vectors are (0-1)
    compression_span DOUBLE PRECISION,     -- span of all planets in degrees
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_forcing_dedup ON planetary_forcing(timestamp);
CREATE INDEX IF NOT EXISTS idx_forcing_time ON planetary_forcing(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_forcing_magnitude ON planetary_forcing(net_magnitude DESC);

COMMIT;
