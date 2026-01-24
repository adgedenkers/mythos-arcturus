-- Mythos Finance Schema v3 - Complete
-- PostgreSQL database schema for multi-bank transaction management

-- ============================================================
-- ACCOUNTS - Track all bank accounts
-- ============================================================
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    bank_name VARCHAR(100),
    account_name VARCHAR(255),
    account_number VARCHAR(50),
    account_type VARCHAR(50) DEFAULT 'checking',
    current_balance DECIMAL(12,2),
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
    transaction_date DATE NOT NULL,
    post_date DATE,
    description TEXT NOT NULL,
    original_description TEXT,
    merchant_name VARCHAR(255),
    amount DECIMAL(12,2) NOT NULL,
    balance DECIMAL(12,2),
    category_primary VARCHAR(100),
    category_secondary VARCHAR(100),
    transaction_type VARCHAR(50),
    is_pending BOOLEAN DEFAULT false,
    is_recurring BOOLEAN DEFAULT false,
    bank_transaction_id VARCHAR(100),
    hash_id VARCHAR(64) NOT NULL,
    source_file VARCHAR(255),
    imported_by VARCHAR(100) DEFAULT 'system',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
    total_rows INTEGER,
    imported_count INTEGER,
    skipped_count INTEGER,
    error_count INTEGER,
    date_range_start DATE,
    date_range_end DATE,
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
    pattern_type VARCHAR(20) DEFAULT 'contains',
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
    frequency VARCHAR(20) DEFAULT 'monthly',
    expected_day INTEGER,
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
INSERT INTO accounts (id, bank_name, account_name, account_type, is_active)
VALUES 
    (1, 'Sunmark', 'Primary Checking', 'checking', true),
    (2, 'USAA', 'Simple Checking', 'checking', true)
ON CONFLICT (id) DO UPDATE SET 
    bank_name = COALESCE(accounts.bank_name, EXCLUDED.bank_name),
    account_name = COALESCE(accounts.account_name, EXCLUDED.account_name);

SELECT setval('accounts_id_seq', GREATEST((SELECT MAX(id) FROM accounts), 2));

-- ============================================================
-- CATEGORY MAPPINGS - Complete set
-- ============================================================
INSERT INTO category_mappings (pattern, pattern_type, category_primary, merchant_name, priority) VALUES
-- Income
('DFAS-CLEVELAND', 'contains', 'Income', 'VA Salary', 200),
('SSA TREAS', 'contains', 'Income', 'Social Security', 200),
('SSA  TREAS', 'contains', 'Income', 'Social Security', 200),
('DIRECT DEP', 'contains', 'Income', 'Direct Deposit', 150),
('PAYROLL', 'contains', 'Income', 'Payroll', 150),
('INTEREST PAID', 'contains', 'Interest Income', NULL, 100),
('External Deposit', 'contains', 'Income', NULL, 50),
('Point Of Sale Deposit', 'contains', 'Income', NULL, 40),
('NYSLRS', 'contains', 'Income', 'NYS Pension', 150),
('Mobile Deposit', 'contains', 'Income', 'Mobile Deposit', 100),

-- Utilities
('NATIONAL GRID', 'contains', 'Utilities', 'National Grid', 100),
('NYSEG', 'contains', 'Utilities', 'NYSEG', 100),
('Blueox', 'contains', 'Utilities', 'Blueox Propane', 100),
('BERT ADAMS', 'contains', 'Utilities', 'Bert Adams Disposal', 100),

-- Internet/Phone
('Spectrum', 'contains', 'Utilities', 'Spectrum', 100),
('Starlink', 'contains', 'Internet', 'Starlink', 100),
('VERIZON', 'contains', 'Phone', 'Verizon', 100),
('AT&T', 'contains', 'Bills & Utilities', 'AT&T', 100),
('ATT ', 'contains', 'Bills & Utilities', 'AT&T', 100),

