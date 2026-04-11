# docs/STREAMS.json

**Language:** json
**Stream:** SYS
**Module:** Documentation
**Lines:** 574

---

### File: docs/STREAMS.json

#### Purpose
This JSON file serves as a configuration and documentation file for the Mythos Development Stream Coordinator. It details the ownership and responsibilities of various subsystems (streams) within the Mythos system, including paths, database tables, Neo4j labels, handlers, API routes, and services.

#### Architecture
The file is structured as a JSON object with a `meta` section and a `streams` section. Each stream within the `streams` section is a detailed object containing information such as name, description, owned paths, database tables, Neo4j labels, handlers, API routes, web templates, services, and other metadata.

#### Patterns
No specific design patterns are used in this JSON file, as it is a configuration file rather than executable code.

#### Dependencies
This JSON file does not import or rely on any external dependencies. It is a standalone configuration file.

#### Interfaces
The file exposes configuration details to other parts of the Mythos system, particularly to subsystems responsible for managing and coordinating the various streams.

#### Database
The file lists the PostgreSQL tables and Neo4j labels owned by each stream:
- **NEU**: `emotional_state_timeseries`, `grid_activation_timeseries`, `introspection_runs`, `perception_log`, `entity_mention_timeseries`, `backlog_analysis`, `pending_intake` (PostgreSQL); `Activation`, `AnchorOutput`, `Archetype`, etc. (Neo4j)
- **LOG**: `harmonic_resonance`, `harmonic_values`, `orch_config_snapshots`, etc. (PostgreSQL); `AppRegistry`, `Commitment`, `CommunicationGap`, etc. (Neo4j)
- **MNE**: `chat_messages`, `conversation_participants`, `conversation_segments`, etc. (PostgreSQL); `BoundaryNeeded`, `Boundary`, `Conversation`, etc. (Neo4j)
- **SEN**: `astro_arabic_parts`, `astro_balance`, `astro_chart_objects`, etc. (PostgreSQL); `Chart`, `Event`, `Location` (Neo4j)
- **SYS**: Various paths and files, but no specific database tables or labels listed.

#### Configuration
The file itself serves as a configuration file, detailing the ownership and responsibilities of each stream. It does not reference external configuration files or environment variables.

#### Key Logic
The key logic in this file is the definition and organization of the streams, detailing their responsibilities and ownership of various system components. This information is used by the Mythos system to manage and coordinate the different subsystems.

#### Integration Points
This file integrates with other parts of the Mythos system by providing configuration details that are used by subsystems to manage paths, database tables, handlers, API routes, and services. For example:
- **NEU**: Manages paths like `/opt/mythos/neuro/`, `/opt/mythos/iris/`, and handlers like `iris_handler.py`.
- **LOG**: Manages paths like `/opt/mythos/skills/`, `/opt/mythos/harmonics/`, and handlers like `ontology_handler.py`.
- **MNE**: Manages paths like `/opt/mythos/voice_memos/`, `/opt/mythos/media/`, and handlers like `voice_handler.py`.
- **SEN**: Manages paths like `/opt/mythos/astrology/`, `/opt/mythos/vision/`, and handlers like `astrology_handler.py`.
- **SYS**: Manages paths like `/opt/mythos/patches/`, `/opt/mythos/docs/`, and handlers like `telegram_bot/bot.py`.

This configuration file is crucial for the Mythos system to understand the ownership and responsibilities of each stream, enabling proper coordination and management of the entire system.
