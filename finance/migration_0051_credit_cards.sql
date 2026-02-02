-- Migration 0051: Add credit card accounts and balances tracking
-- Run with: sudo -u postgres psql -d mythos -f migration_0051_credit_cards.sql

BEGIN;

-- ============================================================
-- 1. ADD CURRENT_BALANCE TO ACCOUNTS TABLE (if not exists)
-- ============================================================
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS current_balance NUMERIC(12,2) DEFAULT 0;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS balance_updated_at TIMESTAMP;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS credit_limit NUMERIC(12,2);
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS min_payment NUMERIC(12,2);
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS payment_due_day INTEGER;

-- ============================================================
-- 2. ADD CREDIT CARD ACCOUNTS
-- ============================================================
INSERT INTO accounts (bank_name, account_name, account_type, abbreviation, current_balance, credit_limit, min_payment, payment_due_day, notes, is_active)
VALUES 
    ('L.L.Bean', 'Mastercard', 'credit', 'LLBEAN', -8423.34, 14650.00, 308.00, 12, 'Rebecca login', true),
    ('Tractor Supply', 'Credit Card', 'credit', 'TSC', -2411.14, 10250.00, 0.00, 12, 'Rebecca login', true),
    ('Old Navy', 'Barclaycard', 'credit', 'OLDNAVY', -6125.72, 6800.00, 59.33, 12, 'rdenkers login', true),
    ('TJX Rewards', 'Mastercard', 'credit', 'TJX', -1.99, 2700.00, 0.00, 18, 'rdenkers login', true),
    ('American Express', 'Blue Cash', 'credit', 'AMEX', -870.83, 1000.00, 0.00, 27, 'Adge card - paid current', true)
ON CONFLICT DO NOTHING;

-- ============================================================
-- 3. UPDATE EXISTING ACCOUNT BALANCES
-- ============================================================
UPDATE accounts SET current_balance = 976.47, balance_updated_at = NOW() WHERE abbreviation = 'SUN';
UPDATE accounts SET current_balance = 1431.65, balance_updated_at = NOW() WHERE abbreviation = 'USAA';
UPDATE accounts SET current_balance = 2086.00, balance_updated_at = NOW() WHERE abbreviation = 'SID';
UPDATE accounts SET current_balance = 7000.00, balance_updated_at = NOW() WHERE abbreviation = 'NBT';
UPDATE accounts SET current_balance = 758.00, balance_updated_at = NOW() WHERE abbreviation = 'DVA';

-- ============================================================
-- 4. ADD USAA LOAN AS DEBT ACCOUNT
-- ============================================================
INSERT INTO accounts (bank_name, account_name, account_type, abbreviation, current_balance, min_payment, payment_due_day, notes, is_active)
VALUES 
    ('USAA', 'Personal Loan', 'loan', 'USAALOAN', -3531.31, 0.00, 13, 'Paid ahead - autopay on', true)
ON CONFLICT DO NOTHING;

COMMIT;

-- Show results
\echo ''
\echo '=== UPDATED ACCOUNTS ==='
SELECT abbreviation, bank_name, account_name, account_type, current_balance, credit_limit, min_payment, payment_due_day 
FROM accounts 
ORDER BY account_type, bank_name;
