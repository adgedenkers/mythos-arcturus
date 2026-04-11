-- NEU-0011: Grid Processing Manifest + Knowledge Extraction Infrastructure
-- Stream: NEU (NEURO)
-- Purpose: Full processing provenance for every message through the Arcturian Grid

-- ============================================================================
-- 1. Grid Processing Manifest
--    One row per node-layer activation per exchange.
--    The audit trail: what touched each message, what version, what it produced.
-- ============================================================================

CREATE TABLE IF NOT EXISTS grid_processing_manifest (
    id              BIGSERIAL PRIMARY KEY,
    exchange_id     TEXT NOT NULL,                       -- Links to grid_activation_timeseries + Neo4j Exchange
    conversation_id TEXT,
    user_uuid       UUID,

    -- What processed it
    node            VARCHAR(20) NOT NULL,                -- anchor, echo, beacon, synth, nexus, mirror, glyph, harmonia, gateway
    layer           INTEGER NOT NULL CHECK (layer >= 1 AND layer <= 9),
    version         VARCHAR(20) NOT NULL,                -- e.g. "1.0", "1.1"
    prompt_hash     VARCHAR(64),                         -- SHA256 of the prompt used (detect drift)

    -- Routing decision
    activated       BOOLEAN NOT NULL DEFAULT true,       -- Did this node-layer actually run?
    skipped_reason  TEXT,                                -- Why it didn't fire (if activated=false)
    activation_score INTEGER,                            -- Grid score that triggered this node (0-100)
    depth_gate      INTEGER,                             -- Max layer reached for this node on this exchange

    -- Input
    input_hash      VARCHAR(64),                         -- SHA256 of input content (detect reprocessing of same content)
    input_chars     INTEGER,                             -- Size of input payload

    -- Output
    output_summary  TEXT,                                -- Brief summary of what this node-layer produced
    extracted_count INTEGER DEFAULT 0,                   -- How many knowledge items were extracted
    output_json     JSONB,                               -- Full structured output (optional, for debugging)

    -- Performance
    processing_ms   INTEGER,
    model_used      VARCHAR(50),

    -- Timestamps
    processed_at    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_node CHECK (node IN ('anchor', 'echo', 'beacon', 'synth', 'nexus', 'mirror', 'glyph', 'harmonia', 'gateway'))
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_gpm_exchange ON grid_processing_manifest (exchange_id);
CREATE INDEX IF NOT EXISTS idx_gpm_node_version ON grid_processing_manifest (node, version, processed_at DESC);
CREATE INDEX IF NOT EXISTS idx_gpm_version_audit ON grid_processing_manifest (node, layer, version);
CREATE INDEX IF NOT EXISTS idx_gpm_stale ON grid_processing_manifest (node, layer, version, activated) WHERE activated = true;
CREATE INDEX IF NOT EXISTS idx_gpm_user_time ON grid_processing_manifest (user_uuid, processed_at DESC);

-- ============================================================================
-- 2. Knowledge Extractions
--    Every fact, preference, observation, directive extracted by any node-layer.
--    The knowledge ledger. Linked to manifest for provenance.
-- ============================================================================

CREATE TABLE IF NOT EXISTS knowledge_extractions (
    id                  BIGSERIAL PRIMARY KEY,
    extraction_id       UUID NOT NULL DEFAULT gen_random_uuid(),  -- Stable ID for Neo4j linking

    -- Source provenance
    exchange_id         TEXT NOT NULL,                   -- Which exchange produced this
    manifest_id         BIGINT REFERENCES grid_processing_manifest(id),
    node                VARCHAR(20) NOT NULL,            -- Which node extracted it
    layer               INTEGER NOT NULL,                -- Which layer
    version             VARCHAR(20) NOT NULL,            -- Version of node-layer that extracted it

    -- Content
    knowledge_type      VARCHAR(20) NOT NULL,            -- fact, preference, observation, directive
    subject             TEXT,                            -- Who/what this is about
    content             TEXT NOT NULL,                   -- The extracted knowledge
    domain              VARCHAR(30),                     -- finance, technical, spiritual, personal, health, household, relationship, etc.
    confidence          REAL DEFAULT 1.0 CHECK (confidence >= 0.0 AND confidence <= 1.0),

    -- Significance (for smart gating)
    significance        INTEGER DEFAULT 1 CHECK (significance >= 1 AND significance <= 5),
    -- 1 = mundane (silently capture)
    -- 2 = minor (silently capture)
    -- 3 = notable (silently capture)
    -- 4 = significant (confirm via Telegram)
    -- 5 = critical (confirm via Telegram)

    -- Lifecycle
    status              VARCHAR(20) DEFAULT 'active',    -- active, superseded, retracted, confirmed
    superseded_by       UUID,                            -- Points to extraction_id of replacement
    confirmed_count     INTEGER DEFAULT 1,               -- How many independent extractions confirm this
    confirmation_sources JSONB DEFAULT '[]'::jsonb,      -- Array of {node, version, exchange_id} that confirmed

    -- Neo4j sync
    neo4j_node_id       TEXT,                            -- Neo4j element ID once written
    neo4j_synced        BOOLEAN DEFAULT false,
    neo4j_synced_at     TIMESTAMP WITH TIME ZONE,

    -- Telegram notification
    notification_sent   BOOLEAN DEFAULT false,
    notification_sent_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_knowledge_type CHECK (knowledge_type IN ('fact', 'preference', 'observation', 'directive')),
    CONSTRAINT valid_status CHECK (status IN ('active', 'superseded', 'retracted', 'confirmed'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ke_exchange ON knowledge_extractions (exchange_id);
CREATE INDEX IF NOT EXISTS idx_ke_type ON knowledge_extractions (knowledge_type, status);
CREATE INDEX IF NOT EXISTS idx_ke_subject ON knowledge_extractions (subject);
CREATE INDEX IF NOT EXISTS idx_ke_significance ON knowledge_extractions (significance DESC) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_ke_unsynced ON knowledge_extractions (neo4j_synced) WHERE neo4j_synced = false;
CREATE INDEX IF NOT EXISTS idx_ke_version ON knowledge_extractions (node, layer, version);
CREATE INDEX IF NOT EXISTS idx_ke_domain ON knowledge_extractions (domain, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ke_notification ON knowledge_extractions (notification_sent, significance) WHERE notification_sent = false AND significance >= 4;

-- ============================================================================
-- 3. Grid Version Registry (Postgres-backed, not YAML)
--    Current version + changelog for each node-layer combination.
--    81 rows when fully populated (9 nodes × 9 layers).
-- ============================================================================

CREATE TABLE IF NOT EXISTS grid_version_registry (
    id              SERIAL PRIMARY KEY,
    node            VARCHAR(20) NOT NULL,
    layer           INTEGER NOT NULL CHECK (layer >= 1 AND layer <= 9),
    version         VARCHAR(20) NOT NULL DEFAULT '1.0',
    prompt_hash     VARCHAR(64),                         -- SHA256 of current prompt
    description     TEXT,                                -- What this node-layer does
    changelog       JSONB DEFAULT '[]'::jsonb,           -- Array of {version, date, change}
    is_active       BOOLEAN DEFAULT true,                -- Can be disabled without deletion
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT unique_node_layer UNIQUE (node, layer),
    CONSTRAINT valid_grid_node CHECK (node IN ('anchor', 'echo', 'beacon', 'synth', 'nexus', 'mirror', 'glyph', 'harmonia', 'gateway'))
);

-- Seed Layer 1 for all 9 nodes (the perception layer — first to be implemented)
INSERT INTO grid_version_registry (node, layer, version, description) VALUES
    ('anchor',   1, '1.0', 'Perception: physical world, location, body, domestic, infrastructure'),
    ('echo',     1, '1.0', 'Perception: memory, identity, ancestors, past events, timelines'),
    ('beacon',   1, '1.0', 'Perception: value, finance, resources, career, purpose'),
    ('synth',    1, '1.0', 'Perception: systems, logic, code, patterns, technical decisions'),
    ('nexus',    1, '1.0', 'Perception: time, scheduling, decisions, convergence points'),
    ('mirror',   1, '1.0', 'Perception: emotions, psyche, shadow, self-reflection, feelings'),
    ('glyph',    1, '1.0', 'Perception: symbols, rituals, encoding, sacred geometry, artifacts'),
    ('harmonia', 1, '1.0', 'Perception: relationships, heart, balance, connection, partnership'),
    ('gateway',  1, '1.0', 'Perception: dreams, spiritual contact, transitions, visions, channeling')
ON CONFLICT (node, layer) DO NOTHING;
