# docs/design-patterns/PATTERNS.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 803

---

### Documentation for `docs/design-patterns/PATTERNS.md`

#### Purpose
This markdown file serves as a comprehensive library of design patterns for the Mythos system, specifically tailored for Iris and any LLM working with the Mythos infrastructure. It provides guidelines and examples for implementing various patterns in Neo4j and PostgreSQL.

#### Architecture
The file is structured into sections based on the storage layer (Neo4j, PostgreSQL, and cross-database patterns). Each pattern includes a description of when to use it, the schema (SQL or Cypher), query examples, integration notes, and anti-patterns.

#### Patterns
- **Factory Pattern**: Not explicitly used, but the patterns can be seen as a factory for creating consistent and reusable designs.
- **Singleton Pattern**: Not applicable.
- **Observer Pattern**: Not applicable.
- **Schema-Aware Node**: A custom pattern to make the graph introspectable.

#### Dependencies
- **Neo4j**: For graph database operations.
- **PostgreSQL**: For relational database operations.
- **Cypher**: Neo4j query language.
- **SQL**: PostgreSQL query language.

#### Interfaces
This file does not expose any direct interfaces but serves as a reference for developers to implement patterns in their code.

#### Database
- **Neo4j**: Patterns include `Ontology Node`, `Relationship Web`, and `Schema-Aware Node`.
- **PostgreSQL**: Patterns include `Conversation Log`.

#### Configuration
No specific configuration files or environment variables are mentioned in this file.

#### Key Logic
- **Ontology Node**: Ensures every entity has a `canonical_id` and required properties.
- **Relationship Web**: Defines typed edges with specific properties and directions.
- **Schema-Aware Node**: Creates schema nodes that describe entity types and their properties.
- **Conversation Log**: Implements immutable append-only records for chat messages with full-text search and embeddings.

#### Integration Points
- **Neo4j Patterns**: Connect to other subsystems via `canonical_id` for cross-database lookups.
- **PostgreSQL Patterns**: Connect to Neo4j via `canonical_id` for linking conversations and entities.

### Detailed Analysis

#### Neo4j Patterns

1. **P1: Ontology Node (Entity Registry)**
   - **When to use**: Storing named entities with relationships.
   - **Schema**: Creates nodes with `canonical_id`, name fields, core data, and metadata.
   - **Query Examples**: Find entities by name, cross-DB lookup by `canonical_id`, count by label.
   - **Anti-patterns**: Avoid creating nodes without `canonical_id`, avoid Neo4j-internal `id()` as a reference, avoid storing large text blobs in Neo4j.

2. **P2: Relationship Web (Typed Edges)**
   - **When to use**: Connecting entities with typed relationships.
   - **Schema**: Creates relationships with specific types, properties, and directions.
   - **Query Examples**: Full relationship map, lineage chain, all protectors of a person.
   - **Anti-patterns**: Avoid generic `RELATED_TO`, avoid storing relationship data as node properties, avoid bidirectional duplicates.

3. **P3: Schema-Aware Node (Self-Describing Graph)**
   - **When to use**: Making the graph introspectable.
   - **Schema**: Creates schema nodes that define entity types, properties, and relationships.
   - **Query Examples**: Schema introspection query.
   - **Anti-patterns**: Avoid skipping Schema nodes, avoid letting Schema drift from actual data, avoid putting mode display logic in application code.

#### PostgreSQL Patterns

1. **P4: Conversation Log (Chat History)**
   - **When to use**: Storing chat messages and interaction logs.
   - **Schema**: Creates tables for conversations and messages with indexes for efficient querying.
   - **Query Examples**: Not provided in the excerpt.
   - **Anti-patterns**: Not explicitly mentioned in the excerpt.

This documentation provides a detailed overview of the design patterns used in the Mythos system, guiding developers on how to implement consistent and efficient data structures and queries in both Neo4j and PostgreSQL.
