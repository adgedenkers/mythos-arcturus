# orchestrator/schema/unified_v2.sql

**Language:** sql
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 52

---

### File: orchestrator/schema/unified_v2.sql

#### Purpose
This SQL file defines and populates tables and views for managing role assignments and configuration snapshots in the Mythos system. It introduces new tables for role assignments and configuration snapshots, and ensures that active role assignments are easily accessible through a view.

#### Architecture
The file consists of several SQL statements:
1. **Table Creation**: `orch_role_assignments` and `orch_config_snapshots` are created with specific columns and constraints.
2. **Index Creation**: An index is created on `orch_role_assignments` to optimize queries for active roles.
3. **Data Insertion**: Initial role assignments are seeded into `orch_role_assignments`.
4. **View Creation**: A view `orch_active_roles` is created to provide a simplified view of active role assignments.

#### Patterns
- **Singleton**: The `orch_active_roles` view acts as a singleton, providing a consistent and simplified interface to the active role assignments.
- **Configuration Management**: The `orch_config_snapshots` table is designed to store configuration snapshots for reproducibility.

#### Dependencies
- **PostgreSQL**: The entire file relies on PostgreSQL for executing the SQL statements.
- **JSONB**: The `orch_role_assignments` and `orch_config_snapshots` tables use JSONB for storing configuration data.

#### Interfaces
- **Tables**: `orch_role_assignments`, `orch_config_snapshots`
- **View**: `orch_active_roles`

#### Database
- **Tables**:
  - `orch_role_assignments`: Stores role assignments with configurations and scores.
  - `orch_config_snapshots`: Stores configuration snapshots for reproducibility.
- **Indexes**:
  - `idx_orch_roles_active`: Index on `orch_role_assignments` for active roles.

#### Configuration
- **Environment Variables**: None directly used in this file.
- **Config Files**: None directly used in this file.

#### Key Logic
- **Role Assignments**: The `orch_role_assignments` table stores mappings between roles and models, including configurations and scores.
- **Configuration Snapshots**: The `orch_config_snapshots` table stores snapshots of configurations for reproducibility.
- **Active Roles View**: The `orch_active_roles` view provides a simplified interface to active role assignments, filtering and formatting the data for easier consumption.

#### Integration Points
- **Mythos Subsystems**: This schema integrates with other subsystems by providing a consistent and structured way to manage role assignments and configuration snapshots.
- **Data Access**: The `orch_active_roles` view can be queried by other parts of the system to get the current active role assignments.
- **Configuration Management**: The `orch_config_snapshots` table can be used by configuration management services to store and retrieve configuration snapshots.

### Summary
This SQL file enhances the Mythos system by introducing new tables for managing role assignments and configuration snapshots. It ensures that active role assignments are easily accessible through a view, providing a robust and reproducible configuration management system.
