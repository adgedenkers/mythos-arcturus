-- Astrological Events Table for Mythos System
-- Captures solar system state changes: ingresses, aspects, stations, eclipses, lunations

DROP TABLE IF EXISTS astro_events CASCADE;

CREATE TABLE astro_events (
    id SERIAL PRIMARY KEY,
    event_date DATE NOT NULL,
    event_time TIME,                          -- NULL if time unknown/all-day
    event_type VARCHAR(50) NOT NULL,          -- ingress, aspect, station, eclipse, lunation, cazimi, stellium
    primary_body VARCHAR(30) NOT NULL,        -- Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Chiron, North Node, etc.
    secondary_body VARCHAR(30),               -- For aspects: the other planet. NULL for ingresses/stations
    aspect_type VARCHAR(30),                  -- conjunction, opposition, trine, square, sextile, quincunx, semi-sextile, semi-square, sesquiquadrate, etc.
    sign_1 VARCHAR(20),                       -- Sign of primary body
    sign_2 VARCHAR(20),                       -- Sign of secondary body (for aspects)
    degree_1 DECIMAL(5,2),                    -- Degree within sign (0-29.99)
    degree_2 DECIMAL(5,2),                    -- Degree of secondary body
    absolute_degree_1 DECIMAL(6,2),           -- Absolute zodiac degree (0-359.99)
    absolute_degree_2 DECIMAL(6,2),
    direction VARCHAR(10),                    -- direct, retrograde, stationary (for stations)
    eclipse_type VARCHAR(20),                 -- solar, lunar, annular, total, partial, penumbral
    significance VARCHAR(20) DEFAULT 'normal', -- major, significant, normal, minor
    notes TEXT,
    cycle_info TEXT,                          -- e.g., "36-year Saturn-Neptune cycle", "final pass of series"
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT valid_event_type CHECK (event_type IN ('ingress', 'aspect', 'station', 'eclipse', 'lunation', 'cazimi', 'stellium', 'other')),
    CONSTRAINT valid_significance CHECK (significance IN ('major', 'significant', 'normal', 'minor'))
);

-- Indexes for common queries
CREATE INDEX idx_astro_events_date ON astro_events(event_date);
CREATE INDEX idx_astro_events_type ON astro_events(event_type);
CREATE INDEX idx_astro_events_primary_body ON astro_events(primary_body);
CREATE INDEX idx_astro_events_significance ON astro_events(significance);
CREATE INDEX idx_astro_events_date_type ON astro_events(event_date, event_type);

-- Insert Jan 15 - Apr 15, 2026 events
INSERT INTO astro_events (event_date, event_time, event_type, primary_body, secondary_body, aspect_type, sign_1, sign_2, degree_1, degree_2, direction, eclipse_type, significance, notes, cycle_info) VALUES

-- JANUARY 2026
('2026-01-17', '07:43:00', 'ingress', 'Venus', NULL, NULL, 'Aquarius', NULL, 0.00, NULL, 'direct', NULL, 'normal', 'Venus enters Aquarius', NULL),
('2026-01-19', '20:45:00', 'ingress', 'Sun', NULL, NULL, 'Aquarius', NULL, 0.00, NULL, 'direct', NULL, 'normal', 'Sun enters Aquarius', NULL),
('2026-01-20', '00:18:00', 'aspect', 'Saturn', 'Uranus', 'sextile', 'Pisces', 'Taurus', 27.57, 27.57, NULL, NULL, 'significant', 'Saturn sextile Uranus - final pass of series', 'Third and final pass; first Apr 2025, second Aug 2025'),
('2026-01-20', '11:41:00', 'ingress', 'Mercury', NULL, NULL, 'Aquarius', NULL, 0.00, NULL, 'direct', NULL, 'normal', 'Mercury enters Aquarius', NULL),
('2026-01-23', '04:16:00', 'ingress', 'Mars', NULL, NULL, 'Aquarius', NULL, 0.00, NULL, 'direct', NULL, 'normal', 'Mars enters Aquarius - joins Sun, Mercury forming stellium', NULL),
('2026-01-24', '20:31:00', 'ingress', 'Pallas', NULL, NULL, 'Pisces', NULL, 0.00, NULL, 'direct', NULL, 'minor', 'Pallas enters Pisces', NULL),
('2026-01-25', '23:47:00', 'lunation', 'Moon', 'Sun', 'square', 'Taurus', 'Aquarius', 6.23, 6.23, NULL, NULL, 'normal', 'First Quarter Moon', NULL),
('2026-01-26', '12:34:00', 'ingress', 'Neptune', NULL, NULL, 'Aries', NULL, 0.00, NULL, 'direct', NULL, 'major', 'Neptune enters Aries - begins 13-year transit', 'Neptune in Aries until 2039; last time 1861-1875'),
('2026-01-27', '15:00:00', 'aspect', 'Mars', 'Pluto', 'conjunction', 'Aquarius', 'Aquarius', 3.57, 3.57, NULL, NULL, 'significant', 'Mars conjunct Pluto - power, intensity, volcanic energy', NULL),

