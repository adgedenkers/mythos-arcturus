# core/migration_0096_routines.sql

**Language:** sql
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 160

---

### Purpose
The `core/migration_0096_routines.sql` file is a SQL migration script that creates and populates several tables to manage recurring routines and calendar events for the Mythos system. It includes tables for routine templates, routine completions, check-in logs, and calendar events.

### Architecture
The file consists of several SQL statements to create tables and indexes, and to insert initial data. The tables are designed to store different aspects of routines and events, including their scheduling, completion status, and metadata.

#### Tables Created:
1. **routines**: Stores routine templates with details such as frequency, assigned person, and priority.
2. **routine_completions**: Tracks the completion status of each routine instance.
3. **checkin_log**: Logs check-ins with the system, including summaries and user responses.
4. **calendar_events**: Manages calendar events with recurrence and source information.

#### Indexes:
- Several indexes are created to optimize queries on specific columns, such as `is_active`, `frequency`, `domain`, `due_date`, `status`, `event_date`, and `person`.

### Patterns
- **Data Access Object (DAO)**: The tables and indexes are designed to facilitate efficient data access and retrieval, which is a common pattern in database design.

### Dependencies
- **PostgreSQL**: The script is written for PostgreSQL and relies on its SQL syntax and features.

### Interfaces
- **Database Tables**: The script exposes several tables (`routines`, `routine_completions`, `checkin_log`, `calendar_events`) that can be queried and updated by other parts of the Mythos system.

### Database
- **Tables Created**:
  - `routines`: Stores routine templates.
  - `routine_completions`: Tracks completion status of routine instances.
  - `checkin_log`: Logs check-ins with the system.
  - `calendar_events`: Manages calendar events.

- **Indexes Created**:
  - `idx_routines_active`, `idx_routines_frequency`, `idx_routines_domain`
  - `idx_routine_completions_date`, `idx_routine_completions_status`, `idx_routine_completions_routine`
  - `idx_checkin_log_date`
  - `idx_calendar_events_date`, `idx_calendar_events_person`

### Configuration
- **Environment Variables**: No specific environment variables are used in this script.
- **Config Files**: No specific configuration files are referenced.

### Key Logic
- **Routine Templates**: The `routines` table stores the details of each routine, including frequency, assigned person, and priority.
- **Completion Tracking**: The `routine_completions` table tracks the completion status of each routine instance, ensuring that the system can monitor and report on routine adherence.
- **Check-in Logs**: The `checkin_log` table logs check-ins with the system, providing a record of user interactions.
- **Calendar Events**: The `calendar_events` table manages calendar events, including their recurrence and source information.

### Integration Points
- **Routines Subsystem**: The `routines` and `routine_completions` tables are integral to the routines subsystem, which is likely integrated with other parts of the Mythos system for task management and reporting.
- **Check-in Subsystem**: The `checkin_log` table is used by the check-in subsystem to log interactions with the system.
- **Calendar Subsystem**: The `calendar_events` table is used by the calendar subsystem to manage and display calendar events.

### Summary
This migration script sets up the necessary tables and indexes to manage recurring routines and calendar events in the Mythos system. It provides a robust structure for tracking routine adherence, logging check-ins, and managing calendar events, which are critical components of the system's life management capabilities.
