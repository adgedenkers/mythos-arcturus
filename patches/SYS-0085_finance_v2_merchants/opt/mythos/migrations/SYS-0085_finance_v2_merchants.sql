-- =============================================================================
-- SYS-0085: Finance v2 Patch D — Merchants & Patterns (re-land)
-- =============================================================================
-- Letter:  D (Finance v2 locked sequence)
-- Stream:  SYS
-- Type:    MINOR (new schema objects, FK on existing transactions)
-- Blast:   HIGH (schema change, Phase 2.5 required)
--
-- SYS-0083 RE-LAND — schema is byte-identical to SYS-0083 (Castor R1+R2
-- cleared). The ONLY change is removal of `SAVEPOINT verify_start` and
-- `ROLLBACK TO SAVEPOINT verify_start` from the inline DO block: PL/pgSQL
-- anonymous DO blocks are not transaction contexts and cannot use SAVEPOINT
-- or ROLLBACK TO SAVEPOINT. The positive CASCADE test already deletes the
-- test transaction and merchant rows explicitly, so no additional cleanup
-- is needed — the tables exit the DO block empty naturally.
--
-- Reviewed by Castor (Gemini) — round 1 (finance review), round 2 (3-question
-- pre-build consultation), round 3 (inline DO block pattern clearance). All
-- revisions incorporated:
--
--   R1.1  ON DELETE RESTRICT on transactions.merchant_id (was SET NULL)
--   R1.2  CHECK (confidence BETWEEN 0 AND 100) on merchant_patterns
--   R1.3  UNIQUE (merchant_id, pattern, pattern_type) on merchant_patterns
--   R1.4  finance.normalize_merchant_name() function + trigger on merchants
--         (single source of truth; importer must call via SELECT)
--   R2.1  ON DELETE CASCADE on merchant_patterns.merchant_id
--   R2.2  No last_matched_*_id column (deferred to Patch E — FK target
--         undecided, observations vs transactions)
--   R2.3  Inline DO block verification (adopted as Finance v2 schema-patch
--         default) — SYS-0085 implements this without SAVEPOINT/ROLLBACK
--         since DO blocks don't support them.
--
-- Depends on: Patch A (SYS-0075, finance schema + accounts), Patch B
--             (SYS-0076, transactions table)
-- =============================================================================

\set ON_ERROR_STOP on

BEGIN;

-- =============================================================================
-- 1. Enum: pattern_type
-- =============================================================================

CREATE TYPE finance.pattern_type AS ENUM ('exact', 'contains', 'regex');

-- =============================================================================
-- 2. Normalization function — single source of truth
-- =============================================================================
-- IMMUTABLE so it can be used in indexed expressions and generated columns
-- if we ever need that. STRICT so NULL input returns NULL (belt-and-suspenders
-- — the NOT NULL constraint on canonical_name should catch this first).
--
-- Normalization rules:
--   1. lowercase
--   2. collapse all whitespace runs (spaces, tabs, newlines, NBSP U+00A0)
--      to a single ASCII space
--   3. trim leading and trailing whitespace
--
-- Castor R1.4: the Python importer MUST call this function via SELECT, never
-- reimplement the logic in Python. That guarantees parity.

CREATE OR REPLACE FUNCTION finance.normalize_merchant_name(raw TEXT)
RETURNS TEXT
LANGUAGE sql
IMMUTABLE
STRICT
AS $$
    SELECT trim(regexp_replace(lower(raw), E'[[:space:]\u00A0]+', ' ', 'g'))
$$;

-- =============================================================================
-- 3. merchants table
-- =============================================================================

