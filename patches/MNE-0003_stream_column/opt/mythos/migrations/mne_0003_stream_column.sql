-- MNE-0003: Add stream column to idea_backlog, seed stream assignments
-- ============================================================================

BEGIN;

-- ── 1. Add stream column ─────────────────────────────────────────────────────

ALTER TABLE idea_backlog
ADD COLUMN IF NOT EXISTS stream varchar(3)
CHECK (stream IN ('NEU', 'LOG', 'MNE', 'SEN', 'SYS'));

CREATE INDEX IF NOT EXISTS idx_backlog_stream ON idea_backlog (stream);

-- ── 2. Seed streams for ordered backlog items ────────────────────────────────

-- NEU (NEURO) — consciousness, Iris core, grid, perception, memory formation
UPDATE idea_backlog SET stream = 'NEU' WHERE id = 'c9b6bff1-c95b-473e-a84a-ab2f0a955f57';  -- Memory summarization worker
UPDATE idea_backlog SET stream = 'NEU' WHERE id = '368da476-6fd5-4fe4-b54d-07fc1ff990c9';  -- Context window management
UPDATE idea_backlog SET stream = 'NEU' WHERE id = 'e96be3c7-fca8-47ca-9f39-f567448327d6';  -- Builder mode
UPDATE idea_backlog SET stream = 'NEU' WHERE id = '13c71214-e727-4d10-9cc2-e46f06835fbe';  -- Perception layer routing
UPDATE idea_backlog SET stream = 'NEU' WHERE id = 'ddf8f5b3-ba1f-491f-8dd0-965afb9242e3';  -- Two-phase grid processing
UPDATE idea_backlog SET stream = 'NEU' WHERE id = '8491b8dd-b241-4e28-bcc0-b90e6c7d4fe3';  -- Iris service skeleton
UPDATE idea_backlog SET stream = 'NEU' WHERE id = 'e6f9604a-7e64-493d-8179-25ef040593ae';  -- Iris consciousness loop
UPDATE idea_backlog SET stream = 'NEU' WHERE id = '011afd1d-7f55-41a0-b310-81aedb99d039';  -- Memory quality control

-- LOG (LOGOS) — skills, LLM orchestration, prompts, preprocessor
UPDATE idea_backlog SET stream = 'LOG' WHERE id = '99f6a192-596a-4a9d-8725-c7307d97ea19';  -- Preprocessor refinement
UPDATE idea_backlog SET stream = 'LOG' WHERE id = 'eaab1a0a-a627-428f-b315-8c37febb561e';  -- Seraphe mode prompt
UPDATE idea_backlog SET stream = 'LOG' WHERE id = '2dbc5275-cee4-488c-ba52-ed479f56ef3e';  -- Additional model testing
UPDATE idea_backlog SET stream = 'LOG' WHERE id = '906d9bed-3a89-4342-83c6-27917e59ef73';  -- Model selection in preprocessor
UPDATE idea_backlog SET stream = 'LOG' WHERE id = '393376f0-8e7d-4337-ba24-866880f96b5c';  -- Self-validation of proposed changes
UPDATE idea_backlog SET stream = 'LOG' WHERE id = 'edd1ad01-e479-4b1d-9d3c-2f715bc167ea';  -- CLI iris command
UPDATE idea_backlog SET stream = 'LOG' WHERE id = 'c5e39aa7-e65a-4d75-93d8-9c62c8da4b25';  -- AI Coding Orchestration

-- MNE (MNEMOS) — memory, documents, backlog intelligence, life management
UPDATE idea_backlog SET stream = 'MNE' WHERE id = '2c8a5869-5d09-4535-b0e9-4bbd7a6d87cc';  -- Backlog analyst + morning briefing
UPDATE idea_backlog SET stream = 'MNE' WHERE id = '5b405bc7-e27d-42a6-8317-3cdc122a76e2';  -- Proactive nudges
UPDATE idea_backlog SET stream = 'MNE' WHERE id = '9bf87d31-8c70-47f0-a146-5935d1fde53d';  -- Analyst evening accuracy tracking
UPDATE idea_backlog SET stream = 'MNE' WHERE id = '3c551dd6-dad8-43be-9b83-0e52184da2d9';  -- Analyst pattern recognition across weeks
UPDATE idea_backlog SET stream = 'MNE' WHERE id = '4e9185c1-8eb9-418f-84fa-80c061ce160c';  -- Dummy data seed script
UPDATE idea_backlog SET stream = 'MNE' WHERE id = '146f1336-6b4e-4de7-b990-90b975971f6b';  -- Neo4j backlog graph
UPDATE idea_backlog SET stream = 'MNE' WHERE id = 'e1daecd2-0c4b-4b42-ba4e-57c48d7c5c19';  -- Iris autonomous telegram
UPDATE idea_backlog SET stream = 'MNE' WHERE id = 'bf4132f4-ea2a-4221-b148-be896b06693d';  -- Routine edit/delete via Telegram

