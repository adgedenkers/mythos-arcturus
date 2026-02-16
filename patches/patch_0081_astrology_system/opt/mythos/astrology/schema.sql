-- Mythos Astrology System Schema
-- Complete natal chart storage with comparison support

-- ============================================================================
-- CORE CHART STORAGE
-- ============================================================================

-- Main chart metadata
CREATE TABLE IF NOT EXISTS astro_charts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Entity identification
    entity_type VARCHAR(50) NOT NULL,  -- 'person', 'event', 'entity', 'location'
    entity_name VARCHAR(255) NOT NULL,
    person_id INTEGER REFERENCES people(id),  -- Link to people table if applicable
    
    -- Birth/event data
    event_datetime TIMESTAMP NOT NULL,
    event_datetime_utc TIMESTAMP NOT NULL,
    timezone VARCHAR(50),
    timezone_offset_minutes INTEGER,
    
    -- Location
    location_name TEXT,
    latitude DECIMAL(10, 6) NOT NULL,
    longitude DECIMAL(10, 6) NOT NULL,
    
    -- Calculation settings
    house_system VARCHAR(30) DEFAULT 'Placidus',
    zodiac_type VARCHAR(20) DEFAULT 'tropical',
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    calculated_by VARCHAR(100),
    notes TEXT,
    
    CONSTRAINT valid_entity_type CHECK (entity_type IN ('person', 'event', 'entity', 'location')),
    CONSTRAINT valid_house_system CHECK (house_system IN ('Placidus', 'Whole Sign', 'Equal House', 'Koch', 'Campanus', 'Regiomontanus', 'Porphyry')),
    CONSTRAINT valid_zodiac CHECK (zodiac_type IN ('tropical', 'sidereal'))
);

CREATE INDEX idx_astro_charts_entity ON astro_charts(entity_type, entity_name);
CREATE INDEX idx_astro_charts_person ON astro_charts(person_id);
CREATE INDEX idx_astro_charts_datetime ON astro_charts(event_datetime);

