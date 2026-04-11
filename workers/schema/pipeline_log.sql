-- ═══════════════════════════════════════════════════════════════
-- PIPELINE LOG SCHEMA v1.0.0
-- ═══════════════════════════════════════════════════════════════
-- Records every message through the consciousness pipeline.
-- Full prompt state captured so any response can be replayed.
--
-- Install: sudo -u postgres psql -d mythos -f pipeline_log.sql

-- Main pipeline runs
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id              BIGSERIAL PRIMARY KEY,
    run_uuid        UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Input
    speaker         TEXT NOT NULL,
    message         TEXT NOT NULL,
    gap_description TEXT,

    -- Routing
    processing_path TEXT CHECK (processing_path IN ('fast', 'standard', 'full', 'fallback')),

    -- Registry version used
    registry_version TEXT NOT NULL,

    -- Timing
    total_elapsed_ms INTEGER,

    -- Final output
    iris_response   TEXT,

    -- Full perception output (JSONB for querying)
    perception      JSONB,

    -- Full context package from DISCOVERY
    discovery       JSONB,

    -- Metadata
    iris_model      TEXT,
    perception_model TEXT
);

-- Individual LLM calls within a pipeline run
CREATE TABLE IF NOT EXISTS pipeline_llm_calls (
    id              BIGSERIAL PRIMARY KEY,
    run_uuid        UUID REFERENCES pipeline_runs(run_uuid) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- What stage
    stage           TEXT NOT NULL CHECK (stage IN ('perception', 'query_builder', 'query_validator', 'strategy', 'iris')),

    -- Model config
    model           TEXT NOT NULL,
    temperature     REAL,

    -- The actual prompts sent
    system_prompt   TEXT NOT NULL,
    user_prompt     TEXT NOT NULL,

    -- Which registry components were included
    prompt_components JSONB,

    -- Response
    raw_response    TEXT,
    parsed_response JSONB,

    -- Timing
    elapsed_ms      INTEGER,

    -- Did it parse successfully?
    parse_success   BOOLEAN DEFAULT true
);

-- Queries executed during DISCOVERY
CREATE TABLE IF NOT EXISTS pipeline_queries (
    id              BIGSERIAL PRIMARY KEY,
    run_uuid        UUID REFERENCES pipeline_runs(run_uuid) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Source
    source_type     TEXT NOT NULL CHECK (source_type IN ('postgres', 'neo4j', 'filesystem', 'command')),
    intent          TEXT,
    query_text      TEXT NOT NULL,

    -- Validation
    validated       BOOLEAN DEFAULT false,
    validator_approved BOOLEAN,
    corrected_query TEXT,
    risk_level      TEXT CHECK (risk_level IN ('safe', 'caution', 'dangerous')),

    -- Results
    rows_returned   INTEGER,
    result_summary  TEXT,
    elapsed_ms      INTEGER,

    -- Priority
    priority        TEXT CHECK (priority IN ('critical', 'helpful', 'background'))
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_created ON pipeline_runs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_speaker ON pipeline_runs(speaker);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_path ON pipeline_runs(processing_path);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_registry ON pipeline_runs(registry_version);
CREATE INDEX IF NOT EXISTS idx_pipeline_llm_calls_run ON pipeline_llm_calls(run_uuid);
CREATE INDEX IF NOT EXISTS idx_pipeline_llm_calls_stage ON pipeline_llm_calls(stage);
CREATE INDEX IF NOT EXISTS idx_pipeline_queries_run ON pipeline_queries(run_uuid);

-- View: quick overview of recent runs
CREATE OR REPLACE VIEW pipeline_recent AS
SELECT
    r.created_at,
    r.speaker,
    LEFT(r.message, 60) AS message_preview,
    r.processing_path,
    r.total_elapsed_ms,
    r.perception->>'message_type' AS msg_type,
    r.perception->>'complexity' AS complexity,
    r.registry_version,
    LEFT(r.iris_response, 80) AS response_preview,
    (SELECT COUNT(*) FROM pipeline_llm_calls c WHERE c.run_uuid = r.run_uuid) AS llm_calls,
    (SELECT COUNT(*) FROM pipeline_queries q WHERE q.run_uuid = r.run_uuid) AS queries_run
FROM pipeline_runs r
ORDER BY r.created_at DESC
LIMIT 50;

-- View: prompt component usage tracking
CREATE OR REPLACE VIEW prompt_component_usage AS
SELECT
    c.stage,
    comp.value::text AS component_id,
    COUNT(*) AS times_used,
    MIN(r.created_at) AS first_used,
    MAX(r.created_at) AS last_used
FROM pipeline_llm_calls c
CROSS JOIN LATERAL jsonb_array_elements(c.prompt_components) AS comp
JOIN pipeline_runs r ON r.run_uuid = c.run_uuid
GROUP BY c.stage, comp.value::text
ORDER BY times_used DESC;
