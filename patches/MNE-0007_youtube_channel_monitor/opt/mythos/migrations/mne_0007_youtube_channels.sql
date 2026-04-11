-- MNE-0007: YouTube Channel Subscriptions
-- Tracks which channels Iris monitors for automatic transcript ingestion

CREATE TABLE IF NOT EXISTS youtube_channel_subscriptions (
    id SERIAL PRIMARY KEY,
    channel_id TEXT NOT NULL UNIQUE,          -- YouTube channel ID (UC...)
    channel_handle TEXT,                       -- @handle (e.g., @stefanburns)
    channel_name TEXT NOT NULL,               -- Display name
    channel_url TEXT,                          -- Full channel URL
    rss_url TEXT,                              -- RSS feed URL
    active BOOLEAN DEFAULT TRUE,              -- Whether to monitor
    check_interval_minutes INTEGER DEFAULT 120, -- How often to poll (default 2 hours)
    last_checked_at TIMESTAMP,                -- Last time we polled
    last_video_at TIMESTAMP,                  -- Published date of most recent video found
    total_videos_ingested INTEGER DEFAULT 0,  -- Running count
    added_by TEXT DEFAULT 'ka_tuarel',        -- Who requested this subscription
    added_at TIMESTAMP DEFAULT NOW(),
    notes TEXT                                -- Any notes about this channel
);

CREATE INDEX IF NOT EXISTS idx_yt_subs_active ON youtube_channel_subscriptions(active) WHERE active = TRUE;
CREATE INDEX IF NOT EXISTS idx_yt_subs_check ON youtube_channel_subscriptions(last_checked_at) WHERE active = TRUE;

-- Also add channel_id to youtube_videos if not populated
-- (we already have the column, just need to populate it going forward)
