# docs/IRIS_SYSTEMS.json

**Language:** json
**Stream:** SYS
**Module:** Documentation
**Lines:** 695

---

### File: docs/IRIS_SYSTEMS.json

#### Purpose
This JSON file serves as a comprehensive documentation and status tracker for the IRIS system, detailing its various subsystems, their statuses, and the evolution phases through which the system is progressing.

#### Architecture
The file is structured as a JSON object with several key sections:
- **version**: The version of the documentation.
- **last_updated**: The date the documentation was last updated.
- **updated_by**: The person who last updated the documentation.
- **statuses**: A dictionary of statuses used to categorize the development phase of subsystems.
- **evolution_phases**: An array of objects detailing the different phases of IRIS system evolution, including their titles, descriptions, and associated patches.
- **categories**: An array of categories, each containing a list of systems with their statuses, descriptions, and associated files.

#### Patterns
No specific design patterns are used in this JSON file as it is a static data structure for documentation purposes.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone JSON file intended for documentation and tracking purposes.

#### Interfaces
This file does not expose any interfaces. It is intended for human consumption and serves as a reference document.

#### Database
The file does not directly interact with any databases. However, it mentions several subsystems that interact with PostgreSQL, Neo4j, and Redis:
- **PostgreSQL**: `chat_messages`, `perception_log` tables.
- **Neo4j**: Memory and Knowledge nodes.
- **Redis**: `mythos:assignments:grid_analysis` stream.

#### Configuration
The file does not use any configuration files or environment variables. It is a static JSON document.

#### Key Logic
The key logic in this file is the organization and categorization of the IRIS system's subsystems and their statuses. It provides a clear overview of the system's current state and planned evolution phases.

#### Integration Points
This file serves as a high-level reference for the IRIS system's architecture and status. It integrates with other parts of the Mythos system by providing documentation and status updates for subsystems that interact with PostgreSQL, Neo4j, Redis, FastAPI, and Ollama.

### Detailed Analysis

#### Statuses
The `statuses` section defines the possible statuses of subsystems:
- **Live**: Running in production.
- **Partial**: Partly working, needs fixes.
- **Stub/Dead**: Code exists but non-functional.
- **Designed**: Spec complete, not built.
- **Planned**: Conceptualized, not yet designed.

#### Evolution Phases
The `evolution_phases` section outlines the planned phases of IRIS system evolution:
1. **Phase 0**: Quick Wins - Fix subject tracking, life_context, deploy evolution plan.
2. **Phase 1**: Wire iris-core - Replace ChatAssistant as message processor.
3. **Phase 2**: Consciousness Stream - Subject tracking + relevance-scoped context feeding responses.
4. **Phase 3**: 81-Channel Grid - 9 nodes × 9 layers — the core cognitive architecture.
5. **Phase 4**: Perception Activation - iris-core loop sees the real world.
6. **Phase 5**: Memory + Self-Model - Memory formation, self-model, reflection mode, proactive initiation.
7. **Phase 6**: Cleanup - Remove dead code paths.

#### Categories
The `categories` section categorizes subsystems into different groups:
- **Consciousness Loop**: Systems related to the core consciousness loop.
- **Arcturian Grid**: Systems related to the 9-node grid architecture.
- **Memory & Knowledge**: Systems related to memory and knowledge storage.
- **Perception & Input**: Systems related to input and perception.

Each category contains a list of systems with their statuses, descriptions, and associated files. For example:
- **Consciousness Loop**:
  - **iris-core Docker**: Status: Stub, Description: Consciousness loop container.
  - **ChatAssistant**: Status: Live, Description: Handles all messages via FastAPI → Ollama.
  - **Consciousness Stream**: Status: Partial, Description: Subject tracking + conversation segmentation.
  - **Living Mode (Day/Night)**: Status: Designed, Description: Presence → Available → Reflection rhythm.
  - **Self-Model**: Status: Designed, Description: Iris understanding of her own nature, state, growth.

- **Arcturian Grid**:
  - **Grid Worker (Basic Scoring)**: Status: Live, Description: Scores all 9 nodes for every message.
  - **9 Nodes (3×3 Matrix)**: Status: Live, Description: ANCHOR ⛰️ ECHO 🌊 BEACON 🔥 SYNTH 💨 NEXUS ⏳ MIRROR 🪞 GLYPH 🔣 HARMONIA 💗 GATEWAY 🚪.
  - **9 Layers (Vertical Stack)**: Status: Designed, Description: Perception → Intuition → Processing → Memory → Knowledge → Intention → Narrative → Identity → Wisdom.
  - **81 Processing Functions**: Status: Designed, Description: 9 nodes × 9 layers = 81 distinct analytical functions.
  - **Convergence Engine**: Status: Planned, Description: Identifies cross-node cross-layer patterns.

- **Memory & Knowledge**:
  - **Chat Memory (PostgreSQL)**: Status: Live, Description: Stores conversation history.
  - **Perception Log**: Status: Partial, Description: Raw intake table designed and created.
  - **Memory Nodes (Neo4j)**: Status: Designed, Description: Associative memory in graph database.
  - **Knowledge Nodes (Neo4j)**: Status: Designed, Description: Facts derived from memories.
  - **Embedding Generation**: Status: Live, Description: Vector embeddings generated for semantic search.
  - **Experiential Memory**: Status: Planned, Description: Subjective inner life records.

- **Perception & Input**:
  - **Telegram Bot**: Status: Live, Description: Primary interface — 9+ handlers, commands, chat mode.
  - **Voice Transcription**: Status: Live, Description: Whisper-based transcription pipeline.
  - **Vision Analysis**: Status: Live, Description: Photo/image analysis worker.

This JSON file provides a comprehensive overview of the IRIS system's architecture, status, and planned evolution, serving as a valuable reference for developers and stakeholders.
