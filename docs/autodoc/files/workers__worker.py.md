# workers/worker.py

**Language:** python
**Stream:** SYS
**Module:** Background Workers
**Lines:** 299

---

### Documentation for `workers/worker.py`

#### Purpose
This file defines the `Worker` class, which is responsible for processing assignments from Redis streams. It dynamically loads the appropriate handler function based on the worker type and processes messages from the specified stream.

#### Architecture
The `Worker` class is the core component of this file. It has several methods to handle initialization, message processing, and shutdown. The class is designed to be instantiated with a specific worker type, which determines the stream and handler function to use.

- **Classes**: 
  - `Worker`: Base worker class for processing assignments.
  
- **Methods**:
  - `__init__`: Initializes the worker with a specific type, sets up logging, Redis connection, and loads the appropriate handler.
  - `_load_handler`: Dynamically loads the handler function based on the worker type.
  - `_placeholder_handler`: A placeholder handler for testing purposes.
  - `run`: Main worker loop that continuously processes messages from the Redis stream.
  - `_process_message`: Processes a single message from the stream.
  - `_shutdown`: Handles shutdown signals gracefully.

- **Top-level functions**:
  - `main`: Entry point for running the worker. Parses command-line arguments and initializes the worker.
  
#### Patterns
- **Factory Pattern**: The `_load_handler` method dynamically loads the appropriate handler function based on the worker type.
- **Singleton Pattern**: The Redis connection is a singleton within the `Worker` instance.

#### Dependencies
- **Imports**: 
  - `os`, `sys`, `json`, `time`, `signal`, `logging`, `importlib`, `redis`, `datetime`, `pathlib`, `dotenv`.
- **Redis**: Used for message queueing and processing.
- **Environment Variables**: Configured via `.env` file.

#### Interfaces
- **Public Methods**:
  - `Worker.__init__(worker_type: str)`: Initializes the worker with a specific type.
  - `Worker.run()`: Main loop for processing messages.
  - `Worker._process_message(stream: str, message_id: str, data: dict) -> bool`: Processes a single message.
  - `Worker._shutdown(signum, frame)`: Handles shutdown signals.

#### Database
- **Redis**:
  - **Streams**: `mythos:assignments:<worker_type>` for each worker type.
  - **Groups**: `worker_type_workers` for each worker type.
  - **Stats**: `mythos:stats:workers` for tracking processed assignments and errors.
  - **Error Handling**: Acknowledges messages and updates stats.

#### Configuration
- **Environment Variables**:
  - `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`: Redis connection details.
- **Configuration File**: `.env` file loaded using `dotenv`.

#### Key Logic
- **Dynamic Handler Loading**: The `_load_handler` method dynamically imports and loads the appropriate handler function based on the worker type.
- **Message Processing**: The `run` method continuously reads messages from the Redis stream and processes them using the `_process_message` method.
- **Shutdown Handling**: The `_shutdown` method handles graceful shutdowns by setting the `running` flag to `False`.

#### Integration Points
- **Redis Streams**: The worker reads from Redis streams and processes messages.
- **Handler Modules**: The worker dynamically loads handler functions from modules in the `workers` package.
- **Systemd Services**: The `main` function provides instructions for running multiple workers using separate processes or systemd services.

### Summary
The `Worker` class in `workers/worker.py` is designed to process assignments from Redis streams. It dynamically loads the appropriate handler function based on the worker type and processes messages in a continuous loop. The class handles initialization, message processing, and graceful shutdowns, making it a core component of the Mythos system's worker framework.