-- FEBRUARY 2026
('2026-02-01', '17:09:00', 'lunation', 'Moon', 'Sun', 'opposition', 'Leo', 'Aquarius', 13.07, 13.07, NULL, NULL, 'normal', 'Full Moon in Leo', NULL),
('2026-02-03', '21:33:00', 'station', 'Uranus', NULL, NULL, 'Taurus', NULL, 27.47, NULL, 'direct', NULL, 'significant', 'Uranus stations Direct', NULL),
('2026-02-06', '17:48:00', 'ingress', 'Mercury', NULL, NULL, 'Pisces', NULL, 0.00, NULL, 'direct', NULL, 'normal', 'Mercury enters Pisces', NULL),
('2026-02-09', '07:43:00', 'lunation', 'Moon', 'Sun', 'square', 'Scorpio', 'Aquarius', 20.77, 20.77, NULL, NULL, 'normal', 'Last Quarter Moon', NULL),
('2026-02-10', '05:18:00', 'ingress', 'Venus', NULL, NULL, 'Pisces', NULL, 0.00, NULL, 'direct', NULL, 'normal', 'Venus enters Pisces - exalted placement', NULL),
('2026-02-11', '23:05:00', 'aspect', 'Mercury', 'North Node', 'conjunction', 'Pisces', 'Pisces', 9.08, 9.08, NULL, NULL, 'normal', 'Mercury conjunct North Node', NULL),
('2026-02-13', '19:11:00', 'ingress', 'Saturn', NULL, NULL, 'Aries', NULL, 0.00, NULL, 'direct', NULL, 'major', 'Saturn enters Aries - Saturn in fall, remains until Apr 2028', 'Saturn in Aries until April 2028'),
('2026-02-17', '07:01:00', 'eclipse', 'Sun', 'Moon', 'conjunction', 'Aquarius', 'Aquarius', 28.82, 28.82, NULL, 'annular', 'major', 'Annular Solar Eclipse - Ring of Fire - launches Aquarius/Leo eclipse series', 'First eclipse on new Aquarius/Leo axis; Year of Fire Horse begins'),
('2026-02-17', '05:44:00', 'aspect', 'Venus', 'North Node', 'conjunction', 'Pisces', 'Pisces', 8.93, 8.93, NULL, NULL, 'normal', 'Venus conjunct North Node', NULL),
('2026-02-18', '10:52:00', 'ingress', 'Sun', NULL, NULL, 'Pisces', NULL, 0.00, NULL, 'direct', NULL, 'normal', 'Sun enters Pisces', NULL),
('2026-02-20', '11:54:00', 'aspect', 'Saturn', 'Neptune', 'conjunction', 'Aries', 'Aries', 0.75, 0.75, NULL, NULL, 'major', 'SATURN CONJUNCT NEPTUNE at Aries Point - dreams meet structure, spiritual ideals must incarnate', '36-year Saturn-Neptune cycle perfects; last conjunction 1989 in Capricorn'),
('2026-02-22', '12:02:00', 'aspect', 'Venus', 'Jupiter', 'trine', 'Pisces', 'Cancer', 15.52, 15.52, NULL, NULL, 'normal', 'Venus trine Jupiter - grace, abundance, ease', NULL),
('2026-02-24', '07:27:00', 'lunation', 'Moon', 'Sun', 'square', 'Gemini', 'Pisces', 5.90, 5.90, NULL, NULL, 'normal', 'First Quarter Moon', NULL),
('2026-02-26', '01:48:00', 'station', 'Mercury', NULL, NULL, 'Pisces', NULL, 22.57, NULL, 'retrograde', NULL, 'significant', 'Mercury stations Retrograde in Pisces', 'Mercury Rx until Mar 20'),
('2026-02-27', '11:20:00', 'aspect', 'Mars', 'Uranus', 'square', 'Aquarius', 'Taurus', 27.70, 27.70, NULL, NULL, 'significant', 'Mars square Uranus - volatile, accident-prone, breakthrough energy', NULL),

