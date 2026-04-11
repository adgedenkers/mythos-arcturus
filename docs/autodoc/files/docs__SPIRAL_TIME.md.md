# docs/SPIRAL_TIME.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 252

---

### Documentation for `docs/SPIRAL_TIME.md`

#### Purpose
This markdown file documents the Spiral Time Architecture, a system inspired by the Maya calendar system but rebuilt using base-9 mathematics. It outlines nested cycles of different lengths that intersect to create unique day signatures, which are used to track personal and structural rhythms.

#### Architecture
The document is structured into several sections, each detailing different aspects of the Spiral Time Architecture:
- **Nested Interlocking Cycles in Base-9**: Overview of the system.
- **Design Lineage**: Comparison with the Maya calendar system.
- **The Base-9 Cycle Stack**: Detailed description of each layer (Pulse, Weave, Arc, Long Spiral, Great Cycle).
- **Day Signature**: Computation and interpretation of day signatures.
- **Epochs and Resets**: Explanation of epochs and how they can be reset.
- **Resonance Windows**: Detection of alignment points between different individuals.
- **Integration Points**: How the system integrates with other components.
- **Open Questions**: List of unresolved design decisions.
- **Next Steps**: Future development tasks.

#### Patterns
- **Pattern Language**: The document uses the concept of nested cycles from the Maya calendar system and applies it to a base-9 system.
- **Modular Design**: Each section can be treated as a module, focusing on a specific aspect of the architecture.

#### Dependencies
- **None**: This markdown file is a documentation artifact and does not directly import or rely on any code or external libraries.

#### Interfaces
- **None**: This is a documentation file and does not expose any interfaces. However, it outlines interfaces that will be needed in future implementation (e.g., `spiral_context` field in conversation records).

#### Database
- **Neo4j**: The document mentions that `(:Epoch)` nodes will be created for each person, linked via `(:Person)-[:HAS_EPOCH]->(:Epoch)`. `(:SpiralSignature)` properties will be added to Conversation nodes. Resonance windows could be materialized as `(:ResonanceWindow)` nodes.

#### Configuration
- **None**: The document does not specify any configuration files or environment variables.

#### Key Logic
- **Day Signature Computation**: Calculation of day signatures based on the number of days since the epoch.
- **Channel Mapping**: Mapping of weave days to specific node pairs in the 9×9 grid.
- **Resonance Window Detection**: Detection of alignment points between different individuals based on their spiral signatures.

#### Integration Points
- **Conversation Metadata System**: Each conversation record will include a `spiral_context` field containing the person's active epoch, spiral signature, and active grid node/channel.
- **Arcturian Grid**: The grid will factor in the spiral signature when processing conversations.
- **Neo4j**: Integration with Neo4j to store epoch nodes and spiral signatures as properties on Conversation nodes.

### Summary of Key Points
- **Spiral Time Architecture**: A system using nested cycles of different lengths to create unique day signatures.
- **Base-9 Cycle Stack**: Layers include Pulse (9 days), Weave (81 days), Arc (729 days), Long Spiral (6,561 days), and Great Cycle (59,049 days).
- **Day Signature**: Computed based on the number of days since the epoch, providing a unique position across all active layers.
- **Epochs and Resets**: Epochs can be set by individuals and can be reset, creating new epochs without destroying old data.
- **Resonance Windows**: Detection of alignment points between different individuals based on their spiral signatures.
- **Integration**: The system integrates with the conversation metadata system and Neo4j to store and compute spiral signatures.

### Next Steps
- **Add `spiral_context` field to conversation schema**.
- **Build `spiral_time.py` module** to compute signatures, manage epochs, and detect resonance windows.
- **Define grid node-to-day mapping**.
- **Integrate with ingest pipeline** to compute and attach spiral signatures at conversation ingest time.
- **Build resonance calculator** to detect alignment windows based on epochs and date ranges.
