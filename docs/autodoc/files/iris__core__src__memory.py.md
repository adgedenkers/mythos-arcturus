# iris/core/src/memory.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 131

---

### Documentation for `iris/core/src/memory.py`

#### Purpose
The `MemorySystem` class in `memory.py` is responsible for managing different types of memory in the Iris system, including experiential, narrative, and semantic memory. It provides methods to initialize, record, recall, and shut down memory operations.

#### Architecture
- **Class**: `MemorySystem`
  - **Attributes**: `config`, `_initialized`
  - **Methods**: 
    - `__init__`: Constructor that initializes the `MemorySystem` with a configuration object.
    - `initialize`: Asynchronously initializes the memory systems.
    - `find_connections`: Asynchronously finds connections between current perceptions and existing memories.
    - `record_cycle`: Asynchronously records a consciousness cycle to memory if significant.
    - `record_experiential`: Asynchronously records a subjective experience to experiential memory.
    - `record_narrative`: Asynchronously records an event to narrative memory.
    - `recall`: Asynchronously recalls memories relevant to a query.
    - `get_recent_context`: Asynchronously retrieves recent context for grounding current thinking.
    - `shutdown`: Asynchronously shuts down the memory systems.

#### Patterns
- **Singleton Pattern**: The `MemorySystem` class can be designed as a singleton to ensure that only one instance of the memory system exists throughout the application.
- **Observer Pattern**: The `find_connections` method can be seen as an observer that reacts to new perceptions by finding connections with existing memories.

#### Dependencies
- **Imports**: 
  - `asyncio`: For asynchronous operations.
  - `structlog`: For logging.
  - `datetime`: For handling timestamps.
  - `typing`: For type hints.
  - `Config`: Configuration class from the `iris.core.config` module.

#### Interfaces
- **Public Methods**:
  - `initialize()`: Initializes the memory systems.
  - `find_connections(perceptions: Dict[str, Any]) -> List[Dict[str, Any]]`: Finds connections between current perceptions and existing memories.
  - `record_cycle(reflections: Dict[str, Any])`: Records a consciousness cycle to memory.
  - `record_experiential(experience: Dict[str, Any])`: Records a subjective experience to experiential memory.
  - `record_narrative(event: Dict[str, Any])`: Records an event to narrative memory.
  - `recall(query: str, limit: int = 10) -> List[Dict[str, Any]]`: Recalls memories relevant to a query.
  - `get_recent_context(hours: int = 24) -> Dict[str, Any]`: Retrieves recent context for grounding current thinking.
  - `shutdown()`: Shuts down the memory systems.

#### Database
- **References**:
  - `datetime`: Used for timestamp operations.
  - `typing`: Used for type hints.

#### Configuration
- **Configuration**: The `MemorySystem` class takes a `Config` object during initialization, which likely contains configuration settings for the memory system.

#### Key Logic
- **Initialization**: The `initialize` method logs the initialization process and sets the `_initialized` flag to `True`.
- **Finding Connections**: The `find_connections` method is designed to query memory stores for related information based on current perceptions.
- **Recording Cycles**: The `record_cycle` method determines if a cycle is significant enough to record and stores it in experiential memory if necessary.
- **Recording Experiential Memory**: The `record_experiential` method logs the recording of a subjective experience and stores it in the experiential memory table.
- **Recording Narrative Memory**: The `record_narrative` method logs the recording of an event and stores it in the narrative memory table.
- **Recalling Memories**: The `recall` method performs a semantic search across memory stores to find relevant memories.
- **Getting Recent Context**: The `get_recent_context` method retrieves recent context by querying recent events and ongoing threads.
- **Shutting Down**: The `shutdown` method logs the shutdown process and sets the `_initialized` flag to `False`.

#### Integration Points
- **Mythos Subsystems**:
  - **Logging**: Uses `structlog` for logging.
  - **Configuration**: Integrates with the `Config` class for configuration settings.
  - **Asynchronous Operations**: Uses `asyncio` for asynchronous operations, which can be integrated with other asynchronous subsystems in Mythos.
  - **Database Operations**: The methods are designed to interact with PostgreSQL and Neo4j databases for storing and retrieving memory data, though specific table and label interactions are marked as `TODO`.

This documentation provides a comprehensive overview of the `MemorySystem` class and its methods, detailing its role in the Mythos system and how it integrates with other components.
