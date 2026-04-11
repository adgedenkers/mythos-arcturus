# docs/generated/components/integrity.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 95

---

### Purpose
The `integrity.md` file serves as a comprehensive reference for the Mythos Integrity Component, detailing its role in monitoring and validating the structural and operational consistency of the Mythos system. It covers key files, data stores, integration points, configuration, and design patterns.

### Architecture
The integrity component is composed of several Python files, each responsible for specific tasks:
- `file_scanner.py`: Scans filesystems for unauthorized file modifications using hash comparison.
- `function_extractor.py`: Extracts and catalogs function signatures from the codebase for dependency tracking.
- `graph.py`: Manages Neo4j graph operations, including node/relationship creation and queries.
- `service_scanner.py`: Validates service configurations, including ports, dependencies, and runtime state.
- `table_scanner.py`: Compares database table schemas against baselines in PostgreSQL.
- `__main__.py`: Orchestrates the full integrity scan cycle and schedules execution.

### Patterns
- **Baseline-Driven Scans**: All scans compare the current state against pre-stored baselines.
- **Graph-Centric Dependency Tracking**: Neo4j graph is rebuilt on every scan, with relationships derived from various extractors.
- **Failure-First Alerting**: Violations trigger immediate Redis queueing, with Telegram alerts sent in batches.
- **Idempotent Scans**: Scanners use `last_scan` timestamps to avoid redundant processing.
- **Modular Scanner Architecture**: Each scanner operates independently but contributes to the unified Neo4j graph.
- **No Direct DB Schema Changes**: Schema comparisons are done using `table_scanner.py` without direct `ALTER TABLE` operations.

### Dependencies
The integrity component relies on:
- PostgreSQL for storing baseline hashes, scan history, and alerts.
- Neo4j for managing the system dependency graph.
- Redis for managing scan locks and alert queues.
- FastAPI for exposing real-time integrity status via an endpoint.
- Ollama for extracting function signatures from code.

### Interfaces
The component exposes:
- `/integrity/status` endpoint via FastAPI for real-time integrity status.
- Telegram Bot integration for pushing violation alerts to the admin channel.

### Database
- **PostgreSQL**:
  - `integrity_baseline`: Stores baseline hashes for files, functions, and service configurations.
  - `integrity_scan_history`: Logs scan timestamps and results.
  - `integrity_alerts`: Tracks active integrity violations with severity.
- **Neo4j**:
  - Nodes: `File`, `Function`, `Service`, `Table`.
  - Relationships: `DEPENDS_ON`, `MODIFIED_BY`, `PART_OF`.

### Configuration
The component uses several environment variables:
- `INTEGRITY_SCAN_INTERVAL`: Scan frequency in seconds (default: 3600).
- `INTEGRITY_BASELINE_DIR`: Path for baseline file storage (default: `/opt/mythos/baseline`).
- `TELEGRAM_BOT_TOKEN`: Bot token for alerting (required).
- `TELEGRAM_CHAT_ID`: Admin chat ID for alerts (required).
- `POSTGRES_INTEGRITY_DB`: PostgreSQL database name (default: `mythos_integrity`).
- `NEO4J_INTEGRITY_URI`: Neo4j connection URI (default: `bolt://neo4j:7687`).

### Key Logic
- **Baseline Comparison**: Each scanner compares the current state against stored baselines.
- **Graph Management**: `graph.py` manages the Neo4j graph, updating nodes and relationships based on the current state.
- **Alerting**: Violations are queued in Redis and pushed to Telegram in batches.

### Integration Points
- **Telegram Bot**: Uses Redis queue (`integrity:alert:pending`) to push violation alerts.
- **PostgreSQL**: Direct writes to `integrity_baseline` for storing baseline data.
- **Neo4j**: Uses `graph.py` API calls for building and querying the system dependency graph.
- **FastAPI**: Exposes `/integrity/status` endpoint for real-time integrity status.
- **Ollama**: Used by `function_extractor.py` for extracting function signatures from code.
