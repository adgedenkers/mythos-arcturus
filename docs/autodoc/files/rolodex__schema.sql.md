# rolodex/schema.sql

**Language:** sql
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 250

---

### File: rolodex/schema.sql

#### Purpose
This SQL file defines the schema for the `rolodex` database, which serves as the identity and directory system for the Mythos platform. It includes tables for managing graph nodes, persons, contacts, entity aliases, proxy registry, astrological data, numerology, node documents, node notes, and sync logs.

#### Architecture
The file is structured into multiple sections, each defining a specific table within the `rolodex` schema. Each table has its own set of columns and constraints, and some tables have foreign key relationships with the `graph_nodes` table.

#### Patterns
- **Foreign Key Relationships**: Used extensively to link related tables, such as `persons` and `contacts` to `graph_nodes`.
- **Indexes**: Created for frequently queried columns to improve performance.

#### Dependencies
- PostgreSQL database system.
- No external dependencies within the file itself.

#### Interfaces
- Exposes tables and columns for other parts of the Mythos system to interact with the identity and directory data.

#### Database
- **Tables**:
  - `rolodex.graph_nodes`: Universal node registry.
  - `rolodex.persons`: Extended identity data for persons.
  - `rolodex.contacts`: Phone book data.
  - `rolodex.entity_aliases`: Maps entity mentions to persons.
  - `rolodex.proxies`: Tracks proxy nodes.
  - `rolodex.astro_charts`: Full astrological chart data.
  - `rolodex.astro_planets`: Individual astrological placements.
  - `rolodex.numerology`: Numerology data.
  - `rolodex.node_documents`: Links files to nodes.
  - `rolodex.node_notes`: Freeform annotations.
  - `rolodex.sync_log`: Tracks Neo4j <-> PostgreSQL sync operations.

#### Configuration
- No specific configuration files or environment variables are used directly in this file. However, the schema and table structures are designed to be configurable through the data inserted into these tables.

#### Key Logic
- **Graph Nodes**: Central registry for all graph nodes, bridging Neo4j and PostgreSQL.
- **Persons**: Detailed identity information, including personal details and relationships.
- **Contacts**: Stores contact information for individuals.
- **Entity Aliases**: Maps entity mentions to specific persons, useful for resolving references.
- **Proxy Registry**: Tracks proxy nodes for various applications.
- **Astrological Data**: Stores full astrological charts and individual planet placements.
- **Numerology**: Stores core numerology numbers and full profiles.
- **Node Documents**: Links files to nodes for documentation purposes.
- **Node Notes**: Freeform annotations for nodes.
- **Sync Log**: Tracks synchronization operations between Neo4j and PostgreSQL.

#### Integration Points
- **Graph Nodes**: Serves as the primary integration point for all other tables, ensuring consistency across the system.
- **Persons**: Integrates with `contacts` and `entity_aliases` to provide comprehensive identity data.
- **Contacts**: Used by the contact management subsystem.
- **Entity Aliases**: Used by the entity resolution subsystem.
- **Proxy Registry**: Used by various application-specific subsystems.
- **Astrological Data**: Used by the astrological subsystem.
- **Numerology**: Used by the numerology subsystem.
- **Node Documents**: Used by the document management subsystem.
- **Node Notes**: Used by the annotation subsystem.
- **Sync Log**: Used by the synchronization subsystem to track and manage sync operations.

### Summary
The `rolodex/schema.sql` file defines the comprehensive schema for the Mythos identity and directory system, ensuring that all identity and directory data is stored and managed efficiently. It integrates with various subsystems within the Mythos platform, providing a robust and flexible data model for managing identities and relationships.
