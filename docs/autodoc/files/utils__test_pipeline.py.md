# utils/test_pipeline.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 155

---

### File: utils/test_pipeline.py

#### Purpose
This file contains a series of test functions to verify the health and functionality of the Mythos orchestration pipeline, including checks for the API, Redis, Qdrant, and message processing.

#### Architecture
The file consists of several top-level functions, each designed to test a specific component of the Mythos system. The `main` function orchestrates these tests and provides a summary of the results.

- **Functions**:
  - `test_api_health`: Checks the health of the API.
  - `test_redis_connection`: Verifies the connection to Redis and checks queue lengths.
  - `test_qdrant`: Ensures Qdrant is responding and lists collections.
  - `test_message_endpoint`: Sends a test message through the pipeline.
  - `check_worker_processing`: Checks if workers are processing messages.
  - `main`: Orchestrates the tests and provides a summary.

#### Patterns
No specific design patterns are used in this file. The functions are straightforward and do not follow patterns like factory, singleton, or observer.

#### Dependencies
- **Imports**: `json`, `time`, `redis`, `requests`, `datetime`
- **External Services**: API (via `requests`), Redis (via `redis`), Qdrant (via `requests`)

#### Interfaces
The file does not expose any interfaces to other parts of the system. It is designed to be run as a standalone script.

#### Database
- **PostgreSQL**: The `datetime` table is referenced, but no direct interaction with PostgreSQL is observed in the provided code.
- **Redis**: Used for queue management and worker status checks.
- **Qdrant**: Checked for availability and collection listing.

#### Configuration
- **Environment Variables**: None
- **Configuration Variables**: `API_URL`, `REDIS_HOST`, `REDIS_PORT`, `API_KEY` are defined as constants within the file.

#### Key Logic
- **API Health Check**: Uses `requests.get` to check the `/health` endpoint.
- **Redis Connection Check**: Uses `redis.Redis` to connect and check queue lengths.
- **Qdrant Check**: Uses `requests.get` to list collections.
- **Message Endpoint Test**: Sends a JSON payload to the `/message` endpoint and checks the response.
- **Worker Processing Check**: Uses Redis to check the number of results and processing keys.

#### Integration Points
- **API**: Interacts with the API to test health and message endpoints.
- **Redis**: Used for queue management and worker status checks.
- **Qdrant**: Checked for availability and collection listing.

### Detailed Documentation

#### Functions

1. **test_api_health**
   - **Purpose**: Checks if the API is responding.
   - **Logic**: Uses `requests.get` to hit the `/health` endpoint and prints the status and response.
   - **Returns**: `True` if the status code is 200, otherwise `False`.

2. **test_redis_connection**
   - **Purpose**: Checks if Redis is responding and verifies queue lengths.
   - **Logic**: Connects to Redis, pings the server, and checks the length of predefined queues.
   - **Returns**: `True` if the connection is successful, otherwise `False`.

3. **test_qdrant**
   - **Purpose**: Checks if Qdrant is responding and lists collections.
   - **Logic**: Uses `requests.get` to list collections and prints the status and collection names.
   - **Returns**: `True` if the request is successful, otherwise `False`.

4. **test_message_endpoint**
   - **Purpose**: Sends a test message through the pipeline.
   - **Logic**: Sends a JSON payload to the `/message` endpoint and prints the status and response.
   - **Returns**: `True` if the status code is 200, otherwise `False`.

5. **check_worker_processing**
   - **Purpose**: Checks if workers are processing messages.
   - **Logic**: Connects to Redis and checks the number of results and processing keys, as well as queue lengths.
   - **Returns**: None (prints the status).

6. **main**
   - **Purpose**: Orchestrates the tests and provides a summary.
   - **Logic**: Runs each test function, waits for worker processing, and prints a summary of the results.
   - **Returns**: `0` if all tests pass, otherwise `1`.

### Configuration Variables
- `API_URL`: Base URL for the API.
- `REDIS_HOST`: Host for Redis.
- `REDIS_PORT`: Port for Redis.
- `API_KEY`: API key for authentication.

### Summary
This file serves as a comprehensive testing suite for the Mythos orchestration pipeline, ensuring that critical components like the API, Redis, and Qdrant are functioning correctly and that messages can be processed through the pipeline.