CREATE TABLE finance.merchants (
    id                          BIGSERIAL PRIMARY KEY,
    canonical_name              TEXT NOT NULL,
    display_name                TEXT,
    default_category_account_id BIGINT REFERENCES finance.accounts(id),
    default_tax_treatment       TEXT,
    normalized_name_key         TEXT NOT NULL UNIQUE,
    metadata                    JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE finance.merchants IS
    'Canonical merchant registry. normalized_name_key is auto-derived from '
    'canonical_name by the merchants_derive_normalized_key trigger — never '
    'set it manually. The Python importer must call '
    'finance.normalize_merchant_name() via SELECT, never reimplement the '
    'logic in Python (Castor R1.4).';

-- Trigger: auto-derive normalized_name_key on INSERT/UPDATE.
-- This is the structural guarantee that importer and DB cannot drift.
-- Even if the importer computes its own key and includes it in the INSERT,
-- the trigger overwrites it with the canonical form.

CREATE OR REPLACE FUNCTION finance.merchants_derive_normalized_key()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.normalized_name_key := finance.normalize_merchant_name(NEW.canonical_name);
    RETURN NEW;
END;
$$;

CREATE TRIGGER merchants_derive_normalized_key
    BEFORE INSERT OR UPDATE OF canonical_name
    ON finance.merchants
    FOR EACH ROW
    EXECUTE FUNCTION finance.merchants_derive_normalized_key();

-- =============================================================================
-- 4. merchant_patterns table
-- =============================================================================

CREATE TABLE finance.merchant_patterns (
    id                  BIGSERIAL PRIMARY KEY,
    pattern             TEXT NOT NULL,
    pattern_type        finance.pattern_type NOT NULL,
    merchant_id         BIGINT NOT NULL
                        REFERENCES finance.merchants(id)
                        ON DELETE CASCADE,
    priority            INTEGER NOT NULL DEFAULT 100,
    confidence          INTEGER NOT NULL DEFAULT 100
                        CHECK (confidence BETWEEN 0 AND 100),
    match_count         INTEGER NOT NULL DEFAULT 0 CHECK (match_count >= 0),
    last_matched_at     TIMESTAMPTZ,
    is_active           BOOLEAN NOT NULL DEFAULT true,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Castor R1.3: prevent duplicate pattern rows per merchant.
    CONSTRAINT merchant_patterns_unique_per_merchant
        UNIQUE (merchant_id, pattern, pattern_type)
);

COMMENT ON TABLE finance.merchant_patterns IS
    'Raw CSV description → merchant resolution patterns. ON DELETE CASCADE '
    'because patterns are functional dependencies of their merchant, not '
    'historical evidence (Castor R2.1). confidence is 0-100 inclusive '
    '(Castor R1.2). (merchant_id, pattern, pattern_type) is unique to '
    'prevent non-deterministic matching in the importer (Castor R1.3).';

-- Indexes
CREATE INDEX merchant_patterns_type_priority_idx
    ON finance.merchant_patterns (pattern_type, priority DESC);

CREATE INDEX merchant_patterns_merchant_id_idx
    ON finance.merchant_patterns (merchant_id);

CREATE INDEX merchant_patterns_active_idx
    ON finance.merchant_patterns (is_active)
    WHERE is_active;

-- =============================================================================
-- 5. Foreign key on transactions.merchant_id
-- =============================================================================
-- Patch B left this column as an unconstrained BIGINT. Now that merchants
-- exists, we add the FK with ON DELETE RESTRICT (Castor R1.1) — deleting a
-- merchant requires an explicit MERGE operation to reassign transactions
-- first. This prevents metadata-destructive deletes.

ALTER TABLE finance.transactions
    ADD CONSTRAINT transactions_merchant_id_fkey
    FOREIGN KEY (merchant_id)
    REFERENCES finance.merchants(id)
    ON DELETE RESTRICT;

-- =============================================================================
-- 6. Inline verification — DO block (no SAVEPOINT, no ROLLBACK)
-- =============================================================================
-- PL/pgSQL anonymous DO blocks are not transaction contexts — SAVEPOINT and
-- ROLLBACK TO SAVEPOINT are not permitted. The test flow below creates one
-- merchant + one pattern + one transaction, runs four negative sub-block
-- tests, then explicitly deletes the transaction and the merchant (which
-- CASCADEs to its patterns). The tables exit the DO block empty.
--
-- Each negative test is wrapped in its own `BEGIN ... EXCEPTION WHEN <err>
-- ... END` sub-block so an expected failure doesn't abort the outer block.

DO $verify$
DECLARE
    v_merchant_id    BIGINT;
    v_txn_id         BIGINT;
    v_err_caught     BOOLEAN;
BEGIN
    RAISE NOTICE 'SYS-0085 inline verification starting...';

    -- ----- POSITIVE TEST: full happy path -----

    -- Insert a merchant with a deliberately messy canonical_name to prove
    -- the normalization trigger fires.
    INSERT INTO finance.merchants (canonical_name)
    VALUES ('  Walmart   SUPERCENTER  ')
    RETURNING id INTO v_merchant_id;

    -- Verify trigger normalized the key.
    PERFORM 1
    FROM finance.merchants
    WHERE id = v_merchant_id
      AND normalized_name_key = 'walmart supercenter';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'POSITIVE TEST FAILED: normalization trigger did not '
            'produce expected key for merchant id %', v_merchant_id;
    END IF;
    RAISE NOTICE '  ✓ normalization trigger fires and produces expected key';

    -- Insert a valid pattern.
    INSERT INTO finance.merchant_patterns
        (pattern, pattern_type, merchant_id, priority, confidence)
    VALUES ('WM SUPERCENTER', 'contains', v_merchant_id, 100, 95);
    RAISE NOTICE '  ✓ valid pattern insert succeeds';

    -- Insert a transaction referencing the merchant.
    INSERT INTO finance.transactions
        (description, merchant_id, kind, posted_date)
    VALUES ('test txn for SYS-0085 verification', v_merchant_id,
            'manual', CURRENT_DATE)
    RETURNING id INTO v_txn_id;
    RAISE NOTICE '  ✓ transaction insert with valid merchant_id succeeds';

    -- ----- NEGATIVE TEST A: FK RESTRICT blocks merchant delete -----
    v_err_caught := false;
    BEGIN
        DELETE FROM finance.merchants WHERE id = v_merchant_id;
    EXCEPTION WHEN foreign_key_violation THEN
        v_err_caught := true;
    END;
    IF NOT v_err_caught THEN
        RAISE EXCEPTION 'NEGATIVE TEST A FAILED: ON DELETE RESTRICT did not '
            'block merchant delete while transaction referenced it';
    END IF;
    RAISE NOTICE '  ✓ ON DELETE RESTRICT blocks merchant delete (R1.1)';

    -- ----- NEGATIVE TEST B: CHECK blocks out-of-range confidence -----
    v_err_caught := false;
    BEGIN
        INSERT INTO finance.merchant_patterns
            (pattern, pattern_type, merchant_id, confidence)
        VALUES ('bogus', 'exact', v_merchant_id, 101);
    EXCEPTION WHEN check_violation THEN
        v_err_caught := true;
    END;
    IF NOT v_err_caught THEN
        RAISE EXCEPTION 'NEGATIVE TEST B FAILED: CHECK constraint did not '
            'reject confidence = 101';
    END IF;
    RAISE NOTICE '  ✓ CHECK (confidence BETWEEN 0 AND 100) enforces (R1.2)';

    -- ----- NEGATIVE TEST C: UNIQUE blocks duplicate pattern -----
    v_err_caught := false;
    BEGIN
        INSERT INTO finance.merchant_patterns
            (pattern, pattern_type, merchant_id)
        VALUES ('WM SUPERCENTER', 'contains', v_merchant_id);
    EXCEPTION WHEN unique_violation THEN
        v_err_caught := true;
    END;
    IF NOT v_err_caught THEN
        RAISE EXCEPTION 'NEGATIVE TEST C FAILED: UNIQUE constraint did not '
            'reject duplicate (merchant_id, pattern, pattern_type)';
    END IF;
    RAISE NOTICE '  ✓ UNIQUE (merchant_id, pattern, pattern_type) enforces (R1.3)';

    -- ----- NEGATIVE TEST D: FK blocks bogus merchant_id on transaction -----
    v_err_caught := false;
    BEGIN
        INSERT INTO finance.transactions
            (description, merchant_id, kind, posted_date)
        VALUES ('bogus', 999999999, 'manual', CURRENT_DATE);
    EXCEPTION WHEN foreign_key_violation THEN
        v_err_caught := true;
    END;
    IF NOT v_err_caught THEN
        RAISE EXCEPTION 'NEGATIVE TEST D FAILED: FK did not reject '
            'transaction with nonexistent merchant_id';
    END IF;
    RAISE NOTICE '  ✓ FK on transactions.merchant_id rejects bogus references';

    -- ----- POSITIVE TEST: CASCADE delete of patterns -----
    -- First remove the transaction blocking the merchant delete.
    DELETE FROM finance.transactions WHERE id = v_txn_id;
    -- Now deleting the merchant should cascade to its patterns.
    DELETE FROM finance.merchants WHERE id = v_merchant_id;
    PERFORM 1 FROM finance.merchant_patterns WHERE merchant_id = v_merchant_id;
    IF FOUND THEN
        RAISE EXCEPTION 'POSITIVE TEST FAILED: CASCADE delete left orphan '
            'pattern rows for merchant id %', v_merchant_id;
    END IF;
    RAISE NOTICE '  ✓ ON DELETE CASCADE on merchant_patterns fires (R2.1)';

    -- No SAVEPOINT/ROLLBACK cleanup: the test transaction and merchant were
    -- already deleted above, and merchant_patterns CASCADEd with it. Tables
    -- exit this DO block empty.

    RAISE NOTICE 'SYS-0085 inline verification complete — all 7 checks passed';
END
$verify$;

COMMIT;
