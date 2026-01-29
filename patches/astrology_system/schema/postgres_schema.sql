-- ============================================================================
-- MYTHOS ASTROLOGY SYSTEM - PostgreSQL Schema
-- ============================================================================
-- This schema stores the FACTS: precise positions, times, calculations.
-- Meanings and relationships live in Neo4j.
-- Bridge key: chart_id (UUID) exists in both systems.
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- REFERENCE TABLES
-- ============================================================================

-- Zodiac Signs (reference)
CREATE TABLE IF NOT EXISTS astro_signs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE,
    symbol VARCHAR(4) NOT NULL,          -- ♈ ♉ ♊ etc
    abbreviation VARCHAR(3) NOT NULL,    -- ARI, TAU, GEM, etc
    element VARCHAR(10) NOT NULL,        -- fire, earth, air, water
    modality VARCHAR(10) NOT NULL,       -- cardinal, fixed, mutable
    polarity VARCHAR(10) NOT NULL,       -- yang, yin
    degree_start NUMERIC(5,2) NOT NULL,  -- 0.00, 30.00, 60.00, etc (ecliptic longitude start)
    degree_end NUMERIC(5,2) NOT NULL,    -- 29.99, 59.99, etc
    sort_order INTEGER NOT NULL          -- 1-12
);

-- Celestial Bodies (reference)
CREATE TABLE IF NOT EXISTS astro_bodies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    symbol VARCHAR(10),                   -- ☉ ☽ ☿ etc
    abbreviation VARCHAR(10) NOT NULL,    -- SUN, MOO, MER, etc
    body_type VARCHAR(30) NOT NULL,       -- luminary, planet, dwarf_planet, asteroid, centaur, point, angle, star, lot
    swiss_eph_id INTEGER,                 -- Swiss Ephemeris body ID (for calculation)
    is_retrograde_capable BOOLEAN DEFAULT false,
    orbital_period_days NUMERIC(12,2),    -- for calculating transits
    mean_daily_motion NUMERIC(8,4),       -- degrees per day average
    default_orb NUMERIC(4,2) DEFAULT 8.0, -- default orb for aspects
    is_active BOOLEAN DEFAULT true        -- include in charts by default
);

-- Houses (reference)
CREATE TABLE IF NOT EXISTS astro_houses (
    id SERIAL PRIMARY KEY,
    number INTEGER NOT NULL UNIQUE,       -- 1-12
    name VARCHAR(50),                     -- "First House", "House of Self"
    abbreviation VARCHAR(5) NOT NULL,     -- H1, H2, etc
    natural_sign VARCHAR(20),             -- Aries for 1st, etc
    axis VARCHAR(20)                      -- identity/partnership, resources/shared, etc
);

-- Aspect Types (reference)
CREATE TABLE IF NOT EXISTS astro_aspect_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE,
    symbol VARCHAR(10),
    angle NUMERIC(6,3) NOT NULL,          -- 0, 60, 90, 120, 180, etc
    orb_default NUMERIC(4,2) NOT NULL,    -- default orb allowance
    is_major BOOLEAN DEFAULT false,
    is_harmonious BOOLEAN,                -- true=harmonious, false=challenging, null=neutral
    sort_order INTEGER
);

-- House Systems (reference)
CREATE TABLE IF NOT EXISTS astro_house_systems (
    id SERIAL PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE,
    code VARCHAR(1) NOT NULL,             -- Swiss Eph code: P=Placidus, W=Whole, etc
    description TEXT
);

-- Fixed Stars (reference)
CREATE TABLE IF NOT EXISTS astro_fixed_stars (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    traditional_name VARCHAR(50),
    constellation VARCHAR(50),
    magnitude NUMERIC(4,2),
    nature TEXT,                          -- planetary nature (e.g., "Mars-Jupiter")
    longitude_j2000 NUMERIC(10,6),        -- position at J2000 epoch
    latitude NUMERIC(10,6),
    annual_precession NUMERIC(8,6)        -- for calculating current position
);

-- ============================================================================
-- CHART TABLES
-- ============================================================================

