# Mythos Finance - Database Schema Report

Generated: 2026-01-23 20:26:22
Database: mythos

## Summary

| Metric | Count |
|--------|-------|
| Expected Tables | 5 |
| Actual Tables | 26 |
| Missing Tables | 0 |
| Extra Tables | 21 |

## ℹ️ Extra Tables (not in expected schema)

- `astrological_events` (2 rows)
- `bundles` (0 rows)
- `categories` (12 rows)
- `chat_messages` (94 rows)
- `emotional_state_timeseries` (0 rows)
- `entity_mention_timeseries` (0 rows)
- `grid_activation_timeseries` (0 rows)
- `institutions` (0 rows)
- `item_images` (9 rows)
- `items_for_sale` (3 rows)
- `media_assets` (0 rows)
- `media_files` (13 rows)
- `message_astrological_context` (0 rows)
- `obligations` (0 rows)
- `pending_intake` (0 rows)
- `people` (3 rows)
- `sales` (0 rows)
- `sales_ingestion_log` (0 rows)
- `sync_log` (0 rows)
- `transaction_history` (0 rows)
- `users` (1 rows)

## Table Details

### accounts

**Rows:** 0

**Status:** ⚠️ Schema mismatch

**Missing Columns:**
- `account_name` (expected: character varying(255))
- `account_number` (expected: character varying(50))
- `bank_name` (expected: character varying(100))
- `notes` (expected: text)

**Extra Columns (in DB, not expected):**
- `account_subtype` (text)
- `available_balance` (numeric(12,2))
- `currency` (text)
- `current_balance` (numeric(12,2))
- `institution_id` (integer)
- `last_balance_update` (timestamp without time zone)
- `limit_balance` (numeric(12,2))
- `mask` (text)
- `name` (text)
- `obligated_amount` (numeric(12,2))
- `official_name` (text)
- `plaid_account_id` (text)
- `true_available_balance` (numeric(12,2))

| Column | Expected | Actual | Match |
|--------|----------|--------|-------|
| account_name | character varying(255) | ❌ MISSING | ❌ |
| account_number | character varying(50) | ❌ MISSING | ❌ |
| account_subtype | - | text | ℹ️ |
| account_type | character varying(50) | text | ⚠️ |
| available_balance | - | numeric(12,2) | ℹ️ |
| bank_name | character varying(100) | ❌ MISSING | ❌ |
| created_at | timestamp without time zone | timestamp without time zone | ✅ |
| currency | - | text | ℹ️ |
| current_balance | - | numeric(12,2) | ℹ️ |
| id | integer | integer | ✅ |
| institution_id | - | integer | ℹ️ |
| is_active | boolean | boolean | ✅ |
| last_balance_update | - | timestamp without time zone | ℹ️ |
| limit_balance | - | numeric(12,2) | ℹ️ |
| mask | - | text | ℹ️ |
| name | - | text | ℹ️ |
| notes | text | ❌ MISSING | ❌ |
| obligated_amount | - | numeric(12,2) | ℹ️ |
| official_name | - | text | ℹ️ |
| plaid_account_id | - | text | ℹ️ |
| true_available_balance | - | numeric(12,2) | ℹ️ |
| updated_at | timestamp without time zone | timestamp without time zone | ✅ |

**Indexes:**
- `accounts_pkey`
- `accounts_plaid_account_id_key`
- `idx_accounts_active`
- `idx_accounts_institution`
- `idx_accounts_type`

### astrological_events

**Status:** ℹ️ Extra table (not in expected schema)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NO | gen_random_uuid() |
| event_type | character varying(50) | NO | - |
| body1 | character varying(50) | YES | - |
| body2 | character varying(50) | YES | - |
| degree | numeric(5,2) | YES | - |
| sign | character varying(20) | YES | - |
| house | integer | YES | - |
| exact_time | timestamp with time zone | NO | - |
| influence_start | timestamp with time zone | YES | - |
| influence_end | timestamp with time zone | YES | - |
| orb_degrees | numeric(4,2) | YES | - |
| description | text | YES | - |
| significance | text | YES | - |
| keywords | ARRAY | YES | - |
| created_at | timestamp with time zone | YES | now() |

