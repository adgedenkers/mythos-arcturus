# updates/apply_patch.sh

**Language:** bash
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 33

---

### Documentation for `updates/apply_patch.sh`

#### Purpose
This script applies a code patch to the Mythos system and restarts relevant services to ensure the changes take effect.

#### Architecture
The script follows a straightforward procedural design:
1. It sets up environment variables for `PATCH_TYPE` and `FILE`.
2. It calls a Python script (`patch_code.py`) to apply the patch.
3. If the patch is successfully applied, it restarts the services and checks their status.
4. If the patch fails, it exits with an error message.

#### Patterns
No specific design patterns are used in this script. It follows a simple procedural flow.

#### Dependencies
- **Environment Variables**: `PATCH_TYPE`, `FILE`
- **External Commands**: `python3`, `sudo`, `systemctl`, `sleep`
- **Python Script**: `/opt/mythos/updates/patch_code.py`

#### Interfaces
- **Inputs**: 
  - `PATCH_TYPE`: Type of patch to apply.
  - `FILE`: File to which the patch should be applied.
  - Additional arguments passed to `patch_code.py`.
- **Outputs**: 
  - Console output indicating the status of the patch application and service restarts.

#### Database
This script does not directly interact with any database tables or Neo4j labels.

#### Configuration
- **Environment Variables**: The script relies on `PATCH_TYPE` and `FILE` passed as arguments.
- **System Configuration**: It uses `systemctl` to manage services, which is configured in the system's service files.

#### Key Logic
1. **Patch Application**: The script calls `patch_code.py` with the provided arguments to apply the patch.
2. **Service Restart**: If the patch is successful, it restarts the `mythos-api` and `mythos-bot` services.
3. **Status Check**: After restarting, it checks the status of `mythos-api` to ensure it is running correctly.

#### Integration Points
- **Python Script**: The script integrates with the Python script `patch_code.py` to apply the patch.
- **System Services**: It interacts with the system's service management (`systemctl`) to restart `mythos-api` and `mythos-bot`.

### Detailed Explanation

1. **Environment Setup**:
   ```bash
   set -e
   ```
   This ensures that the script exits immediately if any command exits with a non-zero status.

2. **Argument Handling**:
   ```bash
   PATCH_TYPE=$1
   FILE=$2
   shift 2
   ```
   The script captures the first two arguments as `PATCH_TYPE` and `FILE`, then shifts the positional parameters to pass any remaining arguments to `patch_code.py`.

3. **Patch Application**:
   ```bash
   python3 /opt/mythos/updates/patch_code.py "$PATCH_TYPE" "$FILE" "$@"
   ```
   This line calls the Python script `patch_code.py` with the provided arguments to apply the patch.

4. **Service Restart and Status Check**:
   ```bash
   if [ $? -eq 0 ]; then
       echo ""
       echo "Restarting services..."
       sudo systemctl restart mythos-api mythos-bot
       sleep 2
       
       echo ""
       echo "Status:"
       sudo systemctl status mythos-api --no-pager -n 3
       echo ""
       echo "✅ Patch applied successfully!"
   else
       echo "❌ Patch failed"
       exit 1
   fi
   ```
   If the patch is successfully applied, the script restarts the `mythos-api` and `mythos-bot` services and checks the status of `mythos-api` to ensure it is running correctly. If the patch fails, it prints an error message and exits with a non-zero status.

This script ensures that any code patches are applied correctly and that the system services are restarted to reflect the changes, maintaining the integrity and functionality of the Mythos system.
