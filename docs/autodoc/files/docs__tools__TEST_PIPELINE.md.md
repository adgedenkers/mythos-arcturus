# docs/tools/TEST_PIPELINE.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 78

---

### File: `docs/tools/TEST_PIPELINE.md`

#### Purpose
This markdown file documents the `Test Pipeline Tool`, a utility script located at `/opt/mythos/utils/test_pipeline.py` that performs a series of health checks on the Mythos system's core components and reports the results.

#### Architecture
The `test_pipeline.py` script is designed as a standalone Python script that sequentially executes several tests on different components of the Mythos system. It does not contain classes but consists of functions that perform specific tests and aggregate the results.

#### Patterns
The script does not employ any specific design patterns. It follows a straightforward procedural approach, where each function performs a distinct test and returns a status.

#### Dependencies
The script imports and relies on:
- `requests` for making HTTP requests to the API.
- `redis` for connecting to the Redis server.
- `qdrant_client` for interacting with the Qdrant database.
- `logging` for logging purposes.

#### Interfaces
The script exposes a command-line interface (CLI) that can be invoked directly or through an alias. It does not expose any APIs or interfaces to other parts of the system.

#### Database
The script reads from and writes to the following:
- **Redis**: Pings the Redis server and checks the queue status.
- **Qdrant**: Queries the collections endpoint.

#### Configuration
The script uses environment variables for configuration, such as:
- `MYTHOS_API_URL`: URL of the Mythos API.
- `REDIS_HOST`: Host of the Redis server.
- `QDRANT_URL`: URL of the Qdrant server.

#### Key Logic
The most important business logic in the script includes:
- **API Health Check**: Sends a GET request to the `/health` endpoint of the Mythos API.
- **Redis Connection Check**: Pings the Redis server and checks the status of the queue.
- **Qdrant Connection Check**: Queries the collections endpoint to ensure the Qdrant server is reachable.
- **Message Pipeline Check**: Sends a test message to the `/message` endpoint to verify the message pipeline.

#### Integration Points
The script integrates with the following subsystems of the Mythos system:
- **API**: Verifies the health of the API through the `/health` endpoint.
- **Redis**: Ensures the Redis server is operational and the queue is functioning correctly.
- **Qdrant**: Verifies the Qdrant database is accessible and the collections are as expected.
- **Message Pipeline**: Tests the message pipeline by sending a test message.

### Summary
The `Test Pipeline Tool` is a critical utility for ensuring the health and operational readiness of the Mythos system. It provides a simple yet comprehensive way to verify the status of core components, making it invaluable for post-deployment verification, CI/CD health checks, and quick sanity checks after system changes.
