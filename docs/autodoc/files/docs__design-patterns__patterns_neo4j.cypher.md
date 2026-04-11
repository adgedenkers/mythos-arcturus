# docs/design-patterns/patterns_neo4j.cypher

**Language:** cypher
**Stream:** SYS
**Module:** Documentation
**Lines:** 268

---

### File: docs/design-patterns/patterns_neo4j.cypher

#### Purpose
This Cypher file serves as a reference for Neo4j schema design patterns, including constraints, indexes, node templates, relationship types, and schema-aware nodes. It provides a standardized vocabulary and structure for creating and querying nodes and relationships in the Neo4j database used by the Mythos system.

#### Architecture
The file is organized into sections, each focusing on a specific aspect of Neo4j schema design:
1. **Constraints & Indexes**: Defines unique constraints and text indexes for core node types.
2. **Ontology Node Templates**: Provides template Cypher queries for creating nodes of various types.
3. **Relationship Types**: Lists standard relationship types and their properties.
4. **Schema-Aware Nodes**: Defines schema nodes that describe the structure and properties of each node type.
5. **Introspection Queries**: Provides queries to introspect the schema and inventory of nodes and relationships.

#### Patterns
- **Singleton Pattern**: The schema nodes (e.g., `Schema {node_type: 'Person'}`) act as singletons, ensuring there is only one instance per node type.
- **Factory Pattern**: The node templates can be seen as a factory for creating nodes of specific types.

#### Dependencies
- **Neo4j**: The file is designed to be run in a Neo4j environment and relies on Neo4j's Cypher query language.
- **UUID Generation**: Uses `randomUUID()` for generating unique identifiers.

#### Interfaces
- **Constraints & Indexes**: Exposes constraints and indexes for core node types.
- **Node Templates**: Provides Cypher templates for creating nodes.
- **Relationship Types**: Defines standard relationship types and their properties.
- **Schema Nodes**: Defines schema nodes that describe the structure of each node type.
- **Introspection Queries**: Provides queries to introspect the schema and inventory.

#### Database
- **Neo4j Labels**: The file defines constraints, indexes, and schema nodes for the following labels:
  - `Person`
  - `Soul`
  - `Event`
  - `Lineage`
  - `Organization`
  - `Location`
  - `Schema`

#### Configuration
- **Environment Variables**: No direct use of environment variables, but the file can be used as a reference for setting up environment-specific configurations.
- **Config Files**: No direct use of config files, but the file can be used to inform configuration settings.

#### Key Logic
- **Unique Constraints**: Ensures that each node type has a unique `canonical_id`.
- **Text Indexes**: Provides text indexes for efficient name lookups.
- **Node Templates**: Provides standardized templates for creating nodes.
- **Relationship Types**: Defines standardized relationship types and their properties.
- **Schema Nodes**: Describes the structure and properties of each node type, including required and optional properties, valid relationships, and example queries.

#### Integration Points
- **Mythos Subsystems**: This file serves as a reference for other subsystems in the Mythos system that interact with Neo4j. It ensures consistency in schema design and provides a standardized vocabulary for creating and querying nodes and relationships.
- **LLM Context Loading**: The introspection queries can be used to load context for language models, providing a structured overview of the Neo4j schema and inventory.

### Summary
This Cypher file is a comprehensive reference for designing and querying the Neo4j schema in the Mythos system. It ensures consistency and standardization across different subsystems by defining constraints, indexes, node templates, relationship types, and schema nodes. The file also provides introspection queries to help with context loading and schema introspection.
