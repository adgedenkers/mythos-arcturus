-- Patch 0093: Create bill_overrides table
-- Stores manual paid/unpaid overrides for recurring bills per month

CREATE TABLE IF NOT EXISTS bill_overrides (
    id              SERIAL PRIMARY KEY,
    bill_id         INTEGER NOT NULL REFERENCES recurring_bills(id) ON DELETE CASCADE,
    month           CHAR(7) NOT NULL,  -- YYYY-MM
    is_paid         BOOLEAN NOT NULL DEFAULT true,
    paid_amount     NUMERIC(12,2),
    paid_date       DATE,
    note            TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (bill_id, month)
);

CREATE INDEX IF NOT EXISTS bill_overrides_month_idx ON bill_overrides (month);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_bill_overrides_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS bill_overrides_updated_at ON bill_overrides;
CREATE TRIGGER bill_overrides_updated_at
    BEFORE UPDATE ON bill_overrides
    FOR EACH ROW EXECUTE FUNCTION update_bill_overrides_updated_at();
