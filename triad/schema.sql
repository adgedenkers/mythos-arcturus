-- Triad Memory System Schema
-- Three layers: Grid (Knowledge), Akashic (Wisdom), Prophetic (Vision)

-- Enable pgvector if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Main conversation record linking all three layers
CREATE TABLE IF NOT EXISTS triad_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Spiral time anchors
    spiral_day INT CHECK (spiral_day BETWEEN 1 AND 9),
    spiral_cycle INT,
    
    -- Source reference (optional - link to original if stored elsewhere)
    source_type VARCHAR(50),  -- 'claude_export', 'telegram', 'manual', etc.
    source_id VARCHAR(255),
    
    -- Raw content hash for integrity (not storing full content)
    content_hash VARCHAR(64),
    
    -- Processing status
    grid_extracted BOOLEAN DEFAULT FALSE,
    akashic_extracted BOOLEAN DEFAULT FALSE,
    prophetic_extracted BOOLEAN DEFAULT FALSE
);

-- Layer 1: Grid (Knowledge) - The 9-node semantic extraction
CREATE TABLE IF NOT EXISTS triad_grid (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES triad_conversations(id) ON DELETE CASCADE,
    extracted_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- The 9 nodes (stored as JSONB for flexibility)
    node_1_context JSONB,      -- Setting, circumstances, prompt
    node_2_entities JSONB,     -- People, places, systems, concepts
    node_3_actions JSONB,      -- What was done, decided, built
    node_4_states JSONB,       -- Emotional/energetic states
    node_5_relationships JSONB, -- Connections established
    node_6_timestamps JSONB,   -- Dates, times, cycles referenced
    node_7_artifacts JSONB,    -- Documents, code, outputs
    node_8_open_threads JSONB, -- Unanswered questions, incomplete tasks
    node_9_declarations JSONB, -- Identity statements, truths claimed
    
    -- Embedding for knowledge retrieval
    embedding vector(1536),
    
    UNIQUE(conversation_id)
);

-- Layer 2: Akashic (Wisdom) - The energetic imprint
CREATE TABLE IF NOT EXISTS triad_akashic (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES triad_conversations(id) ON DELETE CASCADE,
    extracted_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Energetic arc
    entry_valence DECIMAL(3,1) CHECK (entry_valence BETWEEN -5 AND 5),
    entry_quality VARCHAR(100),
    exit_valence DECIMAL(3,1) CHECK (exit_valence BETWEEN -5 AND 5),
    exit_quality VARCHAR(100),
    
    -- Arc type
    arc_type VARCHAR(50) CHECK (arc_type IN (
        'resolution', 'activation', 'integration', 
        'inquiry', 'release', 'stasis', 'spiral'
    )),
    
    -- The distillation
    essence TEXT,              -- 1-2 sentences - what this was REALLY about
    pattern_signature VARCHAR(100), -- Named pattern (e.g., 'scarcity_loop')
    
    -- Domains touched
    domains TEXT[],            -- Array of domain names
    
    -- Echoes and witnesses
    echoes TEXT,               -- What patterns this echoes
    witnessed_by TEXT[],       -- Entities/guides sensed
    
    -- Embedding for pattern matching
    embedding vector(1536),
    
    UNIQUE(conversation_id)
);

-- Layer 3: Prophetic (Vision) - Trajectory sensing
CREATE TABLE IF NOT EXISTS triad_prophetic (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES triad_conversations(id) ON DELETE CASCADE,
    extracted_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Trajectory
    vector TEXT,               -- Direction this is pointing
    attractor TEXT,            -- Shape it's moving toward
    
    -- Readiness
    readiness TEXT,            -- What's nearly ready to manifest
    obstacle TEXT,             -- What might be in the way
    
    -- Invitation and seeds
    invitation TEXT,           -- What this moment is inviting
    seed TEXT,                 -- Seed planted for later
    
    -- Convergences with other threads
    convergences TEXT[],       -- Other threads this is moving toward
    
    -- Embedding for convergence sensing
    embedding vector(1536),
    
    UNIQUE(conversation_id)
);

-- Pattern signatures catalog (for consistency)
CREATE TABLE IF NOT EXISTS triad_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    signature VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    domain VARCHAR(50),
    first_seen TIMESTAMPTZ DEFAULT NOW(),
    occurrence_count INT DEFAULT 1
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_triad_conv_spiral ON triad_conversations(spiral_cycle, spiral_day);
CREATE INDEX IF NOT EXISTS idx_triad_conv_created ON triad_conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_triad_akashic_pattern ON triad_akashic(pattern_signature);
CREATE INDEX IF NOT EXISTS idx_triad_akashic_arc ON triad_akashic(arc_type);
CREATE INDEX IF NOT EXISTS idx_triad_akashic_domains ON triad_akashic USING GIN(domains);
CREATE INDEX IF NOT EXISTS idx_triad_prophetic_seed ON triad_prophetic(seed) WHERE seed IS NOT NULL;

-- Vector indexes (for similarity search)
CREATE INDEX IF NOT EXISTS idx_triad_grid_embedding ON triad_grid USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_triad_akashic_embedding ON triad_akashic USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_triad_prophetic_embedding ON triad_prophetic USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
