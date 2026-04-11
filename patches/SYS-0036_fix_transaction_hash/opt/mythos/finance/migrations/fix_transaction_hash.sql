-- SYS-DRAFT: Add file-level dedup to import_logs
-- Adds file_hash column so we can detect re-imports of the same file

-- Add file content hash column
ALTER TABLE import_logs ADD COLUMN IF NOT EXISTS file_hash VARCHAR(64);

-- Add unique constraint: same file content for same account = already imported
-- (We don't make it globally unique because the same file might theoretically
-- be valid for different accounts, though that's unlikely)
CREATE UNIQUE INDEX IF NOT EXISTS idx_import_logs_file_hash
    ON import_logs(account_id, file_hash);

-- Drop the old hash_id unique constraint on transactions
-- We're replacing transaction-level dedup with file-level dedup
-- But we keep the index for lookups
ALTER TABLE transactions DROP CONSTRAINT IF EXISTS transactions_hash_id_key;

-- Recreate as non-unique index (keep for query performance)
-- The existing idx_transactions_hash may already cover this
-- DROP INDEX IF EXISTS idx_transactions_hash;
-- CREATE INDEX IF NOT EXISTS idx_transactions_hash ON transactions(hash_id);
