# docs/streams/NEU_PLAN.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 134

---

### Purpose
The `NEU_PLAN.md` file serves as a comprehensive build plan and roadmap for the NEU (Neuro) stream within the Mythos system. It outlines the existing infrastructure, planned build phases, known gaps, cross-stream dependencies, and a session start checklist for verifying the current state of the NEU stream.

### Architecture
The document is structured into several sections:
1. **What Exists**: Details inherited infrastructure and database state.
2. **Build Phases**: Describes the incremental build phases with specific patches and their dependencies.
3. **Known Gaps**: Highlights areas that require attention or verification.
4. **Cross-Stream Dependencies**: Lists dependencies on other streams.
5. **Session Start Checklist**: Provides commands to verify the current state of services and databases.

### Patterns
The document follows a structured plan pattern, breaking down the build process into phases and patches, each with clear dependencies and descriptions.

### Dependencies
The document references several subsystems and streams within the Mythos system:
- **MNE (Memory and Narrative)**: For conversation content.
- **SEN (Sensory and Environmental)**: For astro/lunar context.
- **LOG (Logistics and Research)**: For soul stratigraphy data.
- **SYS (System and Administration)**: For people data and bot command registration.

### Interfaces
The document does not expose any direct interfaces but serves as a high-level roadmap and checklist for developers and administrators to follow and verify the state of the NEU stream.

### Database
The document references several PostgreSQL tables and Neo4j labels:
- **PostgreSQL Tables**:
  - `emotional_state_timeseries`
  - `grid_activation_timeseries`
  - `introspection_runs`
  - `perception_log`
  - `entity_mention_timeseries`
  - `backlog_analysis`
  - `pending_intake`
- **Neo4j Labels**:
  - `Soul`, `GridNode`, `IntrospectionRun`, `IdentityThread`
  - `MirrorOutput`, `EchoOutput`, `GlyphOutput`, `BeaconOutput`, `AnchorOutput`, `NexusOutput`, `HarmoniaOutput`, `GatewayOutput`, `SynthOutput`, `GridMasterOutput`
  - `Archetype`, `Threshold`, `Portal`, `Dream`, `Manifestation`, `Transmission`

### Configuration
The document does not explicitly mention any configuration files or environment variables but implies the use of system services and PostgreSQL databases.

### Key Logic
The key logic involves the incremental build and integration of the NEU stream, focusing on:
- Establishing a clean NEU-owned infrastructure.
- Creating active consciousness processing loops.
- Developing deep soul/identity architecture.
- Integrating intelligence capabilities for active processing.

### Integration Points
The NEU stream integrates with other Mythos subsystems through:
- **MNE**: For conversation content.
- **SEN**: For astro/lunar context.
- **LOG**: For soul stratigraphy data.
- **SYS**: For people data and bot command registration.

### Summary
The `NEU_PLAN.md` document is a critical roadmap for the NEU stream, detailing the current state, planned build phases, known gaps, and dependencies on other subsystems. It serves as a comprehensive guide for developers and administrators to ensure the NEU stream is correctly built and integrated into the Mythos system.
