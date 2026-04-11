# migrations/neu_0011_grid_manifest.sql

**Language:** sql
**Stream:** SYS
**Module:** Database Migrations
**Lines:** 153

---

### Purpose
This SQL file, `neu_0011_grid_manifest.sql`, defines the database schema for tracking the processing provenance and knowledge extraction within the Arcturian Grid of the Mythos system. It includes tables for grid processing manifest, knowledge extractions, and grid version registry.

### Architecture
The file consists of three main sections:
1. **Grid Processing Manifest**: A table to log detailed processing information for each node-layer activation.
2. **Knowledge Extractions**: A table to store every piece of knowledge extracted by the nodes.
3. **Grid Version Registry**: A table to manage the versions and changelogs of each node-layer combination.

### Patterns
- **Entity-Relationship Pattern**: The tables are designed to capture the relationships between exchanges, nodes, and knowledge extractions.
- **Audit Logging Pattern**: The `grid_processing_manifest` table logs detailed processing information for auditing purposes.

### Dependencies
- **PostgreSQL**: The file relies on PostgreSQL for creating and managing the tables.
- **Neo4j**: The `knowledge_extractions` table includes fields for Neo4j integration (`neo4j_node_id`, `neo4j_synced`, `neo4j_synced_at`).

### Interfaces
- **Grid Processing Manifest**: Exposes fields for tracking processing details and provenance.
- **Knowledge Extractions**: Exposes fields for storing extracted knowledge and its provenance.
- **Grid Version Registry**: Exposes fields for managing node-layer versions and changelogs.

### Database
- **Tables Created**:
  - `grid_processing_manifest`: Tracks processing details.
  - `knowledge_extractions`: Stores extracted knowledge.
  - `grid_version_registry`: Manages node-layer versions.

### Configuration
- **Environment Variables**: No specific environment variables are used in this file.
- **Configuration Files**: No configuration files are referenced directly.

### Key Logic
- **Grid Processing Manifest**: Captures detailed processing information including node, layer, version, input/output hashes, and timestamps.
- **Knowledge Extractions**: Stores extracted knowledge with provenance details, significance, and lifecycle status.
- **Grid Version Registry**: Manages versions and changelogs for each node-layer combination.

### Integration Points
- **Grid Processing Manifest**: Integrates with the Arcturian Grid to log processing details.
- **Knowledge Extractions**: Integrates with the Arcturian Grid to store extracted knowledge and Neo4j for graph database synchronization.
- **Grid Version Registry**: Integrates with the Arcturian Grid to manage node-layer versions.

### Detailed Breakdown

#### Grid Processing Manifest
- **Purpose**: Logs detailed processing information for each node-layer activation.
- **Fields**:
  - `id`: Unique identifier.
  - `exchange_id`: Links to grid activation timeseries and Neo4j Exchange.
  - `conversation_id`: Conversation identifier.
  - `user_uuid`: User identifier.
  - `node`: Node type (e.g., anchor, echo, beacon).
  - `layer`: Layer number.
  - `version`: Version of the node-layer.
  - `prompt_hash`: SHA256 hash of the prompt.
  - `activated`: Boolean indicating if the node-layer was activated.
  - `skipped_reason`: Reason for skipping if not activated.
  - `activation_score`: Grid score that triggered the node.
  - `depth_gate`: Max layer reached.
  - `input_hash`: SHA256 hash of input content.
  - `input_chars`: Size of input payload.
  - `output_summary`: Summary of output.
  - `extracted_count`: Number of knowledge items extracted.
  - `output_json`: Full structured output.
  - `processing_ms`: Processing time in milliseconds.
  - `model_used`: Model used for processing.
  - `processed_at`: Timestamp of processing.

#### Knowledge Extractions
- **Purpose**: Stores every piece of knowledge extracted by the nodes.
- **Fields**:
  - `id`: Unique identifier.
  - `extraction_id`: Stable ID for Neo4j linking.
  - `exchange_id`: Exchange identifier.
  - `manifest_id`: Foreign key linking to `grid_processing_manifest`.
  - `node`: Node type.
  - `layer`: Layer number.
  - `version`: Version of the node-layer.
  - `knowledge_type`: Type of knowledge (fact, preference, observation, directive).
  - `subject`: Subject of the knowledge.
  - `content`: Extracted knowledge content.
  - `domain`: Domain of the knowledge.
  - `confidence`: Confidence level.
  - `significance`: Significance level.
  - `status`: Status of the knowledge (active, superseded, retracted, confirmed).
  - `superseded_by`: ID of the superseding extraction.
  - `confirmed_count`: Count of independent confirmations.
  - `confirmation_sources`: JSON array of confirmation sources.
  - `neo4j_node_id`: Neo4j element ID.
  - `neo4j_synced`: Boolean indicating if synced with Neo4j.
  - `neo4j_synced_at`: Timestamp of Neo4j sync.
  - `notification_sent`: Boolean indicating if notification sent.
  - `notification_sent_at`: Timestamp of notification sent.
  - `created_at`: Creation timestamp.
  - `updated_at`: Update timestamp.

#### Grid Version Registry
- **Purpose**: Manages versions and changelogs for each node-layer combination.
- **Fields**:
  - `id`: Unique identifier.
  - `node`: Node type.
  - `layer`: Layer number.
  - `version`: Version of the node-layer.
  - `prompt_hash`: SHA256 hash of the prompt.
  - `description`: Description of the node-layer.
  - `changelog`: JSON array of changelog entries.
  - `is_active`: Boolean indicating if the node-layer is active.
  - `updated_at`: Update timestamp.

### Indexes
- **Grid Processing Manifest**:
  - `idx_gpm_exchange`: Index on `exchange_id`.
  - `idx_gpm_node_version`: Index on `node`, `version`, `processed_at`.
  - `idx_gpm_version_audit`: Index on `node`, `layer`, `version`.
  - `idx_gpm_stale`: Index on `node`, `layer`, `version`, `activated`.
  - `idx_gpm_user_time`: Index on `user_uuid`, `processed_at`.

- **Knowledge Extractions**:
  - `idx_ke_exchange`: Index on `exchange_id`.
  - `idx_ke_type`: Index on `knowledge_type`, `status`.
  - `idx_ke_subject`: Index on `subject`.
  - `idx_ke_significance`: Index on `significance`.
  - `idx_ke_unsynced`: Index on `neo4j_synced`.
  - `idx_ke_version`: Index on `node`, `layer`, `version`.
  - `idx_ke_domain`: Index on `domain`, `created_at`.
  - `idx_ke_notification`: Index on `notification_sent`, `significance`.

### Seed Data
- **Grid Version Registry**: Seeds the first layer for all 9 nodes with initial versions and descriptions.

This SQL file is crucial for maintaining the integrity and provenance of the Arcturian Grid's processing and knowledge extraction activities.
