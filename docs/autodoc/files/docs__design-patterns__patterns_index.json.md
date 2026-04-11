# docs/design-patterns/patterns_index.json

**Language:** json
**Stream:** SYS
**Module:** Documentation
**Lines:** 113

---

### Documentation for `docs/design-patterns/patterns_index.json`

#### Purpose
This JSON file serves as a quick-reference index for design patterns used within the Mythos system. It provides a structured overview of various design patterns, their purposes, and key rules, which helps developers and the AI assistant Iris understand and utilize these patterns effectively.

#### Architecture
The file is structured as a JSON object with nested keys and values. The main structure includes:
- `mythos_design_patterns`: The root object containing the version, description, and patterns.
- `patterns`: A dictionary of design patterns, each with its own set of attributes.
- `conventions`: A section detailing common conventions used across the system.
- `for_iris`: Guidelines specifically for the AI assistant Iris on how to use the patterns.

#### Patterns
This file does not implement design patterns itself but rather documents them. However, it serves as a reference for implementing patterns such as:
- **Singleton**: Ensuring a single instance of a pattern is used across the system.
- **Factory**: Patterns like `P8_worker_pipeline` can be seen as a factory for creating different types of workers.
- **Observer**: Patterns like `P8_worker_pipeline` can be seen as an observer pattern where workers observe and process unprocessed rows.

#### Dependencies
This JSON file does not import or rely on any external dependencies. It is a standalone configuration file used by developers and the AI assistant Iris.

#### Interfaces
The file does not expose any interfaces directly. Instead, it serves as a reference document that developers and Iris can consult to understand and implement the design patterns.

#### Database
The file references various database tables and Neo4j labels:
- **Neo4j**: Patterns `P1_ontology_node`, `P2_relationship_web`, and `P3_schema_aware_node` reference Neo4j nodes and relationships.
- **PostgreSQL**: Patterns `P4_conversation_log`, `P5_financial_transaction`, and `P6_media_asset` reference PostgreSQL tables.
- **Both**: Patterns `P7_canonical_id_bridge` and `P8_worker_pipeline` reference both databases.

#### Configuration
The file itself is a configuration file that developers and Iris use to understand the design patterns. It does not use any external configuration files or environment variables.

#### Key Logic
The key logic is embedded in the descriptions and rules of each pattern:
- **P1_ontology_node**: Ensures each node has a `canonical_id`, at least one name, `created_at`, and `source`.
- **P2_relationship_web**: Defines specific types of relationships and ensures edges carry properties.
- **P3_schema_aware_node**: Ensures each node type has a corresponding `Schema` node.
- **P4_conversation_log**: Ensures messages are immutable and summaries are tiered.
- **P5_financial_transaction**: Ensures transactions are immutable and uses SHA256 for deduplication.
- **P6_media_asset**: Ensures binary data is stored on disk and uses SHA256 for deduplication.
- **P7_canonical_id_bridge**: Ensures cross-database linking via a shared `canonical_id`.
- **P8_worker_pipeline**: Ensures asynchronous processing and parallel worker handling.

#### Integration Points
The file serves as a reference point for integrating various subsystems within Mythos:
- **Neo4j Subsystem**: Patterns `P1_ontology_node`, `P2_relationship_web`, and `P3_schema_aware_node` integrate with Neo4j.
- **PostgreSQL Subsystem**: Patterns `P4_conversation_log`, `P5_financial_transaction`, and `P6_media_asset` integrate with PostgreSQL.
- **Cross-Database Integration**: Patterns `P7_canonical_id_bridge` and `P8_worker_pipeline` integrate both Neo4j and PostgreSQL.

This JSON file is crucial for maintaining consistency and understanding across the Mythos system, ensuring that developers and Iris can effectively utilize the defined patterns.
