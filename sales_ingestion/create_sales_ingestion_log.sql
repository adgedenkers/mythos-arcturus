CREATE TABLE IF NOT EXISTS sales_ingestion_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_name TEXT NOT NULL,
    artifact_type TEXT NOT NULL CHECK (artifact_type IN ('sales', 'shoes')),
    status TEXT NOT NULL CHECK (status IN ('staged', 'processing', 'success', 'failed')),
    extract_dir TEXT NOT NULL,
    error TEXT,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    UNIQUE (batch_name, artifact_type)
);

CREATE INDEX IF NOT EXISTS idx_sales_ingestion_log_status
    ON sales_ingestion_log(status);
