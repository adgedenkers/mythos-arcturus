-- Patch 0102: Backlog Intelligence System
-- Part 1: Schema migration for idea_backlog
-- Part 2: backlog_analysis table for analyst output
-- Part 3: Seed existing backlog items with priority ordering

-- ============================================
-- PART 1: Upgrade idea_backlog
-- ============================================

-- Add priority ordering (lower number = higher priority)
ALTER TABLE idea_backlog ADD COLUMN IF NOT EXISTS priority_order INTEGER;

-- Add dependency tracking (array of idea_backlog IDs this item depends on)
ALTER TABLE idea_backlog ADD COLUMN IF NOT EXISTS depends_on INTEGER[];

-- Add blocked_by (computed or manual — which items block this one)
ALTER TABLE idea_backlog ADD COLUMN IF NOT EXISTS blocked_by INTEGER[];

-- Add phase grouping
ALTER TABLE idea_backlog ADD COLUMN IF NOT EXISTS phase TEXT;

-- Add effort estimation
ALTER TABLE idea_backlog ADD COLUMN IF NOT EXISTS estimated_effort TEXT CHECK (estimated_effort IN ('small', 'medium', 'large'));

-- Add category for grouping (infrastructure, finance, iris, consciousness, docs)
ALTER TABLE idea_backlog ADD COLUMN IF NOT EXISTS category TEXT;

-- Add source tracking — where did this item come from
ALTER TABLE idea_backlog ADD COLUMN IF NOT EXISTS source TEXT;

-- Add last_analyzed timestamp — when the analyst last evaluated this item
ALTER TABLE idea_backlog ADD COLUMN IF NOT EXISTS last_analyzed TIMESTAMPTZ;

-- Add analyst_notes — what the 32b model said about this item
ALTER TABLE idea_backlog ADD COLUMN IF NOT EXISTS analyst_notes TEXT;

-- Index for priority queries
CREATE INDEX IF NOT EXISTS idx_backlog_priority ON idea_backlog (priority_order) WHERE status != 'done';

-- ============================================
-- PART 2: backlog_analysis table
-- ============================================

CREATE TABLE IF NOT EXISTS backlog_analysis (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    trigger_type TEXT NOT NULL CHECK (trigger_type IN ('morning', 'post_patch', 'on_demand', 'evening')),
    
    -- The full analysis
    summary TEXT NOT NULL,
    recommendations TEXT,
    flagged_items INTEGER[],
    
    -- Daily context snapshot at time of analysis
    routines_due INTEGER DEFAULT 0,
    routines_completed INTEGER DEFAULT 0,
    calendar_events_today INTEGER DEFAULT 0,
    bills_due_7_days INTEGER DEFAULT 0,
    bills_total_due_7_days NUMERIC(10,2) DEFAULT 0,
    transfer_recommendations JSONB,
    
    -- Backlog state
    total_open_items INTEGER DEFAULT 0,
    items_unblocked INTEGER DEFAULT 0,
    items_blocked INTEGER DEFAULT 0,
    top_priority_item_id INTEGER REFERENCES idea_backlog(id),
    
    -- Accuracy tracking (filled in by evening pass)
    predictions_made INTEGER DEFAULT 0,
    predictions_correct INTEGER DEFAULT 0,
    accuracy_notes TEXT,
    
    -- The raw model output for debugging
    raw_model_response TEXT,
    model_used TEXT
);

