-- MNE: YouTube video transcript storage
CREATE TABLE IF NOT EXISTS youtube_videos (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(20) NOT NULL UNIQUE,
    url TEXT NOT NULL,
    title TEXT,
    channel_name TEXT,
    channel_id TEXT,
    duration_seconds INTEGER,
    published_at TIMESTAMP,
    description TEXT,
    tags TEXT[],
    transcript_vtt TEXT,
    transcript_text TEXT,
    transcript_language VARCHAR(10) DEFAULT 'en',
    transcript_segments JSONB,
    metadata JSONB DEFAULT '{}',
    word_count INTEGER,
    ingested_at TIMESTAMP DEFAULT NOW(),
    processed_by_grid BOOLEAN DEFAULT FALSE,
    grid_processed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_yt_video_id ON youtube_videos(video_id);
CREATE INDEX IF NOT EXISTS idx_yt_channel ON youtube_videos(channel_name);
CREATE INDEX IF NOT EXISTS idx_yt_ingested ON youtube_videos(ingested_at DESC);
CREATE INDEX IF NOT EXISTS idx_yt_text_search ON youtube_videos USING gin(to_tsvector('english', COALESCE(transcript_text, '')));