### bundles

**Status:** ℹ️ Extra table (not in expected schema)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NO | gen_random_uuid() |
| name | text | YES | - |
| description | text | YES | - |
| bundle_price | numeric(10,2) | YES | - |
| item_count | integer | YES | - |
| status | text | YES | 'available'::text |
| sale_id | integer | YES | - |
| created_at | timestamp without time zone | YES | now() |

### categories

**Status:** ℹ️ Extra table (not in expected schema)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | integer | NO | nextval('categories_id_seq'::regclass) |
| name | text | NO | - |
| parent_category_id | integer | YES | - |
| category_type | text | YES | - |
| icon | text | YES | - |
| color | text | YES | - |
| is_system | boolean | YES | false |
| is_active | boolean | YES | true |
| sort_order | integer | YES | - |
| created_at | timestamp without time zone | YES | now() |

### category_mappings

**Rows:** 52

**Status:** ✅ Schema matches

| Column | Expected | Actual | Match |
|--------|----------|--------|-------|
| category_primary | character varying(100) | character varying(100) | ✅ |
| category_secondary | character varying(100) | character varying(100) | ✅ |
| created_at | timestamp without time zone | timestamp without time zone | ✅ |
| id | integer | integer | ✅ |
| is_active | boolean | boolean | ✅ |
| merchant_name | character varying(255) | character varying(255) | ✅ |
| pattern | character varying(255) | character varying(255) | ✅ |
| pattern_type | character varying(20) | character varying(20) | ✅ |
| priority | integer | integer | ✅ |

**Indexes:**
- `category_mappings_pkey`
- `idx_category_mappings_pattern`

### chat_messages

**Status:** ℹ️ Extra table (not in expected schema)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| message_id | integer | NO | nextval('chat_messages_message_id_seq'::regclass) |
| user_uuid | uuid | YES | - |
| telegram_user_id | bigint | YES | - |
| conversation_id | character varying(100) | YES | - |
| role | character varying(20) | YES | - |
| content | text | NO | - |
| mode | character varying(50) | YES | - |
| model_used | character varying(50) | YES | - |
| cypher_generated | text | YES | - |
| sql_generated | text | YES | - |
| response_time_ms | integer | YES | - |
| error_message | text | YES | - |
| created_at | timestamp without time zone | YES | now() |

### emotional_state_timeseries

**Status:** ℹ️ Extra table (not in expected schema)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| time | timestamp with time zone | NO | - |
| user_uuid | uuid | NO | - |
| conversation_id | character varying(100) | YES | - |
| message_id | integer | YES | - |
| emotional_tone | character varying(50) | YES | - |
| intensity | integer | YES | - |
| valence | numeric(3,2) | YES | - |
| arousal | numeric(3,2) | YES | - |
| context_notes | text | YES | - |
| themes | ARRAY | YES | - |

### entity_mention_timeseries

**Status:** ℹ️ Extra table (not in expected schema)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| time | timestamp with time zone | NO | - |
| user_uuid | uuid | NO | - |
| conversation_id | character varying(100) | YES | - |
| message_id | integer | YES | - |
| entity_canonical_id | character varying(255) | NO | - |
| entity_name | character varying(255) | NO | - |
| entity_type | character varying(50) | YES | - |
| mention_context | text | YES | - |
| confidence_score | numeric(3,2) | YES | - |
| extracted_by_node | character varying(20) | YES | - |

### grid_activation_timeseries

**Status:** ℹ️ Extra table (not in expected schema)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| time | timestamp with time zone | NO | - |
| user_uuid | uuid | NO | - |
| conversation_id | character varying(100) | YES | - |
| exchange_id | uuid | YES | - |
| message_id | integer | YES | - |
| anchor_score | integer | YES | - |
| echo_score | integer | YES | - |
| beacon_score | integer | YES | - |
| synth_score | integer | YES | - |
| nexus_score | integer | YES | - |
| mirror_score | integer | YES | - |
| glyph_score | integer | YES | - |
| harmonia_score | integer | YES | - |
| gateway_score | integer | YES | - |
| dominant_node | character varying(20) | YES | - |
| total_activation | integer | YES | - |
| analysis_model | character varying(50) | YES | - |
| processing_time_ms | integer | YES | - |

