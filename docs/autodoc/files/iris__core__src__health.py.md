# iris/core/src/health.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 208

---

### Documentation for `iris/core/src/health.py`

#### Purpose
This file provides health and API endpoints for the Mythos system, including basic health checks, detailed status information, and endpoints for running code in a sandbox and queuing tasks for processing.

#### Architecture
The file is structured around a FastAPI application that exposes several endpoints. It defines three Pydantic models (`CodeRequest`, `TaskRequest`, `TaskResponse`) for request and response validation. The main function `create_health_app` initializes the FastAPI app and defines the routes.

#### Patterns
- **Factory Method**: The `create_health_app` function acts as a factory method, creating and configuring the FastAPI app.
- **Singleton**: The FastAPI app instance is created once and reused, acting as a singleton within the context of the application.

#### Dependencies
- **Imports**: 
  - `structlog` for logging.
  - `FastAPI` and `HTTPException` from `fastapi`.
  - `BaseModel` from `pydantic`.
  - `Optional` from `typing`.

#### Interfaces
- **Endpoints**:
  - `GET /health`: Basic health check.
  - `GET /status`: Detailed status for monitoring.
  - `POST /test_agency`: Run a simple test task.
  - `POST /run_code`: Execute arbitrary code in the sandbox.
  - `POST /task`: Queue a task for self-directed work.

#### Database
- **References**:
  - The file references tables in PostgreSQL (`fastapi`, `pydantic`, `typing`, `task`, `datetime`), but these are likely placeholders or misinterpretations. The actual database interactions are through the `consciousness_loop` and `agency` objects, which are not explicitly defined in this file.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `NEO4J_URI`, `REDIS_HOST` are checked in the `test_agency` function to verify the environment setup.

#### Key Logic
- **Health Check**: The `health` function returns a simple status message.
- **Detailed Status**: The `status` function returns the current state of the `consciousness_loop`.
- **Test Agency**: The `test_agency` function runs a predefined Python script in the sandbox to verify the environment and dependencies.
- **Run Code**: The `run_code` function allows running arbitrary code in the sandbox.
- **Queue Task**: The `queue_task` function queues a task for processing by the system.

#### Integration Points
- **Consciousness Loop**: The `create_health_app` function takes a `consciousness_loop` instance, which is used to access the `agency` for running code and queuing tasks.
- **Agency**: The `agency` object is used to run code in the sandbox and is part of the `consciousness_loop`.

### Detailed Documentation

#### Classes
1. **CodeRequest**
   - **Purpose**: Represents a request to run code in the sandbox.
   - **Attributes**: `code` (str)
   - **Inheritance**: `BaseModel`

2. **TaskRequest**
   - **Purpose**: Represents a request to queue a task.
   - **Attributes**: `goal` (str), `name` (Optional[str]), `max_attempts` (Optional[int])
   - **Inheritance**: `BaseModel`

3. **TaskResponse**
   - **Purpose**: Represents the response from task operations.
   - **Attributes**: `success` (bool), `output` (Optional[str]), `error` (Optional[str]), `duration` (Optional[float]), `stdout` (Optional[str]), `stderr` (Optional[str]), `exit_code` (Optional[int])
   - **Inheritance**: `BaseModel`

#### Functions
1. **create_health_app**
   - **Purpose**: Creates and configures a FastAPI app for health checks and API endpoints.
   - **Arguments**: `consciousness_loop` (The `ConsciousnessLoop` instance)
   - **Returns**: `FastAPI` instance

2. **health**
   - **Purpose**: Provides a basic health check.
   - **Decorators**: `app.get("/health")`
   - **Returns**: JSON response with status and service name.

3. **status**
   - **Purpose**: Provides detailed status information for monitoring.
   - **Decorators**: `app.get("/status")`
   - **Returns**: JSON response with the state of the `consciousness_loop`.

4. **test_agency**
   - **Purpose**: Runs a simple test to verify the agency/sandbox is working.
   - **Decorators**: `app.post("/test_agency")`
   - **Returns**: `TaskResponse` with the result of the test.

5. **run_code**
   - **Purpose**: Runs arbitrary code in the sandbox.
   - **Decorators**: `app.post("/run_code")`
   - **Arguments**: `request` (CodeRequest)
   - **Returns**: `TaskResponse` with the result of the code execution.

6. **queue_task**
   - **Purpose**: Queues a task for processing.
   - **Decorators**: `app.post("/task")`
   - **Arguments**: `request` (TaskRequest)
   - **Returns**: JSON response with the status and details of the queued task.

### Summary
This file provides essential health and API endpoints for the Mythos system, enabling basic health checks, detailed status reporting, and the ability to run code and queue tasks for processing. The `create_health_app` function is central to setting up the FastAPI app, and the various endpoint functions handle specific tasks such as running tests, executing code, and queuing tasks.
