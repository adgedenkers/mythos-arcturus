# docs/live/system-state.txt

**Language:** text
**Stream:** SYS
**Module:** Documentation
**Lines:** 44

---

### File: docs/live/system-state.txt

#### Purpose
This file provides a snapshot of the current state of the Mythos system, including the version, status of various services, database information, and disk usage.

#### Architecture
The file is a text-based report that does not contain any code or classes. It is structured into sections for clarity and ease of reading, with each section detailing a specific aspect of the system's state.

#### Patterns
No design patterns are applicable as this is a plain text file and not a code file.

#### Dependencies
This file does not import or rely on any external dependencies. It is a generated report and does not contain executable code.

#### Interfaces
This file does not expose any interfaces as it is a static text file meant for human consumption.

#### Database
The file mentions the number of PostgreSQL tables (125) but does not provide specific details about the tables or any Neo4j labels.

#### Configuration
The file does not reference any configuration files or environment variables. It is a generated report and does not require configuration.

#### Key Logic
This file does not contain any logic. It is a generated report that aggregates information from various parts of the Mythos system.

#### Integration Points
The file integrates information from various subsystems of the Mythos system, including service statuses, database details, and disk usage. It serves as a centralized point for monitoring the overall health and status of the Mythos infrastructure.

### Detailed Breakdown

1. **Patch & Version**:
   - **Current Patch**: `0000`
   - **Current Version**: `pre-patch-SYS-0051_autodoc_skip_patches-20260403_014608`
   - **Next Patch**: `0001`
   - **Total Patches**: `0`

2. **Services**:
   - **Healthy Services**: 22 out of 23 services are active and running.
   - **Unhealthy Services**: `mythos-obs-graph` is in an activating/auto-restart state.
   - **List of Services**:
     - `mythos-api`
     - `mythos-bot`
     - `mythos-doc-watcher`
     - `mythos-knowledge-map`
     - `mythos-patch-monitor`
     - `mythos-planetary-engine`
     - `mythos-print-watcher`
     - `mythos-segment-manager`
     - `mythos-seismic-ingest`
     - `mythos-solar-ingest`
     - `mythos-transcription-worker`
     - `mythos-trigger`
     - `mythos-voice-watcher`
     - `mythos-worker-embedding`
     - `mythos-worker-entity`
     - `mythos-worker-grid`
     - `mythos-worker-lunar`
     - `mythos-worker-summary`
     - `mythos-worker-temporal`
     - `mythos-worker-vision`
     - `mythos-youtube-monitor`
     - `mythos-youtube-queue`

3. **Database**:
   - **PostgreSQL Tables**: 125 tables

4. **Disk Usage**:
   - **Mythos Size**: 249G
   - **Root Disk**: 902G / 1.8T (52% used)
   - **Available Disk Space**: 838G

### Summary
This file serves as a comprehensive snapshot of the Mythos system's state, providing critical information about the system's version, service statuses, database details, and disk usage. It is a valuable tool for monitoring and maintaining the health and performance of the Mythos infrastructure.
