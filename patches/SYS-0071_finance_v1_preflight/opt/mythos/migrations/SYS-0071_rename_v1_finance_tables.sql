-- SYS-0071: Rename v1 finance tables with v1_ prefix
-- Part of Finance v2 rebuild preflight
-- Per plan v3 §15 (SYS-0071 finance_v1_preflight)
-- Uses rename-not-drop so rollback is possible for 2 weeks until SYS-0079 cleanup

-- Safety: rename is idempotent via IF EXISTS checks would be nice but Postgres
-- ALTER TABLE RENAME does not support IF EXISTS in older versions. We rely on
-- the apply_patch.py preflight safety check to verify the source tables exist
-- and target names don't exist before this runs.

ALTER TABLE accounts          RENAME TO v1_accounts;
ALTER TABLE transactions      RENAME TO v1_transactions;
ALTER TABLE recurring_bills   RENAME TO v1_recurring_bills;
ALTER TABLE recurring_income  RENAME TO v1_recurring_income;
ALTER TABLE bill_payments     RENAME TO v1_bill_payments;
ALTER TABLE bill_overrides    RENAME TO v1_bill_overrides;
ALTER TABLE categories        RENAME TO v1_categories;
ALTER TABLE category_mappings RENAME TO v1_category_mappings;
ALTER TABLE category_rules    RENAME TO v1_category_rules;
ALTER TABLE import_logs       RENAME TO v1_import_logs;
