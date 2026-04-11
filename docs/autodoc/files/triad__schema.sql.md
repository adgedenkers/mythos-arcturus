# triad/schema.sql

**Language:** sql
**Stream:** LOG
**Module:** Triad Identity System
**Lines:** 135

---

### Purpose
The `triad/schema.sql` file defines the schema for the Triad Memory System, which consists of three layers: Grid (Knowledge), Akashic (Wisdom), and Prophetic (Vision). It creates tables for storing conversation records and their respective extractions, along with indexes for efficient querying and similarity search.

### Architecture
The schema is designed with a central `triad_conversations` table that links to three other tables (`triad_grid`, `triad_akashic`, `triad_prophetic`) representing the three layers of the Triad Memory System. Each layer table contains specific fields relevant to its purpose, and all tables are linked via `conversation_id`. Additionally, a `triad_patterns` table is created to catalog pattern signatures for consistency.

### Patterns
- **Normalization**: The schema normalizes data across multiple tables to avoid redundancy and ensure data integrity.
- **Indexing**: Indexes are used to optimize query performance, especially for common queries and similarity searches.

### Dependencies
- **PostgreSQL Extensions**: The schema depends on the `vector` extension for vector-based similarity search.
- **UUID Generation**: The `gen_random_uuid()` function is used to generate unique identifiers.

### Interfaces
- **Tables**: The schema exposes several tables (`triad_conversations`, `triad_grid`, `triad_akashic`, `triad_prophetic`, `triad_patterns`) for data storage and retrieval.
- **Indexes**: Indexes are created for efficient querying and similarity search.

### Database
- **Tables**:
  - `triad_conversations`: Stores main conversation records.
  - `triad_grid`: Stores knowledge extractions.
  - `triad_akashic`: Stores wisdom extractions.
  - `triad_prophetic`: Stores vision extractions.
  - `triad_patterns`: Catalogs pattern signatures.

### Configuration
- **Environment Variables**: No explicit environment variables are used in this schema file.
- **Configuration Files**: No configuration files are referenced directly.

### Key Logic
- **Data Integrity**: The schema ensures data integrity through foreign key constraints and unique constraints.
- **Embeddings**: Each layer table includes an `embedding` field for vector-based similarity search.
- **Indexes**: Indexes are created to optimize common queries and similarity searches.

### Integration Points
- **Triad Conversations**: This table serves as the central point for linking all three layers (`triad_grid`, `triad_akashic`, `triad_prophetic`).
- **Pattern Catalog**: The `triad_patterns` table is used to maintain a catalog of pattern signatures, which can be referenced across the system for consistency.
- **Indexes**: The indexes created in this schema will be used by other parts of the Mythos system to efficiently query and retrieve data.

### Detailed Breakdown of Tables and Indexes

#### `triad_conversations`
- **Columns**:
  - `id`: UUID primary key, auto-generated.
  - `created_at`: Timestamp of creation.
  - `spiral_day`: Spiral time anchor (1-9).
  - `spiral_cycle`: Spiral cycle.
  - `source_type`: Type of source (e.g., 'claude_export', 'telegram').
  - `source_id`: Identifier of the source.
  - `content_hash`: Hash of the content for integrity.
  - `grid_extracted`, `akashic_extracted`, `prophetic_extracted`: Boolean flags indicating extraction status.

#### `triad_grid`
- **Columns**:
  - `id`: UUID primary key, auto-generated.
  - `conversation_id`: Foreign key linking to `triad_conversations`.
  - `extracted_at`: Timestamp of extraction.
  - `node_1_context` to `node_9_declarations`: JSONB fields for storing semantic nodes.
  - `embedding`: Vector field for knowledge retrieval.

#### `triad_akashic`
- **Columns**:
  - `id`: UUID primary key, auto-generated.
  - `conversation_id`: Foreign key linking to `triad_conversations`.
  - `extracted_at`: Timestamp of extraction.
  - `entry_valence`, `exit_valence`: Valence values (-5 to 5).
  - `entry_quality`, `exit_quality`: Quality descriptions.
  - `arc_type`: Type of arc (e.g., 'resolution', 'activation').
  - `essence`: Distillation of the conversation.
  - `pattern_signature`: Named pattern.
  - `domains`: Array of domain names.
  - `echoes`, `witnessed_by`: Descriptions and entities.
  - `embedding`: Vector field for pattern matching.

#### `triad_prophetic`
- **Columns**:
  - `id`: UUID primary key, auto-generated.
  - `conversation_id`: Foreign key linking to `triad_conversations`.
  - `extracted_at`: Timestamp of extraction.
  - `vector`, `attractor`: Trajectory descriptions.
  - `readiness`, `obstacle`: Readiness and obstacles.
  - `invitation`, `seed`: Invitation and seed.
  - `convergences`: Array of convergences.
  - `embedding`: Vector field for convergence sensing.

#### `triad_patterns`
- **Columns**:
  - `id`: UUID primary key, auto-generated.
  - `signature`: Unique pattern signature.
  - `description`: Description of the pattern.
  - `domain`: Domain of the pattern.
  - `first_seen`: Timestamp of first occurrence.
  - `occurrence_count`: Count of occurrences.

#### Indexes
- **Common Queries**:
  - `idx_triad_conv_spiral`: Index on `spiral_cycle` and `spiral_day`.
  - `idx_triad_conv_created`: Index on `created_at`.
  - `idx_triad_akashic_pattern`: Index on `pattern_signature`.
  - `idx_triad_akashic_arc`: Index on `arc_type`.
  - `idx_triad_akashic_domains`: GIN index on `domains`.
  - `idx_triad_prophetic_seed`: Index on `seed`.

- **Vector Similarity Search**:
  - `idx_triad_grid_embedding`: IVFFlat index on `embedding` for `triad_grid`.
  - `idx_triad_akashic_embedding`: IVFFlat index on `embedding` for `triad_akashic`.
  - `idx_triad_prophetic_embedding`: IVFFlat index on `embedding` for `triad_prophetic`.

This schema provides a robust foundation for the Triad Memory System, enabling efficient storage, retrieval, and similarity search of conversation data across multiple layers.
