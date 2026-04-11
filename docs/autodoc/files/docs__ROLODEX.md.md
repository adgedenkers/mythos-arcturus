# docs/ROLODEX.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 74

---

### Purpose
The `ROLODEX.md` file serves as a comprehensive documentation for the Mythos Rolodex Identity System, detailing its architecture, node types, ID conventions, universal properties, and PostgreSQL schema.

### Architecture
The file is structured as a markdown document, organized into sections such as Overview, Node Types, ID Conventions, Universal Properties, and PostgreSQL Schema. Each section provides detailed information about the system's design and components.

### Patterns
No specific design patterns are used in this documentation file, as it is purely informational and does not contain any code or logic.

### Dependencies
This file does not import or rely on any external dependencies. It is a standalone documentation file.

### Interfaces
The file does not expose any interfaces. It is intended for human readers to understand the design and structure of the Mythos Rolodex Identity System.

### Database
The file describes the PostgreSQL schema for the Rolodex system, including tables such as `graph_nodes`, `persons`, `contacts`, `entity_aliases`, `proxies`, `astro_charts`, `astro_planets`, `numerology`, `node_documents`, `node_notes`, and `sync_log`.

### Configuration
The file does not mention any specific configuration files or environment variables. However, it references the `/opt/mythos/docs/ROLODEX_FULL.md` for a full specification.

### Key Logic
The key logic described in this file revolves around the principles of maintaining a canonical identity for each human being, ensuring that subsystems use proxies rather than the canonical identity, and storing relationships and traversal data in the graph while structured data is stored in PostgreSQL.

### Integration Points
The Rolodex system integrates with other Mythos subsystems by providing a canonical identity registry and proxy identities for subsystem-specific use. It ensures that every subsystem references the Rolodex to know who someone is, maintaining consistency and integrity across the system.

### Detailed Breakdown

1. **Overview**:
   - Describes the core principles of the Rolodex system, emphasizing the importance of maintaining a single canonical identity per human being and the use of proxies for subsystem-specific interactions.

2. **Node Types**:
   - Lists the different node types in the graph, each with a specific prefix and label, indicating their purpose within the system.

3. **ID Conventions**:
   - Outlines the conventions for generating IDs for different node types, ensuring a standardized and human-readable format.

4. **Universal Properties**:
   - Specifies the universal properties that apply to all nodes, including `uid`, `canonical_id`, `domain`, `scope`, and `origin`.

5. **PostgreSQL Schema**:
   - Describes the tables within the PostgreSQL schema that support the Rolodex system, detailing the storage of structured and relational data.

6. **Full Specification**:
   - References the full specification document located at `/opt/mythos/docs/ROLODEX_FULL.md` for more detailed information.

This documentation file serves as a critical reference for developers and system administrators working with the Mythos Rolodex Identity System, providing a clear and structured overview of its design and components.
