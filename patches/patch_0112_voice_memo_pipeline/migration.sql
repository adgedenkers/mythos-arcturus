-- Voice Memo Pipeline — Database Migration
-- Patch 0112: voice_memos + voice_memo_segments tables

-- Main voice memos table
CREATE TABLE IF NOT EXISTS voice_memos (
    id              SERIAL PRIMARY KEY,
    filename        TEXT NOT NULL,
    original_path   TEXT,
    archive_path    TEXT,
    source          TEXT DEFAULT 'syncthing',   -- syncthing, telegram, manual
    file_size_bytes BIGINT,
    duration_seconds FLOAT,
    
    -- Transcription
    transcript_full     TEXT,                   -- Plain text, no speaker labels
    transcript_diarized TEXT,                   -- With speaker labels
    language            TEXT,
    diarized            BOOLEAN DEFAULT FALSE,
    speaker_count       INTEGER DEFAULT 0,
    speaker_stats       JSONB,                  -- Per-speaker stats (duration, word count)
    
    -- Processing
    status          TEXT DEFAULT 'pending',     -- pending, processing, complete, error
    error_message   TEXT,
    processing_times JSONB,                     -- convert_s, transcribe_s, diarize_s, total_s
    
    -- Timestamps
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    processed_at    TIMESTAMPTZ
);

-- Individual segments with speaker labels and timestamps
CREATE TABLE IF NOT EXISTS voice_memo_segments (
    id              SERIAL PRIMARY KEY,
    memo_id         INTEGER NOT NULL REFERENCES voice_memos(id) ON DELETE CASCADE,
    segment_index   INTEGER NOT NULL,
    speaker_label   TEXT DEFAULT 'UNKNOWN',     -- SPEAKER_00, SPEAKER_01, etc.
    start_time      FLOAT NOT NULL,             -- seconds
    end_time        FLOAT NOT NULL,             -- seconds
    text            TEXT NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_voice_memos_status ON voice_memos(status);
CREATE INDEX IF NOT EXISTS idx_voice_memos_created ON voice_memos(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_voice_memos_source ON voice_memos(source);
CREATE INDEX IF NOT EXISTS idx_voice_memo_segments_memo ON voice_memo_segments(memo_id);
CREATE INDEX IF NOT EXISTS idx_voice_memo_segments_speaker ON voice_memo_segments(speaker_label);

-- Full-text search on transcripts
CREATE INDEX IF NOT EXISTS idx_voice_memos_transcript_fts 
    ON voice_memos USING gin(to_tsvector('english', COALESCE(transcript_full, '')));
