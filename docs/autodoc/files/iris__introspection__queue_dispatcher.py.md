# iris/introspection/queue_dispatcher.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 115

---

### File: `iris/introspection/queue_dispatcher.py`

#### Purpose
This file manages the dispatching of documentation tasks to Redis queues and provides functionality to check the status of these queues. It ensures tasks are not duplicated and tracks their progress.

#### Architecture
The file consists of several top-level functions:
- `task_hash`: Generates a hash for a given task.
- `_enqueue`: Adds a task to a Redis queue if it hasn't been enqueued before.
- `dispatch_tasks`: Dispatches documentation tasks to various Redis queues based on different criteria.
- `get_queue_status`: Retrieves the current status of the Redis queues.

The file uses Redis to manage task queues and employs a set (`DEDUP_KEY`) to prevent task duplication.

#### Patterns
- **Singleton Pattern**: The Redis client is treated as a singleton, assumed to be a single instance throughout the application.
- **Factory Pattern**: The `_enqueue` function can be seen as a factory for adding tasks to the queue.

#### Dependencies
- `json`: For JSON serialization and deserialization.
- `hashlib`: For generating task hashes.
- `logging`: For logging information and warnings.
- `time`: For timestamping tasks.

#### Interfaces
- `task_hash(task)`: Generates a hash for a given task.
- `_enqueue(r, queue, task)`: Enqueues a task to a Redis queue if it hasn't been enqueued before.
- `dispatch_tasks(redis_client, component_groups, file_list, component_analyses)`: Dispatches documentation tasks to Redis queues and returns the count of dispatched tasks.
- `get_queue_status(redis_client)`: Returns the current status of the Redis queues, including pending tasks and processing stats.

#### Database
- **PostgreSQL Tables**:
  - `dispatched`: Likely used to track dispatched tasks.
  - `TODO`: Possibly used for tracking TODO items.
  - `introspection`: Likely used for introspection data.

#### Configuration
- No explicit configuration files are used, but environment variables or configuration settings might be required to initialize the Redis client.

#### Key Logic
- **Task Hashing**: Each task is hashed to ensure uniqueness before enqueuing.
- **Task Enqueuing**: Tasks are enqueued to specific Redis queues based on their type and criteria.
- **Queue Status**: The status of each queue is tracked, including the number of pending tasks and processing stats.

#### Integration Points
- **Redis**: The file heavily integrates with Redis to manage task queues and deduplication.
- **PostgreSQL**: The file references PostgreSQL tables, indicating that it integrates with the PostgreSQL database to store and retrieve task-related data.
- **Logging**: The file uses the logging module to log important information and warnings.

### Detailed Analysis

#### `task_hash(task)`
- **Purpose**: Generates a hash for a given task to ensure uniqueness.
- **Logic**: Serializes the task to JSON, sorts the keys, hashes the result using SHA-256, and returns the first 16 characters of the hash.

#### `_enqueue(r, queue, task)`
- **Purpose**: Adds a task to a Redis queue if it hasn't been enqueued before.
- **Logic**: Checks if the task hash is already in the deduplication set (`DEDUP_KEY`). If not, it adds the hash to the set and pushes the task to the specified queue.

#### `dispatch_tasks(redis_client, component_groups, file_list, component_analyses)`
- **Purpose**: Dispatches documentation tasks to Redis queues and returns the count of dispatched tasks.
- **Logic**:
  - Iterates over `component_groups` to create and enqueue component documentation tasks.
  - Creates and enqueues architecture entry tasks.
  - Creates and enqueues system map tasks.
  - Creates and enqueues CLI help documentation tasks.
  - Creates and enqueues Telegram help documentation tasks.
  - Creates and enqueues Claude context documentation tasks.
  - Creates and enqueues TODO update tasks.

#### `get_queue_status(redis_client)`
- **Purpose**: Retrieves the current status of the Redis queues, including pending tasks and processing stats.
- **Logic**: Iterates over the defined queues and retrieves the length of each queue. Additionally, it retrieves metadata such as the size of the deduplication set, the number of tasks in processing, and the number of completed tasks.

### Conclusion
This file is crucial for managing the documentation tasks in the Mythos system, ensuring that tasks are uniquely enqueued and providing a mechanism to check the status of the task queues. It integrates with Redis for queue management and PostgreSQL for storing task-related data.