-- Subscriptions
('NETFLIX', 'contains', 'Entertainment', 'Netflix', 100),
('Netflix', 'contains', 'Television', 'Netflix', 100),
('SPOTIFY', 'contains', 'Entertainment', 'Spotify', 100),
('AMAZON PRIME', 'contains', 'Subscriptions', 'Amazon Prime', 100),
('AMZN Digital', 'contains', 'Entertainment', 'Amazon Digital', 100),
('Google One', 'contains', 'Subscriptions', 'Google One', 100),
('APPLE.COM/BILL', 'contains', 'Subscriptions', 'Apple', 100),
('Disney Plus', 'contains', 'Entertainment', 'Disney+', 100),
('DISNEY', 'contains', 'Entertainment', 'Disney+', 100),
('HULU', 'contains', 'Entertainment', 'Hulu', 100),
('HBO MAX', 'contains', 'Entertainment', 'HBO Max', 100),
('PARAMOUNT+', 'contains', 'Entertainment', 'Paramount+', 100),
('WMT PLUS', 'contains', 'Subscriptions', 'Walmart+', 100),
('PEACOCK', 'contains', 'Entertainment', 'Peacock', 100),
('discovery+', 'contains', 'Television', 'Discovery+', 100),
('CLAUDE.AI', 'contains', 'Subscriptions', 'Claude AI', 100),
('OPENAI', 'contains', 'Subscriptions', 'OpenAI', 100),
('ANCESTRY', 'contains', 'Subscriptions', 'Ancestry', 100),
('GODADDY', 'contains', 'Subscriptions', 'GoDaddy', 100),
('ROCKET Money', 'contains', 'Subscriptions', 'Rocket Money', 100),
('OVCIO', 'contains', 'Subscriptions', 'OVCIO', 100),
('JETBRAI', 'contains', 'Subscriptions', 'JetBrains', 100),
('YouTube Premium', 'contains', 'Entertainment', 'YouTube Premium', 100),
('GOOGLE *YOUTUBE', 'contains', 'Entertainment', 'YouTube Premium', 100),
('Prime Video', 'contains', 'Entertainment', 'Amazon Prime Video', 100),
('Microsoft', 'contains', 'Entertainment', 'Microsoft', 100),
('PlayStation', 'contains', 'Entertainment', 'PlayStation', 100),
('Nintendo', 'contains', 'Entertainment', 'Nintendo', 100),
('Notion', 'contains', 'Subscriptions', 'Notion', 100),
('HUGGINGFACE', 'contains', 'Subscriptions', 'HuggingFace', 100),

-- Groceries
('WALMART', 'contains', 'Shopping', 'Walmart', 90),
('WM SUPERCENTER', 'contains', 'Shopping', 'Walmart', 100),
('PRICE CHOPPER', 'contains', 'Groceries', 'Price Chopper', 100),
('ALDI', 'contains', 'Groceries', 'Aldi', 100),
('COSTCO', 'contains', 'Groceries', 'Costco', 100),
('TARGET', 'contains', 'Shopping', 'Target', 90),
('HANNAFORD', 'contains', 'Groceries', 'Hannaford', 100),
('PINE RIDGE GROC', 'contains', 'Groceries', 'Pine Ridge Grocery', 100),

-- Fast Food & Restaurants
('MCDONALD', 'contains', 'Fast Food', 'McDonalds', 100),
('McDonalds', 'contains', 'Fast Food', 'McDonalds', 100),
('BURGER KING', 'contains', 'Fast Food', 'Burger King', 100),
('WENDYS', 'contains', 'Fast Food', 'Wendys', 100),
('Wendy''s', 'contains', 'Fast Food', 'Wendys', 100),
('TACO BELL', 'contains', 'Fast Food', 'Taco Bell', 100),
('CHIPOTLE', 'contains', 'Fast Food', 'Chipotle', 100),
('DUNKIN', 'contains', 'Fast Food', 'Dunkin', 100),
('STARBUCKS', 'contains', 'Fast Food', 'Starbucks', 100),
('PIZZA HUT', 'contains', 'Fast Food', 'Pizza Hut', 100),
('DOMINOS', 'contains', 'Fast Food', 'Dominos', 100),
('SUBWAY', 'contains', 'Fast Food', 'Subway', 100),
('SONIC DRIVE', 'contains', 'Fast Food', 'Sonic', 100),
('SONIC', 'contains', 'Fast Food', 'Sonic', 100),
('FIVE GUYS', 'contains', 'Fast Food', 'Five Guys', 100),
('Jersey Mike', 'contains', 'Fast Food', 'Jersey Mikes', 100),
('CAFFE NERO', 'contains', 'Fast Food', 'Caffe Nero', 100),

-- Restaurants
('APPLEBEES', 'contains', 'Restaurants', 'Applebees', 100),
('SPIEDIE AND RIB', 'contains', 'Restaurants', 'Spiedie & Rib Pit', 100),
('TEXAS ROADHOUSE', 'contains', 'Restaurants', 'Texas Roadhouse', 100),
('RED LOBSTER', 'contains', 'Restaurants', 'Red Lobster', 100),
('CHILIS', 'contains', 'Restaurants', 'Chilis', 100),
('NORWICH BUFFETT', 'contains', 'Restaurants', 'Norwich Buffet', 100),
('ROMA PIZZA', 'contains', 'Restaurants', 'Roma Pizza', 100),
('SEVEN STARS', 'contains', 'Restaurants', 'Seven Stars', 100),
('THE BLACK R', 'contains', 'Restaurants', 'The Black Rose', 100),
('Magros', 'contains', 'Restaurants', 'Magros', 100),
('TST*', 'contains', 'Restaurants', NULL, 80),

