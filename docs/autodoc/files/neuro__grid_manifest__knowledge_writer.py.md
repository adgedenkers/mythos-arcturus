# neuro/grid_manifest/knowledge_writer.py

**Language:** python
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 462

---

### File: `neuro/grid_manifest/knowledge_writer.py`

#### Purpose
The `KnowledgeWriter` class is responsible for writing extracted knowledge to both PostgreSQL and Neo4j databases. It handles deduplication, supersession, and synchronization between the two databases.

#### Architecture
The `KnowledgeWriter` class contains methods for writing individual and batch knowledge extractions, superseding old extractions, and managing notifications. It also includes internal methods for finding similar extractions, confirming existing ones, and creating new ones. The class initializes a Neo4j driver if available and provides a method to close the driver.

#### Patterns
- **Singleton Pattern**: The `KnowledgeWriter` class can be used as a singleton to ensure a single instance manages database connections and operations.
- **Factory Method**: The `_get_conn` function acts as a factory method to create PostgreSQL connections.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `typing`, `datetime`, `dotenv`, `neo4j`
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`, `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

#### Interfaces
- **Public Methods**:
  - `write`: Writes a single knowledge extraction.
  - `write_batch`: Writes multiple extractions.
  - `supersede`: Marks an old extraction as superseded by a new one.
  - `get_unsynced`: Retrieves unsynced extractions.
  - `get_pending_notifications`: Retrieves significant extractions pending notification.
  - `mark_notified`: Marks an extraction as notified.
  - `close`: Closes the Neo4j driver.

#### Database
- **PostgreSQL Tables**:
  - `knowledge_extractions`: Stores knowledge extractions with fields like `extraction_id`, `exchange_id`, `manifest_id`, `node`, `layer`, `version`, `knowledge_type`, `subject`, `content`, `domain`, `confidence`, `significance`, `confirmed_count`, `confirmation_sources`, `status`, `neo4j_synced`, `notification_sent`, `created_at`, `updated_at`, `notification_sent_at`.
- **Neo4j Labels**:
  - `Exchange`: Represents an exchange node.
  - `SUPERSEDED_BY`: Represents the relationship between superseded and new extractions.
  - `EXTRACTED_FROM`: Represents the relationship between an extraction and its source.
  - `ABOUT`: Represents the relationship between an extraction and its subject.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: PostgreSQL connection details.
  - `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`: Neo4j connection details.

#### Key Logic
- **Deduplication**: The `_find_similar` method checks for existing similar extractions to avoid duplication.
- **Confirmation**: The `_confirm_existing` method increments the confirmation count and updates the confidence of an existing extraction.
- **Creation**: The `_create_new` method inserts a new extraction into the PostgreSQL database and writes it to Neo4j.
- **Supersession**: The `supersede` method updates the status of an old extraction to 'superseded' and links it to the new extraction in both PostgreSQL and Neo4j.

#### Integration Points
- **PostgreSQL**: The class interacts with the `knowledge_extractions` table to insert, update, and retrieve extractions.
- **Neo4j**: The class uses the Neo4j driver to write nodes and relationships, ensuring that the graph database is synchronized with the PostgreSQL database.
- **Notification System**: The `get_pending_notifications` and `mark_notified` methods integrate with a notification system to manage significant extractions that require external confirmation.

### Summary
The `KnowledgeWriter` class is a crucial component of the Mythos system, responsible for persisting extracted knowledge in both PostgreSQL and Neo4j databases. It handles deduplication, confirmation, and supersession of knowledge extractions, ensuring data integrity and synchronization between the two databases.
