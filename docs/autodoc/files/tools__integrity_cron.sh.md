# tools/integrity_cron.sh

**Language:** bash
**Stream:** SYS
**Module:** Tools
**Lines:** 30

---

### File: tools/integrity_cron.sh

#### Purpose
This script performs a daily integrity scan of the Mythos system and regenerates live telemetry documents. It logs all activities to a specified log file and ensures the log size is managed.

#### Architecture
The script follows a straightforward procedural design:
1. Sets up environment and logging.
2. Executes a full integrity scan.
3. Regenerates live telemetry documents.
4. Logs start and completion timestamps.
5. Truncates the log file to the last 500 lines.

#### Patterns
- **Procedural Pattern**: The script follows a linear sequence of operations, executing each step in order.

#### Dependencies
- **Environment Variables**: `MYTHOS_ROOT`
- **Python Virtual Environment**: `/opt/mythos/.venv/bin/python3`
- **Python Scripts**: `/opt/mythos/tools/generate_system_state.py`
- **Cron Job**: Configured to run daily at 3:00 AM via `/etc/cron.d/mythos-integrity`

#### Interfaces
- **Log File**: Writes to `/opt/mythos/docs/live/integrity-cron.log`
- **Environment Setup**: Exports `MYTHOS_ROOT` to the environment

#### Database
- **No direct database interaction**: The script does not directly interact with PostgreSQL, Neo4j, or Redis. However, the integrity scan and telemetry generation might indirectly interact with these databases.

#### Configuration
- **Cron Configuration**: `/etc/cron.d/mythos-integrity` schedules the script to run daily at 3:00 AM.
- **Environment Variables**: `MYTHOS_ROOT` is set to `/opt/mythos`.

#### Key Logic
1. **Integrity Scan**: Executes a full integrity scan using the Python module `integrity scan`.
2. **Telemetry Regeneration**: Regenerates live telemetry documents using the Python script `generate_system_state.py`.
3. **Logging**: Logs the start and completion of the script along with timestamps.
4. **Log Management**: Ensures the log file does not grow indefinitely by keeping only the last 500 lines.

#### Integration Points
- **Integrity Module**: The script invokes the `integrity` module to perform the integrity scan.
- **Telemetry Generation**: The script invokes the `generate_system_state.py` script to regenerate live telemetry documents.
- **Cron Job**: The script is scheduled to run daily via a cron job, ensuring regular system checks and telemetry updates.

### Detailed Breakdown

1. **Environment Setup**:
   - `set -euo pipefail`: Ensures the script exits on any error and unbound variables.
   - `VENV="/opt/mythos/.venv/bin/python3"`: Path to the Python interpreter in the virtual environment.
   - `MYTHOS_ROOT="/opt/mythos"`: Root directory of the Mythos system.
   - `LOG="/opt/mythos/docs/live/integrity-cron.log"`: Path to the log file.
   - `export MYTHOS_ROOT`: Exports `MYTHOS_ROOT` to the environment.

2. **Logging Start**:
   - `echo "=== Integrity Scan: $(date) ===" >> "$LOG"`: Logs the start of the integrity scan with a timestamp.

3. **Integrity Scan**:
   - `cd "$MYTHOS_ROOT"`: Changes directory to the Mythos root.
   - `$VENV -m integrity scan >> "$LOG" 2>&1`: Executes the integrity scan module and logs the output.

4. **Telemetry Regeneration**:
   - `$VENV /opt/mythos/tools/generate_system_state.py >> "$LOG" 2>&1`: Executes the telemetry regeneration script and logs the output.

5. **Logging Completion**:
   - `echo "=== Complete: $(date) ===" >> "$LOG"`: Logs the completion of the script with a timestamp.
   - `echo "" >> "$LOG"`: Adds a blank line for readability.

6. **Log Management**:
   - `tail -500 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"`: Truncates the log file to the last 500 lines to prevent it from growing indefinitely.

This script ensures that the Mythos system undergoes regular integrity checks and telemetry updates, maintaining system health and providing up-to-date system state information.
