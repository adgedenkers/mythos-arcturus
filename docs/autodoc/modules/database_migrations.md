# Database Migrations

**Stream:** SYS
**Files:** 9

## Files in this Module

- `migrations/grocery_tables.sql` (57L)
- `migrations/migration_0057_perception_layer.sql` (238L)
- `migrations/migration_0122_consciousness_stream.sql` (122L)
- `migrations/migration_0186_conversation_metadata.sql` (274L)
- `migrations/migration_0186_neo4j_schema.cypher` (235L)
- `migrations/neu_0011_grid_manifest.sql` (153L)
- `migrations/sys_0034_trigger_schema.sql` (209L)
- `migrations/sys_0035_trigger_schema.sql` (209L)
- `migrations/sys_0052_watchlist.sql` (19L)

---

# Mythos Database Migrations Module Documentation

## 1. Module Purpose
The **Database Migrations** module manages schema evolution and data structure initialization for the Mythos system. It ensures consistent database state across PostgreSQL and Neo4j environments by:
- Creating tables, indexes, and constraints for core subsystems (grocery management, perception layer, conversation tracking, etc.)
- Defining graph schema for Neo4j integration
- Implementing versioned schema changes through migration scripts
- Optimizing query performance through indexing strategies
- Enabling full-text search and vector operations for advanced querying

## 2. Architecture Overview
The module follows a layered architecture with two primary database components:

**PostgreSQL Layer**:
- **Schema Evolution**: Migration scripts follow a versioned naming pattern (e.g., migration_0057_perception_layer.sql)
- **Table Relationships**: Creates interconnected tables with foreign key constraints (e.g., `grocery_items` references `grocery_lists`)
- **Index Strategy**: Creates targeted indexes for common query patterns (e.g., `idx_grocery_items_list` on `list_id`)
- **Extension Support**: Conditionally enables extensions like `pgvector` and `citext`

**Neo4j Layer**:
- **Graph Schema**: Defines node labels, relationship types, and constraints via Cypher
- **Hybrid Architecture**: Stores raw content in PostgreSQL while using Neo4j for relationship tracking
- **Synchronization**: Maintains bidirectional relationships between SQL and graph data (e.g., `neo4j_node_id` fields)

**Data Flow**:
1. Migration scripts execute in version order
2. Schema changes propagate to both SQL and graph databases
3. Application code interacts with the resulting schema through ORM and graph clients
4. Indexes and constraints enforce data integrity and optimize queries

## 3. Key Components

### PostgreSQL Components
| Component | Purpose | Key Features |
|----------|---------|--------------|
| `grocery_tables.sql` | Grocery list management | Tables for aisles, lists, and items with indexing strategy |
| `migration_0057_perception_layer.sql` | Idea processing pipeline | `perception_log`, `idea_inbox`, `idea_backlog` with status tracking |
| `migration_0122_consciousness_stream.sql` | Conversation segmentation | `conversation_segments` and `conversation_subject_points` with vector support |
| `migration_0186_conversation_metadata.sql` | Conversation metadata | Normalized tables for participants, turns, and thread groups |
| `migration_0186_neo4j_schema.cypher` | Graph schema | Node/relationship types for conversation analysis |
| `neu_0011_grid_manifest.sql` | Knowledge extraction | Tracks processing provenance and extracted knowledge |
| `sys_0034/35_trigger_schema.sql` | Automation framework | Tables for scheduled triggers and escalation rules |
| `sys_0052_watchlist.sql` | Media tracking | Watchlist management with full-text search |

### Neo4j Components
| Component | Purpose |
|----------|---------|
| Node Labels | `Conversation`, `Person`, `Topic`, `SpiritualConcept` |
| Relationship Types | `INVOLVES`, `MENTIONS`, `BELONGS_TO`, `CONTINUES` |
| Constraints | Unique constraints on node identifiers |
| Indexes | Optimized for common query patterns (e.g., `:Conversation(conversation_id)`) |