CREATE INDEX IF NOT EXISTS idx_analysis_created ON backlog_analysis (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_trigger ON backlog_analysis (trigger_type, created_at DESC);

-- ============================================
-- PART 3: Seed existing open backlog items
-- ============================================
-- This updates items that already exist in idea_backlog.
-- We'll match by title/description keywords since we don't know exact IDs.
-- If items don't exist yet, we INSERT them.

-- First, let's insert the full ordered backlog.
-- We use ON CONFLICT DO UPDATE if there's a unique constraint on title,
-- otherwise we just insert new items for anything not already tracked.

-- Critical Path (1-5)
INSERT INTO idea_backlog (title, description, status, priority_order, phase, estimated_effort, category, source)
VALUES 
('Backlog schema migration', 'Add priority_order, depends_on, blocked_by, phase, estimated_effort to idea_backlog. Update /tasks command.', 'done', 1, '1.8', 'small', 'infrastructure', 'TODO rebuild 2026-02-18')
ON CONFLICT DO NOTHING;

INSERT INTO idea_backlog (title, description, status, priority_order, depends_on, phase, estimated_effort, category, source)
VALUES 
('Backlog analyst + morning briefing', 'core/backlog_analyst.py — 32b model analyzes full system state. Three triggers: morning (3 AM), post-patch, on-demand. Morning briefing via Telegram in Iris voice. Bills due next 7 days + transfer recommendations.', 'active', 2, NULL, '1.8', 'large', 'iris', 'TODO rebuild 2026-02-18')
ON CONFLICT DO NOTHING;

INSERT INTO idea_backlog (title, description, status, priority_order, phase, estimated_effort, category, source)
VALUES 
('Preprocessor refinement', '7b extractor date bugs, create-vs-update confusion, stale event IDs in context. Date validator improvements.', 'open', 3, '1.7', 'medium', 'iris', 'TODO rebuild 2026-02-18')
ON CONFLICT DO NOTHING;

INSERT INTO idea_backlog (title, description, status, priority_order, depends_on, phase, estimated_effort, category, source)
VALUES 
('Proactive nudges', 'Simplified by analyst: nudges = send reminders for items morning analysis flagged. Overdue routines, bill reminders, missed checkins.', 'open', 4, NULL, '1.8', 'medium', 'iris', 'TODO rebuild 2026-02-18')
ON CONFLICT DO NOTHING;

INSERT INTO idea_backlog (title, description, status, priority_order, phase, estimated_effort, category, source)
VALUES 
('Google Calendar sync', 'Start read-only inbound (Google → Mythos) from ahdrld1004@gmail.com shared account. Bidirectional later.', 'open', 5, '1.7', 'medium', 'infrastructure', 'TODO rebuild 2026-02-18')
ON CONFLICT DO NOTHING;

-- High Value (6-12)
INSERT INTO idea_backlog (title, description, status, priority_order, phase, estimated_effort, category, source)
VALUES 
('Credit card parsers', 'LLBean, TSC, TJX, Amex, Old Navy — accounts without auto-import.', 'open', 6, '1.6', 'medium', 'finance', 'existing backlog')
ON CONFLICT DO NOTHING;

INSERT INTO idea_backlog (title, description, status, priority_order, depends_on, phase, estimated_effort, category, source)
VALUES 
('Bill match tuning', 'Verify all 29 bills auto-match correctly after more data flows.', 'open', 7, NULL, '1.6', 'small', 'finance', 'existing backlog')
ON CONFLICT DO NOTHING;

INSERT INTO idea_backlog (title, description, status, priority_order, phase, estimated_effort, category, source)
VALUES 
('Sidney FCU / NBT manual import', 'Manual import flow for remaining bank accounts.', 'open', 8, '1.6', 'small', 'finance', 'existing backlog')
ON CONFLICT DO NOTHING;

INSERT INTO idea_backlog (title, description, status, priority_order, phase, estimated_effort, category, source)
VALUES 
('Routine edit/delete via Telegram', 'Currently can only /routine_add, need edit and remove commands.', 'open', 9, '1.7', 'small', 'iris', 'handoff 2026-02-18')
ON CONFLICT DO NOTHING;

INSERT INTO idea_backlog (title, description, status, priority_order, phase, estimated_effort, category, source)
VALUES 
('Seraphe mode prompt', 'Her own Iris voice — chat mode tuned for Seraphe voice and needs.', 'open', 10, '1.5', 'medium', 'iris', 'existing backlog')
ON CONFLICT DO NOTHING;

INSERT INTO idea_backlog (title, description, status, priority_order, phase, estimated_effort, category, source)
VALUES 
('Context window management', 'Smart truncation + summary injection for Iris conversations.', 'open', 11, '1.5', 'medium', 'iris', 'existing backlog')
ON CONFLICT DO NOTHING;

INSERT INTO idea_backlog (title, description, status, priority_order, depends_on, phase, estimated_effort, category, source)
VALUES 
('Memory summarization worker', 'Redis worker compresses old conversations.', 'open', 12, NULL, '1.5', 'medium', 'iris', 'existing backlog')
ON CONFLICT DO NOTHING;

-- Infrastructure (13-20)
INSERT INTO idea_backlog (title, description, status, priority_order, phase, estimated_effort, category, source)
VALUES 
('mythos-diag command', 'Standardized diagnostic tool: mythos-diag, mythos-diag finance, mythos-diag services, mythos-diag patches.', 'open', 13, '1.5', 'small', 'infrastructure', 'existing backlog')
ON CONFLICT DO NOTHING;

INSERT INTO idea_backlog (title, description, status, priority_order, depends_on, phase, estimated_effort, category, source)
VALUES 
('Builder mode', 'Iris builds her own infrastructure — receives task via Telegram, generates plan, writes files to staging, user reviews and approves.', 'open', 14, NULL, '2.0', 'large', 'iris', 'existing backlog')
ON CONFLICT DO NOTHING;

INSERT INTO idea_backlog (title, description, status, priority_order, depends_on, phase, estimated_effort, category, source)
VALUES 
('Web UI calendar section', 'Calendar view in the web dashboard.', 'open', 15, NULL, '1.7', 'medium', 'infrastructure', 'handoff 2026-02-18')
ON CONFLICT DO NOTHING;

INSERT INTO idea_backlog (title, description, status, priority_order, phase, estimated_effort, category, source)
VALUES 
('Rich contact/provider DB', 'Auto-lookup for doctors, providers, contacts with phone, address, etc.', 'open', 16, '1.7', 'medium', 'infrastructure', 'handoff 2026-02-18')
ON CONFLICT DO NOTHING;

INSERT INTO idea_backlog (title, description, status, priority_order, phase, estimated_effort, category, source)
VALUES 
('Iris web search capability', 'Iris can search the web when she needs current info.', 'open', 17, '1.5', 'medium', 'iris', 'handoff 2026-02-18')
ON CONFLICT DO NOTHING;

INSERT INTO idea_backlog (title, description, status, priority_order, phase, estimated_effort, category, source)
VALUES 
('Redis async queues for Iris', 'Background processing, non-blocking responses.', 'open', 18, '1.5', 'medium', 'infrastructure', 'existing backlog')
ON CONFLICT DO NOTHING;

INSERT INTO idea_backlog (title, description, status, priority_order, phase, estimated_effort, category, source)
VALUES 
('Perception layer routing', 'Route chat_messages into perception_log, activate grid Layer 1.', 'open', 19, '2.0', 'medium', 'consciousness', 'existing backlog')
ON CONFLICT DO NOTHING;

INSERT INTO idea_backlog (title, description, status, priority_order, depends_on, phase, estimated_effort, category, source)
VALUES 
('Two-phase grid processing', 'Grid scoring at perception + deeper layers.', 'open', 20, NULL, '2.0', 'large', 'consciousness', 'existing backlog')
ON CONFLICT DO NOTHING;

-- Horizon (21+)
INSERT INTO idea_backlog (title, description, status, priority_order, phase, category, source)
VALUES 
('Bill calendar visual timeline', 'Visual timeline of bills on a calendar view.', 'open', 21, '1.6', 'finance', 'existing backlog'),
('Iris service skeleton', 'Background consciousness loop (mythos-iris.service).', 'open', 22, '2.0', 'consciousness', 'existing backlog'),
('Email integration', 'Inbound email processing.', 'open', 23, '2.0', 'infrastructure', 'existing backlog'),
('Slack integration', 'Evaluate hybrid: Telegram mobile + Slack structured work.', 'open', 24, '1.5', 'infrastructure', 'existing backlog'),
('Environmental sensors', 'Physical world awareness.', 'open', 25, '3.0', 'consciousness', 'existing backlog'),
('Bash profile builder', 'Standardized bash profile for Arcturus.', 'open', 26, '1.5', 'infrastructure', 'handoff 2026-02-18'),
('Neo4j backlog graph', 'When dependencies get complex enough to justify graph traversal.', 'open', 27, '2.0', 'consciousness', 'TODO rebuild 2026-02-18'),
('Memory quality control', 'Flag/weight good vs bad assistant responses in history.', 'open', 28, '1.5', 'iris', 'existing backlog'),
('Additional model testing', 'Pull and test new models as released.', 'open', 29, '1.5', 'iris', 'existing backlog')
ON CONFLICT DO NOTHING;

-- Documentation backlog
INSERT INTO idea_backlog (title, description, status, priority_order, phase, estimated_effort, category, source)
VALUES 
('Update ARCHITECTURE.md for 0095-0101', 'New tables, services, core files from life awareness sprint.', 'open', 100, '1.7', 'small', 'docs', 'TODO rebuild 2026-02-18'),
('Document routines engine', 'Schema, commands, completion tracking.', 'open', 101, '1.7', 'small', 'docs', 'TODO rebuild 2026-02-18'),
('Document life logging pipeline', 'Extractor → executor → life_events flow.', 'open', 102, '1.7', 'small', 'docs', 'TODO rebuild 2026-02-18'),
('Document calendar system', 'CRUD, formatter, date validation.', 'open', 103, '1.7', 'small', 'docs', 'TODO rebuild 2026-02-18'),
('Document knowledge map auto-rebuild', 'Triggers, listener, rebuild flow.', 'open', 104, '1.7', 'small', 'docs', 'TODO rebuild 2026-02-18'),
('Document checkin system', 'checkin_log, /checkin command.', 'open', 105, '1.7', 'small', 'docs', 'TODO rebuild 2026-02-18'),
('Document review system', '/review, weekly/monthly schedules.', 'open', 106, '1.7', 'small', 'docs', 'TODO rebuild 2026-02-18'),
('Document message processing pipeline', 'Full flow: message → extractor → executor → Iris.', 'open', 107, '1.7', 'small', 'docs', 'TODO rebuild 2026-02-18'),
('Update Telegram command reference', 'New commands from patches 0095-0101.', 'open', 108, '1.7', 'small', 'docs', 'TODO rebuild 2026-02-18')
ON CONFLICT DO NOTHING;