-- MARCH 2026
('2026-03-02', '09:16:00', 'ingress', 'Mars', NULL, NULL, 'Pisces', NULL, 0.00, NULL, 'direct', NULL, 'normal', 'Mars enters Pisces', NULL),
('2026-03-03', '06:38:00', 'eclipse', 'Moon', 'Sun', 'opposition', 'Virgo', 'Pisces', 12.90, 12.90, NULL, 'total', 'major', 'Total Lunar Eclipse in Virgo - final Virgo/Pisces eclipse of cycle', 'Completes Virgo-Pisces eclipse series active since Oct 2023'),
('2026-03-06', '05:45:00', 'ingress', 'Venus', NULL, NULL, 'Aries', NULL, 0.00, NULL, 'direct', NULL, 'normal', 'Venus enters Aries', NULL),
('2026-03-06', NULL, 'stellium', 'Venus', 'Neptune', 'conjunction', 'Aries', 'Aries', NULL, NULL, NULL, NULL, 'significant', 'Stellium: Venus, Neptune, Saturn all in early Aries', NULL),
('2026-03-07', '03:03:00', 'cazimi', 'Mercury', 'Sun', 'conjunction', 'Pisces', 'Pisces', 16.87, 16.87, 'retrograde', NULL, 'significant', 'Mercury cazimi - clarity in retrograde fog, download moment', NULL),
('2026-03-10', '23:30:00', 'station', 'Jupiter', NULL, NULL, 'Cancer', NULL, 15.08, NULL, 'direct', NULL, 'significant', 'Jupiter stations Direct in Cancer', 'Jupiter retrograde since Nov 11, 2025'),
('2026-03-10', '17:22:00', 'ingress', 'Vesta', NULL, NULL, 'Pisces', NULL, 0.00, NULL, 'direct', NULL, 'minor', 'Vesta enters Pisces', NULL),
('2026-03-11', '05:38:00', 'lunation', 'Moon', 'Sun', 'square', 'Sagittarius', 'Pisces', 20.82, 20.82, NULL, NULL, 'normal', 'Last Quarter Moon', NULL),
('2026-03-13', '14:57:00', 'aspect', 'Mars', 'North Node', 'conjunction', 'Pisces', 'Pisces', 8.92, 8.92, NULL, NULL, 'normal', 'Mars conjunct North Node', NULL),
('2026-03-15', '01:13:00', 'ingress', 'Ceres', NULL, NULL, 'Taurus', NULL, 0.00, NULL, 'direct', NULL, 'minor', 'Ceres enters Taurus', NULL),
('2026-03-17', '10:53:00', 'aspect', 'Mercury', 'North Node', 'conjunction', 'Pisces', 'Pisces', 8.97, 8.97, 'retrograde', NULL, 'normal', 'Mercury Rx conjunct North Node - revisiting karmic messages', NULL),
('2026-03-18', '09:08:00', 'aspect', 'Venus', 'Jupiter', 'square', 'Aries', 'Cancer', 15.17, 15.17, NULL, NULL, 'normal', 'Venus square Jupiter - excess, overindulgence possible', NULL),
('2026-03-18', '21:23:00', 'lunation', 'Moon', 'Sun', 'conjunction', 'Pisces', 'Pisces', 28.45, 28.45, NULL, NULL, 'normal', 'New Moon in Pisces', NULL),
('2026-03-20', '10:46:00', 'ingress', 'Sun', NULL, NULL, 'Aries', NULL, 0.00, NULL, 'direct', NULL, 'significant', 'Sun enters Aries - Spring Equinox, Astrological New Year', NULL),
('2026-03-20', '15:33:00', 'station', 'Mercury', NULL, NULL, 'Pisces', NULL, 8.50, NULL, 'direct', NULL, 'significant', 'Mercury stations Direct in Pisces', NULL),
('2026-03-21', '16:59:00', 'aspect', 'Mars', 'Jupiter', 'trine', 'Pisces', 'Cancer', 15.27, 15.27, NULL, NULL, 'normal', 'Mars trine Jupiter - confident action, successful endeavors', NULL),
('2026-03-22', '04:17:00', 'cazimi', 'Neptune', 'Sun', 'conjunction', 'Aries', 'Aries', 1.83, 1.83, NULL, NULL, 'significant', 'Neptune cazimi - Sun illuminates dreams, ego dissolves into collective', NULL),
('2026-03-22', '22:28:00', 'aspect', 'Mercury', 'North Node', 'conjunction', 'Pisces', 'Pisces', 8.77, 8.77, 'direct', NULL, 'normal', 'Mercury conjunct North Node - third pass, integration', NULL),
('2026-03-25', '01:51:00', 'cazimi', 'Saturn', 'Sun', 'conjunction', 'Aries', 'Aries', 4.72, 4.72, NULL, NULL, 'significant', 'Saturn cazimi - Sun illuminates structures, reality checks at Aries Point', NULL),
('2026-03-25', '15:17:00', 'lunation', 'Moon', 'Sun', 'square', 'Cancer', 'Aries', 5.15, 5.15, NULL, NULL, 'normal', 'First Quarter Moon', NULL),
('2026-03-28', '18:11:00', 'aspect', 'Saturn', 'Pluto', 'sextile', 'Aries', 'Aquarius', 5.17, 5.17, NULL, NULL, 'significant', 'Saturn sextile Pluto - structural transformation, power through discipline', NULL),
('2026-03-29', '04:50:00', 'ingress', 'Juno', NULL, NULL, 'Aquarius', NULL, 0.00, NULL, 'direct', NULL, 'minor', 'Juno enters Aquarius', NULL),
('2026-03-30', '12:01:00', 'ingress', 'Venus', NULL, NULL, 'Taurus', NULL, 0.00, NULL, 'direct', NULL, 'normal', 'Venus enters Taurus - domicile placement', NULL),

