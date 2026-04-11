# migrations/sys_0035_trigger_schema.sql

**Language:** sql
**Stream:** SYS
**Module:** Database Migrations
**Lines:** 209

---

### Purpose
The `sys_0035_trigger_schema.sql` file is a PostgreSQL migration script that creates and seeds tables for managing scheduled triggers, trigger logs, and escalation rules within the Mythos system. It ensures the system can schedule and log various automated actions and handle threshold-based escalations.

### Architecture
The file consists of several SQL statements:
1. **Table Creation**: Three tables are created: `scheduled_triggers`, `trigger_log`, and `escalation_rules`.
2. **Indexes**: Indexes are created for efficient querying.
3. **Comments**: Comments are added to provide context for each table.
4. **Seed Data**: Initial data is inserted into `scheduled_triggers` and `escalation_rules` tables.

### Patterns
- **Singleton Pattern**: Not applicable as this is a migration script.
- **Factory Pattern**: Not applicable as this is a migration script.
- **Observer Pattern**: Not applicable as this is a migration script.

### Dependencies
- **PostgreSQL**: The script is designed to run within a PostgreSQL environment.
- **Schema**: The script assumes the existence of a schema where these tables will be created.

### Interfaces
- **Tables**: The script exposes three tables (`scheduled_triggers`, `trigger_log`, `escalation_rules`) to the Mythos system.
- **Indexes**: Indexes are created to optimize queries on these tables.

### Database
- **Tables Created**:
  - `scheduled_triggers`: Stores scheduled triggers with details like name, schedule, action type, and metadata.
  - `trigger_log`: Logs every trigger firing with details like fired_at, context, decisions, actions, and outcomes.
  - `escalation_rules`: Defines threshold-based escalation rules for handling events.
- **Indexes Created**:
  - `idx_triggers_next_fire` on `scheduled_triggers` for efficient querying based on `next_fire`.
  - `idx_triggers_type` on `scheduled_triggers` for efficient querying based on `trigger_type`.
  - `idx_trigger_log_name` on `trigger_log` for efficient querying based on `trigger_name`.
  - `idx_trigger_log_fired` on `trigger_log` for efficient querying based on `fired_at`.

### Configuration
- **Environment Variables**: None directly used in this script.
- **Config Files**: None directly used in this script.

### Key Logic
- **Scheduled Triggers**: The `scheduled_triggers` table stores details about various scheduled triggers, including their type, schedule, action type, and payload.
- **Trigger Log**: The `trigger_log` table logs every trigger firing, capturing context, decisions, actions, and outcomes.
- **Escalation Rules**: The `escalation_rules` table defines threshold-based escalation rules, which are used to handle events based on predefined thresholds and actions.

### Integration Points
- **Mythos API**: The `scheduled_triggers` table is likely integrated with the Mythos API to schedule and manage triggers.
- **Task Management**: The `scheduled_triggers` table integrates with the task management subsystem to execute tasks based on schedules.
- **Event Handling**: The `escalation_rules` table integrates with the event handling subsystem to manage threshold-based escalations.
- **Logging**: The `trigger_log` table integrates with the logging subsystem to log all trigger activities.

### Summary
This migration script sets up the necessary infrastructure for managing scheduled triggers, logging trigger activities, and handling threshold-based escalations within the Mythos system. It ensures that the system can efficiently schedule and log automated actions and respond to events based on predefined rules.
