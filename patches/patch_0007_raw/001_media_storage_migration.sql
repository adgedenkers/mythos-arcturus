-- Mythos Media Storage Migration
-- Sprint 1: Photo Input & Storage
-- Date: 2026-01-21 (Spiral 1.3)
-- 
-- DESIGN PRINCIPLE: Right tool for the job
-- - PostgreSQL for structured metadata (searchable, transactional)
-- - Filesystem for actual files (efficient, no blob storage overhead)
-- - JSONB for flexible analysis data (schema can evolve)
-- - Text arrays for simple tags (no separate junction table needed unless we need it)

-- Core media tracking
CREATE TABLE IF NOT EXISTS media_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_uuid UUID NOT NULL REFERENCES users(user_uuid) ON DELETE CASCADE,
    conversation_id VARCHAR(100),  -- Links to chat context, nullable for standalone uploads
    message_id INTEGER REFERENCES chat_messages(message_id) ON DELETE SET NULL,
    
    -- File metadata
    filename TEXT NOT NULL,
    original_filename TEXT,  -- What the user called it, if available
    file_path TEXT NOT NULL UNIQUE,  -- Absolute path on filesystem
    file_size_bytes BIGINT,
    mime_type TEXT NOT NULL,
    media_type VARCHAR(20) NOT NULL,  -- 'photo', 'video', 'audio', 'document'
    
    -- Telegram-specific (null if uploaded via other means)
    telegram_file_id TEXT,
    telegram_file_unique_id TEXT UNIQUE,  -- Telegram's permanent identifier
    
    -- Visual metadata (null for non-images)
    width INTEGER,
    height INTEGER,
    aspect_ratio NUMERIC(5,3),
    
    -- Processing status
    processed BOOLEAN DEFAULT FALSE,
    analysis_data JSONB,  -- Flexible storage for vision model output
    extracted_text TEXT,  -- OCR results, full-text searchable
    
    -- Simple tagging (start simple, expand if needed)
    auto_tags TEXT[],  -- Tags from vision model
    user_tags TEXT[],  -- Tags from user
    
    -- Timestamps
    uploaded_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    
    CONSTRAINT valid_media_type CHECK (media_type IN ('photo', 'video', 'audio', 'document'))
);

-- Indexes for common queries
CREATE INDEX idx_media_user ON media_files(user_uuid);
CREATE INDEX idx_media_conversation ON media_files(conversation_id) WHERE conversation_id IS NOT NULL;
CREATE INDEX idx_media_uploaded ON media_files(uploaded_at DESC);
CREATE INDEX idx_media_type ON media_files(media_type);
CREATE INDEX idx_media_unprocessed ON media_files(processed, uploaded_at) WHERE NOT processed;

-- Full-text search on extracted text
CREATE INDEX idx_media_text_search ON media_files USING gin(to_tsvector('english', COALESCE(extracted_text, '')));

-- GIN index for tag arrays (enables fast tag lookups)
CREATE INDEX idx_media_auto_tags ON media_files USING gin(auto_tags);
CREATE INDEX idx_media_user_tags ON media_files USING gin(user_tags);

-- Comments for documentation
COMMENT ON TABLE media_files IS 'Media files uploaded by users - photos, videos, documents. Stores metadata and analysis results.';
COMMENT ON COLUMN media_files.file_path IS 'Absolute filesystem path - media stored outside database for efficiency';
COMMENT ON COLUMN media_files.analysis_data IS 'JSONB storage for vision model output - flexible schema that can evolve';
COMMENT ON COLUMN media_files.auto_tags IS 'Array of tags from automatic analysis - simple and efficient for most queries';
COMMENT ON COLUMN media_files.user_tags IS 'Array of user-provided tags - kept separate for provenance';

-- Optional: Entity linking table (START COMMENTED - add if we need it)
-- This would link photos to Neo4j nodes (Soul, Person, Location, etc.)
-- For now, we can store entity references in analysis_data JSONB
-- If we need complex entity queries, we uncomment this:

/*
CREATE TABLE IF NOT EXISTS media_entity_links (
    media_id UUID NOT NULL REFERENCES media_files(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL,  -- 'Soul', 'Person', 'Location', 'Artifact', etc.
    entity_id TEXT NOT NULL,  -- Neo4j node ID or canonical_id
    confidence NUMERIC(3,2),  -- 0.0 to 1.0
    link_reason TEXT,  -- Why this link was made
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (media_id, entity_type, entity_id)
);

CREATE INDEX idx_entity_links_media ON media_entity_links(media_id);
CREATE INDEX idx_entity_links_entity ON media_entity_links(entity_type, entity_id);

COMMENT ON TABLE media_entity_links IS 'Links media to Neo4j entities - only create if complex entity queries needed';
*/

-- View for easy photo browsing
CREATE OR REPLACE VIEW recent_photos AS
SELECT 
    m.id,
    m.filename,
    m.uploaded_at,
    m.width,
    m.height,
    m.processed,
    m.auto_tags,
    m.user_tags,
    u.soul_display_name,
    u.username,
    CASE 
        WHEN m.analysis_data IS NOT NULL THEN 
            m.analysis_data->>'general_description'
        ELSE 
            'Processing...'
    END as description,
    m.conversation_id
FROM media_files m
JOIN users u ON m.user_uuid = u.user_uuid
WHERE m.media_type = 'photo'
ORDER BY m.uploaded_at DESC;

COMMENT ON VIEW recent_photos IS 'Convenient view for browsing recently uploaded photos with basic metadata';

-- Function to search photos by tag
CREATE OR REPLACE FUNCTION search_photos_by_tag(search_tag TEXT)
RETURNS TABLE (
    photo_id UUID,
    filename TEXT,
    uploaded_at TIMESTAMP,
    tags TEXT[],
    uploader TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.id,
        m.filename,
        m.uploaded_at,
        ARRAY(SELECT DISTINCT unnest(m.auto_tags || m.user_tags)) as all_tags,
        u.soul_display_name
    FROM media_files m
    JOIN users u ON m.user_uuid = u.user_uuid
    WHERE m.media_type = 'photo'
      AND (search_tag = ANY(m.auto_tags) OR search_tag = ANY(m.user_tags))
    ORDER BY m.uploaded_at DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION search_photos_by_tag IS 'Search photos by tag - works with both auto and user tags';

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE ON media_files TO mythos_api;
-- GRANT SELECT ON recent_photos TO mythos_api;
-- GRANT EXECUTE ON FUNCTION search_photos_by_tag TO mythos_api;
