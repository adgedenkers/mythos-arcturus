-- SYS-0075: Finance v2 — Infrastructure & Safety (Patch A)
-- Creates: finance schema, core enums, entities, accounts, protection triggers
-- Seeds: Personal + Denkers Co. LLC entities, 5 system accounts
-- Ref: /opt/mythos/docs/FINANCE_V2.md §4, §6, §14, §15

\set ON_ERROR_STOP on

BEGIN;

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. Schema
-- ─────────────────────────────────────────────────────────────────────────────
CREATE SCHEMA finance;
COMMENT ON SCHEMA finance IS 'Finance v2 — double-entry ledger. See docs/FINANCE_V2.md';

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. Enums (Patch A only — other enums deferred to their owning patches)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TYPE finance.entity_kind AS ENUM (
    'individual',
    'llc',
    'corporation',
    'trust'
);

CREATE TYPE finance.account_kind AS ENUM (
    'asset',
    'liability',
    'income',
    'expense',
    'equity'
);

CREATE TYPE finance.normal_balance AS ENUM (
    'debit',
    'credit'
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. finance.entities — entity attribution dimension (§6)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE finance.entities (
    id              BIGSERIAL PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    kind            finance.entity_kind NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT true,
    tax_id_masked   TEXT,
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE finance.entities IS
    'Entity attribution dimension. Every ledger entry belongs to exactly one entity. §6.';

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. finance.accounts — chart of accounts (§4, §14.1)
--    Hybrid: adjacency list (parent_account_id) + materialized path (account_path)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE finance.accounts (
    id                      BIGSERIAL PRIMARY KEY,
    account_path            TEXT NOT NULL UNIQUE,
    name                    TEXT NOT NULL,
    account_kind            finance.account_kind NOT NULL,
    account_subtype         TEXT NOT NULL,
    parent_account_id       BIGINT REFERENCES finance.accounts(id),
    normal_balance          finance.normal_balance NOT NULL,
    currency_code           TEXT NOT NULL DEFAULT 'USD',
    is_postable             BOOLEAN NOT NULL DEFAULT true,
    is_system               BOOLEAN NOT NULL DEFAULT false,
    is_active               BOOLEAN NOT NULL DEFAULT true,
    institution             TEXT,
    account_number_masked   TEXT,
    abbreviation            TEXT,
    metadata                JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE finance.accounts IS
    'Chart of accounts. Real accounts, expense/income categories, equity, and system accounts all live here. §4.';

CREATE INDEX idx_accounts_parent ON finance.accounts(parent_account_id);
CREATE INDEX idx_accounts_kind ON finance.accounts(account_kind);
CREATE INDEX idx_accounts_path_prefix ON finance.accounts(account_path text_pattern_ops);

-- ─────────────────────────────────────────────────────────────────────────────
-- 5. Helper: slugify a name for path segments
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION finance.slugify(input TEXT)
RETURNS TEXT LANGUAGE sql IMMUTABLE AS $$
    SELECT regexp_replace(
               regexp_replace(lower(coalesce(input, '')), '[^a-z0-9]+', '_', 'g'),
               '(^_+|_+$)', '', 'g'
           );
$$;

-- ─────────────────────────────────────────────────────────────────────────────
-- 6. Trigger: materialized path derivation
--    On INSERT/UPDATE: derive account_path from parent chain + slugified name.
--    Exception: if parent is NULL AND an explicit account_path is provided,
--    respect it (this lets system seeds use exact colon paths like
--    'equity:opening_balances' without forcing intermediate parent nodes).
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION finance.tg_accounts_derive_path()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    parent_path TEXT;
BEGIN
    IF NEW.parent_account_id IS NULL THEN
        -- Root node: accept explicit path if given, otherwise slugify name
        IF NEW.account_path IS NULL OR NEW.account_path = '' THEN
            NEW.account_path := finance.slugify(NEW.name);
        END IF;
    ELSE
        SELECT account_path INTO parent_path
        FROM finance.accounts
        WHERE id = NEW.parent_account_id;

        IF parent_path IS NULL THEN
            RAISE EXCEPTION 'parent_account_id % not found', NEW.parent_account_id;
        END IF;

        NEW.account_path := parent_path || ':' || finance.slugify(NEW.name);
    END IF;

    NEW.updated_at := now();
    RETURN NEW;
END;
$$;

CREATE TRIGGER accounts_derive_path
    BEFORE INSERT OR UPDATE OF parent_account_id, name, account_path
    ON finance.accounts
    FOR EACH ROW
    EXECUTE FUNCTION finance.tg_accounts_derive_path();

-- ─────────────────────────────────────────────────────────────────────────────
-- 7. Trigger: cascade path updates to descendants
--    When a non-system account is reparented or renamed, rewrite descendants.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION finance.tg_accounts_cascade_path()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.account_path IS DISTINCT FROM OLD.account_path THEN
        UPDATE finance.accounts
        SET account_path = NEW.account_path || substring(account_path from length(OLD.account_path) + 1),
            updated_at = now()
        WHERE account_path LIKE OLD.account_path || ':%';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER accounts_cascade_path
    AFTER UPDATE OF account_path
    ON finance.accounts
    FOR EACH ROW
    WHEN (NEW.account_path IS DISTINCT FROM OLD.account_path)
    EXECUTE FUNCTION finance.tg_accounts_cascade_path();

-- ─────────────────────────────────────────────────────────────────────────────
-- 8. Trigger: system account protection
--    Blocks UPDATE of critical fields and DELETE when is_system = true.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION finance.tg_accounts_protect_system()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        IF OLD.is_system THEN
            RAISE EXCEPTION 'Cannot delete system account: % (id=%)', OLD.account_path, OLD.id;
        END IF;
        RETURN OLD;
    END IF;

    -- UPDATE
    IF OLD.is_system THEN
        IF NEW.name IS DISTINCT FROM OLD.name
           OR NEW.account_path IS DISTINCT FROM OLD.account_path
           OR NEW.parent_account_id IS DISTINCT FROM OLD.parent_account_id
           OR NEW.account_kind IS DISTINCT FROM OLD.account_kind
           OR NEW.is_system IS DISTINCT FROM OLD.is_system THEN
            RAISE EXCEPTION
                'Cannot modify protected fields on system account: % (id=%)',
                OLD.account_path, OLD.id;
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER accounts_protect_system_update
    BEFORE UPDATE ON finance.accounts
    FOR EACH ROW
    EXECUTE FUNCTION finance.tg_accounts_protect_system();

CREATE TRIGGER accounts_protect_system_delete
    BEFORE DELETE ON finance.accounts
    FOR EACH ROW
    EXECUTE FUNCTION finance.tg_accounts_protect_system();

-- ─────────────────────────────────────────────────────────────────────────────
-- 9. Seed: entities (§6.2)
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO finance.entities (id, name, kind, is_active) VALUES
    (1, 'Personal',        'individual', true),
    (2, 'Denkers Co. LLC', 'llc',        false);

-- Advance sequence past explicit IDs
SELECT setval('finance.entities_id_seq', 2, true);

-- ─────────────────────────────────────────────────────────────────────────────
-- 10. Seed: system accounts (§4.4)
--     Explicit account_path respected because parent_account_id IS NULL.
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO finance.accounts
    (account_path, name, account_kind, account_subtype, normal_balance, is_system, is_postable)
VALUES
    ('equity:opening_balances',          'Opening Balances',          'equity',  'opening_balance',          'credit', true, true),
    ('equity:reconciliation_adjustments','Reconciliation Adjustments','equity',  'reconciliation_adjustment','credit', true, true),
    ('assets:transit:bank_transfers',    'Bank Transfers (Transit)',  'asset',   'transit',                  'debit',  true, true),
    ('expenses:uncategorized',           'Uncategorized Expense',     'expense', 'category',                 'debit',  true, true),
    ('income:uncategorized',             'Uncategorized Income',      'income',  'category',                 'credit', true, true);

COMMIT;