-- Gas
('SPEEDWAY', 'contains', 'Gas', 'Speedway', 100),
('SUNOCO', 'contains', 'Gas', 'Sunoco', 100),
('SHELL', 'contains', 'Gas', 'Shell', 100),
('EXXON', 'contains', 'Gas', 'Exxon', 100),
('MOBIL', 'contains', 'Gas', 'Mobil', 100),
('STEWARTS', 'contains', 'Gas', 'Stewarts', 100),
('STEWART''S SHOP', 'contains', 'Gas', 'Stewarts', 100),
('CUMBERLAND FARMS', 'contains', 'Gas', 'Cumberland Farms', 100),
('MIRABITO', 'contains', 'Gas', 'Mirabito', 100),
('CITGO', 'contains', 'Gas', 'Citgo', 100),
('FASTRAC', 'contains', 'Gas', 'Fastrac', 100),
('BYRNE DAIRY', 'contains', 'Gas', 'Byrne Dairy', 100),
('USA Gas', 'contains', 'Gas', 'USA Gas', 100),

-- Healthcare
('CVS', 'contains', 'Healthcare', 'CVS', 100),
('WALGREENS', 'contains', 'Healthcare', 'Walgreens', 100),
('Chiropr', 'contains', 'Healthcare', 'Chiropractor', 100),
('WANSOR-MOSES', 'contains', 'Healthcare', 'Chiropractor', 100),
('NORWICH FAMILY', 'contains', 'Healthcare', 'Norwich Family Health', 100),
('Mass General', 'contains', 'Healthcare', 'Mass General Hospital', 100),
('BARTLES PHARMAC', 'contains', 'Healthcare', 'Bartles Pharmacy', 100),
('Bartles Pharmacy', 'contains', 'Pharmacy', 'Bartles Pharmacy', 100),

-- Shopping
('AMAZON', 'contains', 'Shopping', 'Amazon', 80),
('AMAZON.COM', 'contains', 'Shopping', 'Amazon', 90),
('SAMS CLUB', 'contains', 'Shopping', 'Sams Club', 100),
('SAMSCLUB', 'contains', 'Shopping', 'Sams Club', 100),
('TRACTOR SUPPLY', 'contains', 'Shopping', 'Tractor Supply', 100),
('DOLLAR GENERAL', 'contains', 'Shopping', 'Dollar General', 100),
('DOLLAR TREE', 'contains', 'Shopping', 'Dollar Tree', 100),
('ETSY', 'contains', 'Shopping', 'Etsy', 100),
('IKEA', 'contains', 'Shopping', 'IKEA', 100),
('HOMEGOODS', 'contains', 'Shopping', 'HomeGoods', 100),
('Marshalls', 'contains', 'Shopping', 'Marshalls', 100),
('T J MAXX', 'contains', 'Shopping', 'TJ Maxx', 100),
('TJ Maxx', 'contains', 'Shopping', 'TJ Maxx', 100),
('BARNESNOBLE', 'contains', 'Books', 'Barnes & Noble', 100),
('Barnes & Noble', 'contains', 'Books', 'Barnes & Noble', 100),
('ZAPPOS', 'contains', 'Shopping', 'Zappos', 100),
('Harbor Freight', 'contains', 'Shopping', 'Harbor Freight', 100),
('SALLY BEAUTY', 'contains', 'Shopping', 'Sally Beauty', 100),
('BLOOM DESIGNS', 'contains', 'Shopping', 'Bloom Designs', 100),
('SACRED BLOOM', 'contains', 'Shopping', 'Sacred Bloom', 100),
('HILLSTOHOME', 'contains', 'Shopping', 'Hills to Home Pet Food', 100),
('PETSTREETST', 'contains', 'Shopping', 'Pet Street', 100),
('THE NEW 5&10', 'contains', 'Shopping', 'The New 5&10', 100),
('BJSWHOL', 'contains', 'Shopping', 'BJs Wholesale', 100),
('Boot Barn', 'contains', 'Clothing', 'Boot Barn', 100),
('LOFT', 'contains', 'Clothing', 'Loft', 100),
('Shoe Carnival', 'contains', 'Clothing', 'Shoe Carnival', 100),
('SQ *', 'contains', 'Shopping', NULL, 80),
('PAYPAL', 'contains', 'Shopping', 'PayPal', 60),
('Jostens', 'contains', 'Shopping', 'Jostens', 100),
('Ticketmaster', 'contains', 'Entertainment', 'Ticketmaster', 100),
('SeatGeek', 'contains', 'Entertainment', 'SeatGeek', 100),
('Regal', 'contains', 'Movies & Dvds', 'Regal Cinemas', 90),
('REGAL', 'contains', 'Movies & Dvds', 'Regal Cinemas', 90),
('Dick''s Warehouse', 'contains', 'Sporting Goods', 'Dicks', 100),
('Bloomingdale', 'contains', 'Shopping', 'Bloomingdales', 100),

