-- ============================================================================
-- MYTHOS ASTROLOGY SYSTEM - PostgreSQL Seed Data
-- ============================================================================

-- ============================================================================
-- ZODIAC SIGNS
-- ============================================================================

INSERT INTO astro_signs (name, symbol, abbreviation, element, modality, polarity, degree_start, degree_end, sort_order) VALUES
('Aries', '♈', 'ARI', 'fire', 'cardinal', 'yang', 0.00, 29.99, 1),
('Taurus', '♉', 'TAU', 'earth', 'fixed', 'yin', 30.00, 59.99, 2),
('Gemini', '♊', 'GEM', 'air', 'mutable', 'yang', 60.00, 89.99, 3),
('Cancer', '♋', 'CAN', 'water', 'cardinal', 'yin', 90.00, 119.99, 4),
('Leo', '♌', 'LEO', 'fire', 'fixed', 'yang', 120.00, 149.99, 5),
('Virgo', '♍', 'VIR', 'earth', 'mutable', 'yin', 150.00, 179.99, 6),
('Libra', '♎', 'LIB', 'air', 'cardinal', 'yang', 180.00, 209.99, 7),
('Scorpio', '♏', 'SCO', 'water', 'fixed', 'yin', 210.00, 239.99, 8),
('Sagittarius', '♐', 'SAG', 'fire', 'mutable', 'yang', 240.00, 269.99, 9),
('Capricorn', '♑', 'CAP', 'earth', 'cardinal', 'yin', 270.00, 299.99, 10),
('Aquarius', '♒', 'AQU', 'air', 'fixed', 'yang', 300.00, 329.99, 11),
('Pisces', '♓', 'PIS', 'water', 'mutable', 'yin', 330.00, 359.99, 12)
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- CELESTIAL BODIES
-- ============================================================================

-- Luminaries
INSERT INTO astro_bodies (name, symbol, abbreviation, body_type, swiss_eph_id, is_retrograde_capable, orbital_period_days, mean_daily_motion, default_orb, is_active) VALUES
('Sun', '☉', 'SUN', 'luminary', 0, false, 365.25, 0.9856, 10.0, true),
('Moon', '☽', 'MOO', 'luminary', 1, false, 27.32, 13.1764, 10.0, true)
ON CONFLICT (name) DO NOTHING;

-- Classical Planets
INSERT INTO astro_bodies (name, symbol, abbreviation, body_type, swiss_eph_id, is_retrograde_capable, orbital_period_days, mean_daily_motion, default_orb, is_active) VALUES
('Mercury', '☿', 'MER', 'planet', 2, true, 87.97, 4.0923, 8.0, true),
('Venus', '♀', 'VEN', 'planet', 3, true, 224.70, 1.6021, 8.0, true),
('Mars', '♂', 'MAR', 'planet', 4, true, 686.98, 0.5240, 8.0, true),
('Jupiter', '♃', 'JUP', 'planet', 5, true, 4332.59, 0.0831, 8.0, true),
('Saturn', '♄', 'SAT', 'planet', 6, true, 10759.22, 0.0335, 8.0, true)
ON CONFLICT (name) DO NOTHING;

-- Modern Planets
INSERT INTO astro_bodies (name, symbol, abbreviation, body_type, swiss_eph_id, is_retrograde_capable, orbital_period_days, mean_daily_motion, default_orb, is_active) VALUES
('Uranus', '♅', 'URA', 'planet', 7, true, 30688.50, 0.0117, 6.0, true),
('Neptune', '♆', 'NEP', 'planet', 8, true, 60182.00, 0.0060, 6.0, true),
('Pluto', '♇', 'PLU', 'dwarf_planet', 9, true, 90560.00, 0.0040, 6.0, true)
ON CONFLICT (name) DO NOTHING;

-- Dwarf Planets
INSERT INTO astro_bodies (name, symbol, abbreviation, body_type, swiss_eph_id, is_retrograde_capable, orbital_period_days, mean_daily_motion, default_orb, is_active) VALUES
('Ceres', '⚳', 'CER', 'dwarf_planet', 17, true, 1680.00, 0.2143, 4.0, true),
('Eris', NULL, 'ERI', 'dwarf_planet', 136199, true, 203830.00, 0.0018, 4.0, true),
('Makemake', NULL, 'MAK', 'dwarf_planet', 136472, true, 112897.00, 0.0032, 3.0, false),
('Haumea', NULL, 'HAU', 'dwarf_planet', 136108, true, 103774.00, 0.0035, 3.0, false),
('Sedna', NULL, 'SED', 'dwarf_planet', 90377, true, 4404480.00, 0.0001, 3.0, false),
('Quaoar', NULL, 'QUA', 'dwarf_planet', 50000, true, 105023.00, 0.0034, 3.0, false),
('Orcus', NULL, 'ORC', 'dwarf_planet', 90482, true, 90470.00, 0.0040, 3.0, false)
ON CONFLICT (name) DO NOTHING;