-- SEN (SENSUS) — external integrations, astrology, people, sensing
UPDATE idea_backlog SET stream = 'SEN' WHERE id = '84a3cd2b-a58c-4228-ad36-40243018016f';  -- Google Calendar sync
UPDATE idea_backlog SET stream = 'SEN' WHERE id = '8f0ec313-7723-4e50-b217-a5e73454ad30';  -- Email integration
UPDATE idea_backlog SET stream = 'SEN' WHERE id = 'cdb4019c-34b9-45d9-9a0d-0753445b029e';  -- Slack integration
UPDATE idea_backlog SET stream = 'SEN' WHERE id = '981839a0-353b-43af-8af9-8538f5864531';  -- Environmental sensors
UPDATE idea_backlog SET stream = 'SEN' WHERE id = '3a1eeb38-c11e-4674-be9b-33afb6f845a2';  -- Web UI calendar section
UPDATE idea_backlog SET stream = 'SEN' WHERE id = 'ac2cadb8-b915-4502-863a-a0097797a2a1';  -- Iris calendar ability
UPDATE idea_backlog SET stream = 'SEN' WHERE id = '001adc04-f5ae-41c4-8513-194fbe9e0be2';  -- Anticipatory transfer suggestions

-- SYS (SYSTEM) — finance, bot core, patches, infra
UPDATE idea_backlog SET stream = 'SYS' WHERE id = '57ebee68-13f9-4e68-be28-c4ef393d5a15';  -- Credit card parsers
UPDATE idea_backlog SET stream = 'SYS' WHERE id = 'fd8dcad1-a3b7-4685-9cb0-2e987c56cce8';  -- Bill match tuning
UPDATE idea_backlog SET stream = 'SYS' WHERE id = 'c4991170-46f6-45e7-99a1-3f5912630d92';  -- Sidney FCU / NBT manual import
UPDATE idea_backlog SET stream = 'SYS' WHERE id = '7486b1ce-6f7b-4c35-a2a1-995c2ef3e505';  -- Bill calendar visual timeline
UPDATE idea_backlog SET stream = 'SYS' WHERE id = 'a98dd626-1d73-4d56-abb2-eb729d535047';  -- Auto-deposit optimization recommendations
UPDATE idea_backlog SET stream = 'SYS' WHERE id = 'abf7a45d-577e-42a8-8262-d7315c0762f2';  -- Import notification with transaction details
UPDATE idea_backlog SET stream = 'SYS' WHERE id = '3060a0eb-642a-4bde-b0b4-a870b6076fba';  -- Bash profile builder
UPDATE idea_backlog SET stream = 'SYS' WHERE id = 'af74b1be-2c1b-4337-b302-5fa812348dba';  -- Docker test environment
UPDATE idea_backlog SET stream = 'SYS' WHERE id = 'fce34cf4-894d-4514-bd1f-375d2b047ac9';  -- Post-patch quality sweep
UPDATE idea_backlog SET stream = 'SYS' WHERE id = '41fd348f-d867-4ad3-8d86-abfe57c79835';  -- Mythos software environment model
UPDATE idea_backlog SET stream = 'SYS' WHERE id = 'f01e8a31-c1c7-44c4-ac30-4d7c35bead44';  -- Audit GitHub repo and add manifests
UPDATE idea_backlog SET stream = 'SYS' WHERE id = '06ac990b-934b-4192-bede-7f416fbce419';  -- Patch monitor manifest enforcement
UPDATE idea_backlog SET stream = 'SYS' WHERE id = 'e2a838b8-3ea2-42fa-bcd5-33c5f43a6c9e';  -- DB schema verification before SQL generation
UPDATE idea_backlog SET stream = 'SYS' WHERE id = '32f5a274-25c7-4609-a370-50c68a0a3b52';  -- CRUD management commands
UPDATE idea_backlog SET stream = 'SYS' WHERE id = '45a5effd-ce11-4bba-9631-54b8f03815d8';  -- Iris send email (infra)
UPDATE idea_backlog SET stream = 'SYS' WHERE id = '22260683-14a9-49ce-b50e-7cf331a2bf6c';  -- Generate instructions for scheduled processes

-- Documentation items — tag as SYS (documentation is system-level)
UPDATE idea_backlog SET stream = 'SYS' WHERE domain = 'documentation' AND stream IS NULL;
UPDATE idea_backlog SET stream = 'SYS' WHERE priority_order BETWEEN 100 AND 199 AND stream IS NULL;

-- ── 3. Add new backlog items ─────────────────────────────────────────────────

-- Rename sweep (route_handler.py, mythos_bot.py, service names)
INSERT INTO idea_backlog (idea, domain, status, priority_order, phase, estimated_effort, stream)
VALUES (
    'Comprehensive file/service rename sweep (route_handler.py → route_planner_handler.py, mythos_bot.py → bot.py, service name audit) — requires Neo4j dependency scan first',
    'development', 'open', 52, '2.0', 'large', 'SYS'
);

-- Neo4j auto-update on patch install
INSERT INTO idea_backlog (idea, domain, status, priority_order, phase, estimated_effort, stream)
VALUES (
    'PatchBase auto-updates Neo4j graph on finish() — every patch writes deployed files, commands, tables, services to graph for dependency tracking',
    'development', 'open', 53, '2.0', 'medium', 'SYS'
);

-- PatchBase structured logging (being built in SYS-0008)
INSERT INTO idea_backlog (idea, domain, status, priority_order, phase, estimated_effort, stream)
VALUES (
    'PatchBase structured logging — JSON + human-readable output persisted to /tmp, consumed by graph and clipboard',
    'development', 'active', 54, '2.0', 'medium', 'SYS'
);

-- Dry-run mode (being built in SYS-0009)
INSERT INTO idea_backlog (idea, domain, status, priority_order, phase, estimated_effort, stream)
VALUES (
    'PatchBase dry-run mode + patch-install --clip clipboard flag + --dry-run validation',
    'development', 'active', 55, '2.0', 'medium', 'SYS'
);

COMMIT;
