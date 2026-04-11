# docs/MONTHLY_MOONS_REFERENCE.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 202

---

### Purpose
This markdown file, `MONTHLY_MOONS_REFERENCE.md`, serves as a comprehensive reference for named monthly moons across 10 cultural/spiritual traditions and 8 special moon types. It provides a cross-reference of lunar names and their meanings, aligned with Gregorian months, and includes details on how this data is structured and queried in the Mythos system.

### Architecture
The file is structured as a markdown document with sections for:
- **Overview**: General description and key insights.
- **Systems Included**: A table listing the cultural/spiritual traditions and their lunar systems.
- **Quick Cross-Reference by Gregorian Month**: Detailed listings of moon names and meanings for each Gregorian month.
- **Special Moon Types**: Definitions and frequencies of special moon types.
- **Database Files**: References to related database files.
- **Queries**: Example SQL queries to retrieve moon data.
- **Neo4j Integration Notes**: Instructions for integrating moon data into the Neo4j graph database.

### Patterns
This file does not implement any design patterns as it is a documentation file rather than a code file. However, it serves as a reference for data integration and querying patterns within the Mythos system.

### Dependencies
The file does not have direct dependencies but references other files and systems:
- **`monthly_moons_ontology.sql`**: PostgreSQL schema and seed data.
- **`monthly_moons_cross_reference.json`**: JSON file for API/Neo4j import.
- **PostgreSQL**: For storing and querying moon data.
- **Neo4j**: For graph database integration.

### Interfaces
This file does not expose interfaces but serves as a reference for:
- **SQL Queries**: Example queries for accessing moon data.
- **Neo4j Integration**: Instructions for integrating moon data into the Neo4j graph database.

### Database
The file references the following database tables and Neo4j labels:
- **PostgreSQL**:
  - `monthly_moons`: Table containing moon data.
  - `v_current_month_moons`: View for current month's moons.
  - `v_moons_by_month`: View for moons by Gregorian month.
- **Neo4j**:
  - `MoonName`: Node for moon names.
  - `NamingSystem`: Node for naming systems.
  - `Deity`: Node for deities.
  - `Festival`: Node for festivals.
  - Relationships: `BELONGS_TO`, `APPROXIMATE_MONTH`, `ASSOCIATED_WITH`, `CELEBRATED_AT`.

### Configuration
The file does not require any configuration but may reference environment variables or configuration files used by the Mythos system for database connections and Neo4j integration.

### Key Logic
The key logic in this file is the cross-referencing of moon names and meanings across different cultural traditions and their alignment with Gregorian months. It also includes special moon types and their frequencies and magical significances.

### Integration Points
This file integrates with other Mythos subsystems through:
- **PostgreSQL**: For storing and querying moon data.
- **Neo4j**: For graph database integration, using the specified nodes and relationships.
- **API**: Through the JSON file (`monthly_moons_cross_reference.json`) for API integration.

### Summary
This markdown file serves as a comprehensive reference for the Mythos system, detailing the named monthly moons across various cultural traditions and special moon types. It provides guidance on how this data is structured in PostgreSQL and Neo4j, and includes example SQL queries and Neo4j integration notes.