-- ============================================================================
-- PLANETARY PLACEMENTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS astro_placements (
    id BIGSERIAL PRIMARY KEY,
    chart_id UUID NOT NULL REFERENCES astro_charts(id) ON DELETE CASCADE,
    
    -- Body identification
    body_name VARCHAR(50) NOT NULL,
    body_type VARCHAR(30),  -- 'planet', 'luminary', 'node', 'asteroid', 'angle', 'point'
    
    -- Position
    longitude DECIMAL(10, 6) NOT NULL,  -- 0-360
    latitude DECIMAL(10, 6),
    distance_au DECIMAL(12, 8),
    
    -- Sign position
    sign VARCHAR(20) NOT NULL,
    sign_degree INTEGER NOT NULL,  -- 0-29
    sign_minute INTEGER NOT NULL,  -- 0-59
    sign_second DECIMAL(5, 2),     -- 0-59.99
    position_display VARCHAR(50),  -- "15°42'33" Aries"
    
    -- House position
    house_number INTEGER,  -- 1-12
    house_position VARCHAR(20),  -- 'early', 'middle', 'late'
    
    -- Motion
    is_retrograde BOOLEAN DEFAULT FALSE,
    daily_motion DECIMAL(10, 6),
    speed_ratio DECIMAL(6, 4),  -- Compared to average speed
    
    -- Dignity
    dignity VARCHAR(20),  -- 'domicile', 'exaltation', 'detriment', 'fall', 'peregrine'
    
    -- Calculation
    calculation_method VARCHAR(50) DEFAULT 'swiss_ephemeris',
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_body_type CHECK (body_type IN ('planet', 'luminary', 'node', 'asteroid', 'angle', 'point', NULL)),
    CONSTRAINT valid_sign CHECK (sign IN ('Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                                           'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces')),
    CONSTRAINT valid_house CHECK (house_number BETWEEN 1 AND 12 OR house_number IS NULL),
    CONSTRAINT valid_dignity CHECK (dignity IN ('domicile', 'exaltation', 'detriment', 'fall', 'peregrine', NULL)),
    
    UNIQUE(chart_id, body_name, calculation_method)
);

CREATE INDEX idx_astro_placements_chart ON astro_placements(chart_id);
CREATE INDEX idx_astro_placements_body ON astro_placements(body_name);
CREATE INDEX idx_astro_placements_sign ON astro_placements(sign);
CREATE INDEX idx_astro_placements_house ON astro_placements(house_number);

-- ============================================================================
-- HOUSE CUSPS
-- ============================================================================

CREATE TABLE IF NOT EXISTS astro_house_cusps (
    id BIGSERIAL PRIMARY KEY,
    chart_id UUID NOT NULL REFERENCES astro_charts(id) ON DELETE CASCADE,
    
    house_number INTEGER NOT NULL,  -- 1-12
    
    -- Position
    longitude DECIMAL(10, 6) NOT NULL,
    sign VARCHAR(20) NOT NULL,
    sign_degree INTEGER NOT NULL,
    sign_minute INTEGER NOT NULL,
    sign_second DECIMAL(5, 2),
    position_display VARCHAR(50),
    
    -- Interception
    intercepted_sign VARCHAR(20),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_house_number CHECK (house_number BETWEEN 1 AND 12),
    CONSTRAINT valid_cusp_sign CHECK (sign IN ('Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                                                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces')),
    
    UNIQUE(chart_id, house_number)
);

CREATE INDEX idx_astro_house_cusps_chart ON astro_house_cusps(chart_id);
CREATE INDEX idx_astro_house_cusps_house ON astro_house_cusps(house_number);

-- ============================================================================
-- ASPECTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS astro_aspects (
    id BIGSERIAL PRIMARY KEY,
    chart_id UUID NOT NULL REFERENCES astro_charts(id) ON DELETE CASCADE,
    
    -- Bodies involved
    body1_name VARCHAR(50) NOT NULL,
    body2_name VARCHAR(50) NOT NULL,
    
    -- Aspect
    aspect_type VARCHAR(30) NOT NULL,
    aspect_angle DECIMAL(5, 2) NOT NULL,  -- 0, 30, 60, 90, 120, 150, 180
    orb DECIMAL(5, 2) NOT NULL,
    orb_percentage DECIMAL(5, 2),  -- % of max orb
    
    -- Dynamics
    is_applying BOOLEAN,
    is_separating BOOLEAN,
    is_partile BOOLEAN,  -- Exact degree
    
    -- Strength
    is_major BOOLEAN DEFAULT TRUE,
    strength_score DECIMAL(5, 2),  -- 0-100
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_aspect_type CHECK (aspect_type IN ('Conjunction', 'Opposition', 'Trine', 'Square', 'Sextile',
                                                          'Quincunx', 'Semi-sextile', 'Semi-square', 'Sesquiquadrate')),
    
    UNIQUE(chart_id, body1_name, body2_name, aspect_type)
);

CREATE INDEX idx_astro_aspects_chart ON astro_aspects(chart_id);
CREATE INDEX idx_astro_aspects_bodies ON astro_aspects(body1_name, body2_name);
CREATE INDEX idx_astro_aspects_type ON astro_aspects(aspect_type);

-- ============================================================================
-- CHART COMPARISONS
-- ============================================================================

-- Track chart-to-chart comparisons (synastry, composite, davison)
CREATE TABLE IF NOT EXISTS astro_chart_comparisons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    comparison_type VARCHAR(30) NOT NULL,  -- 'synastry', 'composite', 'davison'
    
    -- Charts being compared
    chart1_id UUID NOT NULL REFERENCES astro_charts(id) ON DELETE CASCADE,
    chart2_id UUID NOT NULL REFERENCES astro_charts(id) ON DELETE CASCADE,
    chart3_id UUID REFERENCES astro_charts(id) ON DELETE CASCADE,  -- For tri-wheels
    
    -- Composite chart (if type = 'composite' or 'davison')
    composite_chart_id UUID REFERENCES astro_charts(id) ON DELETE CASCADE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    notes TEXT,
    
    CONSTRAINT valid_comparison_type CHECK (comparison_type IN ('synastry', 'composite', 'davison', 'triwheel')),
    CONSTRAINT different_charts CHECK (chart1_id != chart2_id)
);

CREATE INDEX idx_comparisons_chart1 ON astro_chart_comparisons(chart1_id);
CREATE INDEX idx_comparisons_chart2 ON astro_chart_comparisons(chart2_id);
CREATE INDEX idx_comparisons_type ON astro_chart_comparisons(comparison_type);

-- Inter-chart aspects
CREATE TABLE IF NOT EXISTS astro_comparison_aspects (
    id BIGSERIAL PRIMARY KEY,
    comparison_id UUID NOT NULL REFERENCES astro_chart_comparisons(id) ON DELETE CASCADE,
    
    -- Bodies from different charts
    chart1_body VARCHAR(50) NOT NULL,
    chart2_body VARCHAR(50) NOT NULL,
    
    -- Aspect
    aspect_type VARCHAR(30) NOT NULL,
    aspect_angle DECIMAL(5, 2) NOT NULL,
    orb DECIMAL(5, 2) NOT NULL,
    
    -- Strength
    is_major BOOLEAN DEFAULT TRUE,
    strength_score DECIMAL(5, 2),
    
    -- Interpretation hints
    harmony_score DECIMAL(5, 2),  -- -100 to +100
    keywords TEXT[],
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_comp_aspect_type CHECK (aspect_type IN ('Conjunction', 'Opposition', 'Trine', 'Square', 'Sextile',
                                                               'Quincunx', 'Semi-sextile'))
);

CREATE INDEX idx_comp_aspects_comparison ON astro_comparison_aspects(comparison_id);
CREATE INDEX idx_comp_aspects_bodies ON astro_comparison_aspects(chart1_body, chart2_body);

-- ============================================================================
-- HELPER VIEWS
-- ============================================================================

-- Quick chart summary view
CREATE OR REPLACE VIEW astro_chart_summary AS
SELECT 
    c.id,
    c.entity_name,
    c.entity_type,
    c.event_datetime,
    c.location_name,
    -- Sun sign
    (SELECT sign FROM astro_placements WHERE chart_id = c.id AND body_name = 'Sun' LIMIT 1) as sun_sign,
    -- Moon sign
    (SELECT sign FROM astro_placements WHERE chart_id = c.id AND body_name = 'Moon' LIMIT 1) as moon_sign,
    -- Rising sign
    (SELECT sign FROM astro_house_cusps WHERE chart_id = c.id AND house_number = 1 LIMIT 1) as rising_sign,
    -- Counts
    (SELECT COUNT(*) FROM astro_placements WHERE chart_id = c.id) as placement_count,
    (SELECT COUNT(*) FROM astro_aspects WHERE chart_id = c.id) as aspect_count,
    c.created_at
FROM astro_charts c;

-- Planet position across all charts
CREATE OR REPLACE VIEW astro_all_placements AS
SELECT 
    c.entity_name,
    c.entity_type,
    p.body_name,
    p.sign,
    p.sign_degree,
    p.house_number,
    p.is_retrograde,
    p.dignity,
    p.position_display,
    c.event_datetime,
    c.id as chart_id
FROM astro_charts c
JOIN astro_placements p ON c.id = p.chart_id
ORDER BY p.body_name, c.entity_name;

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- Function to get all placements for a chart as JSON
CREATE OR REPLACE FUNCTION get_chart_placements(chart_uuid UUID)
RETURNS JSON AS $$
SELECT json_agg(
    json_build_object(
        'body', body_name,
        'sign', sign,
        'degree', sign_degree,
        'minute', sign_minute,
        'house', house_number,
        'retrograde', is_retrograde,
        'display', position_display
    )
)
FROM astro_placements
WHERE chart_id = chart_uuid
ORDER BY 
    CASE body_name
        WHEN 'Sun' THEN 1
        WHEN 'Moon' THEN 2
        WHEN 'Mercury' THEN 3
        WHEN 'Venus' THEN 4
        WHEN 'Mars' THEN 5
        WHEN 'Jupiter' THEN 6
        WHEN 'Saturn' THEN 7
        WHEN 'Uranus' THEN 8
        WHEN 'Neptune' THEN 9
        WHEN 'Pluto' THEN 10
        ELSE 99
    END;
$$ LANGUAGE SQL;

-- Function to find charts by planet in sign
CREATE OR REPLACE FUNCTION find_charts_by_placement(
    p_body VARCHAR(50),
    p_sign VARCHAR(20)
)
RETURNS TABLE(
    entity_name VARCHAR(255),
    degree_display VARCHAR(50),
    house_number INTEGER,
    chart_id UUID
) AS $$
SELECT 
    c.entity_name,
    p.position_display,
    p.house_number,
    c.id
FROM astro_charts c
JOIN astro_placements p ON c.id = p.chart_id
WHERE p.body_name = p_body
  AND p.sign = p_sign
ORDER BY c.entity_name;
$$ LANGUAGE SQL;

-- ============================================================================
-- GRANTS
-- ============================================================================

GRANT SELECT, INSERT, UPDATE, DELETE ON astro_charts TO adge;
GRANT SELECT, INSERT, UPDATE, DELETE ON astro_placements TO adge;
GRANT SELECT, INSERT, UPDATE, DELETE ON astro_house_cusps TO adge;
GRANT SELECT, INSERT, UPDATE, DELETE ON astro_aspects TO adge;
GRANT SELECT, INSERT, UPDATE, DELETE ON astro_chart_comparisons TO adge;
GRANT SELECT, INSERT, UPDATE, DELETE ON astro_comparison_aspects TO adge;

GRANT USAGE, SELECT ON SEQUENCE astro_placements_id_seq TO adge;
GRANT USAGE, SELECT ON SEQUENCE astro_house_cusps_id_seq TO adge;
GRANT USAGE, SELECT ON SEQUENCE astro_aspects_id_seq TO adge;
GRANT USAGE, SELECT ON SEQUENCE astro_comparison_aspects_id_seq TO adge;

-- ============================================================================
-- DONE
-- ============================================================================

-- Summary
DO $$
BEGIN
    RAISE NOTICE 'Astrology schema installed successfully';
    RAISE NOTICE 'Tables: astro_charts, astro_placements, astro_house_cusps, astro_aspects';
    RAISE NOTICE 'Tables: astro_chart_comparisons, astro_comparison_aspects';
    RAISE NOTICE 'Views: astro_chart_summary, astro_all_placements';
    RAISE NOTICE 'Functions: get_chart_placements(), find_charts_by_placement()';
END $$;