### import_logs

**Rows:** 0

**Status:** ✅ Schema matches

| Column | Expected | Actual | Match |
|--------|----------|--------|-------|
| account_id | integer | integer | ✅ |
| date_range_end | date | date | ✅ |
| date_range_start | date | date | ✅ |
| error_count | integer | integer | ✅ |
| file_path | text | text | ✅ |
| id | integer | integer | ✅ |
| imported_at | timestamp without time zone | timestamp without time zone | ✅ |
| imported_by | character varying(100) | character varying(100) | ✅ |
| imported_count | integer | integer | ✅ |
| notes | text | text | ✅ |
| skipped_count | integer | integer | ✅ |
| source_file | character varying(255) | character varying(255) | ✅ |
| total_rows | integer | integer | ✅ |

**Indexes:**
- `import_logs_pkey`

### institutions

**Status:** ℹ️ Extra table (not in expected schema)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | integer | NO | nextval('institutions_id_seq'::regclass) |
| item_id | text | NO | - |
| access_token | text | NO | - |
| institution_id | text | NO | - |
| institution_name | text | NO | - |
| status | text | YES | 'active'::text |
| last_successful_sync | timestamp without time zone | YES | - |
| last_sync_attempt | timestamp without time zone | YES | - |
| error_code | text | YES | - |
| error_message | text | YES | - |
| created_at | timestamp without time zone | YES | now() |
| updated_at | timestamp without time zone | YES | now() |

### item_images

**Status:** ℹ️ Extra table (not in expected schema)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | integer | NO | nextval('item_images_id_seq'::regclass) |
| item_id | uuid | YES | - |
| filename | text | NO | - |
| original_filename | text | YES | - |
| view_type | text | YES | - |
| is_primary | boolean | YES | false |
| asset_sha256 | text | YES | - |
| asset_rel_path | text | YES | - |
| telegram_file_id | text | YES | - |
| telegram_file_unique_id | text | YES | - |
| width | integer | YES | - |
| height | integer | YES | - |
| file_size_bytes | integer | YES | - |
| batch_name | text | YES | - |
| created_at | timestamp without time zone | YES | now() |

### items_for_sale

**Status:** ℹ️ Extra table (not in expected schema)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NO | gen_random_uuid() |
| item_type | text | NO | - |
| brand | text | YES | - |
| model | text | YES | - |
| title | text | YES | - |
| description | text | YES | - |
| category | text | NO | - |
| gender_category | text | NO | - |
| size_label | text | YES | - |
| size_numeric | numeric(5,1) | YES | - |
| size_width | text | YES | - |
| condition | text | NO | - |
| estimated_price | numeric(10,2) | YES | - |
| listed_price | numeric(10,2) | YES | - |
| colors | ARRAY | YES | - |
| materials | ARRAY | YES | - |
| features | jsonb | YES | - |
| country_of_manufacture | text | YES | - |
| original_retail_price | numeric(10,2) | YES | - |
| care_instructions | text | YES | - |
| confidence_score | numeric(3,2) | YES | - |
| inferred_fields | ARRAY | YES | - |
| extraction_notes | text | YES | - |
| status | text | YES | 'available'::text |
| sale_id | integer | YES | - |
| bundle_id | uuid | YES | - |
| created_at | timestamp without time zone | YES | now() |
| listed_date | timestamp without time zone | YES | - |
| sold_date | timestamp without time zone | YES | - |
| updated_at | timestamp without time zone | YES | now() |

### media_assets

**Status:** ℹ️ Extra table (not in expected schema)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| sha256 | text | NO | - |
| file_ext | text | YES | - |
| rel_path | text | NO | - |
| byte_size | integer | YES | - |
| created_at | timestamp without time zone | YES | now() |

### media_files

