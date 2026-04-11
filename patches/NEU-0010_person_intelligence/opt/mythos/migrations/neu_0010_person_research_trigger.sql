-- NEU-0010: Person Intelligence Pipeline
-- Trigger for processing queued person research tasks during idle time

INSERT INTO scheduled_triggers (
    name, trigger_type, schedule, action_type, action_payload,
    context_queries, decision_prompt, enabled, priority, metadata
) VALUES (
    'person_deep_research',
    'interval',
    '300',
    'run_task',
    '{"task": "person_deep_research"}'::jsonb,
    '[]'::jsonb,
    NULL,
    false,
    'low',
    '{"description": "Process queued person deep research tasks from Redis"}'::jsonb
)
ON CONFLICT (name) DO NOTHING;
