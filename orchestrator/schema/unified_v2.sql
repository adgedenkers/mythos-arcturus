-- ═══════════════════════════════════════════════════════
-- UNIFIED ORCHESTRATOR SCHEMA ADDITIONS v2.0.0
-- ═══════════════════════════════════════════════════════
-- Adds role assignments and config snapshots to existing
-- orch_* and pipeline_* tables.

-- Maps models to pipeline roles with bench scores
CREATE TABLE IF NOT EXISTS orch_role_assignments (
    id              SERIAL PRIMARY KEY,
    role            TEXT NOT NULL,
    model_id        TEXT NOT NULL,
    config          JSONB NOT NULL DEFAULT '{}',
    score           REAL,
    promoted_from   TEXT,
    promoted_at     TIMESTAMPTZ DEFAULT NOW(),
    is_active       BOOLEAN DEFAULT true,
    UNIQUE(role, model_id)
);

CREATE INDEX IF NOT EXISTS idx_orch_roles_active
    ON orch_role_assignments(role) WHERE is_active = true;

-- Config snapshots for full reproducibility
CREATE TABLE IF NOT EXISTS orch_config_snapshots (
    id              SERIAL PRIMARY KEY,
    snapshot_id     TEXT UNIQUE NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    registry_yaml   TEXT NOT NULL,
    settings_json   JSONB NOT NULL,
    source          TEXT NOT NULL,
    source_id       TEXT
);

-- Seed current role assignments from what's working
INSERT INTO orch_role_assignments (role, model_id, config, score, promoted_from, is_active)
VALUES
    ('perception', 'qwen2_5_32b', '{"model": "qwen2.5:32b", "temperature": 0.1, "num_predict": 1024, "timeout": 30}', 0.73, 'manual_calibration_20260226', true),
    ('iris', 'iris_thinking_v2', '{"model": "iris-thinking-v2:latest", "temperature": 0.4, "num_predict": 4096, "timeout": 60}', null, 'initial_assignment', true)
ON CONFLICT (role, model_id) DO NOTHING;

-- View: current role assignments
CREATE OR REPLACE VIEW orch_active_roles AS
SELECT
    role,
    model_id,
    config->>'model' AS model_name,
    (config->>'temperature')::real AS temperature,
    score,
    promoted_at
FROM orch_role_assignments
WHERE is_active = true
ORDER BY role;
