-- ============================================================
-- Mythos Design Patterns: PostgreSQL Reference Schemas
-- Version: 1.0
-- Purpose: Copy-paste ready SQL for all PostgreSQL patterns
-- Usage: Use as reference when building new features.
--        Do NOT run this wholesale — pick the pattern you need.
-- ============================================================

-- ============================================================
-- P4: CONVERSATION LOG
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_uuid UUID NOT NULL,
    platform VARCHAR(50) NOT NULL,
    mode VARCHAR(50) DEFAULT 'chat',
    title VARCHAR(500),
    spiral_number INTEGER,
    spiral_day INTEGER,
    status VARCHAR(20) DEFAULT 'active',
    message_count INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    last_message_at TIMESTAMPTZ DEFAULT NOW(),
    canonical_id UUID UNIQUE
);

CREATE INDEX IF NOT EXISTS idx_conv_user ON conversations(user_uuid);
CREATE INDEX IF NOT EXISTS idx_conv_status ON conversations(status);
CREATE INDEX IF NOT EXISTS idx_conv_last_msg ON conversations(last_message_at DESC);
CREATE INDEX IF NOT EXISTS idx_conv_spiral ON conversations(spiral_number, spiral_day);

CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    user_uuid UUID NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    mode VARCHAR(50) DEFAULT 'chat',
    has_media BOOLEAN DEFAULT FALSE,
    media_refs UUID[],
    embedding vector(384),
    mentioned_entities TEXT[],
    mentioned_dates DATE[],
    emotional_tone VARCHAR(50),
    spiral_number INTEGER,
    spiral_day INTEGER,
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
);

CREATE INDEX IF NOT EXISTS idx_msg_conv ON chat_messages(conversation_id, created_at);
CREATE INDEX IF NOT EXISTS idx_msg_user ON chat_messages(user_uuid);
CREATE INDEX IF NOT EXISTS idx_msg_fts ON chat_messages USING GIN(tsv);
CREATE INDEX IF NOT EXISTS idx_msg_embedding ON chat_messages USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_msg_unprocessed ON chat_messages(processed) WHERE processed = FALSE;
CREATE INDEX IF NOT EXISTS idx_msg_spiral ON chat_messages(spiral_number, spiral_day);
CREATE INDEX IF NOT EXISTS idx_msg_entities ON chat_messages USING GIN(mentioned_entities);

CREATE TABLE IF NOT EXISTS conversation_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    user_uuid UUID NOT NULL,
    tier INTEGER NOT NULL,
    start_message_id UUID REFERENCES chat_messages(id),
    end_message_id UUID REFERENCES chat_messages(id),
    message_count INTEGER,
    summary_text TEXT NOT NULL,
    themes TEXT[],
    emotional_tone VARCHAR(50),
    key_entities TEXT[],
    decisions_made TEXT[],
    open_questions TEXT[],
    embedding vector(384),
    original_tokens INTEGER,
    summary_tokens INTEGER,
    compression_ratio NUMERIC(5,2),
    parent_summary_id UUID REFERENCES conversation_summaries(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_summ_conv ON conversation_summaries(conversation_id);
CREATE INDEX IF NOT EXISTS idx_summ_tier ON conversation_summaries(tier);
CREATE INDEX IF NOT EXISTS idx_summ_embedding ON conversation_summaries USING ivfflat (embedding vector_cosine_ops);


-- ============================================================
-- P5: FINANCIAL TRANSACTIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS financial_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    canonical_id UUID UNIQUE,
    name VARCHAR(200) NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    institution VARCHAR(200),
    last_four VARCHAR(4),
    owner_uuid UUID,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS financial_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES financial_accounts(id),
    transaction_date DATE NOT NULL,
    posted_date DATE,
    description TEXT NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    tags TEXT[],
    import_source VARCHAR(50),
    import_batch_id UUID,
    raw_data JSONB,
    external_id VARCHAR(500),
    fingerprint VARCHAR(64),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(fingerprint, account_id)
);

CREATE INDEX IF NOT EXISTS idx_txn_account ON financial_transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_txn_date ON financial_transactions(transaction_date DESC);
CREATE INDEX IF NOT EXISTS idx_txn_category ON financial_transactions(category);
CREATE INDEX IF NOT EXISTS idx_txn_amount ON financial_transactions(amount);
CREATE INDEX IF NOT EXISTS idx_txn_fingerprint ON financial_transactions(fingerprint);
CREATE INDEX IF NOT EXISTS idx_txn_tags ON financial_transactions USING GIN(tags);

CREATE TABLE IF NOT EXISTS financial_obligations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    amount_expected NUMERIC(12,2),
    frequency VARCHAR(20) NOT NULL,
    due_day INTEGER,
    account_id UUID REFERENCES financial_accounts(id),
    category VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    auto_pay BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================================
-- P6: MEDIA ASSETS
-- ============================================================

CREATE TABLE IF NOT EXISTS media_assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    canonical_id UUID UNIQUE,
    filename VARCHAR(500) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_size_bytes BIGINT,
    asset_sha256 VARCHAR(64) NOT NULL,
    asset_rel_path TEXT NOT NULL,
    source_platform VARCHAR(50),
    source_id VARCHAR(500),
    uploaded_by UUID,
    width INTEGER,
    height INTEGER,
    exif_data JSONB,
    gps_lat NUMERIC(10,7),
    gps_lon NUMERIC(10,7),
    taken_at TIMESTAMPTZ,
    vision_description TEXT,
    vision_entities TEXT[],
    vision_tags TEXT[],
    esoteric_analysis JSONB,
    duration_seconds NUMERIC(10,2),
    transcript TEXT,
    conversation_id UUID,
    message_id UUID,
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(asset_sha256)
);

CREATE INDEX IF NOT EXISTS idx_media_type ON media_assets(mime_type);
CREATE INDEX IF NOT EXISTS idx_media_sha ON media_assets(asset_sha256);
CREATE INDEX IF NOT EXISTS idx_media_gps ON media_assets(gps_lat, gps_lon) WHERE gps_lat IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_media_taken ON media_assets(taken_at DESC) WHERE taken_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_media_tags ON media_assets USING GIN(vision_tags);
CREATE INDEX IF NOT EXISTS idx_media_entities ON media_assets USING GIN(vision_entities);
CREATE INDEX IF NOT EXISTS idx_media_unprocessed ON media_assets(processed) WHERE processed = FALSE;
