-- ============================================
-- Knowledge Map Rebuild Triggers
-- ============================================
-- Fires on changes to key reference tables.
-- Uses pg_notify to signal that the knowledge
-- map needs rebuilding.
-- ============================================

-- Function that sends a notification
CREATE OR REPLACE FUNCTION notify_knowledge_map_rebuild()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('knowledge_map_rebuild', json_build_object(
        'table', TG_TABLE_NAME,
        'operation', TG_OP,
        'timestamp', NOW()
    )::text);
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Trigger on recurring_bills
DROP TRIGGER IF EXISTS trg_bills_knowledge_map ON recurring_bills;
CREATE TRIGGER trg_bills_knowledge_map
    AFTER INSERT OR UPDATE OR DELETE ON recurring_bills
    FOR EACH ROW EXECUTE FUNCTION notify_knowledge_map_rebuild();

-- Trigger on accounts
DROP TRIGGER IF EXISTS trg_accounts_knowledge_map ON accounts;
CREATE TRIGGER trg_accounts_knowledge_map
    AFTER INSERT OR UPDATE OR DELETE ON accounts
    FOR EACH ROW EXECUTE FUNCTION notify_knowledge_map_rebuild();

-- Trigger on routines
DROP TRIGGER IF EXISTS trg_routines_knowledge_map ON routines;
CREATE TRIGGER trg_routines_knowledge_map
    AFTER INSERT OR UPDATE OR DELETE ON routines
    FOR EACH ROW EXECUTE FUNCTION notify_knowledge_map_rebuild();
