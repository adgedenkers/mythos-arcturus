-- SYS-0076: Finance v2 — Ledger & Data Layer (Patch B)
-- Creates: import/observation/transaction/entry tables + deferred balance trigger
-- Depends on: SYS-0075 (finance schema, entities, accounts)
-- Ref: /opt/mythos/docs/FINANCE_V2.md §2.3, §2.5, §14.2, §14.3

\set ON_ERROR_STOP on

BEGIN;

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. Enums
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TYPE finance.transaction_kind AS ENUM (
    'imported',
    'manual',
    'transfer',
    'adjustment',
    'reversal',
    'opening_balance'
);

CREATE TYPE finance.observation_status AS ENUM (
    'new',
    'duplicate',
    'matched',
    'flagged',
    'reversed',
    'ignored'
);

CREATE TYPE finance.import_status AS ENUM (
    'running',
    'completed',
    'failed',
    'reversed'
);

CREATE TYPE finance.direction AS ENUM (
    'inflow',
    'outflow'
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. finance.import_sources — per-institution profile (§3.4, §14.3)
--    Schema only; institution rows seeded in Patch D alongside the importer.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE finance.import_sources (
    id                              BIGSERIAL PRIMARY KEY,
    institution_name                TEXT NOT NULL UNIQUE,
    parser_module                   TEXT NOT NULL,
    has_transaction_id              BOOLEAN NOT NULL DEFAULT false,
    has_running_balance             BOOLEAN NOT NULL DEFAULT false,
    date_tolerance_days             INTEGER NOT NULL DEFAULT 1,
    description_stable_after_post   BOOLEAN NOT NULL DEFAULT true,
    amount_always_exact             BOOLEAN NOT NULL DEFAULT true,
    date_column_semantics           TEXT NOT NULL DEFAULT 'posted',
    auto_skip_threshold             INTEGER NOT NULL DEFAULT 95,
    review_threshold                INTEGER NOT NULL DEFAULT 70,
    notes                           TEXT,
    created_at                      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT import_sources_thresholds_sane
        CHECK (auto_skip_threshold BETWEEN 0 AND 100
           AND review_threshold    BETWEEN 0 AND 100
           AND review_threshold <= auto_skip_threshold)
);

COMMENT ON TABLE finance.import_sources IS
    'Per-institution importer tuning profile. Seeded in Patch D. §3.4.';

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. finance.imports — first-class import event (§11.1, §14.3)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE finance.imports (
    id                  BIGSERIAL PRIMARY KEY,
    source_file         TEXT NOT NULL,
    account_id          BIGINT NOT NULL REFERENCES finance.accounts(id),
    import_source_id    BIGINT REFERENCES finance.import_sources(id),
    started_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at        TIMESTAMPTZ,
    status              finance.import_status NOT NULL DEFAULT 'running',
    rows_total          INTEGER,
    rows_new            INTEGER,
    rows_updated        INTEGER,
    rows_skipped        INTEGER,
    rows_flagged        INTEGER,
    drift_detected      BOOLEAN NOT NULL DEFAULT false,
    drift_amount_minor  BIGINT,
    change_manifest     JSONB,
    can_reverse         BOOLEAN NOT NULL DEFAULT true,
    reversed_at         TIMESTAMPTZ,
    reversed_by         TEXT
);

CREATE INDEX idx_imports_account_started ON finance.imports(account_id, started_at DESC);
CREATE INDEX idx_imports_status ON finance.imports(status);

COMMENT ON TABLE finance.imports IS
    'First-class import events. Every CSV drop creates one. Reversible via relational undo. §11.';

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. finance.transactions — envelope around entries (§2.4, §14.2)
--    merchant_id is plain BIGINT (no FK) — merchants table arrives in Patch C.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE finance.transactions (
    id                          BIGSERIAL PRIMARY KEY,
    description                 TEXT NOT NULL,
    merchant_id                 BIGINT,
    memo                        TEXT,
    kind                        finance.transaction_kind NOT NULL,
    posted_date                 DATE NOT NULL,
    effective_date              DATE,
    imported_at                 TIMESTAMPTZ,
    transfer_group_id           UUID,
    reversed_by_transaction_id  BIGINT REFERENCES finance.transactions(id),
    metadata                    JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_transactions_posted_date ON finance.transactions(posted_date);
CREATE INDEX idx_transactions_merchant ON finance.transactions(merchant_id)
    WHERE merchant_id IS NOT NULL;
CREATE INDEX idx_transactions_transfer_group ON finance.transactions(transfer_group_id)
    WHERE transfer_group_id IS NOT NULL;
CREATE INDEX idx_transactions_reversed_by ON finance.transactions(reversed_by_transaction_id)
    WHERE reversed_by_transaction_id IS NOT NULL;
CREATE INDEX idx_transactions_kind ON finance.transactions(kind);

COMMENT ON TABLE finance.transactions IS
    'Transaction envelopes. Metadata mutable; entries beneath are append-only. §2.4.';
COMMENT ON COLUMN finance.transactions.merchant_id IS
    'Plain BIGINT for now. FK to finance.merchants added in Patch C (SYS-0077+).';

-- ─────────────────────────────────────────────────────────────────────────────
-- 5. finance.entries — the ledger, append-only (§2.1, §14.2)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE finance.entries (
    id                    BIGSERIAL PRIMARY KEY,
    transaction_id        BIGINT NOT NULL REFERENCES finance.transactions(id),
    account_id            BIGINT NOT NULL REFERENCES finance.accounts(id),
    entity_id             BIGINT NOT NULL REFERENCES finance.entities(id) DEFAULT 1,
    amount_minor          BIGINT NOT NULL,
    entry_date            DATE NOT NULL,
    tax_treatment         TEXT,
    reversed_by_entry_id  BIGINT REFERENCES finance.entries(id),
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_entries_transaction ON finance.entries(transaction_id);
CREATE INDEX idx_entries_account_date ON finance.entries(account_id, entry_date);
CREATE INDEX idx_entries_entity ON finance.entries(entity_id);
CREATE INDEX idx_entries_account_live ON finance.entries(account_id)
    WHERE reversed_by_entry_id IS NULL;
CREATE INDEX idx_entries_reversed_by ON finance.entries(reversed_by_entry_id)
    WHERE reversed_by_entry_id IS NOT NULL;

COMMENT ON TABLE finance.entries IS
    'Append-only ledger entries. Integer cents. Every transaction_id must sum to 0. §2.1, §2.2.';

-- ─────────────────────────────────────────────────────────────────────────────
-- 6. finance.source_observations — raw CSV row layer (§2.3, §14.3)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE finance.source_observations (
    id                              BIGSERIAL PRIMARY KEY,
    import_id                       BIGINT NOT NULL REFERENCES finance.imports(id),
    account_id                      BIGINT NOT NULL REFERENCES finance.accounts(id),
    bank_transaction_id             TEXT,
    posted_date                     DATE NOT NULL,
    effective_date                  DATE,
    amount_minor                    BIGINT NOT NULL,
    raw_description                 TEXT NOT NULL,
    normalized_description          TEXT NOT NULL,
    dedup_normalized_description    TEXT NOT NULL,
    source_running_balance_minor    BIGINT,
    row_order                       INTEGER,
    raw_row                         JSONB NOT NULL,
    exact_fingerprint               TEXT NOT NULL,
    coarse_fingerprint              TEXT NOT NULL,
    matched_transaction_id          BIGINT REFERENCES finance.transactions(id),
    matched_observation_id          BIGINT REFERENCES finance.source_observations(id),
    status                          finance.observation_status NOT NULL DEFAULT 'new',
    match_method                    TEXT,
    match_score                     INTEGER,
    match_margin                    INTEGER,
    created_at                      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_obs_account_date ON finance.source_observations(account_id, posted_date);
CREATE INDEX idx_obs_exact_fp ON finance.source_observations(exact_fingerprint);
CREATE INDEX idx_obs_coarse_fp ON finance.source_observations(coarse_fingerprint);
CREATE INDEX idx_obs_bank_txn_id ON finance.source_observations(bank_transaction_id)
    WHERE bank_transaction_id IS NOT NULL;
CREATE INDEX idx_obs_import ON finance.source_observations(import_id);
CREATE INDEX idx_obs_matched_txn ON finance.source_observations(matched_transaction_id)
    WHERE matched_transaction_id IS NOT NULL;
CREATE INDEX idx_obs_status ON finance.source_observations(status);

COMMENT ON TABLE finance.source_observations IS
    'Immutable raw CSV row layer. Every import row lands here unconditionally. §2.3.';

-- ─────────────────────────────────────────────────────────────────────────────
-- 7. Deferred balance constraint trigger (§2.5)
--    Enforces SUM(amount_minor) = 0 per transaction_id at COMMIT time.
--    Deferred so multi-entry transactions can be inserted row-by-row.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION finance.tg_entries_enforce_balance()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    target_txn BIGINT;
    imbalance  BIGINT;
BEGIN
    IF TG_OP = 'DELETE' THEN
        target_txn := OLD.transaction_id;
    ELSE
        target_txn := NEW.transaction_id;
    END IF;

    SELECT COALESCE(SUM(amount_minor), 0)
      INTO imbalance
      FROM finance.entries
     WHERE transaction_id = target_txn;

    IF imbalance <> 0 THEN
        RAISE EXCEPTION
            'Transaction % is unbalanced: sum(amount_minor) = % (must be 0)',
            target_txn, imbalance;
    END IF;

    RETURN NULL;
END;
$$;

CREATE CONSTRAINT TRIGGER entries_enforce_balance
    AFTER INSERT OR UPDATE OR DELETE ON finance.entries
    DEFERRABLE INITIALLY DEFERRED
    FOR EACH ROW
    EXECUTE FUNCTION finance.tg_entries_enforce_balance();

COMMENT ON FUNCTION finance.tg_entries_enforce_balance() IS
    'Deferred: fires at COMMIT. Rejects any transaction whose entries do not sum to zero. §2.5.';

COMMIT;
