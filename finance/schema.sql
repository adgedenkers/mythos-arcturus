-- Mythos Finance Schema v2
-- PostgreSQL database schema for multi-bank transaction management
-- Location: /opt/mythos/finance/schema.sql

-- ============================================================
-- ACCOUNTS - Track all bank accounts
-- ============================================================
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    bank_name VARCHAR(100) NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    account_number VARCHAR(50),
    account_type VARCHAR(50) DEFAULT 'checking',
    is_active BOOLEAN DEFAULT true,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TRANSACTIONS - Main transaction storage
-- ============================================================
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    
    -- Core transaction data
    transaction_date DATE NOT NULL,
    post_date DATE,
    description TEXT NOT NULL,
    original_description TEXT,
    merchant_name VARCHAR(255),
    
    -- Amounts
    amount DECIMAL(12,2) NOT NULL,
    balance DECIMAL(12,2),
    
    -- Categorization
    category_primary VARCHAR(100),
    category_secondary VARCHAR(100),
    transaction_type VARCHAR(50), -- debit, credit, transfer, fee
    
    -- Status
    is_pending BOOLEAN DEFAULT false,
    is_recurring BOOLEAN DEFAULT false,
    
    -- Deduplication
    bank_transaction_id VARCHAR(100),
    hash_id VARCHAR(64) NOT NULL,
    
    -- Metadata
    source_file VARCHAR(255),
    imported_by VARCHAR(100) DEFAULT 'system',
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure no duplicates
    UNIQUE(hash_id)
);

