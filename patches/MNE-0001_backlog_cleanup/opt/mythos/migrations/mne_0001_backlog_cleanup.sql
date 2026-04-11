-- MNE-0001: Backlog cleanup — mark completions, assign priority_order, archive dupes
-- ============================================================================

BEGIN;

-- ── 1. Mark completed items as done ──────────────────────────────────────────

-- mythos-diag command — deployed SYS-0005
UPDATE idea_backlog
SET status = 'done', completed_at = NOW(), last_updated = NOW()
WHERE id = '77ec73a7-9828-40d7-ada8-0da33fa6ced2'
  AND status != 'done';

-- "Rich contact/provider database" at priority_order 16 — already done (a8195513 is done)
-- The ordered row 27b86c6d is still open — mark it done too since the unordered dupe is done
UPDATE idea_backlog
SET status = 'done', completed_at = NOW(), last_updated = NOW()
WHERE id = '27b86c6d-7da5-47e5-b431-d23eeb08078e'
  AND status != 'done';

-- "Iris web search capability" — ordered row 9b91c962 still open, but e180cac6 is done
UPDATE idea_backlog
SET status = 'done', completed_at = NOW(), last_updated = NOW()
WHERE id = '9b91c962-4e7c-4fbc-b6fe-cda35cd73fc0'
  AND status != 'done';

-- "Redis async queues for Iris" — ordered row 81817121 open, but 1cb541cb is done
UPDATE idea_backlog
SET status = 'done', completed_at = NOW(), last_updated = NOW()
WHERE id = '81817121-568a-4abf-9f3a-b8e466825f94'
  AND status != 'done';

-- "Bash profile builder" — ordered row 3060a0eb open, dupe ca2cc881 also open. Keep ordered one, archive dupe.
UPDATE idea_backlog
SET is_archived = true, archived_at = NOW(), last_updated = NOW()
WHERE id = 'ca2cc881-0782-4928-8139-ada0c56e8135';

-- "Iris web search" dupe — e180cac6 is done, archive it (the ordered row is now also done)
UPDATE idea_backlog
SET is_archived = true, archived_at = NOW(), last_updated = NOW()
WHERE id = 'e180cac6-4202-442c-89d2-64ba2f5b654f';

-- "Redis queues" dupe — 1cb541cb is done, archive it
UPDATE idea_backlog
SET is_archived = true, archived_at = NOW(), last_updated = NOW()
WHERE id = '1cb541cb-35b2-46d6-aa8f-c11e5550c3b2';

-- "Rich contact/provider" dupe — a8195513 is done, archive it
UPDATE idea_backlog
SET is_archived = true, archived_at = NOW(), last_updated = NOW()
WHERE id = 'a8195513-bb62-4013-a587-ab6a7228896d';


-- ── 2. Tag personal tasks with domain='task' if not already tagged ───────────
-- These are clearly personal/life items sitting in the backlog without domain

UPDATE idea_backlog SET domain = 'task', idea_type = 'task'
WHERE id IN (
    '5f040a38-9b32-4a11-ba90-27321a0e0102',  -- Spending Report
    'fa3faab5-7491-4e16-89e1-9dda715b741c',  -- Find Snow Removal
    '7b1f0b4b-0414-4f8f-8be1-9f16be1bbb1a',  -- Install Fitz's Desk Hardware
    '915b029d-0896-46ce-91bc-7cc262dd0046',  -- Put away pool floats
    '8fb26d40-b6c8-49ee-b57d-4932e9213bdd',  -- Financial Reports
    '782d6ed3-e1fa-4377-8ad7-a0f134847a81',  -- change fb notifications
    '0310f875-bb66-432d-8fff-25016e570282',  -- talk to Rebecca about animals
    'e1daecd2-0c4b-4b42-ba4e-57c48d7c5c19',  -- Iris send telegram on own (actually dev — skip)
    '22260683-14a9-49ce-b50e-7cf331a2bf6c',  -- generate instructions for scheduled processes
    '45a5effd-ce11-4bba-9631-54b8f03815d8'   -- Iris needs ability to send email
) AND domain IS DISTINCT FROM 'task';

-- Actually, some of those are dev items. Let me be more precise:
-- Personal tasks only:
UPDATE idea_backlog SET domain = 'task', idea_type = 'task'
WHERE id IN (
    '5f040a38-9b32-4a11-ba90-27321a0e0102',  -- Spending Report
    'fa3faab5-7491-4e16-89e1-9dda715b741c',  -- Find Snow Removal
    '7b1f0b4b-0414-4f8f-8be1-9f16be1bbb1a',  -- Install Fitz's Desk Hardware
    '915b029d-0896-46ce-91bc-7cc262dd0046',  -- Put away pool floats
    '8fb26d40-b6c8-49ee-b57d-4932e9213bdd',  -- Financial Reports
    '782d6ed3-e1fa-4377-8ad7-a0f134847a81',  -- change fb notifications
    '0310f875-bb66-432d-8fff-25016e570282'    -- talk to Rebecca about animals
) AND domain IS DISTINCT FROM 'task';

