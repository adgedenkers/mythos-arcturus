# migrations/sys_0034_trigger_schema.sql

**Language:** sql
**Stream:** SYS
**Module:** Database Migrations
**Lines:** 209

---

### Documentation for `migrations/sys_0034_trigger_schema.sql`

#### Purpose
This SQL file is responsible for creating and seeding the database schema for the trigger infrastructure in the Mythos system. It defines tables for scheduled triggers, trigger logs, and escalation rules, and seeds these tables with initial data.

#### Architecture
The file consists of several sections:
1. **Table Creation**: Defines three tables (`scheduled_triggers`, `trigger_log`, and `escalation_rules`).
2. **Indexes**: Adds indexes to improve query performance.
3. **Comments**: Provides descriptive comments for each table.
4. **Seed Data**: Inserts initial data into the `scheduled_triggers` and `escalation_rules` tables.

#### Patterns
- **Singleton**: The creation of tables and indexes is idempotent due to the use of `CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS`.
- **Seed Data**: The file uses `INSERT INTO ... ON CONFLICT (name) DO NOTHING` to ensure that seed data is only inserted if it does not already exist.

#### Dependencies
- **PostgreSQL**: The file is written in SQL and relies on PostgreSQL for execution.
- **Database Connection**: Requires a connection to the PostgreSQL database where the Mythos system is hosted.

#### Interfaces
- **Tables**: Exposes the following tables to the system:
  - `scheduled_triggers`
  - `trigger_log`
  - `escalation_rules`

#### Database
- **Tables Created**:
  - `scheduled_triggers`: Stores scheduled triggers with details like name, schedule, action type, and payload.
  - `trigger_log`: Logs every trigger firing with context, decisions, actions, and outcomes.
  - `escalation_rules`: Defines threshold-based escalation rules for various events.

#### Configuration
- **Environment Variables**: No specific environment variables are used in this file.
- **Configuration Files**: No configuration files are referenced directly in this file.

#### Key Logic
- **Table Definitions**:
  - `scheduled_triggers`: Manages scheduled triggers with various attributes like `trigger_type`, `schedule`, `action_type`, and `action_payload`.
  - `trigger_log`: Logs detailed information about each trigger firing.
  - `escalation_rules`: Manages escalation rules for different event patterns and tiers.
- **Indexes**: Enhances performance by creating indexes on `next_fire` and `trigger_type` for `scheduled_triggers`, and `trigger_name` and `fired_at` for `trigger_log`.
- **Seed Data**: Inserts predefined triggers and escalation rules to ensure the system has initial configurations.

#### Integration Points
- **Mythos API**: The `scheduled_triggers` table is likely used by the Mythos API to schedule and manage triggers.
- **Task Management**: The `scheduled_triggers` table integrates with the task management subsystem to execute tasks based on schedules.
- **Event Handling**: The `escalation_rules` table integrates with the event handling subsystem to manage escalations based on event patterns and thresholds.
- **Logging**: The `trigger_log` table integrates with the logging subsystem to maintain an audit trail of trigger firings.

### Summary
This SQL file sets up the core infrastructure for managing scheduled triggers, logging trigger activities, and defining escalation rules in the Mythos system. It ensures that the system has a robust mechanism for scheduling tasks, logging activities, and handling escalations based on predefined rules and thresholds.
