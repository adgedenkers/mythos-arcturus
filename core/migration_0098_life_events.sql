-- ============================================
-- Patch 0098: Life Events & Extractor Support
-- ============================================

-- Life events log: captures everything from conversations
CREATE TABLE IF NOT EXISTS life_events (
    id              SERIAL PRIMARY KEY,
    description     TEXT NOT NULL,
    domain          VARCHAR(50) DEFAULT 'personal',
        -- personal, finance, health, household, work, spiritual, mood
    person          VARCHAR(50) DEFAULT 'adge',
        -- adge, rebecca, fitz, family
    mood            VARCHAR(100),
    
    -- Source tracking
    source          VARCHAR(50) DEFAULT 'iris',
        -- iris (extracted from conversation), manual, system
    source_message  TEXT,           -- the original message that triggered this
    extraction_data JSONB,          -- raw extraction JSON for debugging
    
    -- Actions taken
    actions_taken   JSONB,          -- what the executor did [{action, result}]
    
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_life_events_date ON life_events(created_at);
CREATE INDEX IF NOT EXISTS idx_life_events_domain ON life_events(domain);
CREATE INDEX IF NOT EXISTS idx_life_events_person ON life_events(person);
