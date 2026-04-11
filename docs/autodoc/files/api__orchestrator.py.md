# api/orchestrator.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 242

---

### File: api/orchestrator.py

#### Purpose
The `Orchestrator` class in `api/orchestrator.py` is responsible for dispatching extraction assignments to Redis streams for asynchronous processing. It provides methods to dispatch various types of tasks and check for summary rebuild triggers.

#### Architecture
The file contains a single class `Orchestrator` and a top-level function `get_orchestrator`. The `Orchestrator` class has methods for initializing the Redis connection, dispatching tasks, and retrieving statistics. The `get_orchestrator` function ensures a single global instance of the `Orchestrator`.

#### Patterns
- **Singleton Pattern**: The `get_orchestrator` function ensures that only one instance of `Orchestrator` is created and reused throughout the application.

#### Dependencies
- **Imports**: `os`, `json`, `uuid`, `logging`, `redis`, `dotenv`, `datetime`, `typing`
- **Environment Variables**: `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`
- **Redis**: Used for task dispatching and statistics tracking.

#### Interfaces
- **Public Methods**:
  - `dispatch(assignment_type: str, payload: Dict[str, Any]) -> str`: Dispatches an assignment to the appropriate Redis stream.
  - `dispatch_message_extraction(message_id: int, content: str, user_uuid: str, conversation_id: str, photos: Optional[List[Dict]] = None) -> Dict[str, str]`: Dispatches all extraction tasks for a message.
  - `dispatch_entity_resolution(message_id: int, user_uuid: str, conversation_id: str, entities: Dict[str, List[str]], exchange_id: Optional[str] = None) -> str`: Dispatches an entity resolution task.
  - `dispatch_summary_rebuild(conversation_id: str, user_uuid: str, tier: int, start_idx: int, end_idx: int) -> str`: Dispatches a summary rebuild task.
  - `check_summary_triggers(conversation_id: str, message_count: int) -> List[Dict]`: Checks if summary rebuilds should be triggered.
  - `get_stats() -> Dict[str, Any]`: Retrieves orchestrator statistics.

#### Database
- **PostgreSQL Tables**: `datetime`, `typing`, `dotenv`, `stats` (used for configuration and statistics tracking).
- **Redis**: Used for task dispatching and statistics tracking.

#### Configuration
- **Environment Variables**: `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`
- **Configuration File**: `.env` file located at `/opt/mythos/.env`

#### Key Logic
- **Task Dispatching**: The `dispatch` method adds a task to the appropriate Redis stream based on the `assignment_type`.
- **Summary Triggers**: The `check_summary_triggers` method determines if summary rebuilds should be triggered based on the message count.
- **Statistics Tracking**: The `get_stats` method retrieves and returns statistics about dispatched assignments and worker activity.

#### Integration Points
- **Redis Streams**: Tasks are dispatched to Redis streams for asynchronous processing.
- **Worker Queues**: The dispatched tasks are picked up by worker queues for processing.
- **Configuration and Statistics**: Uses PostgreSQL tables for configuration and statistics tracking.

### Detailed Documentation

#### Class: `Orchestrator`
- **Purpose**: Dispatches extraction assignments to Redis streams for asynchronous processing.
- **Methods**:
  - `__init__`: Initializes the Redis connection and verifies it.
  - `_verify_connection`: Verifies the Redis connection.
  - `dispatch`: Dispatches an assignment to the appropriate Redis stream.
  - `dispatch_message_extraction`: Dispatches all extraction tasks for a message.
  - `dispatch_entity_resolution`: Dispatches an entity resolution task.
  - `dispatch_summary_rebuild`: Dispatches a summary rebuild task.
  - `check_summary_triggers`: Checks if summary rebuilds should be triggered.
  - `get_stats`: Retrieves orchestrator statistics.

#### Function: `get_orchestrator`
- **Purpose**: Ensures a single global instance of `Orchestrator` is created and reused.
- **Logic**: Uses a singleton pattern to return the global instance of `Orchestrator`.

### Example Usage
```python
from api.orchestrator import get_orchestrator

orchestrator = get_orchestrator()

# Dispatch a grid analysis task
assignment_id = orchestrator.dispatch("grid", {"message_id": 123, "content": "Sample content", "user_uuid": "user1", "conversation_id": "conv1"})

# Dispatch all extraction tasks for a message
assignments = orchestrator.dispatch_message_extraction(123, "Sample content", "user1", "conv1", [{"id": "photo1", "file_path": "/path/to/photo1"}])

# Check for summary rebuild triggers
tasks = orchestrator.check_summary_triggers("conv1", 20)

# Get orchestrator statistics
stats = orchestrator.get_stats()
```

This file is crucial for the Mythos system as it manages the dispatching of tasks to worker queues and ensures that the system can handle asynchronous processing efficiently.