-- APRIL 2026 (through Apr 15)
('2026-04-01', '22:12:00', 'lunation', 'Moon', 'Sun', 'opposition', 'Libra', 'Aries', 12.35, 12.35, NULL, NULL, 'normal', 'Full Moon in Libra', NULL),
('2026-04-09', '15:36:00', 'ingress', 'Mars', NULL, NULL, 'Aries', NULL, 0.00, NULL, 'direct', NULL, 'significant', 'Mars enters Aries - Mars in domicile, major activation energy', NULL),
('2026-04-10', '00:51:00', 'lunation', 'Moon', 'Sun', 'square', 'Capricorn', 'Aries', 20.33, 20.33, NULL, NULL, 'normal', 'Last Quarter Moon', NULL),
('2026-04-12', '22:28:00', 'aspect', 'Mars', 'Neptune', 'conjunction', 'Aries', 'Aries', 2.65, 2.65, NULL, NULL, 'significant', 'Mars conjunct Neptune - spiritual warrior, action meets dream, possible confusion in action', NULL),
('2026-04-13', '01:19:00', 'aspect', 'Venus', 'Jupiter', 'sextile', 'Taurus', 'Cancer', 16.78, 16.78, NULL, NULL, 'normal', 'Venus sextile Jupiter - grace, ease, pleasant connections', NULL),
('2026-04-14', '23:21:00', 'ingress', 'Mercury', NULL, NULL, 'Aries', NULL, 0.00, NULL, 'direct', NULL, 'normal', 'Mercury enters Aries', NULL);

-- Verify insert
SELECT COUNT(*) as total_events FROM astro_events;
SELECT event_type, COUNT(*) as count FROM astro_events GROUP BY event_type ORDER BY count DESC;
SELECT * FROM astro_events WHERE significance = 'major' ORDER BY event_date;