-- ============================================================
-- IMPORT_LOGS - Track all imports
-- ============================================================
CREATE TABLE IF NOT EXISTS import_logs (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    source_file VARCHAR(255) NOT NULL,
    file_path TEXT,
    
    -- Stats
    total_rows INTEGER,
    imported_count INTEGER,
    skipped_count INTEGER,
    error_count INTEGER,
    
    -- Date range of transactions
    date_range_start DATE,
    date_range_end DATE,
    
    -- Metadata
    imported_by VARCHAR(100) DEFAULT 'system',
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- ============================================================
-- CATEGORY_MAPPINGS - Auto-categorization rules
-- ============================================================
CREATE TABLE IF NOT EXISTS category_mappings (
    id SERIAL PRIMARY KEY,
    pattern VARCHAR(255) NOT NULL,
    pattern_type VARCHAR(20) DEFAULT 'contains', -- contains, starts_with, regex
    category_primary VARCHAR(100) NOT NULL,
    category_secondary VARCHAR(100),
    merchant_name VARCHAR(255),
    priority INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- RECURRING_BILLS - Track expected recurring transactions
-- ============================================================
CREATE TABLE IF NOT EXISTS recurring_bills (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    merchant_name VARCHAR(255) NOT NULL,
    expected_amount DECIMAL(12,2),
    amount_variance DECIMAL(12,2) DEFAULT 5.00,
    frequency VARCHAR(20) DEFAULT 'monthly', -- monthly, weekly, biweekly, annual
    expected_day INTEGER, -- day of month (1-31)
    category_primary VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_hash ON transactions(hash_id);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_primary);
CREATE INDEX IF NOT EXISTS idx_transactions_merchant ON transactions(merchant_name);
CREATE INDEX IF NOT EXISTS idx_category_mappings_pattern ON category_mappings(pattern);

-- ============================================================
-- DEFAULT ACCOUNTS
-- ============================================================
INSERT INTO accounts (id, bank_name, account_name, account_type) VALUES
(1, 'Sunmark', 'Primary Checking', 'checking'),
(2, 'USAA', 'Simple Checking', 'checking')
ON CONFLICT DO NOTHING;

-- Reset sequence to avoid conflicts
SELECT setval('accounts_id_seq', (SELECT MAX(id) FROM accounts));

-- ============================================================
-- DEFAULT CATEGORY MAPPINGS
-- ============================================================
INSERT INTO category_mappings (pattern, pattern_type, category_primary, merchant_name, priority) VALUES
-- Utilities
('NATIONAL GRID', 'contains', 'Utilities', 'National Grid', 100),
('NYSEG', 'contains', 'Utilities', 'NYSEG', 100),
('Spectrum', 'contains', 'Utilities', 'Spectrum', 100),
('Starlink', 'contains', 'Internet', 'Starlink', 100),
('VERIZON', 'contains', 'Phone', 'Verizon', 100),

-- Subscriptions
('NETFLIX', 'contains', 'Entertainment', 'Netflix', 100),
('SPOTIFY', 'contains', 'Entertainment', 'Spotify', 100),
('AMAZON PRIME', 'contains', 'Subscriptions', 'Amazon Prime', 100),
('AMZN Digital', 'contains', 'Entertainment', 'Amazon Digital', 100),
('Google One', 'contains', 'Subscriptions', 'Google One', 100),
('APPLE.COM/BILL', 'contains', 'Subscriptions', 'Apple', 100),
('Disney Plus', 'contains', 'Entertainment', 'Disney+', 100),
('HULU', 'contains', 'Entertainment', 'Hulu', 100),
('HBO MAX', 'contains', 'Entertainment', 'HBO Max', 100),
('PARAMOUNT+', 'contains', 'Entertainment', 'Paramount+', 100),
('WMT PLUS', 'contains', 'Subscriptions', 'Walmart+', 100),

-- Groceries
('WALMART', 'contains', 'Groceries', 'Walmart', 90),
('PRICE CHOPPER', 'contains', 'Groceries', 'Price Chopper', 100),
('ALDI', 'contains', 'Groceries', 'Aldi', 100),
('COSTCO', 'contains', 'Groceries', 'Costco', 100),
('TARGET', 'contains', 'Shopping', 'Target', 90),
('HANNAFORD', 'contains', 'Groceries', 'Hannaford', 100),

-- Fast Food & Restaurants
('MCDONALD', 'contains', 'Fast Food', 'McDonalds', 100),
('BURGER KING', 'contains', 'Fast Food', 'Burger King', 100),
('WENDYS', 'contains', 'Fast Food', 'Wendys', 100),
('TACO BELL', 'contains', 'Fast Food', 'Taco Bell', 100),
('CHIPOTLE', 'contains', 'Fast Food', 'Chipotle', 100),
('DUNKIN', 'contains', 'Fast Food', 'Dunkin', 100),
('STARBUCKS', 'contains', 'Fast Food', 'Starbucks', 100),
('PIZZA HUT', 'contains', 'Fast Food', 'Pizza Hut', 100),
('DOMINOS', 'contains', 'Fast Food', 'Dominos', 100),
('SUBWAY', 'contains', 'Fast Food', 'Subway', 100),

-- Gas
('SPEEDWAY', 'contains', 'Gas', 'Speedway', 100),
('SUNOCO', 'contains', 'Gas', 'Sunoco', 100),
('SHELL', 'contains', 'Gas', 'Shell', 100),
('EXXON', 'contains', 'Gas', 'Exxon', 100),
('MOBIL', 'contains', 'Gas', 'Mobil', 100),
('STEWARTS', 'contains', 'Gas', 'Stewarts', 100),
('CUMBERLAND FARMS', 'contains', 'Gas', 'Cumberland Farms', 100),

-- Healthcare
('CVS', 'contains', 'Healthcare', 'CVS', 100),
('WALGREENS', 'contains', 'Healthcare', 'Walgreens', 100),
('Chiropr', 'contains', 'Healthcare', 'Chiropractor', 100),

-- Income
('SSA  TREAS', 'contains', 'Income', 'Social Security', 200),
('DIRECT DEP', 'contains', 'Income', 'Direct Deposit', 150),
('PAYROLL', 'contains', 'Income', 'Payroll', 150),
('INTEREST PAID', 'contains', 'Interest Income', NULL, 100),

-- Transfers
('TRANSFER', 'contains', 'Transfer', NULL, 50),
('XFER', 'contains', 'Transfer', NULL, 50),

-- Fees
('OVERDRAFT', 'contains', 'Bank Fees', 'Overdraft Fee', 200),
('NSF FEE', 'contains', 'Bank Fees', 'NSF Fee', 200),
('SERVICE CHARGE', 'contains', 'Bank Fees', 'Service Charge', 100),
('ATM FEE', 'contains', 'Bank Fees', 'ATM Fee', 100)

ON CONFLICT DO NOTHING;

-- ============================================================
-- HELPER FUNCTIONS
-- ============================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
DROP TRIGGER IF EXISTS update_accounts_updated_at ON accounts;
CREATE TRIGGER update_accounts_updated_at
    BEFORE UPDATE ON accounts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_transactions_updated_at ON transactions;
CREATE TRIGGER update_transactions_updated_at
    BEFORE UPDATE ON transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
