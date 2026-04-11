# migrations/migration_0057_perception_layer.sql

**Language:** sql
**Stream:** SYS
**Module:** Database Migrations
**Lines:** 238

---

### File: migrations/migration_0057_perception_layer.sql

#### Purpose
This SQL file defines the schema for the Perception Layer of the Mythos system, creating three tables: `perception_log`, `idea_inbox`, and `idea_backlog`. It also creates several views to help with querying these tables.

#### Architecture
The file consists of SQL commands to create tables and views. Each table is designed to capture different stages of the perception and idea processing pipeline:
- `perception_log`: Captures raw input data.
- `idea_inbox`: Stores auto-captured lists from conversations for review.
- `idea_backlog`: Curates ideas that have survived the review process.

#### Patterns
- **Table Creation**: Uses standard SQL `CREATE TABLE` statements.
- **Indexes**: Multiple indexes are created to optimize query performance.
- **Views**: Helper views are created to provide pre-filtered and sorted data.

#### Dependencies
- PostgreSQL database.
- `gen_random_uuid()` function for generating UUIDs.

#### Interfaces
- **Tables**:
  - `perception_log`: Exposes raw perception data.
  - `idea_inbox`: Exposes auto-captured lists.
  - `idea_backlog`: Exposes curated ideas.
- **Views**:
  - `v_inbox_pending`: Lists pending items in the idea inbox.
  - `v_backlog_open`: Lists open items in the idea backlog.
  - `v_perception_recent`: Lists recent perceptions.

#### Database
- **Tables**:
  - `perception_log`: Stores raw perception data.
  - `idea_inbox`: Stores auto-captured lists for review.
  - `idea_backlog`: Stores curated ideas.
- **Indexes**: Multiple indexes are created on each table to optimize queries.
- **Views**: Pre-defined views for querying specific subsets of data.

#### Configuration
- No explicit configuration files or environment variables are used in this migration file. However, the system relies on PostgreSQL settings and configurations.

#### Key Logic
- **Perception Log**:
  - Captures raw input data with metadata and processing results.
  - Tracks the level of processing (`processed_to_level`).
  - Includes soft delete (`is_deleted`).
- **Idea Inbox**:
  - Captures lists of ideas or options from conversations.
  - Tracks review status and disposition.
  - Includes metadata like domain and tags.
- **Idea Backlog**:
  - Curates ideas that have survived the review process.
  - Tracks priority, status, and relationships.
  - Includes progress tracking and notes.

#### Integration Points
- **Perception Log**:
  - Linked to `idea_inbox` via `idea_inbox_ids`.
  - Linked to Neo4j memory nodes via `memory_ids`.
- **Idea Inbox**:
  - Linked to `perception_log` via `perception_id`.
  - Linked to `idea_backlog` via `kept_item_ids`.
- **Idea Backlog**:
  - Linked to `idea_inbox` via `inbox_id`.
  - Linked to `perception_log` via `perception_id`.
  - Supports sub-tasks via `parent_id`.

### Summary
This migration file sets up the foundational tables and views for the Perception Layer of the Mythos system, enabling the capture, review, and curation of ideas and perceptions. The design includes comprehensive metadata and indexing to support efficient querying and processing.
