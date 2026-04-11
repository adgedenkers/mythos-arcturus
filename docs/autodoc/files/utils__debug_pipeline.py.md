# utils/debug_pipeline.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 202

---

### File: utils/debug_pipeline.py

#### Purpose
This file provides a set of utility functions to debug and monitor the Mythos system, including showing system status, queue contents, worker results, sending test messages, and viewing worker logs.

#### Architecture
The file consists of several top-level functions, each designed to perform a specific debugging task. These functions are executed based on command-line arguments passed to the script. The functions interact with various components of the Mythos system, such as Redis, API endpoints, and system services.

#### Patterns
- **Command Pattern**: The script uses a dictionary (`commands`) to map command-line arguments to corresponding functions, allowing for flexible command execution.
- **Singleton Pattern**: The Redis client (`r`) is instantiated once and reused across multiple functions.

#### Dependencies
- **Standard Libraries**: `json`, `sys`, `subprocess`
- **External Libraries**: `redis`, `requests`
- **Environment**: `datetime` from the `datetime` module

#### Interfaces
The file exposes several functions that can be called from the command line:
- `status()`: Displays the full system status.
- `queues()`: Displays the contents of all queues.
- `results()`: Displays worker results.
- `clear()`: Clears all queues and results.
- `send(message)`: Sends a test message to the system.
- `logs(worker, lines)`: Displays worker logs.
- `help()`: Displays available commands and usage.

#### Database
- **Redis**: The file interacts with Redis to manage queues and results.
  - **Queues**: `mythos:grid`, `mythos:embedding`, `mythos:vision`, `mythos:temporal`, `mythos:entity`, `mythos:summary`
  - **Results**: Keys matching the pattern `mythos:result:*`

#### Configuration
- **Environment Variables**: None
- **Constants**: 
  - `API_URL`: `"http://localhost:8000"`
  - `REDIS_HOST`: `"localhost"`
  - `REDIS_PORT`: `6379`
  - `API_KEY`: `"cHPIHNR7DOE_rq85ZDjJkAiJcbik8ub7U9iTGCjbwyc"`

#### Key Logic
- **status()**: Fetches and displays the status of the API, Redis, Qdrant, and worker services.
- **queues()**: Lists the contents of each queue.
- **results()**: Lists the results stored in Redis.
- **clear()**: Clears all queues and results.
- **send()**: Sends a test message to the API.
- **logs()**: Retrieves and displays worker logs using `journalctl`.
- **help()**: Displays usage information for the debug tool.

#### Integration Points
- **API**: The script interacts with the Mythos API to send messages and check health.
- **Redis**: Used to manage queues and results.
- **Qdrant**: The script checks the status of Qdrant collections.
- **System Services**: The script uses `systemctl` to check the status of worker services and `journalctl` to retrieve logs.

### Detailed Function Descriptions

1. **status()**
   - Displays the full system status, including API health, Redis connectivity, Qdrant collections, and worker statuses.

2. **queues()**
   - Lists the contents of each queue, showing up to the first 5 items in each queue.

3. **results()**
   - Lists the results stored in Redis, showing up to 10 results.

4. **clear()**
   - Clears all queues and results stored in Redis.

5. **send(message)**
   - Sends a test message to the API. If no message is provided, a default message is generated.

6. **logs(worker, lines)**
   - Displays the logs for a specified worker, defaulting to the `grid` worker and showing the last 20 lines.

7. **help()**
   - Displays usage information and available commands for the debug tool.

### Command Execution
The script is designed to be executed from the command line, with the first argument specifying the command to execute. If no command is provided, the `status` command is executed by default. The script supports additional arguments for commands like `send` and `logs`.