**Status:** ℹ️ Extra table (not in expected schema)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NO | gen_random_uuid() |
| user_uuid | uuid | NO | - |
| conversation_id | character varying(100) | YES | - |
| message_id | integer | YES | - |
| filename | text | NO | - |
| original_filename | text | YES | - |
| file_path | text | NO | - |
| file_size_bytes | bigint | YES | - |
| mime_type | text | NO | - |
| media_type | character varying(20) | NO | - |
| telegram_file_id | text | YES | - |
| telegram_file_unique_id | text | YES | - |
| width | integer | YES | - |
| height | integer | YES | - |
| aspect_ratio | numeric(5,3) | YES | - |
| processed | boolean | YES | false |
| analysis_data | jsonb | YES | - |
| extracted_text | text | YES | - |
| auto_tags | ARRAY | YES | - |
| user_tags | ARRAY | YES | - |
| uploaded_at | timestamp without time zone | YES | now() |
| processed_at | timestamp without time zone | YES | - |

### message_astrological_context

**Status:** ℹ️ Extra table (not in expected schema)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| message_id | integer | NO | - |
| astrological_event_id | uuid | NO | - |
| relevance_score | numeric(3,2) | YES | - |
| auto_linked | boolean | YES | true |

### obligations

**Status:** ℹ️ Extra table (not in expected schema)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | integer | NO | nextval('obligations_id_seq'::regclass) |
| description | text | NO | - |
| amount | numeric(12,2) | NO | - |
| obligation_date | date | NO | - |
| source_account_id | integer | YES | - |
| payment_account_id | integer | YES | - |
| fulfilled | boolean | YES | false |
| fulfilled_at | timestamp without time zone | YES | - |
| fulfilled_transaction_id | bigint | YES | - |
| notes | text | YES | - |
| created_by | text | YES | 'user'::text |
| created_at | timestamp without time zone | YES | now() |
| updated_at | timestamp without time zone | YES | now() |

### pending_intake

**Status:** ℹ️ Extra table (not in expected schema)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NO | gen_random_uuid() |
| telegram_user_id | bigint | NO | - |
| telegram_chat_id | bigint | NO | - |
| photo_count | integer | YES | 0 |
| photos | jsonb | YES | '[]'::jsonb |
| status | text | YES | 'collecting'::text |
| item_id | uuid | YES | - |
| error_message | text | YES | - |
| created_at | timestamp without time zone | YES | now() |
| updated_at | timestamp without time zone | YES | now() |

### people

**Status:** ℹ️ Extra table (not in expected schema)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | integer | NO | nextval('people_id_seq'::regclass) |
| prefix | character varying(20) | YES | - |
| first_name | character varying(100) | NO | - |
| middle_name | character varying(100) | YES | - |
| last_name | character varying(100) | NO | - |
| suffix | character varying(20) | YES | - |
| known_as | character varying(100) | YES | - |
| display_text | character varying(300) | YES | - |
| date_of_birth | date | YES | - |
| dob_year | integer | YES | - |
| dob_month | integer | YES | - |
| dob_day | integer | YES | - |
| time_of_birth | time without time zone | YES | - |
| birth_city | character varying(100) | YES | - |
| birth_state | character varying(100) | YES | - |
| birth_zip | character varying(20) | YES | - |
| birth_country | character varying(100) | YES | - |
| date_of_death | date | YES | - |
| dod_year | integer | YES | - |
| dod_month | integer | YES | - |
| dod_day | integer | YES | - |
| canonical_id | character varying(200) | YES | - |
| notes | text | YES | - |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| updated_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| created_by | character varying(100) | YES | - |
| modified_by | character varying(100) | YES | - |

### recurring_bills

**Rows:** 0

**Status:** ✅ Schema matches

| Column | Expected | Actual | Match |
|--------|----------|--------|-------|
| account_id | integer | integer | ✅ |
| amount_variance | numeric(12,2) | numeric(12,2) | ✅ |
| category_primary | character varying(100) | character varying(100) | ✅ |
| created_at | timestamp without time zone | timestamp without time zone | ✅ |
| expected_amount | numeric(12,2) | numeric(12,2) | ✅ |
| expected_day | integer | integer | ✅ |
| frequency | character varying(20) | character varying(20) | ✅ |
| id | integer | integer | ✅ |
| is_active | boolean | boolean | ✅ |
| merchant_name | character varying(255) | character varying(255) | ✅ |
| notes | text | text | ✅ |

