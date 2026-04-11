# docs/design-patterns/SCHEMA_AS_NODES_PATTERN.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 147

---

### Purpose
The `SCHEMA_AS_NODES_PATTERN.md` file documents the Schema-as-Nodes design pattern used in the Mythos system, specifically within the Neo4j graph database. This pattern ensures that the graph database is self-documenting by embedding schema definitions directly within the graph itself, making it comprehensible and usable by both humans and machine learning models like Iris.

### Architecture
The document is structured as a markdown file, organized into sections that explain the core insight, the pattern itself, its importance for LLMs, implementation rules, anti-patterns it prevents, and its context within the Mythos system. It does not contain any executable code but serves as a comprehensive guide for implementing and understanding the Schema-as-Nodes pattern.

### Patterns
- **Self-Documenting Pattern**: Ensures that every node and relationship in the graph contains enough metadata to be self-explanatory.
- **Ownership Pattern**: Each node and schema node is tagged with its owning development stream, ensuring clear ownership and preventing orphaned data.

### Dependencies
This markdown file does not have any direct dependencies. However, it relies on the Neo4j graph database and the Mythos system's architecture for practical implementation.

### Interfaces
The document does not expose any interfaces but serves as a reference for developers and architects to implement the Schema-as-Nodes pattern in the Mythos system.

### Database
- **Neo4j Labels**: `SchemaLabel`, `SchemaRelationship`
- **Neo4j Nodes**: `SchemaLabel` nodes contain metadata about labels, and `SchemaRelationship` nodes contain metadata about relationship types.

### Configuration
- **STREAMS.json**: A machine-readable stream registry that parallels the graph-level ownership.
- **Neo4j App Registry**: Documents ownership of all graph labels.

### Key Logic
The key logic revolves around embedding schema definitions directly within the graph as nodes, ensuring that every node and relationship is self-explanatory. This includes:
- Creating `SchemaLabel` nodes for each label.
- Creating `SchemaRelationship` nodes for each relationship type.
- Ensuring every node has a `created` timestamp and a `stream` tag.
- Querying the schema layer to discover the graph's structure and semantics.

### Integration Points
- **Neo4j**: The pattern is implemented directly within the Neo4j graph database.
- **Mythos AI (Iris)**: The pattern ensures that the graph is self-describing, making it easier for the LLM to reason over the data.
- **Ontology/Glossary System**: Terms and definitions are stored as graph nodes, contributing to the self-documenting nature of the graph.
- **Stream Ownership Model**: Ensures that every node is tagged with its originating development stream, facilitating ownership and management.

### Summary
The `SCHEMA_AS_NODES_PATTERN.md` document outlines the Schema-as-Nodes design pattern, ensuring that the Neo4j graph database in the Mythos system is self-documenting and comprehensible. This pattern is crucial for making the graph data usable by both humans and machine learning models, particularly by embedding schema definitions directly within the graph. The document serves as a comprehensive guide for implementing this pattern within the Mythos system, emphasizing the importance of self-documenting nodes and clear ownership.
