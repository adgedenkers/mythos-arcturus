-- NEU-0009: Decision Gate — Seed test triggers
-- Two disabled triggers that route through the decision gate for testing

-- smart_service_check: gathers service status + journal, LLM decides restart/notify/log_only
INSERT INTO scheduled_triggers (
    name, trigger_type, schedule, action_type, action_payload,
    context_queries, decision_prompt, enabled, priority, metadata
) VALUES (
    'smart_service_check',
    'interval',
    '3600',
    'decision_gate',
    '{}',
    '[
        {"provider": "service_status", "args": {"service": "mythos-worker-grid"}},
        {"provider": "journalctl", "args": {"unit": "mythos-worker-grid", "lines": 30}}
    ]'::jsonb,
    'You are a system operations assistant for the Mythos infrastructure on Arcturus.

Analyze the following service diagnostics and decide what action to take.

Diagnostics:
{context}

Available actions:
- "restart": The service is clearly unhealthy or crashed. Restart it.
- "notify_human": Something looks concerning but not critical. Alert the operator.
- "log_only": Everything looks normal. Just log this check, no action needed.

Consider:
- Is the service active and running?
- Are there error patterns in the journal?
- Has the service restarted recently (NRestarts)?
- Is memory usage abnormal?

Decide which action to take and how confident you are.',
    false,
    'normal',
    '{"model": "qwen2.5:32b", "description": "Smart service health check with LLM judgment"}'::jsonb
)
ON CONFLICT (name) DO NOTHING;

-- smart_disk_check: gathers disk usage, LLM decides alert/ignore
INSERT INTO scheduled_triggers (
    name, trigger_type, schedule, action_type, action_payload,
    context_queries, decision_prompt, enabled, priority, metadata
) VALUES (
    'smart_disk_check',
    'interval',
    '3600',
    'decision_gate',
    '{}',
    '[
        {"provider": "disk_usage", "args": {"path": "/"}},
        {"provider": "disk_usage", "args": {"path": "/opt/mythos"}}
    ]'::jsonb,
    'You are a system operations assistant for the Mythos infrastructure on Arcturus.

Analyze the following disk usage data and decide what action to take.

Disk usage:
{context}

Available actions:
- "alert": Disk usage is critically high (above 90%) or trending toward full. Alert immediately.
- "warn": Disk usage is elevated (above 75%) but not critical. Notify operator.
- "log_only": Disk usage is normal. No action needed.

Consider:
- What percentage of each filesystem is used?
- Is /opt/mythos (where the main system lives) at risk?
- Is the root filesystem healthy?

Decide which action to take and how confident you are.',
    false,
    'low',
    '{"model": "qwen2.5:32b", "description": "Smart disk usage check with LLM judgment"}'::jsonb
)
ON CONFLICT (name) DO NOTHING;