**Indexes:**
- `recurring_bills_pkey`

### sales

**Status:** ℹ️ Extra table (not in expected schema)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| sale_id | integer | NO | nextval('sales_sale_id_seq'::regclass) |
| platform | text | NO | - |
| marketplace_title | text | YES | - |
| marketplace_description | text | YES | - |
| marketplace_listing_url | text | YES | - |
| marketplace_id | text | YES | - |
| asking_price | numeric(10,2) | YES | - |
| final_price | numeric(10,2) | YES | - |
| shipping_cost | numeric(10,2) | YES | 0 |
| buyer_name | text | YES | - |
| buyer_contact | text | YES | - |
| payment_method | text | YES | - |
| payment_status | text | YES | 'pending'::text |
| shipping_status | text | YES | 'not_applicable'::text |
| pickup_location | text | YES | 'Magro''s Restaurant & Pizzeria, 104 East Main Street, Norwich NY'::text |
| pickup_contact | text | YES | 'Hannah'::text |
| created_at | timestamp without time zone | YES | now() |
| listed_at | timestamp without time zone | YES | - |
| sold_at | timestamp without time zone | YES | - |
| updated_at | timestamp without time zone | YES | now() |

### sales_ingestion_log

**Status:** ℹ️ Extra table (not in expected schema)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | integer | NO | nextval('sales_ingestion_log_id_seq'::regclass) |
| batch_name | text | NO | - |
| artifact_type | text | NO | - |
| status | text | NO | - |
| extract_dir | text | YES | - |
| error | text | YES | - |
| items_created | integer | YES | - |
| created_at | timestamp without time zone | YES | now() |
| updated_at | timestamp without time zone | YES | now() |

### sync_log

**Status:** ℹ️ Extra table (not in expected schema)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | bigint | NO | nextval('sync_log_id_seq'::regclass) |
| institution_id | integer | YES | - |
| sync_started_at | timestamp without time zone | NO | - |
| sync_completed_at | timestamp without time zone | YES | - |
| duration_ms | integer | YES | - |
| status | text | NO | - |
| transactions_added | integer | YES | 0 |
| transactions_updated | integer | YES | 0 |
| transactions_removed | integer | YES | 0 |
| balances_updated | integer | YES | 0 |
| error_code | text | YES | - |
| error_message | text | YES | - |
| sync_type | text | YES | 'automatic'::text |
| created_at | timestamp without time zone | YES | now() |

### transaction_history

**Status:** ℹ️ Extra table (not in expected schema)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | bigint | NO | nextval('transaction_history_id_seq'::regclass) |
| transaction_id | bigint | NO | - |
| field_name | text | NO | - |
| old_value | text | YES | - |
| new_value | text | YES | - |
| changed_by | text | YES | - |
| changed_at | timestamp without time zone | YES | now() |
| reason | text | YES | - |

### transactions

**Rows:** 0

**Status:** ⚠️ Schema mismatch

**Missing Columns:**
- `balance` (expected: numeric(12,2))
- `bank_transaction_id` (expected: character varying(100))
- `category_primary` (expected: character varying(100))
- `category_secondary` (expected: character varying(100))
- `created_at` (expected: timestamp without time zone)
- `description` (expected: text)
- `hash_id` (expected: character varying(64))
- `imported_by` (expected: character varying(100))
- `original_description` (expected: text)
- `source_file` (expected: character varying(255))

**Extra Columns (in DB, not expected):**
- `authorized_date` (date)
- `category` (ARRAY)
- `currency` (text)
- `imported_at` (timestamp without time zone)
- `location_address` (text)
- `location_city` (text)
- `location_country` (text)
- `location_postal_code` (text)
- `location_region` (text)
- `name` (text)
- `payment_channel` (text)
- `plaid_transaction_id` (text)
- `previous_version_id` (bigint)
- `primary_category` (text)
- `recurring_pattern_id` (integer)
- `subcategory` (text)
- `tags` (ARRAY)
- `version` (integer)

