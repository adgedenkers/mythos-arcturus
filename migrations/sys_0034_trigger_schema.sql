-- SYS-0034: Trigger Infrastructure Schema
-- Creates: scheduled_triggers, trigger_log, escalation_rules

BEGIN;

-- ═══════════════════════════════════════════════════
-- scheduled_triggers — the heartbeat registry
-- ═══════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS scheduled_triggers (
    id              SERIAL PRIMARY KEY,
    name            TEXT UNIQUE NOT NULL,
    trigger_type    TEXT NOT NULL CHECK (trigger_type IN ('cron', 'interval', 'once', 'event')),
    schedule        TEXT NOT NULL,
    action_type     TEXT NOT NULL CHECK (action_type IN (
        'redis_push', 'telegram_notify', 'run_task', 'api_call',
        'reflex', 'decision_gate', 'run_command'
    )),
    action_payload  JSONB NOT NULL DEFAULT '{}',
    context_queries JSONB DEFAULT '[]',
    decision_prompt TEXT,
    enabled         BOOLEAN NOT NULL DEFAULT true,
    priority        TEXT NOT NULL DEFAULT 'normal' CHECK (priority IN ('critical', 'high', 'normal', 'low')),
    last_fired      TIMESTAMPTZ,
    next_fire       TIMESTAMPTZ,
    fire_count      INTEGER NOT NULL DEFAULT 0,
    last_result     JSONB,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_triggers_next_fire ON scheduled_triggers (next_fire)
    WHERE enabled = true;
CREATE INDEX IF NOT EXISTS idx_triggers_type ON scheduled_triggers (trigger_type);

COMMENT ON TABLE scheduled_triggers IS 'Iris autonomic trigger registry — scheduled, event-based, and threshold-based triggers';


-- ═══════════════════════════════════════════════════
-- trigger_log — full audit trail of every firing
-- ═══════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS trigger_log (
    id                  SERIAL PRIMARY KEY,
    trigger_name        TEXT NOT NULL,
    fired_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    context_gathered    JSONB,
    route               TEXT CHECK (route IN ('reflex', 'decision_gate', 'direct', 'task')),
    decision_prompt     TEXT,
    decision_response   TEXT,
    decision_parsed     JSONB,
    actions_taken       JSONB,
    duration_ms         INTEGER,
    llm_duration_ms     INTEGER,
    success             BOOLEAN,
    error               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_trigger_log_name ON trigger_log (trigger_name);
CREATE INDEX IF NOT EXISTS idx_trigger_log_fired ON trigger_log (fired_at DESC);

COMMENT ON TABLE trigger_log IS 'Audit trail for every trigger firing — context, decisions, actions, outcomes';


-- ═══════════════════════════════════════════════════
-- escalation_rules — threshold-based event escalation
-- ═══════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS escalation_rules (
    id                      SERIAL PRIMARY KEY,
    event_pattern           TEXT NOT NULL,
    tier                    INTEGER NOT NULL CHECK (tier BETWEEN 0 AND 3),
    threshold               INTEGER NOT NULL DEFAULT 1,
    ttl_seconds             INTEGER NOT NULL DEFAULT 3600,
    action_type             TEXT NOT NULL CHECK (action_type IN (
        'reflex', 'alert', 'investigate', 'emergency'
    )),
    action_payload          JSONB NOT NULL DEFAULT '{}',
    decision_prompt_template TEXT,
    context_queries         JSONB DEFAULT '[]',
    enabled                 BOOLEAN NOT NULL DEFAULT true,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (event_pattern, tier)
);

COMMENT ON TABLE escalation_rules IS 'Threshold-based escalation ladder — Redis counters trigger tiered responses';


-- ═══════════════════════════════════════════════════
-- Seed triggers
-- ═══════════════════════════════════════════════════

-- Morning briefing — 6:30 AM EST (11:30 UTC)
INSERT INTO scheduled_triggers (name, trigger_type, schedule, action_type, action_payload, priority, metadata)
VALUES (
    'morning_briefing',
    'cron',
    '30 11 * * *',
    'run_task',
    '{"task": "morning_briefing", "description": "Daily morning briefing — overnight events, schedule, priorities"}',
    'high',
    '{"stream": "NEU", "notes": "UTC schedule — 6:30 AM EST / 7:30 AM EDT"}'
) ON CONFLICT (name) DO NOTHING;

-- Evening summary — 9:00 PM EST (02:00 UTC next day)
INSERT INTO scheduled_triggers (name, trigger_type, schedule, action_type, action_payload, priority, metadata)
VALUES (
    'evening_summary',
    'cron',
    '0 2 * * *',
    'run_task',
    '{"task": "evening_summary", "description": "End of day summary — what got done, what carries forward"}',
    'normal',
    '{"stream": "NEU", "notes": "UTC schedule — 9:00 PM EST / 10:00 PM EDT"}'
) ON CONFLICT (name) DO NOTHING;

-- Weekly review — Monday 8:00 AM EST (13:00 UTC)
INSERT INTO scheduled_triggers (name, trigger_type, schedule, action_type, action_payload, priority, metadata)
VALUES (
    'weekly_review',
    'cron',
    '0 13 * * 1',
    'run_task',
    '{"task": "weekly_financial_review", "description": "Weekly financial review + system health summary"}',
    'normal',
    '{"stream": "SYS", "notes": "UTC schedule — 8:00 AM EST Monday"}'
) ON CONFLICT (name) DO NOTHING;

-- Monthly review — 25th at 8:00 AM EST (13:00 UTC)
INSERT INTO scheduled_triggers (name, trigger_type, schedule, action_type, action_payload, priority, metadata)
VALUES (
    'monthly_review',
    'cron',
    '0 13 25 * *',
    'run_task',
    '{"task": "monthly_review", "description": "Monthly financial + system review"}',
    'normal',
    '{"stream": "SYS", "notes": "UTC schedule — 8:00 AM EST on 25th"}'
) ON CONFLICT (name) DO NOTHING;

-- Service health check — every 5 minutes
INSERT INTO scheduled_triggers (name, trigger_type, schedule, action_type, action_payload, priority, metadata)
VALUES (
    'service_health',
    'interval',
    '300',
    'reflex',
    '{"reflex": "check_all_services", "services": ["mythos-api", "mythos-bot", "mythos-patch-monitor", "mythos-worker-grid", "mythos-worker-vision", "mythos-worker-embedding", "mythos-worker-entity", "mythos-worker-summary", "mythos-worker-temporal", "mythos-voice-watcher", "mythos-transcription-worker", "mythos-segment-manager", "mythos-knowledge-map", "mythos-doc-watcher"]}',
    'critical',
    '{"stream": "SYS"}'
) ON CONFLICT (name) DO NOTHING;

-- Idle task sweep — every 30 minutes
INSERT INTO scheduled_triggers (name, trigger_type, schedule, action_type, action_payload, priority, metadata)
VALUES (
    'idle_sweep',
    'interval',
    '1800',
    'run_task',
    '{"task": "next_idle_task", "description": "Run next available idle task from registry"}',
    'low',
    '{"stream": "NEU"}'
) ON CONFLICT (name) DO NOTHING;

-- Transit precompute — daily at midnight EST (05:00 UTC)
INSERT INTO scheduled_triggers (name, trigger_type, schedule, action_type, action_payload, priority, metadata)
VALUES (
    'transit_precompute',
    'cron',
    '0 5 * * *',
    'run_task',
    '{"task": "transit_precompute", "description": "Precompute daily astrology transits"}',
    'normal',
    '{"stream": "SEN"}'
) ON CONFLICT (name) DO NOTHING;


-- ═══════════════════════════════════════════════════
-- Seed escalation rules
-- ═══════════════════════════════════════════════════

-- Service crash escalation ladder
INSERT INTO escalation_rules (event_pattern, tier, threshold, ttl_seconds, action_type, action_payload)
VALUES
    ('crash:*', 0, 1, 3600, 'reflex', '{"action": "log_only", "note": "systemd handles first restart"}'),
    ('crash:*', 1, 2, 3600, 'alert', '{"telegram": true, "template": "⚠️ {entity} crashed {count}x in the last hour"}'),
    ('crash:*', 2, 3, 3600, 'investigate', '{"gather": ["journalctl", "git_log", "service_status"], "prompt": "service_crash_investigation"}'),
    ('crash:*', 3, 5, 3600, 'emergency', '{"disable_service": true, "telegram": true, "full_diagnostic": true}')
ON CONFLICT (event_pattern, tier) DO NOTHING;

-- Task failure escalation
INSERT INTO escalation_rules (event_pattern, tier, threshold, ttl_seconds, action_type, action_payload)
VALUES
    ('task_fail:*', 1, 3, 7200, 'alert', '{"telegram": true, "template": "⚠️ Task {entity} failed {count}x in 2 hours"}'),
    ('task_fail:*', 2, 5, 7200, 'investigate', '{"gather": ["iris_task_log", "service_status"], "prompt": "task_failure_analysis"}')
ON CONFLICT (event_pattern, tier) DO NOTHING;

-- Import failure escalation
INSERT INTO escalation_rules (event_pattern, tier, threshold, ttl_seconds, action_type, action_payload)
VALUES
    ('import_fail:*', 1, 1, 7200, 'alert', '{"telegram": true, "template": "⚠️ Import failed for {entity}: {error}"}')
ON CONFLICT (event_pattern, tier) DO NOTHING;

-- Disk usage escalation
INSERT INTO escalation_rules (event_pattern, tier, threshold, ttl_seconds, action_type, action_payload)
VALUES
    ('disk_high', 1, 1, 3600, 'alert', '{"telegram": true, "template": "⚠️ Disk usage at {detail}%"}'),
    ('disk_high', 2, 3, 3600, 'investigate', '{"gather": ["disk_usage"], "prompt": "disk_analysis"}')
ON CONFLICT (event_pattern, tier) DO NOTHING;

COMMIT;
