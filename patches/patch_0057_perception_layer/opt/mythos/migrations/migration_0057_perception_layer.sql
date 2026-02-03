-- Migration 0057: Perception Layer Foundation
-- Created: 2026-02-03
--
-- Tables:
--   perception_log  - Raw intake of everything Iris perceives
--   idea_inbox      - Auto-captured lists from conversations
--   idea_backlog    - Curated ideas worth keeping
--
-- This is Layer 1 (PERCEPTION) of the consciousness architecture.

-- ============================================================
-- PERCEPTION_LOG
-- ============================================================
-- The raw intake of everything. All input enters here.
-- This is the foundation - nothing else works without it.

CREATE TABLE IF NOT EXISTS perception_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Source identification
    source VARCHAR(50) NOT NULL,          -- conversation, transaction, email, sensor, manual, observation
    source_id VARCHAR(255),               -- Reference to source record if applicable
    source_platform VARCHAR(50),          -- telegram, slack, bank_csv, etc.
    
    -- The raw content
    content TEXT NOT NULL,                -- The actual text/description
    raw_data JSONB,                       -- Structured data blob (full message, transaction details, etc.)
    
    -- Context
    participants JSONB,                   -- Who was involved ["Ka'tuar'el", "Claude"]
    location VARCHAR(255),                -- Physical location if known
    time_context VARCHAR(50),             -- morning, evening, crisis, routine, etc.
    spiral_day INT,                       -- Day in spiral time (1-9) if applicable
    
    -- Grid processing results (Layer 1 - PERCEPTION)
    node_activations JSONB,               -- {ANCHOR: 0.8, ECHO: 0.7, BEACON: 0.95, ...}
    extracted_elements JSONB,             -- What each node found at perception level
    
    -- Intuition results (Layer 2 - INTUITION)
    felt_sense TEXT,                      -- The gut-sense summary
    intuition_data JSONB,                 -- Detailed intuition by node
    
    -- Processing metadata
    processed_to_level INT DEFAULT 1,     -- How far up the stack did this go? (1-9)
    memory_ids JSONB,                     -- Links to Memory nodes created from this (Neo4j UUIDs)
    idea_inbox_ids JSONB,                 -- Links to idea_inbox records spawned from this
    
    -- Timestamps
    processed_at TIMESTAMPTZ,
    
    -- Soft delete
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Indexes for perception_log
CREATE INDEX IF NOT EXISTS idx_perception_created ON perception_log(created_at);
CREATE INDEX IF NOT EXISTS idx_perception_source ON perception_log(source);
CREATE INDEX IF NOT EXISTS idx_perception_platform ON perception_log(source_platform);
CREATE INDEX IF NOT EXISTS idx_perception_processed_level ON perception_log(processed_to_level);
CREATE INDEX IF NOT EXISTS idx_perception_nodes ON perception_log USING GIN(node_activations);
CREATE INDEX IF NOT EXISTS idx_perception_not_deleted ON perception_log(is_deleted) WHERE is_deleted = FALSE;

-- ============================================================
-- IDEA_INBOX
-- ============================================================
-- Auto-captured lists from conversations.
-- When Iris detects "here are N options/ideas/approaches/etc",
-- they land here for later review.

CREATE TABLE IF NOT EXISTS idea_inbox (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Source linkage
    perception_id UUID REFERENCES perception_log(id),  -- Which perception spawned this
    conversation_context TEXT,                          -- Brief description of what was being discussed
    
    -- The list itself
    list_type VARCHAR(50),                -- options, ideas, improvements, steps, approaches, suggestions, etc.
    items JSONB NOT NULL,                 -- Array of the items: [{text: "...", index: 1}, ...]
    item_count INT,                       -- How many items in the list
    
    -- What happened
    chosen_item INT,                      -- Index of item that was pursued (if any)
    chosen_text TEXT,                     -- The text of the chosen item
    
    -- Review status
    reviewed BOOLEAN DEFAULT FALSE,
    reviewed_at TIMESTAMPTZ,
    review_notes TEXT,                    -- Notes from triage
    
    -- Disposition
    disposition VARCHAR(20) DEFAULT 'pending',  -- pending, kept, dismissed, merged, deferred
    kept_item_ids JSONB,                  -- Links to idea_backlog records for kept items
    
    -- Surfacing
    last_surfaced TIMESTAMPTZ,            -- When Iris last reminded about this
    surface_count INT DEFAULT 0,          -- How many times surfaced
    snooze_until TIMESTAMPTZ,             -- Don't surface until this time
    
    -- Metadata
    domain VARCHAR(50),                   -- finance, iris, mythos, personal, work, etc.
    tags JSONB                            -- Additional categorization
);

-- Indexes for idea_inbox
CREATE INDEX IF NOT EXISTS idx_inbox_created ON idea_inbox(created_at);
CREATE INDEX IF NOT EXISTS idx_inbox_perception ON idea_inbox(perception_id);
CREATE INDEX IF NOT EXISTS idx_inbox_reviewed ON idea_inbox(reviewed);
CREATE INDEX IF NOT EXISTS idx_inbox_disposition ON idea_inbox(disposition);
CREATE INDEX IF NOT EXISTS idx_inbox_pending ON idea_inbox(disposition) WHERE disposition = 'pending';
CREATE INDEX IF NOT EXISTS idx_inbox_domain ON idea_inbox(domain);

