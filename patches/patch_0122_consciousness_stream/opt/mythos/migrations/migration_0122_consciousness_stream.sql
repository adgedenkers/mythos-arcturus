-- Migration 0122: Consciousness Stream — Conversation Awareness Layer
-- Creates the linear subject tracking and conversation segmentation tables.
-- 
-- conversation_subject_points: The archaeological record. Every subject beat
-- of every conversation, forever. Append-only.
--
-- conversation_segments: The interpreted conversation units. Open, close,
-- reattach, distill to graph.

BEGIN;

-- Enable pgvector if available (non-fatal if not installed)
DO $$
BEGIN
    CREATE EXTENSION IF NOT EXISTS vector;
    RAISE NOTICE 'pgvector extension enabled';
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'pgvector not available — subject vectors will be NULL until installed';
END $$;

-- ═══════════════════════════════════════════════════════════════════════════
-- Conversation Segments — the interpreted conversation units
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS conversation_segments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at           TIMESTAMPTZ,

    chat_id             BIGINT NOT NULL,
    telegram_id         BIGINT,

    -- Segment identity
    status              VARCHAR(20) NOT NULL DEFAULT 'open'
                        CHECK (status IN ('open', 'soft_closed', 'closed', 'archived')),
    subject_summary     TEXT,
    subject_tags        TEXT[] DEFAULT '{}',

    -- Metrics
    point_count         INT DEFAULT 0,
    duration_seconds    INT,
    first_point_at      TIMESTAMPTZ,
    last_point_at       TIMESTAMPTZ,

    -- Reattach tracking
    reattach_count      INT DEFAULT 0,
    parent_segment_id   UUID REFERENCES conversation_segments(id),

    -- Distillation to Neo4j
    distilled_to_neo4j  BOOLEAN DEFAULT FALSE,
    neo4j_node_id       VARCHAR(100),

    -- Emotional summary
    dominant_tone       VARCHAR(50),
    energy_arc          VARCHAR(50)
);

CREATE INDEX IF NOT EXISTS idx_cs_chat_status ON conversation_segments(chat_id, status);
CREATE INDEX IF NOT EXISTS idx_cs_chat_updated ON conversation_segments(chat_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_cs_status ON conversation_segments(status);

-- ═══════════════════════════════════════════════════════════════════════════
-- Conversation Subject Points — the linear record, the trajectory
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS conversation_subject_points (
    id                  BIGSERIAL PRIMARY KEY,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    chat_id             BIGINT NOT NULL,
    telegram_id         BIGINT,
    perception_id       UUID REFERENCES perception_log(id),
    segment_id          UUID REFERENCES conversation_segments(id),

    -- The subject fingerprint
    subject_summary     TEXT NOT NULL,
    subject_tags        TEXT[] DEFAULT '{}',
    -- subject_vector added conditionally below if pgvector is available

    -- Trajectory metadata
    shift_detected      BOOLEAN DEFAULT FALSE,
    shift_magnitude     FLOAT,
    previous_point_id   BIGINT REFERENCES conversation_subject_points(id),

    -- Conversation feel
    emotional_tone      VARCHAR(50),
    energy_level        VARCHAR(20),

    -- Raw reference
    message_preview     TEXT,
    role                VARCHAR(20) DEFAULT 'user'
                        CHECK (role IN ('user', 'assistant'))
);

-- Add vector column if pgvector is available
DO $$
BEGIN
    ALTER TABLE conversation_subject_points ADD COLUMN subject_vector vector(384);
    RAISE NOTICE 'subject_vector column added (384d for all-MiniLM-L6-v2)';
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'pgvector not available — skipping subject_vector column';
END $$;

CREATE INDEX IF NOT EXISTS idx_csp_chat_created ON conversation_subject_points(chat_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_csp_segment ON conversation_subject_points(segment_id);
CREATE INDEX IF NOT EXISTS idx_csp_tags ON conversation_subject_points USING GIN(subject_tags);
CREATE INDEX IF NOT EXISTS idx_csp_created ON conversation_subject_points(created_at DESC);

-- ═══════════════════════════════════════════════════════════════════════════
-- Record migration
-- ═══════════════════════════════════════════════════════════════════════════

INSERT INTO perception_log (source, source_platform, content, raw_data)
VALUES (
    'system',
    'migration',
    'Migration 0122: Consciousness Stream tables created',
    '{"migration": "0122", "tables": ["conversation_segments", "conversation_subject_points"]}'::jsonb
);

COMMIT;
