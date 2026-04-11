# finance/schema_report.md

**Language:** markdown
**Stream:** SYS
**Module:** Finance System
**Lines:** 705

---

### Purpose
The `finance/schema_report.md` file provides a detailed report on the current state of the database schema for the Mythos Finance subsystem. It compares the expected schema with the actual schema, highlighting any discrepancies, extra tables, and missing columns.

### Architecture
The file is a markdown document that contains structured information about the database schema. It includes:
- A summary section with metrics on expected and actual tables.
- A list of extra tables not in the expected schema.
- Detailed information for each table, including rows, status, missing and extra columns, and indexes.

### Patterns
No design patterns are applicable as this is a static report file and not executable code.

### Dependencies
This file does not import or rely on any external dependencies. It is a static report generated from the database schema.

### Interfaces
This file does not expose any interfaces as it is a static report and not an executable component.

### Database
The report covers various tables in the PostgreSQL database used by the Mythos Finance subsystem. It includes tables such as `accounts`, `astrological_events`, `bundles`, `categories`, `category_mappings`, `chat_messages`, `emotional_state_timeseries`, `entity_mention_timeseries`, `grid_activation_timeseries`, `import_logs`, `institutions`, `item_images`, `items_for_sale`, and `media_assets`.

### Configuration
The report does not use any configuration files or environment variables. It is a static document generated from the database schema.

### Key Logic
The key logic involves comparing the expected schema with the actual schema and identifying any discrepancies. This is achieved through:
- Counting the number of expected and actual tables.
- Listing extra tables not in the expected schema.
- Detailing each table with information on rows, status, missing and extra columns, and indexes.

### Integration Points
This file integrates with the Mythos Finance subsystem by providing a comprehensive report on the database schema. It helps in identifying and resolving schema discrepancies, ensuring that the database structure aligns with the expected design.

### Detailed Analysis

#### Summary
- **Expected Tables:** 5
- **Actual Tables:** 26
- **Missing Tables:** 0
- **Extra Tables:** 21

#### Extra Tables
- `astrological_events`
- `bundles`
- `categories`
- `chat_messages`
- `emotional_state_timeseries`
- `entity_mention_timeseries`
- `grid_activation_timeseries`
- `institutions`
- `item_images`
- `items_for_sale`
- `media_assets`
- `media_files`
- `message_astrological_context`
- `obligations`
- `pending_intake`
- `people`
- `sales`
- `sales_ingestion_log`
- `sync_log`
- `transaction_history`
- `users`

#### Table Details
- **accounts**
  - **Rows:** 0
  - **Status:** ⚠️ Schema mismatch
  - **Missing Columns:** `account_name`, `account_number`, `bank_name`, `notes`
  - **Extra Columns:** `account_subtype`, `available_balance`, `currency`, `current_balance`, `institution_id`, `last_balance_update`, `limit_balance`, `mask`, `name`, `obligated_amount`, `official_name`, `plaid_account_id`, `true_available_balance`
  - **Indexes:** `accounts_pkey`, `accounts_plaid_account_id_key`, `idx_accounts_active`, `idx_accounts_institution`, `idx_accounts_type`

- **astrological_events**
  - **Status:** ℹ️ Extra table (not in expected schema)
  - **Columns:** `id`, `event_type`, `body1`, `body2`, `degree`, `sign`, `house`, `exact_time`, `influence_start`, `influence_end`, `orb_degrees`, `description`, `significance`, `keywords`, `created_at`

- **bundles**
  - **Status:** ℹ️ Extra table (not in expected schema)
  - **Columns:** `id`, `name`, `description`, `bundle_price`, `item_count`, `status`, `sale_id`, `created_at`

- **categories**
  - **Status:** ℹ️ Extra table (not in expected schema)
  - **Columns:** `id`, `name`, `parent_category_id`, `category_type`, `icon`, `color`, `is_system`, `is_active`, `sort_order`, `created_at`

- **category_mappings**
  - **Rows:** 52
  - **Status:** ✅ Schema matches
  - **Columns:** `category_primary`, `category_secondary`, `created_at`, `id`, `is_active`, `merchant_name`, `pattern`, `pattern_type`, `priority`
  - **Indexes:** `category_mappings_pkey`, `idx_category_mappings_pattern`

- **chat_messages**
  - **Status:** ℹ️ Extra table (not in expected schema)
  - **Columns:** `message_id`, `user_uuid`, `telegram_user_id`, `conversation_id`, `role`, `content`, `mode`, `model_used`, `cypher_generated`, `sql_generated`, `response_time_ms`, `error_message`, `created_at`

- **emotional_state_timeseries**
  - **Status:** ℹ️ Extra table (not in expected schema)
  - **Columns:** `time`, `user_uuid`, `conversation_id`, `message_id`, `emotional_tone`, `intensity`, `valence`, `arousal`, `context_notes`, `themes`

- **entity_mention_timeseries**
  - **Status:** ℹ️ Extra table (not in expected schema)
  - **Columns:** `time`, `user_uuid`, `conversation_id`, `message_id`, `entity_canonical_id`, `entity_name`, `entity_type`, `mention_context`, `confidence_score`, `extracted_by_node`

- **grid_activation_timeseries**
  - **Status:** ℹ️ Extra table (not in expected schema)
  - **Columns:** `time`, `user_uuid`, `conversation_id`, `exchange_id`, `message_id`, `anchor_score`, `echo_score`, `beacon_score`, `synth_score`, `nexus_score`, `mirror_score`, `glyph_score`, `harmonia_score`, `gateway_score`, `dominant_node`, `total_activation`, `analysis_model`, `processing_time_ms`

- **import_logs**
  - **Rows:** 0
  - **Status:** ✅ Schema matches
  - **Columns:** `account_id`, `date_range_end`, `date_range_start`, `error_count`, `file_path`, `id`, `imported_at`, `imported_by`, `imported_count`, `notes`, `skipped_count`, `source_file`, `total_rows`
  - **Indexes:** `import_logs_pkey`

- **institutions**
  - **Status:** ℹ️ Extra table (not in expected schema)
  - **Columns:** `id`, `item_id`, `access_token`, `institution_id`, `institution_name`, `status`, `last_successful_sync`, `last_sync_attempt`, `error_code`, `error_message`, `created_at`, `updated_at`

- **item_images**
  - **Status:** ℹ️ Extra table (not in expected schema)
  - **Columns:** `id`, `item_id`, `filename`, `original_filename`, `view_type`, `is_primary`, `asset_sha256`, `asset_rel_path`, `telegram_file_id`, `telegram_file_unique_id`, `width`, `height`, `file_size_bytes`, `batch_name`, `created_at`

- **items_for_sale**
  - **Status:** ℹ️ Extra table (not in expected schema)
  - **Columns:** `id`, `item_type`, `brand`, `model`, `title`, `description`, `category`, `gender_category`, `size_label`, `size_numeric`, `size_width`, `condition`, `estimated_price`, `listed_price`, `colors`, `materials`, `features`, `country_of_manufacture`, `original_retail_price`, `care_instructions`, `confidence_score`, `inferred_fields`, `extraction_notes`, `status`, `sale_id`, `bundle_id`, `created_at`, `listed_date`, `sold_date`, `updated_at`

- **media_assets**
  - **Status:** ℹ️ Extra table (not in expected schema)
  - **Columns:** `sha256`, `file_ext`, `rel_path`, `byte_size`, `created_at`

This report helps in maintaining the integrity and consistency of the database schema by identifying and documenting any deviations from the expected schema.
