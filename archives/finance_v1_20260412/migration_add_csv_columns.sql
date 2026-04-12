-- Mythos Finance Schema Migration
-- Adds columns needed for CSV import while preserving existing Plaid schema
-- Run: psql -d mythos -f migration_add_csv_columns.sql

-- ============================================================
-- ACCOUNTS TABLE - Add missing columns
-- ============================================================

-- Add bank_name (map from institution_name via institutions table for existing)
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS bank_name character varying(100);

-- Add account_name (can use existing 'name' column, but add for compatibility)
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS account_name character varying(255);

-- Add account_number (can use existing 'mask' for display, but add full number)
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS account_number character varying(50);

-- Add notes
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS notes text;

-- Populate bank_name from name if empty
UPDATE accounts SET bank_name = name WHERE bank_name IS NULL AND name IS NOT NULL;
UPDATE accounts SET account_name = official_name WHERE account_name IS NULL AND official_name IS NOT NULL;
UPDATE accounts SET account_name = name WHERE account_name IS NULL AND name IS NOT NULL;

-- ============================================================
-- TRANSACTIONS TABLE - Add columns for CSV import
-- ============================================================

-- Core description fields (existing has 'name', we need 'description')
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS description text;
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS original_description text;

-- Balance tracking
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS balance numeric(12,2);

-- Category fields (existing has 'primary_category', add standardized ones)
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS category_primary character varying(100);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS category_secondary character varying(100);

-- Deduplication
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS bank_transaction_id character varying(100);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS hash_id character varying(64);

-- Import tracking
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS source_file character varying(255);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS imported_by character varying(100);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP;

-- Populate description from name if empty
UPDATE transactions SET description = name WHERE description IS NULL AND name IS NOT NULL;
UPDATE transactions SET original_description = name WHERE original_description IS NULL AND name IS NOT NULL;

-- Populate category_primary from primary_category if empty
UPDATE transactions SET category_primary = primary_category WHERE category_primary IS NULL AND primary_category IS NOT NULL;

-- Populate bank_transaction_id from plaid_transaction_id if empty
UPDATE transactions SET bank_transaction_id = plaid_transaction_id WHERE bank_transaction_id IS NULL AND plaid_transaction_id IS NOT NULL;

-- Create hash_id for existing transactions that don't have one
UPDATE transactions 
SET hash_id = encode(sha256(
    (COALESCE(account_id::text, '') || '|' || 
     COALESCE(transaction_date::text, '') || '|' || 
     COALESCE(amount::text, '') || '|' || 
     COALESCE(name, ''))::bytea
), 'hex')
WHERE hash_id IS NULL;

-- ============================================================
-- INDEXES for new columns
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_transactions_hash ON transactions(hash_id);
CREATE INDEX IF NOT EXISTS idx_transactions_source ON transactions(source_file);

-- ============================================================
-- UNIQUE CONSTRAINT on hash_id (for deduplication)
-- ============================================================

-- First ensure no duplicates exist
-- If this fails, you have duplicate hashes to resolve
DO $$
BEGIN
    -- Try to add unique constraint
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'transactions_hash_id_key'
    ) THEN
        ALTER TABLE transactions ADD CONSTRAINT transactions_hash_id_key UNIQUE (hash_id);
    END IF;
EXCEPTION WHEN others THEN
    RAISE NOTICE 'Could not add unique constraint on hash_id - may have duplicates';
END $$;

-- ============================================================
-- INSERT DEFAULT ACCOUNTS for CSV import (if not exists)
-- ============================================================

-- Sunmark - ID 1
INSERT INTO accounts (id, bank_name, account_name, account_type, is_active)
VALUES (1, 'Sunmark', 'Primary Checking', 'checking', true)
ON CONFLICT (id) DO UPDATE SET 
    bank_name = COALESCE(accounts.bank_name, EXCLUDED.bank_name),
    account_name = COALESCE(accounts.account_name, EXCLUDED.account_name);

-- USAA - ID 2  
INSERT INTO accounts (id, bank_name, account_name, account_type, is_active)
VALUES (2, 'USAA', 'Simple Checking', 'checking', true)
ON CONFLICT (id) DO UPDATE SET 
    bank_name = COALESCE(accounts.bank_name, EXCLUDED.bank_name),
    account_name = COALESCE(accounts.account_name, EXCLUDED.account_name);

-- Reset sequence
SELECT setval('accounts_id_seq', GREATEST((SELECT MAX(id) FROM accounts), 2));

-- ============================================================
-- VERIFY
-- ============================================================

DO $$
DECLARE
    col_count integer;
BEGIN
    SELECT COUNT(*) INTO col_count
    FROM information_schema.columns 
    WHERE table_name = 'transactions' 
    AND column_name IN ('description', 'hash_id', 'source_file', 'category_primary');
    
    IF col_count = 4 THEN
        RAISE NOTICE '✓ Migration successful - all required columns present';
    ELSE
        RAISE NOTICE '⚠ Migration incomplete - only % of 4 required columns found', col_count;
    END IF;
END $$;
