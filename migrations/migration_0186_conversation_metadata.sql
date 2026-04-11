-- ============================================================================
-- Mythos Conversation Metadata Schema
-- PostgreSQL — System of Record + Search + Raw Log Storage
-- ============================================================================
-- Design principles:
--   1. ONE table for conversations, including raw_payload (no separate raw log table)
--   2. Postgres owns all data storage; Neo4j only gets IDs + relationship structure
--   3. JSONB for evolving fields; normalized tables only where we query by FK
--   4. FTS across summary, decisions, actions, tags, and raw content
--   5. Idempotent upsert via (source_provider, session_id, started_at) + content_hash
-- ============================================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;

-- Enums
DO $$ BEGIN
  CREATE TYPE conversation_type AS ENUM (
    'technical_build', 'channeling', 'research', 'life_log',
    'planning', 'genealogy', 'astrology', 'mythos_dev', 'other'
  );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE initiator_type AS ENUM ('human', 'model', 'system', 'unknown');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;


-- ============================================================================
-- CORE TABLE: conversations
-- This is the single source of truth. Raw logs live here in raw_payload.
-- ============================================================================
CREATE TABLE IF NOT EXISTS conversations (
  conversation_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- ── Identity & Provenance ──────────────────────────────────────────────
  source_model           TEXT NOT NULL,                   -- "claude-opus-4-5", "qwen2.5-32b", etc.
  source_provider        TEXT,                             -- "anthropic", "ollama", "openai"
  session_id             TEXT,                             -- upstream session/thread id
  thread_group_id        UUID,                             -- optional cluster for multi-session threads
  ingest_source          TEXT NOT NULL,                    -- "api", "manual_paste", "import_file", "telegram"
  ingest_idempotency_key TEXT,                             -- optional external dedup key

  -- ── Time ───────────────────────────────────────────────────────────────
  started_at             TIMESTAMPTZ NOT NULL,
  ended_at               TIMESTAMPTZ,
  ingested_at            TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- ── Core Fields ────────────────────────────────────────────────────────
  conversation_type      conversation_type NOT NULL DEFAULT 'other',
  initiated_by           initiator_type NOT NULL DEFAULT 'unknown',
  topic_tags             TEXT[] NOT NULL DEFAULT '{}',

  -- ── Structural Metadata ────────────────────────────────────────────────
  turn_count             INTEGER NOT NULL DEFAULT 0,
  token_estimate_total   INTEGER,
  token_estimates_per_turn JSONB,                          -- [{turn_idx, speaker, tokens}, ...]

  produced_tools         BOOLEAN NOT NULL DEFAULT FALSE,
  produced_code          BOOLEAN NOT NULL DEFAULT FALSE,
  produced_files         BOOLEAN NOT NULL DEFAULT FALSE,
  produced_artifacts     BOOLEAN NOT NULL DEFAULT FALSE,

  branching_points       JSONB,                            -- [{turn_idx, from_topic, to_topic, note}, ...]

  -- ── Semantic Layer ─────────────────────────────────────────────────────
  summary                TEXT,
  key_decisions          JSONB,                            -- [{decision, rationale, tags, turn_idx}, ...]
  action_items           JSONB,                            -- [{action, owner, due, status, turn_idx}, ...]

  -- ── Entity References (lightweight cache; graph is canonical for rels) ─
  entities               JSONB,                            -- {people:[], systems:[], topics:[],
                                                           --  spiritual_concepts:[], places:[], other:[]}

  -- ── Spiral Time Context ─────────────────────────────────────────────────
  -- Computed at ingest from the primary participant's active epoch.
  -- Structure: {
  --   epoch_id: UUID,
  --   epoch_started_at: "2025-10-19",
  --   days_since_epoch: 132,
  --   signature: {
  --     pulse_day: 6,       pulse_cycle: 15,
  --     weave_day: 52,      weave_cycle: 2,
  --     arc_day: 132,       arc_cycle: 1,
  --     long_day: 132,      long_cycle: 1
  --   },
  --   active_node: 6,
  --   active_channel: {source_node: 6, target_node: 7},
  --   arc_passage: 1
  -- }
  spiral_context         JSONB,

  -- ── Graph Edge Hints (canonical edges live in Neo4j) ───────────────────
  edges                  JSONB,                            -- [{type:"CONTINUES", to_conversation_id:"..."}, ...]

  -- ── Raw Payload — THE conversation log lives here ──────────────────────
  -- Store the full export: Claude JSON, Ollama chat dump, pasted text, etc.
  -- This is the archive. Everything above is derived/indexed from this.
  raw_payload            JSONB,

  -- ── Flexible Metadata Overflow ─────────────────────────────────────────
  metadata               JSONB NOT NULL DEFAULT '{}'::jsonb,

  -- ── Versioning & Idempotency ───────────────────────────────────────────
  revision               INTEGER NOT NULL DEFAULT 1,
  content_hash           TEXT,                             -- SHA-256 of canonical JSON (for dedup)

  -- ── Full-Text Search Vector ────────────────────────────────────────────
  search_doc             TSVECTOR,

  -- ── Natural Key Constraint ─────────────────────────────────────────────
  UNIQUE NULLS NOT DISTINCT (source_provider, session_id, started_at)
);