-- ============================================================
-- IDEA_BACKLOG
-- ============================================================
-- The curated keeper list. Ideas that survived triage.
-- This is the master "to do shit" list.

CREATE TABLE IF NOT EXISTS idea_backlog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Source linkage
    inbox_id UUID REFERENCES idea_inbox(id),  -- Which inbox item this came from
    perception_id UUID REFERENCES perception_log(id),  -- Original perception
    
    -- The idea itself
    idea TEXT NOT NULL,                   -- The actual idea/task/improvement
    context TEXT,                         -- Additional context
    original_text TEXT,                   -- Exact text from the conversation
    
    -- Classification
    domain VARCHAR(50),                   -- finance, iris, mythos, grid, personal, work, etc.
    category VARCHAR(100),                -- More specific: "finance/projection", "iris/memory", etc.
    idea_type VARCHAR(50),                -- task, improvement, feature, research, question, etc.
    tags JSONB,                           -- Flexible tagging
    
    -- Priority and status
    priority VARCHAR(20) DEFAULT 'medium',  -- critical, high, medium, low, someday
    status VARCHAR(20) DEFAULT 'open',      -- open, in_progress, blocked, done, dismissed
    blocked_reason TEXT,                    -- Why blocked, if blocked
    
    -- Relationships
    parent_id UUID REFERENCES idea_backlog(id),  -- For sub-tasks
    related_ids JSONB,                     -- Links to related ideas
    
    -- Progress tracking
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    dismissed_at TIMESTAMPTZ,
    dismissed_reason TEXT,
    
    -- Notes and updates
    notes TEXT,                           -- Running notes
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    update_history JSONB,                 -- [{timestamp, note}, ...]
    
    -- Surfacing
    last_surfaced TIMESTAMPTZ,
    surface_count INT DEFAULT 0,
    next_review TIMESTAMPTZ,              -- When to review this again
    
    -- Soft delete
    is_archived BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMPTZ
);

-- Indexes for idea_backlog
CREATE INDEX IF NOT EXISTS idx_backlog_created ON idea_backlog(created_at);
CREATE INDEX IF NOT EXISTS idx_backlog_inbox ON idea_backlog(inbox_id);
CREATE INDEX IF NOT EXISTS idx_backlog_domain ON idea_backlog(domain);
CREATE INDEX IF NOT EXISTS idx_backlog_priority ON idea_backlog(priority);
CREATE INDEX IF NOT EXISTS idx_backlog_status ON idea_backlog(status);
CREATE INDEX IF NOT EXISTS idx_backlog_open ON idea_backlog(status) WHERE status = 'open';
CREATE INDEX IF NOT EXISTS idx_backlog_active ON idea_backlog(is_archived) WHERE is_archived = FALSE;
CREATE INDEX IF NOT EXISTS idx_backlog_parent ON idea_backlog(parent_id);
CREATE INDEX IF NOT EXISTS idx_backlog_tags ON idea_backlog USING GIN(tags);

-- ============================================================
-- HELPER VIEWS
-- ============================================================

-- Pending inbox items (need review)
CREATE OR REPLACE VIEW v_inbox_pending AS
SELECT 
    id, created_at, conversation_context, list_type, 
    item_count, items, domain,
    EXTRACT(DAY FROM NOW() - created_at) as days_old
FROM idea_inbox
WHERE disposition = 'pending'
  AND reviewed = FALSE
ORDER BY created_at;

-- Open backlog items by priority
CREATE OR REPLACE VIEW v_backlog_open AS
SELECT 
    id, idea, domain, category, priority, status,
    created_at,
    EXTRACT(DAY FROM NOW() - created_at) as days_old
FROM idea_backlog
WHERE status IN ('open', 'in_progress')
  AND is_archived = FALSE
ORDER BY 
    CASE priority 
        WHEN 'critical' THEN 1 
        WHEN 'high' THEN 2 
        WHEN 'medium' THEN 3 
        WHEN 'low' THEN 4 
        WHEN 'someday' THEN 5 
    END,
    created_at;

-- Recent perceptions (last 24 hours)
CREATE OR REPLACE VIEW v_perception_recent AS
SELECT 
    id, created_at, source, source_platform,
    LEFT(content, 100) as content_preview,
    node_activations,
    processed_to_level
FROM perception_log
WHERE created_at > NOW() - INTERVAL '24 hours'
  AND is_deleted = FALSE
ORDER BY created_at DESC;

-- ============================================================
-- COMMENTS
-- ============================================================

COMMENT ON TABLE perception_log IS 'Layer 1 of consciousness - raw intake of all input';
COMMENT ON TABLE idea_inbox IS 'Auto-captured lists from conversations - pending review';
COMMENT ON TABLE idea_backlog IS 'Curated ideas - the master backlog of things worth doing';

COMMENT ON COLUMN perception_log.processed_to_level IS 'How far up the 9-layer stack this was processed (1=perception only, 9=full wisdom)';
COMMENT ON COLUMN perception_log.node_activations IS 'Grid scores: {ANCHOR: 0.8, ECHO: 0.7, ...}';
COMMENT ON COLUMN idea_inbox.disposition IS 'pending=needs review, kept=moved to backlog, dismissed=not worth keeping, merged=combined with existing, deferred=review later';
COMMENT ON COLUMN idea_backlog.priority IS 'critical=do now, high=this week, medium=this month, low=eventually, someday=maybe never';
