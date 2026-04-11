# docs/AUTONOMIC_SYSTEM.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 818

---

### Purpose
The `AUTONOMIC_SYSTEM.md` file serves as a design document for the Iris Autonomic System, detailing its theoretical foundation, architectural design, and database schema. It outlines the system's components, their interactions, and the principles guiding its implementation.

### Architecture
The document describes the Iris Autonomic System as comprising three primary layers:
1. **Trigger Engine**: Manages time-based, event-based, and threshold-based triggers.
2. **Action Router**: Routes actions to either reflexes, decision gates (Ollama), or direct execution.
3. **Action Plan**: Executes actions through Telegram notifications, Redis queues, and Postgres writes.
4. **Context Engine**: Gathers context from various sources like filesystem, Postgres, Neo4j, and Redis.
5. **Learning System**: Tracks outcomes, refines prompts, and promotes reflexes based on performance.

### Patterns
The design leverages several architectural patterns:
- **Observer Pattern**: The trigger engine observes various events and schedules.
- **Decision Tree**: The action router uses a decision tree to route actions based on their type and context.
- **Component-Based Architecture**: The system is modular, with distinct components handling specific tasks.

### Dependencies
The document references several dependencies and subsystems:
- **Ollama**: Used for decision-making via prompts.
- **Postgres**: Stores scheduled triggers, trigger logs, and escalation rules.
- **Redis**: Manages event counters with TTL-based decay.
- **Neo4j**: Provides graph-based context queries.
- **Telegram**: Used for notifications.

### Interfaces
The document does not explicitly list interfaces but implies the following:
- **Trigger Engine**: Interfaces with time-based, event-based, and threshold-based triggers.
- **Action Router**: Interfaces with reflexes, decision gates, and direct execution components.
- **Action Plan**: Interfaces with Telegram, Redis, and Postgres for notifications, queue management, and writes.

### Database
The document describes several database tables and Redis keys:
- **`scheduled_triggers`**: Stores details about scheduled triggers.
- **`trigger_log`**: Logs the execution of triggers.
- **`event_counters`**: Redis keys for event counters with TTL-based decay.
- **`escalation_rules`**: Stores rules for escalation based on event patterns.

### Configuration
The document mentions several configuration elements:
- **Streams**: The system is designed to affect multiple streams (NEU, SYS, LOG, SEN).
- **Environment Variables**: `.env` file is sanitized and used for configuration.
- **STREAMS.json**: Configuration file for streams.

### Key Logic
The key logic revolves around:
- **Trigger Management**: Scheduling and executing triggers based on time, events, and thresholds.
- **Action Routing**: Deciding whether to execute a reflex, consult Ollama, or execute directly.
- **Context Gathering**: Collecting necessary context from various sources before executing actions.
- **Learning and Adaptation**: Tracking outcomes, refining prompts, and promoting reflexes based on performance.

### Integration Points
The system integrates with several subsystems:
- **Postgres**: For storing and querying scheduled triggers, logs, and escalation rules.
- **Redis**: For managing event counters and queue management.
- **Neo4j**: For graph-based context queries.
- **Ollama**: For decision-making via prompts.
- **Telegram**: For notifications.
- **Filesystem**: For reading files and logs.
- **Git History**: For historical context.
- **Service Status**: For monitoring service health.

### Summary
The `AUTONOMIC_SYSTEM.md` document provides a comprehensive design for the Iris Autonomic System, detailing its theoretical foundation, architectural design, and database schema. It outlines the system's components, their interactions, and the principles guiding its implementation, emphasizing modularity, decision-making, and continuous learning.
