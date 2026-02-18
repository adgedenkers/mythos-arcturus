-- ============================================
-- Patch 0096: Recurring Routines Engine
-- ============================================
-- Creates the routine template and completion
-- tracking system for Iris life management.
-- ============================================

-- Routine templates: what needs to happen and when
CREATE TABLE IF NOT EXISTS routines (
    id              SERIAL PRIMARY KEY,
    title           TEXT NOT NULL,
    description     TEXT,
    
    -- Schedule
    frequency       VARCHAR(20) NOT NULL DEFAULT 'daily',
        -- daily, weekly, monthly, weekdays, weekends
    day_of_week     INTEGER,        -- 0=Mon..6=Sun (for weekly)
    day_of_month    INTEGER,        -- 1-31 (for monthly)
    time_due        TIME,           -- optional: when it should be done by
    
    -- Categorization
    domain          VARCHAR(50) DEFAULT 'personal',
        -- personal, finance, household, health, work, mythos, spiritual
    priority        VARCHAR(20) DEFAULT 'medium',
        -- high, medium, low
    
    -- Who
    assigned_to     VARCHAR(50) DEFAULT 'adge',
        -- adge, rebecca, shared, fitz
    
    -- Behavior
    auto_create     BOOLEAN DEFAULT true,   -- auto-generate daily instances
    nudge_enabled   BOOLEAN DEFAULT true,   -- Iris can remind about this
    nudge_after     TIME,                   -- nudge if not done by this time
    
    -- State
    is_active       BOOLEAN DEFAULT true,
    sort_order      INTEGER DEFAULT 100,    -- for display ordering
    
    -- Meta
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Completion tracking: did it get done today/this week/this month?
CREATE TABLE IF NOT EXISTS routine_completions (
    id              SERIAL PRIMARY KEY,
    routine_id      INTEGER NOT NULL REFERENCES routines(id) ON DELETE CASCADE,
    due_date        DATE NOT NULL,          -- the date this instance is for
    
    -- Status
    status          VARCHAR(20) DEFAULT 'pending',
        -- pending, done, skipped, missed
    completed_at    TIMESTAMP,
    completed_by    VARCHAR(50),            -- who marked it done
    
    -- Notes
    notes           TEXT,                   -- optional note on completion
    
    -- Meta
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- One completion record per routine per due date
    UNIQUE(routine_id, due_date)
);

-- Checkin log: track when Adge checks in with Iris
CREATE TABLE IF NOT EXISTS checkin_log (
    id              SERIAL PRIMARY KEY,
    checkin_date    DATE NOT NULL,
    checkin_time    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    checkin_type    VARCHAR(20) DEFAULT 'morning',
        -- morning, midday, evening, manual
    summary         TEXT,                   -- what Iris reported
    user_response   TEXT,                   -- what Adge said back
    
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Calendar events (manual until Google Calendar integration)
CREATE TABLE IF NOT EXISTS calendar_events (
    id              SERIAL PRIMARY KEY,
    title           TEXT NOT NULL,
    description     TEXT,
    event_date      DATE NOT NULL,
    start_time      TIME,
    end_time        TIME,
    location        TEXT,
    
    -- Who
    person          VARCHAR(50) DEFAULT 'adge',
        -- adge, rebecca, fitz, family
    
    -- Recurrence (simple)
    is_recurring    BOOLEAN DEFAULT false,
    recurrence_rule TEXT,                   -- future: ical RRULE format
    
    -- Source
    source          VARCHAR(50) DEFAULT 'manual',
        -- manual, google_calendar, iris
    external_id     VARCHAR(255),           -- Google Calendar event ID
    
    -- State
    is_active       BOOLEAN DEFAULT true,
    
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_routines_active ON routines(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_routines_frequency ON routines(frequency);
CREATE INDEX IF NOT EXISTS idx_routines_domain ON routines(domain);
CREATE INDEX IF NOT EXISTS idx_routine_completions_date ON routine_completions(due_date);
CREATE INDEX IF NOT EXISTS idx_routine_completions_status ON routine_completions(status);
CREATE INDEX IF NOT EXISTS idx_routine_completions_routine ON routine_completions(routine_id);
CREATE INDEX IF NOT EXISTS idx_checkin_log_date ON checkin_log(checkin_date);
CREATE INDEX IF NOT EXISTS idx_calendar_events_date ON calendar_events(event_date);
CREATE INDEX IF NOT EXISTS idx_calendar_events_person ON calendar_events(person);

-- ============================================
-- Seed: Initial routines
-- ============================================

-- DAILY ROUTINES
INSERT INTO routines (title, description, frequency, domain, priority, time_due, nudge_after, sort_order)
VALUES
    ('Check bank imports', 'Verify USAA and Sunmark auto-imports ran. Check Telegram for import notifications.', 
     'daily', 'finance', 'high', '09:00', '10:00', 10),
    
    ('Review transactions', 'Look at yesterday''s transactions. Anything unexpected? Any charges you don''t recognize? Any subscriptions that changed?', 
     'daily', 'finance', 'high', '09:15', '10:30', 20),
    
    ('Check calendar', 'Review today''s appointments and events for you, Rebecca, and Fitz.', 
     'daily', 'personal', 'medium', '08:30', '09:30', 5);

-- WEEKLY ROUTINES (Sunday)
INSERT INTO routines (title, description, frequency, day_of_week, domain, priority, time_due, nudge_after, sort_order)
VALUES
    ('Weekly financial review', 'Run /review. Read the snapshot. Balances, runway, trouble spots. Answer the 5 questions: How much discretionary? Avoidable spending? What''s coming? Making it to payday? Which credit card gets focus?', 
     'weekly', 6, 'finance', 'high', '18:00', '19:00', 10),
    
    ('Finance conversation with Rebecca', 'Share what you found in the review. Three things: here''s what we have, here''s what''s coming, here''s what I think. Not a presentation — a conversation.',
     'weekly', 6, 'finance', 'high', '19:00', '20:00', 20);

-- MONTHLY ROUTINES (20th of month — after all income has landed)
INSERT INTO routines (title, description, frequency, day_of_month, domain, priority, sort_order)
VALUES
    ('Full monthly financial review', 'Total income vs total spending. Is the net positive? Category deep-dive — where did the money actually go? Break open Shopping and Cash categories transaction by transaction.',
     'monthly', 20, 'finance', 'high', 10),
    
    ('Subscription audit', 'Review all 28+ recurring bills. Do we actually use each one weekly? Kill what we don''t. YouTube Premium, Ancestry, Rocket Money, Walmart+, streaming services — $200+/month in subscriptions.',
     'monthly', 20, 'finance', 'high', 20),
    
    ('Credit card strategy', 'Total credit card debt check. Pick the highest-interest or nearest-to-limit card. Decide extra payment amount. Track total debt month over month — is it going up or down?',
     'monthly', 20, 'finance', 'high', 30),
    
    ('Set monthly targets', 'Three numbers: max discretionary spending, extra credit card payment amount, minimum checking buffer. Write them down. Tell Rebecca.',
     'monthly', 20, 'finance', 'high', 40);