-- Core chart record
CREATE TABLE IF NOT EXISTS astro_charts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Who/what this chart is for
    entity_type VARCHAR(20) NOT NULL,     -- person, event, entity, horary, election
    entity_name VARCHAR(100) NOT NULL,    -- "Ka'tuar'el", "Iris", "Wedding", etc
    entity_id UUID,                       -- optional link to souls table or other entity
    
    -- Birth/event data
    event_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    event_datetime_utc TIMESTAMP NOT NULL,
    timezone VARCHAR(50) NOT NULL,
    timezone_offset_minutes INTEGER NOT NULL,
    
    -- Location
    location_name VARCHAR(200),
    latitude NUMERIC(10,7) NOT NULL,
    longitude NUMERIC(11,7) NOT NULL,
    altitude_meters NUMERIC(8,2) DEFAULT 0,
    
    -- Calculation settings
    house_system VARCHAR(30) DEFAULT 'Placidus',
    zodiac_type VARCHAR(20) DEFAULT 'tropical', -- tropical or sidereal
    ayanamsa VARCHAR(30),                 -- if sidereal, which ayanamsa
    
    -- Metadata
    notes TEXT,
    source VARCHAR(50),                   -- birth certificate, memory, rectified, etc
    source_accuracy VARCHAR(20),          -- exact, approximate, rectified, unknown
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Chart type
    chart_type VARCHAR(30) DEFAULT 'natal', -- natal, transit, progressed, solar_return, lunar_return, composite, synastry, horary, election, event
    
    -- For derived charts, link to base chart
    base_chart_id UUID REFERENCES astro_charts(id),
    
    -- For synastry/composite, second person
    partner_chart_id UUID REFERENCES astro_charts(id)
);

CREATE INDEX idx_astro_charts_entity ON astro_charts(entity_type, entity_name);
CREATE INDEX idx_astro_charts_datetime ON astro_charts(event_datetime_utc);
CREATE INDEX idx_astro_charts_type ON astro_charts(chart_type);

-- ============================================================================
-- PLACEMENTS (positions in a chart)
-- ============================================================================

-- Individual body placements in a chart
CREATE TABLE IF NOT EXISTS astro_placements (
    id SERIAL PRIMARY KEY,
    chart_id UUID NOT NULL REFERENCES astro_charts(id) ON DELETE CASCADE,
    body_name VARCHAR(50) NOT NULL,       -- references astro_bodies.name
    
    -- Position in zodiac
    longitude NUMERIC(12,8) NOT NULL,     -- 0-360 degrees, high precision
    latitude NUMERIC(10,8),               -- ecliptic latitude (for planets)
    distance_au NUMERIC(14,8),            -- distance from Earth in AU
    
    -- Derived position data
    sign VARCHAR(20) NOT NULL,
    sign_degree INTEGER NOT NULL,         -- 0-29
    sign_minute INTEGER NOT NULL,         -- 0-59
    sign_second NUMERIC(5,2),             -- 0-59.99
    
    -- Display format: "15°42'33" Aries"
    position_display VARCHAR(30) NOT NULL,
    
    -- House placement
    house_number INTEGER,                 -- 1-12
    house_position NUMERIC(8,4),          -- degrees into the house
    
    -- Motion
    is_retrograde BOOLEAN DEFAULT false,
    daily_motion NUMERIC(10,6),           -- degrees per day at this moment
    speed_ratio NUMERIC(6,4),             -- ratio to mean speed (1.0 = average)
    
    -- Dignity (calculated, stored for quick access)
    dignity VARCHAR(20),                  -- domicile, exaltation, detriment, fall, peregrine
    
    -- For calculated points that have multiple methods
    calculation_method VARCHAR(30),       -- true, mean, oscillating, etc
    
    UNIQUE(chart_id, body_name, calculation_method)
);

CREATE INDEX idx_astro_placements_chart ON astro_placements(chart_id);
CREATE INDEX idx_astro_placements_body ON astro_placements(body_name);
CREATE INDEX idx_astro_placements_sign ON astro_placements(sign);

-- House cusps for a chart
CREATE TABLE IF NOT EXISTS astro_house_cusps (
    id SERIAL PRIMARY KEY,
    chart_id UUID NOT NULL REFERENCES astro_charts(id) ON DELETE CASCADE,
    house_number INTEGER NOT NULL,        -- 1-12
    
    -- Cusp position
    longitude NUMERIC(12,8) NOT NULL,
    sign VARCHAR(20) NOT NULL,
    sign_degree INTEGER NOT NULL,
    sign_minute INTEGER NOT NULL,
    sign_second NUMERIC(5,2),
    position_display VARCHAR(30) NOT NULL,
    
    -- Intercepted sign (if any)
    intercepted_sign VARCHAR(20),
    
    UNIQUE(chart_id, house_number)
);

