-- Grocery List System
-- Stream: SYS (shared infrastructure)

-- Predefined aisles with sort order for store walkthrough
CREATE TABLE IF NOT EXISTS grocery_aisles (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    icon TEXT DEFAULT '🛒',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Grocery lists (support multiple lists)
CREATE TABLE IF NOT EXISTS grocery_lists (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL DEFAULT 'Shopping List',
    telegram_user_id BIGINT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Individual items on a list
CREATE TABLE IF NOT EXISTS grocery_items (
    id SERIAL PRIMARY KEY,
    list_id INTEGER NOT NULL REFERENCES grocery_lists(id) ON DELETE CASCADE,
    aisle_id INTEGER REFERENCES grocery_aisles(id),
    name TEXT NOT NULL,
    quantity TEXT DEFAULT '1',
    checked BOOLEAN DEFAULT FALSE,
    checked_at TIMESTAMPTZ,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_grocery_items_list ON grocery_items(list_id);
CREATE INDEX IF NOT EXISTS idx_grocery_items_aisle ON grocery_items(aisle_id);
CREATE INDEX IF NOT EXISTS idx_grocery_items_checked ON grocery_items(list_id, checked);

-- Seed aisles in typical store walkthrough order
INSERT INTO grocery_aisles (name, sort_order, icon) VALUES
    ('Produce',           1,  '🥬'),
    ('Bakery',            2,  '🍞'),
    ('Deli',              3,  '🥩'),
    ('Meat & Seafood',    4,  '🥩'),
    ('Dairy & Eggs',      5,  '🥛'),
    ('Frozen',            6,  '🧊'),
    ('Breakfast & Cereal',7,  '🥣'),
    ('Pasta & Grains',    8,  '🍝'),
    ('Canned Goods',      9,  '🥫'),
    ('Condiments & Spices',10,'🧂'),
    ('Snacks',            11, '🍿'),
    ('Beverages',         12, '🥤'),
    ('Household',         13, '🧹'),
    ('Health & Beauty',   14, '💊'),
    ('Other',             99, '🛒')
ON CONFLICT (name) DO NOTHING;