-- Home Improvement
('LOWE''S', 'contains', 'Home Improvement', 'Lowes', 100),
('HOME DEP', 'contains', 'Home Improvement', 'Home Depot', 100),
('NST THE HOME DE', 'contains', 'Home Improvement', 'Home Depot', 100),
('Auchinachie', 'contains', 'Home Improvement', 'Auchinachie Services', 100),
('CANAL STREET HARDWARE', 'contains', 'Home Improvement', 'Canal Street Hardware', 100),
('Ocooch Hardwoods', 'contains', 'Home', 'Ocooch Hardwoods', 100),

-- Travel
('DOUBLETREE', 'contains', 'Travel', 'DoubleTree Hotel', 100),
('EXPEDIA', 'contains', 'Travel', 'Expedia', 100),

-- Personal Care
('BEAUTY NAILS', 'contains', 'Personal Care', 'Beauty Nails', 100),
('WIWI', 'contains', 'Personal Care', 'Nails', 100),
('Vestal Nails', 'contains', 'Personal Care', 'Vestal Nails', 100),

-- Transfers
('TRANSFER', 'contains', 'Transfer', NULL, 50),
('XFER', 'contains', 'Transfer', NULL, 50),
('AMEX EPAYMENT', 'contains', 'Transfer', 'AMEX Payment', 100),
('External Withdrawal', 'contains', 'Transfer', NULL, 50),
('Internet Transfer', 'contains', 'Transfer', 'Internal Transfer', 100),
('Withdrawal 341', 'contains', 'Transfer', 'Internal Transfer', 100),
('Withdrawal 250', 'contains', 'Transfer', 'Internal Transfer', 100),
('USAA FUNDS TRANSFER', 'contains', 'Transfer', 'USAA Transfer', 100),
('ICPayment', 'contains', 'Transfer', 'IC Payment', 100),

-- Credit Card Payments
('AMEX EPAYMENT', 'contains', 'Credit Card Payment', 'AMEX', 90),
('American Express Credit', 'contains', 'Credit Card Payment', 'AMEX', 100),
('BARCLAYCARD', 'contains', 'Credit Card Payment', 'Barclays', 100),
('LLBEANMASTERCARD', 'contains', 'Credit Card Payment', 'LL Bean Card', 100),
('TJX Rew', 'contains', 'Credit Card Payment', 'TJX Card', 100),
('CAPITAL ONE', 'contains', 'Credit Card Payment', 'Capital One', 100),
('USAA Loan', 'contains', 'Financial', 'USAA Loan', 100),

-- Insurance
('PROGRESSIVE INS', 'contains', 'Insurance', 'Progressive', 100),

-- Fees
('Overdraft Fee', 'contains', 'Bank Fees', 'Overdraft', 200),
('NSF FEE', 'contains', 'Bank Fees', 'NSF Fee', 200),
('SERVICE CHARGE', 'contains', 'Bank Fees', 'Service Charge', 100),
('ATM FEE', 'contains', 'Bank Fees', 'ATM Fee', 100),
('ATM REBATE', 'contains', 'Atm Fee', 'ATM Rebate', 100),

-- Cash/ATM
('NBT BANK', 'contains', 'Cash', 'ATM', 100),
('ATM Withdrawal', 'contains', 'Cash', 'ATM', 50),
('Binghamton Mobi', 'contains', 'Cash', 'ATM', 100),

-- Checks
('CHECK #', 'contains', 'Check', 'Check Payment', 100),

-- Charity
('WIKIMED', 'contains', 'Charity', 'Wikipedia', 100),
('Wikimedia', 'contains', 'Charity', 'Wikipedia', 100),

-- Government
('Albanyvitalstats', 'contains', 'Government', 'NY Vital Records', 100),

-- Misc
('Overdraft Protection', 'contains', 'Transfer', 'Overdraft Protection', 100),
('ROAD RUNNER', 'contains', 'Shopping', 'Road Runner Sports', 100)

ON CONFLICT DO NOTHING;

-- ============================================================
-- TRIGGERS
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

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