CREATE INDEX idx_astro_house_cusps_chart ON astro_house_cusps(chart_id);

-- ============================================================================
-- ASPECTS
-- ============================================================================

-- Aspects within a single chart (natal aspects)
CREATE TABLE IF NOT EXISTS astro_aspects (
    id SERIAL PRIMARY KEY,
    chart_id UUID NOT NULL REFERENCES astro_charts(id) ON DELETE CASCADE,
    
    -- The two bodies in aspect
    body1_name VARCHAR(50) NOT NULL,
    body2_name VARCHAR(50) NOT NULL,
    
    -- Aspect details
    aspect_type VARCHAR(30) NOT NULL,     -- conjunction, trine, square, etc
    aspect_angle NUMERIC(6,3) NOT NULL,   -- exact angle of aspect type
    
    -- Actual separation
    orb NUMERIC(6,3) NOT NULL,            -- actual orb in degrees
    is_applying BOOLEAN,                  -- true=applying, false=separating
    
    -- Strength/significance
    orb_percentage NUMERIC(5,2),          -- how tight (100% = exact)
    is_major BOOLEAN DEFAULT false,
    
    UNIQUE(chart_id, body1_name, body2_name, aspect_type)
);

CREATE INDEX idx_astro_aspects_chart ON astro_aspects(chart_id);
CREATE INDEX idx_astro_aspects_type ON astro_aspects(aspect_type);

-- ============================================================================
-- TRANSITS
-- ============================================================================

-- Transit events (transiting planet aspecting natal position)
CREATE TABLE IF NOT EXISTS astro_transits (
    id SERIAL PRIMARY KEY,
    natal_chart_id UUID NOT NULL REFERENCES astro_charts(id) ON DELETE CASCADE,
    
    -- Transit timing
    transit_datetime_utc TIMESTAMP NOT NULL,
    
    -- Transiting body
    transiting_body VARCHAR(50) NOT NULL,
    transiting_longitude NUMERIC(12,8) NOT NULL,
    transiting_sign VARCHAR(20) NOT NULL,
    transiting_is_retrograde BOOLEAN DEFAULT false,
    
    -- Natal body being aspected
    natal_body VARCHAR(50) NOT NULL,
    natal_longitude NUMERIC(12,8) NOT NULL,
    
    -- Aspect
    aspect_type VARCHAR(30) NOT NULL,
    orb NUMERIC(6,3) NOT NULL,
    is_applying BOOLEAN,
    
    -- Event type
    event_type VARCHAR(30),               -- exact, enters_orb, leaves_orb, station_on
    
    -- Significance
    is_major BOOLEAN DEFAULT false,
    
    UNIQUE(natal_chart_id, transit_datetime_utc, transiting_body, natal_body, aspect_type, event_type)
);

CREATE INDEX idx_astro_transits_chart ON astro_transits(natal_chart_id);
CREATE INDEX idx_astro_transits_datetime ON astro_transits(transit_datetime_utc);
CREATE INDEX idx_astro_transits_bodies ON astro_transits(transiting_body, natal_body);

-- ============================================================================
-- EPHEMERIS (daily planetary positions)
-- ============================================================================

-- Daily ephemeris for all tracked bodies
CREATE TABLE IF NOT EXISTS astro_ephemeris (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    body_name VARCHAR(50) NOT NULL,
    
    -- Position at midnight UTC
    longitude NUMERIC(12,8) NOT NULL,
    latitude NUMERIC(10,8),
    distance_au NUMERIC(14,8),
    
    -- Derived
    sign VARCHAR(20) NOT NULL,
    sign_degree INTEGER NOT NULL,
    position_display VARCHAR(30) NOT NULL,
    
    -- Motion
    is_retrograde BOOLEAN DEFAULT false,
    daily_motion NUMERIC(10,6),
    
    -- For lunar data
    moon_phase VARCHAR(20),               -- new, waxing_crescent, first_quarter, etc
    moon_phase_percentage NUMERIC(5,2),   -- 0-100
    is_void_of_course BOOLEAN DEFAULT false,
    void_of_course_until TIMESTAMP,
    
    UNIQUE(date, body_name)
);

CREATE INDEX idx_astro_ephemeris_date ON astro_ephemeris(date);
CREATE INDEX idx_astro_ephemeris_body ON astro_ephemeris(body_name);
CREATE INDEX idx_astro_ephemeris_sign ON astro_ephemeris(sign);

