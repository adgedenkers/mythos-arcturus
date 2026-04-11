-- SYS-0052: Watchlist table
-- Stream: SYS | Type: MINOR

CREATE TABLE IF NOT EXISTS watchlist (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    media_type VARCHAR(20) NOT NULL DEFAULT 'show',  -- show, movie
    platform VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'want',      -- want, watching, watched
    added_by VARCHAR(50) NOT NULL DEFAULT 'adge',    -- adge, seraphe
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    watched_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_watchlist_status ON watchlist(status);
CREATE INDEX IF NOT EXISTS idx_watchlist_platform ON watchlist(platform);
CREATE INDEX IF NOT EXISTS idx_watchlist_title_search ON watchlist USING GIN(to_tsvector('english', title));
