-- SDIP Foundation Tables
-- LOG-0001: Sovereign Document Intelligence Platform
-- Creates all core tables for document chunking, sensitivity, and audit

-- Enable pgvector extension (for future embedding storage)
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- sdip_sources: registered directories/repos to scan
-- ============================================================
CREATE TABLE IF NOT EXISTS sdip_sources (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    path TEXT NOT NULL,
    source_type TEXT DEFAULT 'directory',      -- directory, git_repo, obsidian_vault
    scan_schedule TEXT,                         -- cron expression or NULL for manual
    last_scanned TIMESTAMPTZ,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- sdip_documents: master file catalog
-- ============================================================
CREATE TABLE IF NOT EXISTS sdip_documents (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sdip_sources(id),
    relative_path TEXT NOT NULL,
    filename TEXT NOT NULL,
    content_hash TEXT NOT NULL,                  -- SHA-256
    file_size INTEGER,
    file_format TEXT,                            -- md, json, html, docx, etc.
    category TEXT,                               -- from classification
    subcategory TEXT,
    quality TEXT,                                -- substantial, fragment, stub
    summary TEXT,
    status TEXT DEFAULT 'active',                -- active, archived, superseded
    superseded_by INTEGER REFERENCES sdip_documents(id),
    last_scanned TIMESTAMPTZ DEFAULT now(),
    last_modified TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(source_id, relative_path)
);

-- ============================================================
-- sdip_chunks: document sections with sensitivity
-- ============================================================
CREATE TABLE IF NOT EXISTS sdip_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES sdip_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,                -- position in document (0-based)
    parent_heading TEXT,                          -- nearest parent heading, if any
    content_text TEXT NOT NULL,
    word_count INTEGER,
    content_embedding VECTOR(384),               -- for semantic search (populated later)
    sensitivity_level TEXT DEFAULT 'PUBLIC',      -- PUBLIC, INTERNAL, SENSITIVE, RESTRICTED
    sensitivity_tags TEXT[] DEFAULT '{}',         -- PII, PHI, CREDENTIALS, LEGAL_HOLD, etc.
    classification_json JSONB,                   -- full LLM classification result
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(document_id, chunk_index)
);

-- ============================================================
-- sdip_sensitivity: detailed detection records
-- ============================================================
CREATE TABLE IF NOT EXISTS sdip_sensitivity (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL REFERENCES sdip_chunks(id) ON DELETE CASCADE,
    sensitivity_type TEXT NOT NULL,              -- PII, PHI, CREDENTIALS, LEGAL_HOLD, CLASSIFIED
    detection_method TEXT NOT NULL,              -- regex, llm, manual, propagated
    detected_pattern TEXT,                       -- what triggered the detection
    confidence FLOAT DEFAULT 1.0,
    reviewed_by TEXT,                            -- NULL = unreviewed
    review_timestamp TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- sdip_classifications: full history for audit trail
-- ============================================================
CREATE TABLE IF NOT EXISTS sdip_classifications (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES sdip_documents(id) ON DELETE CASCADE,
    model_used TEXT NOT NULL,
    classification_json JSONB NOT NULL,
    confidence FLOAT,
    classified_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- sdip_actions: proposed and executed reorganization actions
-- ============================================================
CREATE TABLE IF NOT EXISTS sdip_actions (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES sdip_documents(id),
    chunk_id INTEGER REFERENCES sdip_chunks(id),
    action_type TEXT NOT NULL,                   -- merge, archive, rename, restructure, redact
    proposed_by TEXT NOT NULL,                   -- model name or 'manual'
    proposal_json JSONB,                        -- details of what's proposed
    status TEXT DEFAULT 'proposed',              -- proposed, approved, executed, rejected
    approved_by TEXT,
    executed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- sdip_audit_log: every content access
-- ============================================================
CREATE TABLE IF NOT EXISTS sdip_audit_log (
    id SERIAL PRIMARY KEY,
    requester TEXT NOT NULL,                     -- user, API key, or service name
    document_id INTEGER REFERENCES sdip_documents(id),
    chunk_id INTEGER REFERENCES sdip_chunks(id),
    action TEXT NOT NULL,                        -- read, search, export, redact
    content_served BOOLEAN DEFAULT true,         -- false if blocked
    redaction_applied TEXT,                      -- mask, summarize, block, flag, NULL
    metadata JSONB,
    timestamp TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- Indexes
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_sdip_chunks_document ON sdip_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_sdip_chunks_sensitivity ON sdip_chunks(sensitivity_level);
CREATE INDEX IF NOT EXISTS idx_sdip_sensitivity_type ON sdip_sensitivity(sensitivity_type);
CREATE INDEX IF NOT EXISTS idx_sdip_documents_category ON sdip_documents(category);
CREATE INDEX IF NOT EXISTS idx_sdip_documents_status ON sdip_documents(status);
CREATE INDEX IF NOT EXISTS idx_sdip_documents_hash ON sdip_documents(content_hash);
CREATE INDEX IF NOT EXISTS idx_sdip_audit_timestamp ON sdip_audit_log(timestamp);
