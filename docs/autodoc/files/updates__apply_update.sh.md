# updates/apply_update.sh

**Language:** bash
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 38

---

### File: `updates/apply_update.sh`

#### Purpose
This script is designed to apply updates to the Mythos system by sourcing a specified update script and optionally restarting relevant services.

#### Architecture
- **Functions**: The script does not define any functions; it is a linear sequence of commands.
- **Data Flow**: The script takes a single argument, `UPDATE_FILE`, which is the path to the update script to be sourced. It checks if the file exists and then sources it. If a variable `RESTART_SERVICES` is set to `true` within the sourced script, it restarts specified services and checks their status.

#### Patterns
- **None**: This script does not follow any specific design patterns as it is a simple procedural script.

#### Dependencies
- **System Commands**: `echo`, `source`, `sudo`, `systemctl`
- **Environment Variables**: `UPDATE_FILE`, `RESTART_SERVICES`

#### Interfaces
- **Inputs**: 
  - `UPDATE_FILE`: Path to the update script.
- **Outputs**: 
  - Console output indicating the progress and status of the update process.

#### Database
- **None**: This script does not interact with any databases or Neo4j labels.

#### Configuration
- **None**: The script does not use any configuration files or environment variables beyond the command-line argument and the `RESTART_SERVICES` variable.

#### Key Logic
1. **Argument Validation**: Checks if the `UPDATE_FILE` argument is provided and if the file exists.
2. **Sourcing the Update Script**: Sources the specified update script.
3. **Service Restart**: If `RESTART_SERVICES` is set to `true` in the update script, it restarts the `mythos-api` and `mythos-bot` services and checks their status.

#### Integration Points
- **Update Scripts**: The script integrates with custom update scripts that are passed as arguments. These scripts can define the `RESTART_SERVICES` variable to control whether services should be restarted.
- **System Services**: The script interacts with the system's service manager (`systemctl`) to restart the `mythos-api` and `mythos-bot` services.

### Detailed Breakdown

1. **Argument Validation**:
   ```bash
   if [ -z "$UPDATE_FILE" ]; then
       echo "Usage: ./apply_update.sh <update_file.sh>"
       exit 1
   fi

   if [ ! -f "$UPDATE_FILE" ]; then
       echo "Error: Update file not found: $UPDATE_FILE"
       exit 1
   fi
   ```
   - Checks if the `UPDATE_FILE` argument is provided and if the file exists.

2. **Sourcing the Update Script**:
   ```bash
   source "$UPDATE_FILE"
   ```
   - Sources the specified update script, which can contain any necessary update logic.

3. **Service Restart**:
   ```bash
   if [ "$RESTART_SERVICES" = "true" ]; then
       echo ""
       echo "Restarting services..."
       sudo systemctl restart mythos-api
       sudo systemctl restart mythos-bot
       sleep 2
       echo ""
       echo "Service status:"
       sudo systemctl status mythos-api --no-pager -n 3
       sudo systemctl status mythos-bot --no-pager -n 3
   fi
   ```
   - Checks if the `RESTART_SERVICES` variable is set to `true` in the sourced update script.
   - If true, restarts the `mythos-api` and `mythos-bot` services and checks their status.

4. **Completion Message**:
   ```bash
   echo ""
   echo "✅ Update complete!"
   ```
   - Outputs a completion message once the update process is finished.

This script provides a flexible and automated way to apply updates to the Mythos system by sourcing custom update scripts and optionally restarting services, ensuring the system remains up-to-date and functional.