| Column | Expected | Actual | Match |
|--------|----------|--------|-------|
| account_id | integer | integer | ✅ |
| amount | numeric(12,2) | numeric(12,2) | ✅ |
| authorized_date | - | date | ℹ️ |
| balance | numeric(12,2) | ❌ MISSING | ❌ |
| bank_transaction_id | character varying(100) | ❌ MISSING | ❌ |
| category | - | ARRAY | ℹ️ |
| category_primary | character varying(100) | ❌ MISSING | ❌ |
| category_secondary | character varying(100) | ❌ MISSING | ❌ |
| created_at | timestamp without time zone | ❌ MISSING | ❌ |
| currency | - | text | ℹ️ |
| description | text | ❌ MISSING | ❌ |
| hash_id | character varying(64) | ❌ MISSING | ❌ |
| id | integer | bigint | ⚠️ |
| imported_at | - | timestamp without time zone | ℹ️ |
| imported_by | character varying(100) | ❌ MISSING | ❌ |
| is_pending | boolean | boolean | ✅ |
| is_recurring | boolean | boolean | ✅ |
| location_address | - | text | ℹ️ |
| location_city | - | text | ℹ️ |
| location_country | - | text | ℹ️ |
| location_postal_code | - | text | ℹ️ |
| location_region | - | text | ℹ️ |
| merchant_name | character varying(255) | text | ⚠️ |
| name | - | text | ℹ️ |
| notes | text | text | ✅ |
| original_description | text | ❌ MISSING | ❌ |
| payment_channel | - | text | ℹ️ |
| plaid_transaction_id | - | text | ℹ️ |
| post_date | date | date | ✅ |
| previous_version_id | - | bigint | ℹ️ |
| primary_category | - | text | ℹ️ |
| recurring_pattern_id | - | integer | ℹ️ |
| source_file | character varying(255) | ❌ MISSING | ❌ |
| subcategory | - | text | ℹ️ |
| tags | - | ARRAY | ℹ️ |
| transaction_date | date | date | ✅ |
| transaction_type | character varying(50) | text | ⚠️ |
| updated_at | timestamp without time zone | timestamp without time zone | ✅ |
| version | - | integer | ℹ️ |

**Indexes:**
- `idx_transactions_account`
- `idx_transactions_category`
- `idx_transactions_date`
- `idx_transactions_merchant`
- `idx_transactions_pending`
- `idx_transactions_plaid_id`
- `transactions_pkey`
- `transactions_plaid_transaction_id_key`

### users

**Status:** ℹ️ Extra table (not in expected schema)

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| user_uuid | uuid | NO | gen_random_uuid() |
| username | character varying(50) | NO | - |
| telegram_id | bigint | YES | - |
| soul_canonical_id | character varying(100) | YES | - |
| soul_display_name | character varying(100) | YES | - |
| created_at | timestamp without time zone | YES | now() |

## 🔧 Suggested Migration SQL

Run these commands to fix schema issues:

```sql
ALTER TABLE accounts ADD COLUMN bank_name character varying(100);
ALTER TABLE accounts ADD COLUMN account_name character varying(255);
ALTER TABLE accounts ADD COLUMN account_number character varying(50);
ALTER TABLE accounts ADD COLUMN notes text;
ALTER TABLE transactions ADD COLUMN description text;
ALTER TABLE transactions ADD COLUMN original_description text;
ALTER TABLE transactions ADD COLUMN balance numeric(12,2);
ALTER TABLE transactions ADD COLUMN category_primary character varying(100);
ALTER TABLE transactions ADD COLUMN category_secondary character varying(100);
ALTER TABLE transactions ADD COLUMN bank_transaction_id character varying(100);
ALTER TABLE transactions ADD COLUMN hash_id character varying(64);
ALTER TABLE transactions ADD COLUMN source_file character varying(255);
ALTER TABLE transactions ADD COLUMN imported_by character varying(100);
ALTER TABLE transactions ADD COLUMN created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP;
```