-- Dev items — tag as domain='development'
UPDATE idea_backlog SET domain = 'development'
WHERE id IN (
    'e1daecd2-0c4b-4b42-ba4e-57c48d7c5c19',  -- Iris send telegram on own
    '22260683-14a9-49ce-b50e-7cf331a2bf6c',  -- generate instructions for scheduled processes
    '45a5effd-ce11-4bba-9631-54b8f03815d8',  -- Iris send email
    'ac2cadb8-b915-4502-863a-a0097797a2a1',  -- Iris calendar ability
    'c5e39aa7-e65a-4d75-93d8-9c62c8da4b25',  -- AI Coding Orchestration
    '4a257724-c9b1-4616-909d-c44b44d9b9d2'   -- Iris web search (open dupe)
) AND domain IS NULL;

-- Documentation items — tag as domain='documentation'
UPDATE idea_backlog SET domain = 'documentation'
WHERE id IN (
    '685cd746-23a5-4eee-935a-0b84c05e0001',  -- Document: API endpoints
    '468a362c-1728-40c2-97b6-0affcc2ba495',  -- Document: Worker services
    '2fab8a95-107d-407a-8897-4963135aa65e',  -- Document: Sell mode
    'ad4b3199-5fdf-4bc7-8560-7dbe901e0047',  -- Document: Astrology system
    '84e23e4a-7913-49e5-b1fb-e6ff7f2a6c30',  -- Document: Finance system
    'e02363b4-b080-4034-8286-a411e56c38fe',  -- Document: Iris system
    '4868af85-2293-4295-8f82-3d92bb33e299',  -- Document: Services reference
    'eb25cca3-92fe-4720-b73e-57343d1b1107',  -- Document: Core modules
    'cc48a868-f90d-486c-a699-1f95b1e0e144'   -- Document: Telegram commands
) AND domain IS NULL;


-- ── 3. Assign priority_order to unordered dev/doc items ──────────────────────

-- Dev items without priority_order — slot them after the existing ordered items
UPDATE idea_backlog SET priority_order = 47, phase = '1.5', estimated_effort = 'medium'
WHERE id = 'e1daecd2-0c4b-4b42-ba4e-57c48d7c5c19' AND priority_order IS NULL;  -- Iris autonomous telegram

UPDATE idea_backlog SET priority_order = 48, phase = '2.0', estimated_effort = 'medium'
WHERE id = '45a5effd-ce11-4bba-9631-54b8f03815d8' AND priority_order IS NULL;  -- Iris send email

UPDATE idea_backlog SET priority_order = 49, phase = '1.7', estimated_effort = 'small'
WHERE id = '22260683-14a9-49ce-b50e-7cf331a2bf6c' AND priority_order IS NULL;  -- scheduled process docs

UPDATE idea_backlog SET priority_order = 50, phase = '1.7', estimated_effort = 'medium'
WHERE id = 'ac2cadb8-b915-4502-863a-a0097797a2a1' AND priority_order IS NULL;  -- Iris calendar ability

UPDATE idea_backlog SET priority_order = 51, phase = '2.0', estimated_effort = 'large'
WHERE id = 'c5e39aa7-e65a-4d75-93d8-9c62c8da4b25' AND priority_order IS NULL;  -- AI Coding Orchestration

-- Archive the open dupe of "Iris web search" (4a257724) — ordered row 9b91c962 now marked done
UPDATE idea_backlog SET is_archived = true, archived_at = NOW(), last_updated = NOW()
WHERE id = '4a257724-c9b1-4616-909d-c44b44d9b9d2';

-- Documentation items — assign order in the 110+ range (after existing 100-108)
UPDATE idea_backlog SET priority_order = 110, domain = 'documentation', estimated_effort = 'small'
WHERE id = '685cd746-23a5-4eee-935a-0b84c05e0001' AND priority_order IS NULL;

UPDATE idea_backlog SET priority_order = 111, domain = 'documentation', estimated_effort = 'small'
WHERE id = '468a362c-1728-40c2-97b6-0affcc2ba495' AND priority_order IS NULL;

UPDATE idea_backlog SET priority_order = 112, domain = 'documentation', estimated_effort = 'small'
WHERE id = '2fab8a95-107d-407a-8897-4963135aa65e' AND priority_order IS NULL;

UPDATE idea_backlog SET priority_order = 113, domain = 'documentation', estimated_effort = 'small'
WHERE id = 'ad4b3199-5fdf-4bc7-8560-7dbe901e0047' AND priority_order IS NULL;

UPDATE idea_backlog SET priority_order = 114, domain = 'documentation', estimated_effort = 'small'
WHERE id = '84e23e4a-7913-49e5-b1fb-e6ff7f2a6c30' AND priority_order IS NULL;

UPDATE idea_backlog SET priority_order = 115, domain = 'documentation', estimated_effort = 'small'
WHERE id = 'e02363b4-b080-4034-8286-a411e56c38fe' AND priority_order IS NULL;

UPDATE idea_backlog SET priority_order = 116, domain = 'documentation', estimated_effort = 'small'
WHERE id = '4868af85-2293-4295-8f82-3d92bb33e299' AND priority_order IS NULL;

UPDATE idea_backlog SET priority_order = 117, domain = 'documentation', estimated_effort = 'small'
WHERE id = 'eb25cca3-92fe-4720-b73e-57343d1b1107' AND priority_order IS NULL;

UPDATE idea_backlog SET priority_order = 118, domain = 'documentation', estimated_effort = 'small'
WHERE id = 'cc48a868-f90d-486c-a699-1f95b1e0e144' AND priority_order IS NULL;

COMMIT;
