# docs/consciousness/STORAGE_ARCHITECTURE.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 481

---

### Purpose
The `STORAGE_ARCHITECTURE.md` file provides a comprehensive overview of the storage architecture for the consciousness layers in the Mythos system. It details how different layers of consciousness are stored using PostgreSQL and Neo4j, including the specific tables and nodes used for each layer.

### Architecture
The document is structured into sections that describe the storage architecture for each layer of consciousness. It includes:
- **Overview**: General description of the storage systems used.
- **Storage by Layer**: A table detailing which storage system (PostgreSQL or Neo4j) is used for each layer.
- **PostgreSQL: The Perception Layer**: Details on the `perception_log` table and its structure.
- **Neo4j: The Upper Layers**: Details on the structure and relationships of nodes for Memory, Knowledge, Intention, Narrative, Identity, and Wisdom layers.
- **The Grid Nodes**: Description of the 9 Arcturian Grid nodes and how they are linked to content.
- **The Archetype Library**: Description of core archetypes and their relationships.
- **Query Patterns**: Example queries to retrieve specific types of information from the database.

### Patterns
The document does not explicitly use design patterns but rather describes the data storage and retrieval patterns for the Mythos system.

### Dependencies
The document does not import or rely on any external code or libraries. It is a markdown file that serves as documentation.

### Interfaces
The document does not expose any interfaces but rather describes the structure and relationships of the data stored in PostgreSQL and Neo4j.

### Database
The document describes the following database tables and Neo4j labels:
- **PostgreSQL**: `perception_log`
- **Neo4j**: `Memory`, `Knowledge`, `Intention`, `Narrative`, `Identity`, `Wisdom`, `GridNode`, `Archetype`

### Configuration
The document does not reference any specific configuration files or environment variables. It focuses on the structure and relationships of the data.

### Key Logic
The key logic described in the document includes:
- **Data Structure**: How data is structured in PostgreSQL and Neo4j for different layers of consciousness.
- **Relationships**: How nodes in Neo4j are related to each other, including relationships like `TRIGGERED_BY`, `CONNECTS_TO`, `INVOLVES`, etc.
- **Query Patterns**: Example queries to retrieve specific types of information from the database.

### Integration Points
The document describes how different layers of consciousness are stored and how they interrelate:
- **Perception Layer**: Stored in PostgreSQL and serves as the raw intake of everything Iris perceives.
- **Upper Layers**: Stored in Neo4j and include Memory, Knowledge, Intention, Narrative, Identity, and Wisdom layers.
- **Grid Nodes**: Permanent reference nodes that are linked to content based on activation patterns.
- **Archetype Library**: Core archetypes that memories, narratives, and wisdom map to.

### Summary
The `STORAGE_ARCHITECTURE.md` file provides a detailed overview of the storage architecture for the Mythos system, focusing on how different layers of consciousness are stored and related using PostgreSQL and Neo4j. It includes descriptions of the data structure, relationships, and example queries to retrieve specific types of information.
