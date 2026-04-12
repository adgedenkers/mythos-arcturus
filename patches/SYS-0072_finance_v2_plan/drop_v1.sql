BEGIN;

DROP TABLE IF EXISTS public.v1_accounts CASCADE;
DROP TABLE IF EXISTS public.v1_bill_overrides CASCADE;
DROP TABLE IF EXISTS public.v1_bill_payments CASCADE;
DROP TABLE IF EXISTS public.v1_categories CASCADE;
DROP TABLE IF EXISTS public.v1_category_mappings CASCADE;
DROP TABLE IF EXISTS public.v1_category_rules CASCADE;
DROP TABLE IF EXISTS public.v1_import_logs CASCADE;
DROP TABLE IF EXISTS public.v1_recurring_bills CASCADE;
DROP TABLE IF EXISTS public.v1_recurring_income CASCADE;
DROP TABLE IF EXISTS public.v1_transactions CASCADE;

COMMIT;
