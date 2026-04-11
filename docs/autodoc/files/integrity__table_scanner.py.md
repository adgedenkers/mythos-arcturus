# integrity/table_scanner.py

**Language:** python
**Stream:** SYS
**Module:** Integrity Scanner
**Lines:** 213

---

### File: `integrity/table_scanner.py`

#### Purpose
This file contains functions to scan PostgreSQL tables, columns, and foreign keys, and then merge this information into Neo4j as nodes and relationships.

#### Architecture
The file consists of several top-level functions:
- `get_pg_connection`: Establishes a connection to the PostgreSQL database.
- `scan_tables`: The main function that orchestrates the scanning process, calling other helper functions to merge tables, columns, and foreign key relationships into Neo4j.
- `_merge_table`: Merges a table node into Neo4j.
- `_merge_column`: Merges a column node into Neo4j and links it to its corresponding table.
- `_merge_fk_relationship`: Creates a `REFERENCES` relationship between tables for a foreign key.

#### Patterns
- **Singleton Pattern**: The `get_driver` function from `integrity.graph` is used to get a Neo4j driver, which is a singleton pattern to ensure only one driver instance is used.
- **Helper Functions**: The `_merge_table`, `_merge_column`, and `_merge_fk_relationship` functions are helper functions that encapsulate specific tasks, promoting code reusability and modularity.

#### Dependencies
- `os`: For environment variable access.
- `logging`: For logging errors and information.
- `datetime`: For timestamp generation.
- `psycopg2`: For PostgreSQL database connection and querying.
- `psycopg2.extras`: For dictionary cursor.
- `integrity.graph`: For Neo4j driver and query execution functions.

#### Interfaces
- `get_pg_connection`: Provides a PostgreSQL connection.
- `scan_tables`: Exposes the main scanning logic and returns scan statistics.
- `_merge_table`: Merges a table node into Neo4j.
- `_merge_column`: Merges a column node into Neo4j and links it to its table.
- `_merge_fk_relationship`: Creates a `REFERENCES` relationship between tables for a foreign key.

#### Database
- **PostgreSQL**:
  - Tables: `information_schema.tables`, `information_schema.columns`, `information_schema.table_constraints`, `information_schema.key_column_usage`, `information_schema.constraint_column_usage`.
- **Neo4j**:
  - Labels: `IntegrityTable`, `IntegrityColumn`, `IntegrityDatabase`.
  - Relationships: `HAS_TABLE`, `HAS_COLUMN`, `REFERENCES`.

#### Configuration
- Environment variables:
  - `POSTGRES_DB`: Database name.
  - `POSTGRES_USER`: Database user.
  - `POSTGRES_PASSWORD`: Database password.
  - `POSTGRES_HOST`: Database host.
  - `POSTGRES_PORT`: Database port.

#### Key Logic
- **Table Scanning**: The `scan_tables` function queries PostgreSQL to retrieve tables, columns, and foreign keys, then merges this information into Neo4j.
- **Node and Relationship Creation**: The `_merge_table`, `_merge_column`, and `_merge_fk_relationship` functions use Cypher queries to create nodes and relationships in Neo4j.
- **Error Handling**: The `scan_tables` function logs errors and includes them in the returned statistics.

#### Integration Points
- **Neo4j Integration**: The file integrates with Neo4j through the `get_driver`, `run_write`, and `run_query` functions from `integrity.graph`.
- **PostgreSQL Integration**: The file connects to PostgreSQL using `psycopg2` and retrieves metadata from the `information_schema` tables.
- **Logging**: Uses the `logging` module to log errors and information, which can be integrated with the broader logging system of the Mythos platform.

This file plays a crucial role in maintaining the integrity and cataloging of the PostgreSQL database by ensuring that the Neo4j graph database is up-to-date with the latest schema information.
