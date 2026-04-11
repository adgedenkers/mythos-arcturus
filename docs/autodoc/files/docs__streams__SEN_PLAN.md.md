# docs/streams/SEN_PLAN.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 140

---

### Purpose
The `SEN_PLAN.md` file serves as a comprehensive build plan and documentation for the `SEN` (SENSUS) stream within the Mythos system. It outlines the existing infrastructure, build phases, known gaps, cross-stream dependencies, and a session start checklist.

### Architecture
The file is structured as a markdown document, organized into sections such as "What Exists," "Build Phases," "Known Gaps," "Cross-Stream Dependencies," and "Session Start Checklist." Each section contains detailed information about the current state, planned phases, and dependencies.

### Patterns
This document does not implement any design patterns as it is a documentation file rather than a code file.

### Dependencies
The document does not import or rely on any external code or libraries. Instead, it references various components and subsystems within the Mythos system.

### Interfaces
The document does not expose interfaces but rather serves as a reference for developers and system administrators to understand the `SEN` stream's architecture and dependencies.

### Database
The document references several database tables and Neo4j labels:
- **PostgreSQL Tables:**
  - `astro_natal_charts`
  - `astrological_events`
  - `message_astrological_context`
  - `calendar_events`
  - `routines`
  - `routine_completions`
  - `recurring_schedules`
  - `checkin_log`
  - `daily_tasks`
  - `known_locations`
  - `known_routes`
- **Neo4j Labels:**
  - `Chart` nodes
  - `Event` nodes
  - `Location` nodes

### Configuration
The document does not specify any configuration files or environment variables directly. However, it references the need for API keys and the potential need for rotation in the weather handler.

### Key Logic
The document outlines the key logic and phases for building the `SEN` stream:
1. **Verification of Core Infrastructure**: Ensuring all sensory inputs are clean and operational.
2. **Environmental Awareness**: Producing a continuous environmental awareness stream for the NEU subsystem.
3. **Sensory Integration**: Feeding data into NEU consciousness, MNE memory, and LOG knowledge graph.
4. **Sensory Intelligence**: Anticipating environmental conditions rather than just reporting them.

### Integration Points
The document highlights several integration points with other subsystems:
- **NEU**: Writing to `perception_log`, linking transits to `Soul` nodes, and feeding routine completions.
- **MNE**: Mirroring significant calendar events to `life_events`.
- **SYS**: Registering bot commands and reading `Person` nodes.
- **LOG**: Storing synastry analysis as `Event` nodes.

### Detailed Analysis

#### What Exists (Inherited from Legacy Patches)
- **Core Infrastructure**: The document lists various components inherited from legacy patches, including the Astrology Engine, Astro Chart Command, Ephemeris Data, Lunar Data, Calendar System, Weather Handler, Routines Engine, Route Planner, Vision Prompts, and Astrological Context per Message.
- **Database State**: It mentions the presence of several PostgreSQL tables and their current state.
- **Neo4j State**: It lists the presence of `Chart`, `Event`, and `Location` nodes.

#### Build Phases
- **Phase 1 — SEN Foundations**: Focuses on verifying the operational status of core components.
- **Phase 2 — Environmental Awareness**: Aims to produce a continuous environmental awareness stream.
- **Phase 3 — Sensory Integration**: Integrates data into NEU consciousness, MNE memory, and LOG knowledge graph.
- **Phase 4 — Sensory Intelligence**: Anticipates environmental conditions based on patterns and cycles.

#### Known Gaps
- **S2b Lunar System**: Unclear if it runs continuously or on-demand.
- **Message Astrological Context**: Unclear if it is populated in real-time.
- **Routines Engine**: Unclear status of completion tracking.
- **Weather Handler**: Potential need to rotate API keys.
- **Vision Prompts**: Unclear consumption.
- **Route Planner**: Unknown integration status.

#### Cross-Stream Dependencies
- **NEU**: Writing to `perception_log`, linking transits to `Soul` nodes.
- **MNE**: Mirroring significant calendar events to `life_events`.
- **SYS**: Reading `Person` nodes and registering bot commands.

#### Session Start Checklist
- **Astrology Engine**: Checks the presence and content of the `astrology` directory and `astro_natal_charts` table.
- **Lunar Data**: Checks the presence of lunar data files.
- **Calendar**: Checks the presence and recent entries in `calendar_events`.
- **Message Astrological Context**: Checks the presence and recent entries in `message_astrological_context`.
- **Routines**: Checks the presence and recent entries in `routines` and `routine_completions`.

This document serves as a critical reference for the development and maintenance of the `SEN` stream within the Mythos system.