-- Thread group index (for clustering related sessions)
CREATE INDEX IF NOT EXISTS idx_conversations_thread_group
  ON conversations (thread_group_id) WHERE thread_group_id IS NOT NULL;


-- ============================================================================
-- PARTICIPANTS (normalized — we query "all convos with person X")
-- ============================================================================
CREATE TABLE IF NOT EXISTS conversation_participants (
  conversation_id  UUID NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
  participant_type TEXT NOT NULL,            -- "human", "model", "system"
  participant_id   TEXT NOT NULL,            -- stable key: email, handle, model id
  display_name     TEXT,
  role             TEXT,                     -- "user", "assistant", "observer", "channel"
  PRIMARY KEY (conversation_id, participant_type, participant_id)
);

CREATE INDEX IF NOT EXISTS idx_participants_by_person
  ON conversation_participants (participant_id, participant_type);


-- ============================================================================
-- TURNS (essential — different conversation types have different shapes)
-- Content stored here AND in raw_payload is intentional:
--   raw_payload = verbatim archive (never touched after ingest)
--   turns = structured, queryable, indexable per-turn data
-- This is not duplication — it's raw vs. indexed. Same data, different access pattern.
-- ============================================================================
CREATE TABLE IF NOT EXISTS conversation_turns (
  conversation_id  UUID NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
  turn_idx         INTEGER NOT NULL,
  speaker_type     TEXT NOT NULL,            -- "human", "model", "tool", "system"
  speaker_id       TEXT,
  created_at       TIMESTAMPTZ,
  token_estimate   INTEGER,
  content          TEXT,                     -- plain text of the turn
  content_json     JSONB,                    -- structured: tool calls, attachments, code blocks
  PRIMARY KEY (conversation_id, turn_idx)
);


-- ============================================================================
-- THREAD GROUPS (lightweight clustering for multi-session work)
-- ============================================================================
CREATE TABLE IF NOT EXISTS thread_groups (
  thread_group_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name             TEXT NOT NULL,            -- "Finance module buildout", "Cathar lineage research"
  description      TEXT,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  topic_tags       TEXT[] NOT NULL DEFAULT '{}',
  metadata         JSONB NOT NULL DEFAULT '{}'::jsonb
);


