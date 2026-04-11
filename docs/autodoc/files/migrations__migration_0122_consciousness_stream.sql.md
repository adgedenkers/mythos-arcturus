# migrations/migration_0122_consciousness_stream.sql

**Language:** sql
**Stream:** SYS
**Module:** Database Migrations
**Lines:** 122

---

### Purpose
This SQL file (`migrations/migration_0122_consciousness_stream.sql`) is a database migration script that creates two new tables: `conversation_segments` and `conversation_subject_points`. These tables are designed to track the linear progression and segmentation of conversations within the Mythos system.

### Architecture
The file consists of several sections:
1. **Enabling pgvector Extension**: Conditionally enables the `pgvector` extension for vector operations.
2. **Creating `conversation_segments` Table**: Defines the structure of the `conversation_segments` table, including various fields such as `id`, `created_at`, `updated_at`, `chat_id`, `status`, `subject_summary`, `subject_tags`, and more.
3. **Creating `conversation_subject_points` Table**: Defines the structure of the `conversation_subject_points` table, including fields like `id`, `created_at`, `chat_id`, `perception_id`, `segment_id`, `subject_summary`, `subject_tags`, and more.
4. **Adding Vector Column Conditionally**: Adds a `subject_vector` column to `conversation_subject_points` if `pgvector` is available.
5. **Creating Indexes**: Creates several indexes to optimize queries on both tables.
6. **Recording Migration**: Inserts a record into the `perception_log` table to log the migration.

### Patterns
- **Conditional Execution**: The script uses conditional execution blocks (`DO $$ ... $$`) to enable the `pgvector` extension and add the `subject_vector` column only if the extension is available.
- **Transaction Management**: The entire script is wrapped in a `BEGIN; ... COMMIT;` block to ensure atomicity.

### Dependencies
- **PostgreSQL Extensions**: The script relies on the `pgvector` extension for vector operations, but it is non-fatal if the extension is not installed.
- **Existing Tables**: The script references the `perception_log` table for logging the migration.

### Interfaces
- **Tables**: The script exposes two new tables: `conversation_segments` and `conversation_subject_points`.
- **Indexes**: Several indexes are created to optimize queries on these tables.

### Database
- **Tables Created**:
  - `conversation_segments`: Tracks the segments of conversations.
  - `conversation_subject_points`: Tracks the linear progression of conversation subjects.
- **Indexes Created**:
  - `idx_cs_chat_status`, `idx_cs_chat_updated`, `idx_cs_status` for `conversation_segments`.
  - `idx_csp_chat_created`, `idx_csp_segment`, `idx_csp_tags`, `idx_csp_created` for `conversation_subject_points`.

### Configuration
- **Environment Variables**: No specific environment variables are used directly in this script.
- **Configuration Files**: No configuration files are referenced.

### Key Logic
- **Conditional Extension Handling**: The script conditionally handles the `pgvector` extension and the `subject_vector` column to ensure compatibility.
- **Index Creation**: Indexes are created to optimize queries on the `chat_id`, `status`, `updated_at`, `created_at`, and `subject_tags` fields.

### Integration Points
- **Perception Log**: The script logs the migration in the `perception_log` table, integrating with the logging subsystem.
- **Foreign Key References**: The `conversation_subject_points` table references the `perception_log` and `conversation_segments` tables, integrating with other parts of the Mythos system.

This migration script is crucial for setting up the infrastructure to track and segment conversations, providing a foundation for further analysis and processing within the Mythos system.