-- Major Asteroids
INSERT INTO astro_bodies (name, symbol, abbreviation, body_type, swiss_eph_id, is_retrograde_capable, orbital_period_days, mean_daily_motion, default_orb, is_active) VALUES
('Pallas', '⚴', 'PAL', 'asteroid', 2, true, 1684.87, 0.2137, 4.0, true),
('Juno', '⚵', 'JUN', 'asteroid', 3, true, 1594.00, 0.2259, 4.0, true),
('Vesta', '⚶', 'VES', 'asteroid', 4, true, 1325.75, 0.2716, 4.0, true),
('Hygiea', NULL, 'HYG', 'asteroid', 10, true, 2030.00, 0.1773, 2.0, false),
('Psyche', NULL, 'PSY', 'asteroid', 16, true, 1828.00, 0.1969, 2.0, false),
('Eros', NULL, 'ERO', 'asteroid', 433, true, 643.00, 0.5600, 2.0, false)
ON CONFLICT (name) DO NOTHING;

-- Centaurs
INSERT INTO astro_bodies (name, symbol, abbreviation, body_type, swiss_eph_id, is_retrograde_capable, orbital_period_days, mean_daily_motion, default_orb, is_active) VALUES
('Chiron', '⚷', 'CHI', 'centaur', 15, true, 18500.00, 0.0195, 5.0, true),
('Pholus', NULL, 'PHO', 'centaur', 5145, true, 33636.00, 0.0107, 3.0, false),
('Nessus', NULL, 'NES', 'centaur', 7066, true, 44060.00, 0.0082, 3.0, false),
('Chariklo', NULL, 'CHA', 'centaur', 10199, true, 23818.00, 0.0151, 2.0, false)
ON CONFLICT (name) DO NOTHING;

-- Lunar Points
INSERT INTO astro_bodies (name, symbol, abbreviation, body_type, swiss_eph_id, is_retrograde_capable, orbital_period_days, mean_daily_motion, default_orb, is_active) VALUES
('North Node', '☊', 'NNO', 'point', 10, false, 6798.38, 0.0530, 6.0, true),
('South Node', '☋', 'SNO', 'point', NULL, false, 6798.38, 0.0530, 6.0, true),
('Black Moon Lilith', '⚸', 'LIL', 'point', 12, false, 3231.50, 0.1114, 4.0, true)
ON CONFLICT (name) DO NOTHING;

-- Calculated Points & Angles
INSERT INTO astro_bodies (name, symbol, abbreviation, body_type, swiss_eph_id, is_retrograde_capable, orbital_period_days, mean_daily_motion, default_orb, is_active) VALUES
('Part of Fortune', '⊗', 'POF', 'lot', NULL, false, NULL, NULL, 4.0, true),
('Vertex', 'Vx', 'VTX', 'point', NULL, false, NULL, NULL, 3.0, true),
('Ascendant', 'AC', 'ASC', 'angle', NULL, false, NULL, NULL, 8.0, true),
('Midheaven', 'MC', 'MC', 'angle', NULL, false, NULL, NULL, 8.0, true),
('Descendant', 'DC', 'DSC', 'angle', NULL, false, NULL, NULL, 6.0, true),
('Imum Coeli', 'IC', 'IC', 'angle', NULL, false, NULL, NULL, 6.0, true)
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- HOUSES
-- ============================================================================

INSERT INTO astro_houses (number, name, abbreviation, natural_sign, axis) VALUES
(1, 'House of Self', 'H1', 'Aries', 'self-other'),
(2, 'House of Values', 'H2', 'Taurus', 'resources'),
(3, 'House of Communication', 'H3', 'Gemini', 'knowledge'),
(4, 'House of Home', 'H4', 'Cancer', 'private-public'),
(5, 'House of Creativity', 'H5', 'Leo', 'creativity'),
(6, 'House of Health', 'H6', 'Virgo', 'service'),
(7, 'House of Partnership', 'H7', 'Libra', 'self-other'),
(8, 'House of Transformation', 'H8', 'Scorpio', 'resources'),
(9, 'House of Philosophy', 'H9', 'Sagittarius', 'knowledge'),
(10, 'House of Career', 'H10', 'Capricorn', 'private-public'),
(11, 'House of Community', 'H11', 'Aquarius', 'creativity'),
(12, 'House of the Unconscious', 'H12', 'Pisces', 'service')
ON CONFLICT (number) DO NOTHING;

