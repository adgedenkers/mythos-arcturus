## autonomic_system

### Purpose
The **autonomic_system** component of Mythos is designed to manage Iris's self-maintaining infrastructure, encompassing three primary engines: a trigger engine for scheduled and event-based actions, an idle task engine for background maintenance tasks, and a context engine for collecting diagnostic data from various sources. This system operates through three deployment phases, each progressively adding functionality.

### Key Files and Structure
- **Service**: `mythos-trigger.service`
- **Tables**:
  - `scheduled_triggers`: Stores scheduled trigger configurations.
  - `trigger_log`: Logs the execution of triggers.
  - `escalation_rules`: Defines rules for escalation based on trigger outcomes.
  - `iris_task_log`: Tracks the status and results of tasks executed by the idle task engine.

### Data Flow
1. **Trigger Engine**: Triggers are scheduled or fired based on events, with actions logged in `trigger_log` and escalations handled according to `escalation_rules`.
2. **Idle Task Engine**: Executes five background maintenance tasks, logging their status and results in `iris_task_log`.
3. **Context Engine**: Gathers diagnostic data from files, Postgres, Neo4j, Redis, git repositories, services, and disk usage through 13 providers.

### Dependencies and Integration Points
- **External Systems**:
  - Files: For reading/writing diagnostic logs.
  - Databases (Postgres, Neo4j): For querying operational data.
  - Caches (Redis): For quick access to frequently used information.
  - Git Repositories: For tracking changes in codebases.
  - Services and Disk Usage: Monitoring for performance diagnostics.

### Known Issues or Technical Debt
- Currently, the system is under development with no files or lines of code committed yet. This indicates that all architectural components are conceptual at this stage and require implementation.
- Future phases will need to address integration testing between engines and external systems to ensure seamless operation.
- The context engine's data gathering mechanism needs further refinement for efficient handling of large datasets from various sources.

This section provides a foundational overview of the **autonomic_system** component, highlighting its purpose, structure, and planned operational flow within Mythos.
