# sdip/migrations/001_create_tables.sql

**Language:** sql
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 130

---

### Purpose
The `001_create_tables.sql` file is a migration script that creates the foundational tables for the Sovereign Document Intelligence Platform (SDIP) within the Mythos system. It sets up the necessary PostgreSQL tables to manage document sources, document metadata, document chunks, sensitivity detection, classification history, proposed actions, and audit logs.

### Architecture
The file consists of a series of SQL `CREATE TABLE` statements, each defining a specific table with its columns and constraints. Additionally, it includes `CREATE INDEX` statements to optimize query performance on frequently accessed columns.

### Patterns
- **Database Schema Migration**: This file follows a typical database schema migration pattern, where each migration script is versioned and incrementally modifies the database schema.

### Dependencies
- **PostgreSQL Extensions**: The script requires the `vector` extension for future embedding storage capabilities.

### Interfaces
- **None**: This is a migration script and does not expose any interfaces. It is intended to be executed as part of the database setup process.

### Database
- **Tables Created**:
  - `sdip_sources`: Stores information about document sources (directories, Git repositories, etc.).
  - `sdip_documents`: Catalogs individual documents with metadata and relationships to sources.
  - `sdip_chunks`: Manages document chunks with sensitivity information.
  - `sdip_sensitivity`: Records detailed sensitivity detection records.
  - `sdip_classifications`: Maintains a history of document classifications for audit purposes.
  - `sdip_actions`: Tracks proposed and executed actions on documents and chunks.
  - `sdip_audit_log`: Logs every content access for auditing.

### Configuration
- **None**: The script does not rely on any configuration files or environment variables. It is a standalone migration script.

### Key Logic
- **Table Definitions**: The script defines the structure of each table, including primary keys, foreign keys, and constraints.
- **Indexes**: It creates indexes on frequently accessed columns to optimize query performance.

### Integration Points
- **Foreign Keys**: The tables are interconnected via foreign keys, ensuring referential integrity:
  - `sdip_documents` references `sdip_sources`.
  - `sdip_chunks` references `sdip_documents`.
  - `sdip_sensitivity` references `sdip_chunks`.
  - `sdip_classifications` references `sdip_documents`.
  - `sdip_actions` references `sdip_documents` and `sdip_chunks`.
  - `sdip_audit_log` references `sdip_documents` and `sdip_chunks`.

### Summary
This migration script is crucial for setting up the initial database schema for the SDIP component of the Mythos system. It defines the structure for managing document sources, documents, document chunks, sensitivity detection, classification history, proposed actions, and audit logs, ensuring that the system can effectively handle and track document intelligence operations.
