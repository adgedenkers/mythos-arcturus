# docs/streams/MNE_PLAN.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 144

---

### Purpose
The `MNE_PLAN.md` file serves as a detailed build plan and documentation for the MNE (MNEMOS) stream within the Mythos system. It outlines the current state of the memory and conversation infrastructure, planned build phases, known gaps, cross-stream dependencies, and a session start checklist.

### Architecture
The file is structured as a markdown document with sections for:
- **Overview**: Stream prefix, current patch, and legacy patches affecting MNE.
- **Existing Infrastructure**: Core infrastructure and database state.
- **Build Phases**: Detailed phases with specific patches, descriptions, and dependencies.
- **Known Gaps**: Areas that need verification or improvement.
- **Cross-Stream Dependencies**: Dependencies on other streams.
- **Session Start Checklist**: Commands to check the health and status of MNE services and data.

### Patterns
The document follows a **document pattern** for system documentation, detailing the current state and future plans in a structured manner. It also uses a **table pattern** to list build phases and dependencies.

### Dependencies
The document does not directly import or rely on any code or libraries but references various services, tables, and patches within the Mythos system.

### Interfaces
The document does not expose any interfaces but serves as a reference for developers and system administrators to understand the current state and future plans of the MNE stream.

### Database
The document references several database tables and Neo4j labels:
- **PostgreSQL Tables**: `conversations`, `conversation_turns`, `voice_memos`, `voice_memo_segments`, `doc_worker_runs`, `spiral_epochs`, `media_assets`, `media_files`, `life_events`, `idea_inbox`, `idea_backlog`.
- **Neo4j Labels**: `Conversation`, `File`, `Directory`, `ThreadGroup`, `Event`, `Person`, `Location`, `Concept`.

### Configuration
The document does not specify any configuration files or environment variables but mentions the need to verify the health of various services and data pipelines.

### Key Logic
The key logic described in the document revolves around:
- Verifying and stabilizing the existing memory infrastructure.
- Implementing recall infrastructure to enable semantic and keyword-based search.
- Capturing richer experiences through voice memos, photos, and media.
- Creating a persistent identity memory to track the arc of relationships.

### Integration Points
The document highlights several integration points with other Mythos subsystems:
- **NEU**: Embedding of conversation content.
- **LOG**: Ontology term linking for subjects.
- **SEN**: Calendar event context for photos.
- **SYS**: People data and bot command registration.

### Summary
The `MNE_PLAN.md` document serves as a comprehensive guide for the MNE stream within the Mythos system. It provides a clear roadmap for building and maintaining the memory and conversation infrastructure, detailing current state, planned phases, known gaps, and cross-stream dependencies. This document is crucial for developers and administrators to understand and manage the MNE stream effectively.
