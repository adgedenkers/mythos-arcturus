-- SEN-0002: Solar & Space Weather Observatory Tables
-- Creates tables for solar wind, geomagnetic indices, solar flares, CMEs, radiation flux

BEGIN;

-- Real-time solar wind measurements (DSCOVR/ACE)
CREATE TABLE IF NOT EXISTS solar_wind_readings (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    speed DOUBLE PRECISION,          -- km/s
    density DOUBLE PRECISION,        -- protons/cm³
    temperature DOUBLE PRECISION,    -- Kelvin
    bx DOUBLE PRECISION,             -- nT (IMF components)
    by DOUBLE PRECISION,             -- nT
    bz DOUBLE PRECISION,             -- nT
    bt DOUBLE PRECISION,             -- nT (total field)
    source TEXT DEFAULT 'DSCOVR',    -- DSCOVR or ACE
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_solar_wind_timestamp ON solar_wind_readings(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_solar_wind_speed ON solar_wind_readings(speed) WHERE speed IS NOT NULL;

-- Deduplicate on source + timestamp
CREATE UNIQUE INDEX IF NOT EXISTS idx_solar_wind_dedup 
    ON solar_wind_readings(source, timestamp);

-- Geomagnetic indices (Kp, Dst, AE)
CREATE TABLE IF NOT EXISTS geomagnetic_indices (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    index_type TEXT NOT NULL,         -- 'Kp', 'Dst', 'AE'
    value DOUBLE PRECISION NOT NULL,
    storm_level TEXT,                 -- G1-G5 for Kp >= 5
    source TEXT DEFAULT 'SWPC',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_geomag_timestamp ON geomagnetic_indices(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_geomag_type ON geomagnetic_indices(index_type);
CREATE UNIQUE INDEX IF NOT EXISTS idx_geomag_dedup 
    ON geomagnetic_indices(index_type, timestamp, source);

-- Solar flare events
CREATE TABLE IF NOT EXISTS solar_flares (
    id BIGSERIAL PRIMARY KEY,
    flare_id TEXT UNIQUE,             -- DONKI ID
    begin_time TIMESTAMPTZ,
    peak_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    class_type TEXT,                  -- A, B, C, M, X
    class_value DOUBLE PRECISION,    -- e.g. 5.4 for M5.4
    source_location TEXT,            -- e.g. N23W45
    active_region INTEGER,           -- NOAA AR number
    linked_events JSONB,             -- related CMEs, SEPs
    source TEXT DEFAULT 'DONKI',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_flare_peak ON solar_flares(peak_time DESC);
CREATE INDEX IF NOT EXISTS idx_flare_class ON solar_flares(class_type);

-- Coronal mass ejections
CREATE TABLE IF NOT EXISTS cme_events (
    id BIGSERIAL PRIMARY KEY,
    cme_id TEXT UNIQUE,               -- DONKI activity ID
    start_time TIMESTAMPTZ,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    half_angle DOUBLE PRECISION,     -- degrees (angular width / 2)
    speed DOUBLE PRECISION,          -- km/s
    type TEXT,                        -- S (slow), C (common), O (occasional)
    is_earth_directed BOOLEAN DEFAULT FALSE,
    predicted_arrival TIMESTAMPTZ,
    arrival_actual TIMESTAMPTZ,
    impact_probability DOUBLE PRECISION,
    note TEXT,
    linked_events JSONB,
    source TEXT DEFAULT 'DONKI',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cme_start ON cme_events(start_time DESC);
CREATE INDEX IF NOT EXISTS idx_cme_earth ON cme_events(is_earth_directed) WHERE is_earth_directed = TRUE;

-- Radiation flux (proton/electron)
CREATE TABLE IF NOT EXISTS radiation_flux (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    flux_type TEXT NOT NULL,          -- 'proton_10MeV', 'proton_100MeV', 'electron_2MeV'
    value DOUBLE PRECISION NOT NULL,  -- pfu (particle flux units)
    energy_threshold TEXT,            -- '>10 MeV', '>100 MeV', '>2 MeV'
    storm_level TEXT,                 -- S1-S5 for proton storms
    source TEXT DEFAULT 'SWPC',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_radflux_timestamp ON radiation_flux(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_radflux_type ON radiation_flux(flux_type);
CREATE UNIQUE INDEX IF NOT EXISTS idx_radflux_dedup 
    ON radiation_flux(flux_type, timestamp, source);

-- High-speed stream and shock detection events (derived)
CREATE TABLE IF NOT EXISTS solar_wind_events (
    id BIGSERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,          -- 'high_speed_stream', 'shock', 'sector_boundary'
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    peak_speed DOUBLE PRECISION,
    peak_density DOUBLE PRECISION,
    peak_bt DOUBLE PRECISION,
    min_bz DOUBLE PRECISION,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sw_events_time ON solar_wind_events(start_time DESC);
CREATE INDEX IF NOT EXISTS idx_sw_events_type ON solar_wind_events(event_type);

COMMIT;