-- Ingresses (planet entering new sign)
CREATE TABLE IF NOT EXISTS astro_ingresses (
    id SERIAL PRIMARY KEY,
    body_name VARCHAR(50) NOT NULL,
    entering_sign VARCHAR(20) NOT NULL,
    leaving_sign VARCHAR(20) NOT NULL,
    ingress_datetime_utc TIMESTAMP NOT NULL,
    is_retrograde_ingress BOOLEAN DEFAULT false,
    
    UNIQUE(body_name, entering_sign, ingress_datetime_utc)
);

CREATE INDEX idx_astro_ingresses_datetime ON astro_ingresses(ingress_datetime_utc);

-- Retrograde periods
CREATE TABLE IF NOT EXISTS astro_retrogrades (
    id SERIAL PRIMARY KEY,
    body_name VARCHAR(50) NOT NULL,
    
    -- Shadow period (pre-retrograde)
    shadow_start_datetime_utc TIMESTAMP,
    shadow_start_degree NUMERIC(12,8),
    
    -- Station retrograde
    station_retrograde_datetime_utc TIMESTAMP NOT NULL,
    station_retrograde_degree NUMERIC(12,8) NOT NULL,
    station_retrograde_sign VARCHAR(20) NOT NULL,
    
    -- Station direct
    station_direct_datetime_utc TIMESTAMP,
    station_direct_degree NUMERIC(12,8),
    station_direct_sign VARCHAR(20),
    
    -- Shadow period (post-retrograde)
    shadow_end_datetime_utc TIMESTAMP,
    shadow_end_degree NUMERIC(12,8),
    
    UNIQUE(body_name, station_retrograde_datetime_utc)
);

CREATE INDEX idx_astro_retrogrades_body ON astro_retrogrades(body_name);
CREATE INDEX idx_astro_retrogrades_datetime ON astro_retrogrades(station_retrograde_datetime_utc);

-- ============================================================================
-- ECLIPSES
-- ============================================================================

CREATE TABLE IF NOT EXISTS astro_eclipses (
    id SERIAL PRIMARY KEY,
    eclipse_datetime_utc TIMESTAMP NOT NULL,
    
    -- Type
    eclipse_type VARCHAR(20) NOT NULL,    -- solar_total, solar_partial, solar_annular, lunar_total, lunar_partial, lunar_penumbral
    body VARCHAR(10) NOT NULL,            -- sun or moon
    
    -- Position
    longitude NUMERIC(12,8) NOT NULL,
    sign VARCHAR(20) NOT NULL,
    sign_degree INTEGER NOT NULL,
    position_display VARCHAR(30) NOT NULL,
    
    -- Saros cycle
    saros_series INTEGER,
    saros_member INTEGER,
    
    -- Visibility
    visibility_path TEXT,                 -- geographic description
    max_duration_minutes NUMERIC(6,2),
    
    UNIQUE(eclipse_datetime_utc, eclipse_type)
);

CREATE INDEX idx_astro_eclipses_datetime ON astro_eclipses(eclipse_datetime_utc);
CREATE INDEX idx_astro_eclipses_sign ON astro_eclipses(sign);

-- ============================================================================
-- ASTROLOGICAL EVENTS (general)
-- ============================================================================

CREATE TABLE IF NOT EXISTS astro_events (
    id SERIAL PRIMARY KEY,
    event_datetime_utc TIMESTAMP NOT NULL,
    
    -- Event type
    event_type VARCHAR(50) NOT NULL,      -- conjunction, ingress, station, eclipse, moon_phase, aspect_exact
    event_subtype VARCHAR(50),            -- specific (e.g., "mars_saturn_conjunction")
    
    -- Bodies involved
    body1_name VARCHAR(50) NOT NULL,
    body2_name VARCHAR(50),               -- null for single-body events like ingress
    
    -- Position
    longitude NUMERIC(12,8),
    sign VARCHAR(20),
    position_display VARCHAR(50),
    
    -- Description
    title VARCHAR(200) NOT NULL,          -- "Mars conjunct Saturn at 15° Pisces"
    description TEXT,
    
    -- Significance
    significance_level INTEGER DEFAULT 5, -- 1-10 scale
    
    UNIQUE(event_datetime_utc, event_type, body1_name, body2_name)
);

