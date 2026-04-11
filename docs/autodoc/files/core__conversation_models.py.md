# core/conversation_models.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 399

---

### File: core/conversation_models.py

#### Purpose
This file defines the core models and enums used to represent conversations within the Mythos system. It includes various Pydantic models for different aspects of a conversation, such as participants, turns, decisions, and spiritual concepts, as well as enums for conversation types and edge types.

#### Architecture
The file is structured around several Pydantic models and enums:

1. **Enums**:
   - `ConversationType`: Represents different types of conversations (e.g., technical build, channeling).
   - `InitiatorType`: Represents the type of initiator (e.g., human, model).
   - `EdgeType`: Represents different types of edges in the conversation graph (e.g., CONTINUES, BUILDS_ON).

2. **Models**:
   - `Participant`: Represents a participant in the conversation.
   - `BranchPoint`: Represents a branching point in the conversation.
   - `Decision`: Represents a decision made during the conversation.
   - `ActionItem`: Represents an action item from the conversation.
   - `SpiritualConceptRef`: Represents a spiritual concept with a domain.
   - `EntityRefs`: Represents a lightweight cache of entities for full-text search indexing.
   - `ConversationEdge`: Represents an edge in the conversation graph.
   - `SpiralSignature`: Represents the position across nested cycles.
   - `SpiralContext`: Represents the spiral time context for a conversation.
   - `SpiralEpoch`: Represents a personal time anchor in the spiral history.
   - `Turn`: Represents a turn in the conversation.
   - `ConversationRecord`: Represents the canonical conversation metadata object.

#### Patterns
- **Factory Method**: Not explicitly used.
- **Singleton**: Not explicitly used.
- **Observer**: Not explicitly used.
- **Data Transfer Object (DTO)**: Used through Pydantic models to serialize and validate data.

#### Dependencies
- `hashlib`: For computing SHA-256 hashes.
- `json`: For JSON serialization.
- `datetime`: For date and time handling.
- `enum`: For defining enums.
- `typing`: For type annotations.
- `uuid`: For generating unique identifiers.
- `pydantic`: For defining and validating models.

#### Interfaces
- **Enums**: `ConversationType`, `InitiatorType`, `EdgeType`.
- **Models**: `Participant`, `BranchPoint`, `Decision`, `ActionItem`, `SpiritualConceptRef`, `EntityRefs`, `ConversationEdge`, `SpiralSignature`, `SpiralContext`, `SpiralEpoch`, `Turn`, `ConversationRecord`.
- **Methods**:
  - `compute_signature`: Computes the full spiral signature for a given date under an epoch.
  - `compute_content_hash`: Computes a SHA-256 hash from canonical fields for idempotent upsert.
  - `sync_turn_count`: Synchronizes the turn count with the actual turns.
  - `sync_spiritual_concepts_to_entities`: Synchronizes spiritual concepts with the entity cache.

#### Database
- **PostgreSQL**: 
  - `ConversationRecord`: The full object is serialized and stored in PostgreSQL.
  - `EntityRefs`: Used for full-text search indexing.
- **Neo4j**: 
  - `ConversationRecord`: Only specific fields (e.g., `conversation_id`, `started_at`, `ended_at`, `type`, `source_model`, `revision`) and relationship edges are stored.
  - `SpiritualConceptRef`: Mapped to `(:SpiritualConcept)` nodes in Neo4j.

#### Configuration
- No explicit configuration files or environment variables are used in this file.

#### Key Logic
- **Spiral Signature Calculation**: Computes the position across nested cycles using base-9 modular arithmetic.
- **Content Hashing**: Computes a SHA-256 hash from canonical fields to ensure idempotent upserts.
- **Turn Count Synchronization**: Ensures the `turn_count` field is in sync with the actual number of turns.
- **Entity Synchronization**: Ensures the `entities.spiritual_concepts` field is in sync with the `spiritual_concepts` list for full-text search indexing.

#### Integration Points
- **PostgreSQL**: The `ConversationRecord` model is serialized and stored in PostgreSQL.
- **Neo4j**: The `ConversationRecord` model is used to create nodes and edges in Neo4j.
- **FastAPI**: The models defined here are likely used in API endpoints to handle conversation data.
- **Ollama**: The `raw_payload` field in `ConversationRecord` holds the verbatim conversation log, which could be from Ollama or other sources.
- **Redis**: Not directly referenced in this file, but Redis could be used for caching or other purposes in the broader system.
- **Other Mythos Subsystems**: The models and enums defined here are likely used across various subsystems for consistent data representation and validation.