## 4. Design Patterns
1. **Schema Versioning**: Migration files use numeric prefixes (e.g., 0057, 0122) for ordered execution
2. **Conditional Execution**: Uses `DO $$ ... $$` blocks for optional extension handling
3. **Normalization**: Splits data into related tables (e.g., `conversation_participants` vs. `conversations`)
4. **Index Optimization**: Creates indexes based on query patterns (e.g., `idx_csp_tags` for tag-based filtering)
5. **Singleton Pattern**: Ensures unique creation of extensions/enums with `IF NOT EXISTS` clauses
6. **Idempotent Operations**: Uses `MERGE` in Neo4j and `INSERT ... ON CONFLICT` in PostgreSQL for safe updates

## 5. Data Model

### PostgreSQL Tables
| Table | Description | Key Columns |
|-------|-------------|-------------|
| `grocery_aisles` | Predefined store aisles | `id`, `name`, `sort_order`, `icon` |
| `grocery_lists` | User grocery lists | `id`, `telegram_user_id`, `name` |
| `grocery_items` | List items with status | `id`, `list_id`, `aisle_id`, `checked` |
| `perception_log` | Raw input tracking | `id`, `input_text`, `processed_to_level` |
| `idea_inbox` | Auto-captured ideas | `id`, `perception_id`, `review_status` |
| `idea_backlog` | Curated ideas | `id`, `inbox_id`, `priority`, `status` |
| `scheduled_triggers` | Automation framework | `id`, `name`, `schedule`, `action_type` |
| `watchlist` | Media tracking | `id`, `title`, `platform`, `status` |

### Neo4j Schema
**Node Labels**:
- `Conversation` (properties: `conversation_id`, `summary`)
- `Person` (properties: `person_id`, `name`)
- `Topic` (properties: `topic_id`, `name`)

**Relationship Types**:
- `INVOLVES` (Conversation → Person)
- `MENTIONS` (Conversation → Topic)
- `CONTINUES` (Conversation → Conversation)

## 6. API Surface
**Exposed Tables/Views**:
- `grocery_aisles`, `grocery_lists`, `grocery_items` (grocery management)
- `perception_log`, `idea_inbox`, `idea_backlog` (perception layer)
- `conversation_segments`, `conversation_subject_points` (consciousness stream)
- `scheduled_triggers`, `trigger_log` (automation framework)

**Exposed Views**:
- `v_inbox_pending` (pending ideas)
- `v_backlog_open` (active backlog items)
- `v_perception_recent` (recent perceptions)

**Graph Schema**:
- Node labels and relationship types defined in `migration_0057_perception_layer.sql`

## 7. Dependencies
**Database Requirements**:
- PostgreSQL 12+ with:
  - `pgvector` extension (for vector operations)
  - `citext` extension (case-insensitive text)
  - `pgcrypto` (for UUID generation)
- Neo4j 4.4+ with:
  - Full-text indexes
  - Constraint enforcement

**System Integrations**:
- **Telegram**: `grocery_lists` table uses `telegram_user_id` for user association
- **Neo4j**: PostgreSQL tables include `neo4j_node_id` fields for graph synchronization
- **Arcturian Grid**: `grid_processing_manifest` tracks knowledge extraction provenance

## 8. Configuration
**Database Configuration**:
- **PostgreSQL**:
  - Ensure `pgvector` is installed: `CREATE EXTENSION IF NOT EXISTS vector;`
  - Configure `search_path` to include migration schemas
- **Neo4j**:
  - Create constraints: `CREATE CONSTRAINT FOR (c:Conversation) REQUIRE c.conversation_id IS UNIQUE`
  - Create indexes: `CREATE INDEX FOR (t:Topic) ON (t.name)`

**Environment Variables**:
- Not directly used in migration files, but system-level configuration may include:
  - `DATABASE_URL` for PostgreSQL connection
  - `NEO4J_URI` for Neo4j connection
  - `MIGRATION_DIR` for migration script location

**Execution Order**:
1. Run all `grocery_tables.sql` first
2. Execute perception layer migrations (0057-0122)
3. Apply conversation metadata (0186)
4. Configure Neo4j schema
5. Run trigger and watchlist migrations (0034-0052)

---

This module forms the foundational data infrastructure for Mythos, enabling complex interactions between SQL and graph databases while maintaining performance and data integrity through strategic indexing and schema design.
