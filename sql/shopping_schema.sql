-- ============================================================
-- Patch 0135: Shopping Lists — PostgreSQL Schema
-- Follows Mythos P5 conventions: UUID PKs, TIMESTAMPTZ, source tracking
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Stores ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS stores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100),         -- grocery, hardware, auto_parts, pharmacy, general
    latitude NUMERIC(10,8),
    longitude NUMERIC(11,8),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    notes TEXT,
    visit_frequency INTEGER DEFAULT 0,
    last_visited TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    source VARCHAR(50) DEFAULT 'manual',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_store_name ON stores(name);
CREATE INDEX IF NOT EXISTS idx_store_category ON stores(category);
CREATE INDEX IF NOT EXISTS idx_store_active ON stores(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_store_gps ON stores(latitude, longitude) WHERE latitude IS NOT NULL;

-- ── Shopping Items (the "what") ─────────────────────
CREATE TABLE IF NOT EXISTS shopping_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    department VARCHAR(100),       -- produce, dairy, hardware, automotive, pharmacy
    default_quantity NUMERIC(10,2) DEFAULT 1,
    default_unit VARCHAR(50),      -- each, lb, oz, gallon, box, bag, pack
    notes TEXT,
    usual_price NUMERIC(10,2),
    last_purchased TIMESTAMPTZ,
    purchase_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    source VARCHAR(50) DEFAULT 'manual',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_item_name ON shopping_items(name);
CREATE INDEX IF NOT EXISTS idx_item_dept ON shopping_items(department);
CREATE INDEX IF NOT EXISTS idx_item_active ON shopping_items(is_active) WHERE is_active = TRUE;

-- ── Item-Store associations (which items at which stores) ──
CREATE TABLE IF NOT EXISTS item_stores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_id UUID NOT NULL REFERENCES shopping_items(id) ON DELETE CASCADE,
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    aisle VARCHAR(50),
    department_override VARCHAR(100),
    usual_price NUMERIC(10,2),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(item_id, store_id)
);

CREATE INDEX IF NOT EXISTS idx_is_item ON item_stores(item_id);
CREATE INDEX IF NOT EXISTS idx_is_store ON item_stores(store_id);

-- ── Shopping Lists (the "when/why") ─────────────────
CREATE TABLE IF NOT EXISTS shopping_lists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',   -- active, completed, archived
    target_store_id UUID REFERENCES stores(id),
    completed_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    source VARCHAR(50) DEFAULT 'manual',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_list_status ON shopping_lists(status);
CREATE INDEX IF NOT EXISTS idx_list_active ON shopping_lists(is_active) WHERE is_active = TRUE;

-- ── List Items (junction: list + item + overrides) ──
CREATE TABLE IF NOT EXISTS shopping_list_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    list_id UUID NOT NULL REFERENCES shopping_lists(id) ON DELETE CASCADE,
    item_id UUID NOT NULL REFERENCES shopping_items(id) ON DELETE CASCADE,
    quantity NUMERIC(10,2),
    unit_override VARCHAR(50),
    priority VARCHAR(20) DEFAULT 'normal',  -- urgent, high, normal, low
    notes TEXT,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    added_by VARCHAR(50) DEFAULT 'manual',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(list_id, item_id)
);

CREATE INDEX IF NOT EXISTS idx_li_list ON shopping_list_items(list_id);
CREATE INDEX IF NOT EXISTS idx_li_item ON shopping_list_items(item_id);
CREATE INDEX IF NOT EXISTS idx_li_completed ON shopping_list_items(completed);

-- ── Purchase History (immutable log — follows P5 pattern) ──
CREATE TABLE IF NOT EXISTS purchase_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_id UUID NOT NULL REFERENCES shopping_items(id),
    store_id UUID REFERENCES stores(id),
    quantity NUMERIC(10,2),
    unit VARCHAR(50),
    price NUMERIC(10,2),
    purchased_at TIMESTAMPTZ DEFAULT NOW(),
    source VARCHAR(50) DEFAULT 'manual',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ph_item ON purchase_history(item_id);
CREATE INDEX IF NOT EXISTS idx_ph_store ON purchase_history(store_id);
CREATE INDEX IF NOT EXISTS idx_ph_date ON purchase_history(purchased_at DESC);

-- ── Default "Master List" ──
INSERT INTO shopping_lists (name, description, source)
SELECT 'Master List', 'Default shopping list — items auto-added here', 'system'
WHERE NOT EXISTS (SELECT 1 FROM shopping_lists WHERE name = 'Master List');
