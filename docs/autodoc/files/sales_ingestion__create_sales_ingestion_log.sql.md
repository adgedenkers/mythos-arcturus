# sales_ingestion/create_sales_ingestion_log.sql

**Language:** sql
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 14

---

### File: `sales_ingestion/create_sales_ingestion_log.sql`

#### Purpose
This SQL file creates a table `sales_ingestion_log` in the PostgreSQL database to log the status and details of sales ingestion batches. It also creates an index on the `status` column to improve query performance.

#### Architecture
- **Table Creation**: The file contains SQL commands to create a table named `sales_ingestion_log` if it does not already exist.
- **Indexes**: An index is created on the `status` column to optimize queries filtering by status.

#### Patterns
- **N/A**: This file is a simple SQL script and does not involve any design patterns.

#### Dependencies
- **PostgreSQL**: This script is dependent on PostgreSQL for executing the SQL commands.
- **UUID Extension**: The `gen_random_uuid()` function is used, which requires the `uuid-ossp` extension to be installed in PostgreSQL.

#### Interfaces
- **N/A**: This is a database schema definition file and does not expose any interfaces directly.

#### Database
- **Table**: `sales_ingestion_log`
  - **Columns**:
    - `id`: UUID, primary key, auto-generated using `gen_random_uuid()`
    - `batch_name`: TEXT, not null
    - `artifact_type`: TEXT, not null, with a check constraint to ensure it is either 'sales' or 'shoes'
    - `status`: TEXT, not null, with a check constraint to ensure it is one of 'staged', 'processing', 'success', or 'failed'
    - `extract_dir`: TEXT, not null
    - `error`: TEXT, optional
    - `created_at`: TIMESTAMP, auto-generated using `now()`
    - `updated_at`: TIMESTAMP, auto-generated using `now()`
  - **Constraints**:
    - `UNIQUE (batch_name, artifact_type)`: Ensures that each combination of `batch_name` and `artifact_type` is unique.
- **Index**: `idx_sales_ingestion_log_status` on the `status` column.

#### Configuration
- **N/A**: This file does not use any configuration files or environment variables.

#### Key Logic
- **Table Creation**: The primary logic is to create a table with specific columns and constraints to log the status and details of sales ingestion batches.
- **Index Creation**: An index is created on the `status` column to optimize queries that filter by status.

#### Integration Points
- **Mythos Subsystems**: This table is likely used by the sales ingestion subsystem to log the progress and status of ingestion batches. It may be queried by other subsystems (e.g., monitoring, reporting) to check the status of ingestion processes.

### Summary
This SQL script is designed to create a logging table for sales ingestion processes within the Mythos system. It ensures that each batch's status and details are recorded with appropriate constraints and an index to optimize status-based queries. The table is integral to the sales ingestion subsystem and may be used by other subsystems for monitoring and reporting purposes.