-- ============================================================================
-- SPIRAL EPOCHS (personal time anchors — archaeological strata model)
-- A person can have multiple epochs. Only one is active (ended_at IS NULL).
-- Old epochs persist as historical strata, never deleted.
-- ============================================================================
CREATE TABLE IF NOT EXISTS spiral_epochs (
  epoch_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  person_id        TEXT NOT NULL,              -- matches conversation_participants.participant_id
  epoch_number     INTEGER NOT NULL DEFAULT 1, -- sequential per person
  started_at       DATE NOT NULL,              -- the anchor day (Day 0)
  ended_at         DATE,                       -- NULL = active epoch
  reason           TEXT,                       -- "Initial activation", "Conscious reset", etc.
  metadata         JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),

  UNIQUE (person_id, epoch_number)
);

CREATE INDEX IF NOT EXISTS idx_spiral_epochs_person
  ON spiral_epochs (person_id);
CREATE INDEX IF NOT EXISTS idx_spiral_epochs_active
  ON spiral_epochs (person_id) WHERE ended_at IS NULL;


-- ============================================================================
-- INDEXES
-- ============================================================================

-- Time & filtering
CREATE INDEX IF NOT EXISTS idx_conversations_started_at ON conversations (started_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversations_type       ON conversations (conversation_type);
CREATE INDEX IF NOT EXISTS idx_conversations_model      ON conversations (source_model);
CREATE INDEX IF NOT EXISTS idx_conversations_provider   ON conversations (source_provider);

-- Tags (GIN for array containment: WHERE topic_tags @> ARRAY['mythos'])
CREATE INDEX IF NOT EXISTS idx_conversations_tags_gin
  ON conversations USING GIN (topic_tags);

-- JSONB deep search
CREATE INDEX IF NOT EXISTS idx_conversations_metadata_gin
  ON conversations USING GIN (metadata jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_conversations_decisions_gin
  ON conversations USING GIN (key_decisions jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_conversations_actions_gin
  ON conversations USING GIN (action_items jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_conversations_entities_gin
  ON conversations USING GIN (entities jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_conversations_spiral_gin
  ON conversations USING GIN (spiral_context jsonb_path_ops);

-- FTS
CREATE INDEX IF NOT EXISTS idx_conversations_search_doc
  ON conversations USING GIN (search_doc);

-- Content hash for dedup
CREATE INDEX IF NOT EXISTS idx_conversations_content_hash
  ON conversations (content_hash) WHERE content_hash IS NOT NULL;


-- ============================================================================
-- FTS TRIGGER
-- Builds a weighted search vector from summary, decisions, actions, tags,
-- and entities (including spiritual concepts).
-- ============================================================================
CREATE OR REPLACE FUNCTION conversations_search_doc_update() RETURNS trigger AS $$
BEGIN
  NEW.search_doc :=
    setweight(to_tsvector('english', coalesce(NEW.summary, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(NEW.key_decisions::text, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(NEW.action_items::text, '')), 'B') ||
    setweight(to_tsvector('english', array_to_string(NEW.topic_tags, ' ')), 'C') ||
    setweight(to_tsvector('english', coalesce(NEW.entities::text, '')), 'C');
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_conversations_search_doc ON conversations;

CREATE TRIGGER trg_conversations_search_doc
BEFORE INSERT OR UPDATE ON conversations
FOR EACH ROW EXECUTE FUNCTION conversations_search_doc_update();


-- ============================================================================
-- HELPER VIEWS
-- ============================================================================

-- Quick view: conversations with participant names
CREATE OR REPLACE VIEW v_conversations_with_participants AS
SELECT
  c.conversation_id,
  c.started_at,
  c.conversation_type,
  c.source_model,
  c.summary,
  c.topic_tags,
  c.thread_group_id,
  tg.name AS thread_group_name,
  array_agg(DISTINCT cp.display_name) FILTER (WHERE cp.display_name IS NOT NULL) AS participant_names
FROM conversations c
LEFT JOIN conversation_participants cp USING (conversation_id)
LEFT JOIN thread_groups tg USING (thread_group_id)
GROUP BY c.conversation_id, tg.name;
