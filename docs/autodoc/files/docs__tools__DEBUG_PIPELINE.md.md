# docs/tools/DEBUG_PIPELINE.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 194

---

### Purpose
The `debug_pipeline.py` script is a multi-purpose debugging and monitoring tool for the Mythos orchestration pipeline. It provides real-time visibility into system health, queue status, worker activity, and message flow.

### Architecture
The script is structured as a command-line utility with several subcommands, each handling a specific debugging or monitoring task. The main entry point is the `main` function, which parses command-line arguments and delegates to the appropriate handler function based on the subcommand provided.

### Patterns
- **Command Pattern**: The script uses a command pattern where each subcommand (e.g., `status`, `queues`, `results`) is handled by a dedicated function.
- **Singleton Pattern**: The Redis client and HTTP client are initialized once and reused across different commands.

### Dependencies
- `redis`: Used to interact with Redis for queue monitoring and result retrieval.
- `requests`: Used to send HTTP requests for API health checks.
- `systemd`: Used to check and manage worker service status.

### Interfaces
The script exposes several command-line interfaces:
- `status`: Checks system health.
- `queues`: Displays contents of all Redis worker queues.
- `results`: Shows worker processing results stored in Redis.
- `clear`: Clears all queues and results.
- `send [message]`: Sends a test message through the pipeline.
- `logs [worker] [lines]`: Shows recent logs from a worker service.
- `help`: Displays command reference.

### Database
- **Redis**: The script interacts with Redis to monitor queues and retrieve worker results.
- **Neo4j**: Not directly used in this script, but the script can indirectly interact with Neo4j through the API.

### Configuration
Configuration is defined at the top of the script:
```python
API_URL = "http://localhost:8000"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
API_KEY = "cHPIHNR7DOE_rq85ZDjJkAiJcbik8ub7U9iTGCjbwyc"  # ka
```

### Key Logic
- **Health Check**: The `status` command checks the health of the API, Redis, Qdrant, and worker services.
- **Queue Monitoring**: The `queues` command retrieves and displays the contents of various Redis worker queues.
- **Result Retrieval**: The `results` command fetches and displays worker processing results from Redis.
- **Message Sending**: The `send` command sends a test message through the pipeline using the API.
- **Log Retrieval**: The `logs` command retrieves and displays recent logs from specified worker services.

### Integration Points
- **API**: The script interacts with the Mythos API to check health and send test messages.
- **Redis**: The script uses Redis to monitor queues and retrieve worker results.
- **Worker Services**: The script checks the status of worker services using `systemd` and retrieves logs from worker services.
- **Qdrant**: The script checks the health of the Qdrant service, though it does not directly interact with Qdrant.

### Troubleshooting
The script includes troubleshooting steps for common issues such as connection problems with the API, worker service issues, and queue backlogs. These steps guide users through checking service statuses and logs, and restarting services if necessary.
