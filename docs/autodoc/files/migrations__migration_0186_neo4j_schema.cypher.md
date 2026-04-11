# migrations/migration_0186_neo4j_schema.cypher

**Language:** cypher
**Stream:** SYS
**Module:** Database Migrations
**Lines:** 235

---

### File: migrations/migration_0186_neo4j_schema.cypher

#### Purpose
This Cypher file defines the schema for the Neo4j graph database used in the Mythos system. It includes constraints, indexes, node types, relationship types, and example queries to interact with the graph data.

#### Architecture
The file is structured into several sections:
1. **Constraints**: Defines uniqueness constraints for various node labels.
2. **Indexes**: Creates indexes for frequently queried properties.
3. **Node Types**: Describes the structure and properties of each node type.
4. **Relationship Types**: Outlines the types of relationships between nodes.
5. **Canonical Merge Patterns**: Provides Cypher patterns for upserting nodes and relationships.
6. **Example Queries**: Demonstrates how to query the graph for specific information.

#### Patterns
- **Idempotent Upserts**: Uses `MERGE` to ensure idempotent operations.
- **Parameterized Queries**: Utilizes parameters for dynamic data insertion.

#### Dependencies
- **Neo4j**: The file is designed to be executed in a Neo4j environment.
- **Cypher**: The language used to define and query the graph schema.

#### Interfaces
- **Constraints and Indexes**: Exposed to ensure data integrity and query performance.
- **Node and Relationship Types**: Exposed to allow other parts of the system to interact with the graph.
- **Canonical Merge Patterns**: Exposed as reusable patterns for data ingestion.

#### Database
- **Neo4j Labels**: `Conversation`, `Person`, `System`, `Topic`, `SpiritualConcept`, `ThreadGroup`, `Epoch`.
- **Neo4j Relationships**: `INVOLVES`, `MENTIONS`, `USES`, `INVOKES`, `BELONGS_TO`, `CONTINUES`, `BUILDS_ON`, `REFERENCES`, `CONTRADICTS`, `HAS_EPOCH`, `WITHIN_EPOCH`, `RELATED_TO`, `ORIGINATES_FROM`, `HOLDS`, `CARRIES`.

#### Configuration
- **Environment Variables**: None directly used in this file.
- **Configuration Files**: None directly used in this file.

#### Key Logic
- **Constraints and Indexes**: Ensure data integrity and optimize query performance.
- **Node and Relationship Types**: Define the structure of the graph.
- **Canonical Merge Patterns**: Provide reusable patterns for upserting nodes and relationships.
- **Example Queries**: Demonstrate how to query the graph for specific information.

#### Integration Points
- **PostgreSQL**: The Neo4j graph only stores IDs and relationships, with raw content and summaries stored in PostgreSQL.
- **Ingest Pipeline**: The canonical merge patterns are used by the ingest pipeline to populate the graph.
- **Query Interface**: The example queries can be used by other parts of the system to retrieve information from the graph.

### Detailed Breakdown

#### Constraints
- **conversation_id_unique**: Ensures each `Conversation` node has a unique `conversation_id`.
- **person_id_unique**: Ensures each `Person` node has a unique `person_id`.
- **system_id_unique**: Ensures each `System` node has a unique `system_id`.
- **topic_id_unique**: Ensures each `Topic` node has a unique `topic_id`.
- **spiritual_concept_id_unique**: Ensures each `SpiritualConcept` node has a unique `concept_id`.
- **thread_group_id_unique**: Ensures each `ThreadGroup` node has a unique `thread_group_id`.
- **epoch_id_unique**: Ensures each `Epoch` node has a unique `epoch_id`.

#### Indexes
- **conversation_started_at**: Indexes the `started_at` property of `Conversation` nodes.
- **conversation_type**: Indexes the `type` property of `Conversation` nodes.
- **topic_name**: Indexes the `name` property of `Topic` nodes.
- **spiritual_concept_name**: Indexes the `name` property of `SpiritualConcept` nodes.
- **person_name**: Indexes the `name` property of `Person` nodes.
- **system_name**: Indexes the `name` property of `System` nodes.

#### Node Types
- **Conversation**: Minimal properties include `conversation_id`, `started_at`, `type`, `source_model`, `revision`.
- **Person**: Properties include `person_id`, `name`.
- **System**: Properties include `system_id`, `name`.
- **Topic**: Properties include `topic_id`, `name`.
- **SpiritualConcept**: Properties include `concept_id`, `name`, `domain`.
- **ThreadGroup**: Properties include `thread_group_id`, `name`.
- **Epoch**: Properties include `epoch_id`, `person_id`, `epoch_number`, `started_at`, `ended_at`, `reason`.

#### Relationship Types
- **Conversation → Entity relationships**:
  - `INVOLVES`: Links a `Conversation` to a `Person`.
  - `MENTIONS`: Links a `Conversation` to a `Topic`.
  - `USES`: Links a `Conversation` to a `System`.
  - `INVOKES`: Links a `Conversation` to a `SpiritualConcept`.
  - `BELONGS_TO`: Links a `Conversation` to a `ThreadGroup`.
- **Conversation → Conversation relationships**:
  - `CONTINUES`: Links a `Conversation` to another `Conversation` as a continuation.
  - `BUILDS_ON`: Links a `Conversation` to another `Conversation` as an extension.
  - `REFERENCES`: Links a `Conversation` to another `Conversation` as a reference.
  - `CONTRADICTS`: Links a `Conversation` to another `Conversation` as a contradiction.
- **Person → Epoch relationships**:
  - `HAS_EPOCH`: Links a `Person` to an `Epoch`.
- **Conversation → Epoch relationships**:
  - `WITHIN_EPOCH`: Links a `Conversation` to an `Epoch`.
- **SpiritualConcept relationships**:
  - `RELATED_TO`: Links a `SpiritualConcept` to another `SpiritualConcept`.
  - `ORIGINATES_FROM`: Links a `SpiritualConcept` to its origin.
  - `HOLDS`: Links a `Person` to a `SpiritualConcept`.
  - `CARRIES`: Links a `Person` to a `SpiritualConcept`.

#### Canonical Merge Patterns
- **Upsert a conversation**: Inserts or updates a `Conversation` node.
- **Link to ThreadGroup**: Links a `Conversation` to a `ThreadGroup`.
- **Link people**: Links a `Conversation` to multiple `Person` nodes.
- **Link systems**: Links a `Conversation` to multiple `System` nodes.
- **Link topics**: Links a `Conversation` to multiple `Topic` nodes.
- **Link spiritual concepts**: Links a `Conversation` to multiple `SpiritualConcept` nodes.
- **Conversation-to-conversation edges**: Links a `Conversation` to other `Conversation` nodes with various relationship types.

#### Example Queries
- **All conversations invoking a spiritual concept**: Retrieves all conversations that invoke a specific spiritual concept.
- **Trace concept evolution across sessions**: Traces the evolution of a spiritual concept across multiple sessions.
- **All spiritual concepts discussed alongside a person**: Retrieves all spiritual concepts discussed alongside a specific person.
- **Thread group traversal**: Traverses a thread group to retrieve all conversations.
- **Spiritual concept network**: Retrieves the network of relationships between spiritual concepts.