CREATE INDEX idx_astro_events_datetime ON astro_events(event_datetime_utc);
CREATE INDEX idx_astro_events_type ON astro_events(event_type);
CREATE INDEX idx_astro_events_significance ON astro_events(significance_level);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Current sky view (today's positions)
CREATE OR REPLACE VIEW v_current_sky AS
SELECT 
    e.body_name,
    b.symbol,
    b.body_type,
    e.sign,
    e.sign_degree,
    e.position_display,
    e.is_retrograde,
    e.moon_phase,
    e.is_void_of_course
FROM astro_ephemeris e
JOIN astro_bodies b ON e.body_name = b.name
WHERE e.date = CURRENT_DATE
AND b.is_active = true
ORDER BY 
    CASE b.body_type 
        WHEN 'luminary' THEN 1 
        WHEN 'planet' THEN 2 
        WHEN 'dwarf_planet' THEN 3
        WHEN 'asteroid' THEN 4
        WHEN 'centaur' THEN 5
        ELSE 6 
    END,
    e.longitude;

-- Upcoming significant transits view (requires natal chart parameter)
-- This would be used as a function or with a WHERE clause

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Calculate sign from longitude
CREATE OR REPLACE FUNCTION get_sign_from_longitude(lng NUMERIC)
RETURNS VARCHAR(20) AS $$
BEGIN
    RETURN CASE 
        WHEN lng >= 0 AND lng < 30 THEN 'Aries'
        WHEN lng >= 30 AND lng < 60 THEN 'Taurus'
        WHEN lng >= 60 AND lng < 90 THEN 'Gemini'
        WHEN lng >= 90 AND lng < 120 THEN 'Cancer'
        WHEN lng >= 120 AND lng < 150 THEN 'Leo'
        WHEN lng >= 150 AND lng < 180 THEN 'Virgo'
        WHEN lng >= 180 AND lng < 210 THEN 'Libra'
        WHEN lng >= 210 AND lng < 240 THEN 'Scorpio'
        WHEN lng >= 240 AND lng < 270 THEN 'Sagittarius'
        WHEN lng >= 270 AND lng < 300 THEN 'Capricorn'
        WHEN lng >= 300 AND lng < 330 THEN 'Aquarius'
        WHEN lng >= 330 AND lng < 360 THEN 'Pisces'
        ELSE 'Unknown'
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Calculate degree within sign
CREATE OR REPLACE FUNCTION get_sign_degree(lng NUMERIC)
RETURNS INTEGER AS $$
BEGIN
    RETURN FLOOR(lng::numeric % 30)::INTEGER;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Format position for display
CREATE OR REPLACE FUNCTION format_position(lng NUMERIC)
RETURNS VARCHAR(30) AS $$
DECLARE
    sign_deg INTEGER;
    sign_min INTEGER;
    sign_sec NUMERIC(5,2);
    sign_name VARCHAR(20);
BEGIN
    sign_name := get_sign_from_longitude(lng);
    sign_deg := FLOOR(lng::numeric % 30)::INTEGER;
    sign_min := FLOOR(((lng::numeric % 30) - sign_deg) * 60)::INTEGER;
    sign_sec := ((((lng::numeric % 30) - sign_deg) * 60) - sign_min) * 60;
    
    RETURN sign_deg || '°' || LPAD(sign_min::text, 2, '0') || '''' || 
           LPAD(FLOOR(sign_sec)::text, 2, '0') || '" ' || sign_name;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Calculate aspect between two longitudes
CREATE OR REPLACE FUNCTION calculate_aspect(lng1 NUMERIC, lng2 NUMERIC)
RETURNS TABLE(aspect_type VARCHAR, orb NUMERIC, is_applying BOOLEAN) AS $$
DECLARE
    diff NUMERIC;
    aspects RECORD;
BEGIN
    -- Calculate shortest arc
    diff := ABS(lng1 - lng2);
    IF diff > 180 THEN
        diff := 360 - diff;
    END IF;
    
    -- Check each aspect type
    FOR aspects IN 
        SELECT name, angle, orb_default 
        FROM astro_aspect_types 
        ORDER BY is_major DESC, orb_default DESC
    LOOP
        IF ABS(diff - aspects.angle) <= aspects.orb_default THEN
            RETURN QUERY SELECT 
                aspects.name::VARCHAR,
                ABS(diff - aspects.angle),
                NULL::BOOLEAN; -- would need motion data to determine applying
            RETURN;
        END IF;
    END LOOP;
    
    RETURN;
END;
$$ LANGUAGE plpgsql STABLE;