-- ============================================================================
-- ASPECT TYPES
-- ============================================================================

INSERT INTO astro_aspect_types (name, symbol, angle, orb_default, is_major, is_harmonious, sort_order) VALUES
('Conjunction', '☌', 0.000, 10.00, true, NULL, 1),
('Opposition', '☍', 180.000, 8.00, true, false, 2),
('Trine', '△', 120.000, 8.00, true, true, 3),
('Square', '□', 90.000, 7.00, true, false, 4),
('Sextile', '⚹', 60.000, 6.00, true, true, 5),
('Quincunx', '⚻', 150.000, 3.00, false, NULL, 6),
('Semi-sextile', '⚺', 30.000, 2.00, false, NULL, 7),
('Semi-square', NULL, 45.000, 2.00, false, false, 8),
('Sesquiquadrate', NULL, 135.000, 2.00, false, false, 9),
('Quintile', NULL, 72.000, 2.00, false, true, 10),
('Bi-quintile', NULL, 144.000, 2.00, false, true, 11)
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- HOUSE SYSTEMS
-- ============================================================================

INSERT INTO astro_house_systems (name, code, description) VALUES
('Placidus', 'P', 'Most popular Western system. Time-based division.'),
('Whole Sign', 'W', 'Ancient system. Each sign = one house.'),
('Equal House', 'E', 'Ascendant is 1st cusp, all houses 30 degrees.'),
('Koch', 'K', 'Similar to Placidus with different calculation.'),
('Campanus', 'C', 'Space-based. Prime vertical divided equally.'),
('Regiomontanus', 'R', 'Celestial equator divided equally.'),
('Porphyry', 'O', 'Quadrants divided into three equal parts.'),
('Topocentric', 'T', 'Modified Placidus for high latitudes.')
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- FIXED STARS (Major)
-- ============================================================================

INSERT INTO astro_fixed_stars (name, traditional_name, constellation, magnitude, nature, longitude_j2000, latitude, annual_precession) VALUES
('Regulus', 'Cor Leonis', 'Leo', 1.35, 'Mars-Jupiter', 149.828, 0.466, 0.0139),
('Spica', 'Alpha Virginis', 'Virgo', 0.98, 'Venus-Mars', 203.672, -2.052, 0.0139),
('Algol', 'Caput Medusae', 'Perseus', 2.12, 'Saturn-Jupiter', 56.168, 22.415, 0.0139),
('Antares', 'Cor Scorpii', 'Scorpius', 1.09, 'Mars-Jupiter', 249.290, -4.569, 0.0139),
('Aldebaran', 'Eye of Taurus', 'Taurus', 0.87, 'Mars', 69.682, -5.469, 0.0139),
('Fomalhaut', 'Mouth of Fish', 'Piscis Austrinus', 1.16, 'Venus-Mercury', 333.549, -21.122, 0.0139),
('Sirius', 'Dog Star', 'Canis Major', -1.46, 'Jupiter-Mars', 104.084, -39.609, 0.0139),
('Vega', 'Alpha Lyrae', 'Lyra', 0.03, 'Venus-Mercury', 279.235, 61.726, 0.0139),
('Arcturus', 'Alpha Bootis', 'Bootes', -0.05, 'Mars-Jupiter', 213.915, 30.741, 0.0139),
('Polaris', 'North Star', 'Ursa Minor', 1.98, 'Saturn-Venus', 37.951, 66.077, 0.0139),
('Betelgeuse', 'Alpha Orionis', 'Orion', 0.42, 'Mars-Mercury', 88.795, -16.039, 0.0139),
('Rigel', 'Beta Orionis', 'Orion', 0.13, 'Jupiter-Saturn', 78.640, -31.116, 0.0139),
('Pleiades', 'Alcyone', 'Taurus', 2.87, 'Moon-Mars', 60.027, 4.047, 0.0139)
ON CONFLICT (name) DO NOTHING;
