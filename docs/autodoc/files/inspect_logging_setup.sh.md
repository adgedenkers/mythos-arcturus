# inspect_logging_setup.sh

**Language:** bash
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 70

---

### File: `inspect_logging_setup.sh`

#### Purpose
This bash script inspects specific Python files within the Mythos system to analyze their logging setup, including metadata, imports, and usage of logging functions.

#### Architecture
The script follows a straightforward procedural design:
1. Sets up an array of file paths to inspect.
2. Prints system and Python version information.
3. Iterates over each file in the array, performing various checks and prints:
   - File metadata (permissions, size, SHA256 hash).
   - Logging-related imports and configurations.
   - Usage of `basicConfig`, handler creation, and `getLogger`.
   - Logger names and partial content (top and bottom 40 lines).

#### Patterns
- **Procedural Pattern**: The script follows a linear flow of operations, with no complex patterns like factory or singleton.

#### Dependencies
- **External Commands**: `uname`, `ls`, `sha256sum`, `grep`, `sed`, `tail`.
- **Python Environment**: `/opt/mythos/.venv/bin/python` for version information.

#### Interfaces
- **Output**: The script outputs inspection results to the console, providing a detailed report on the logging setup of specified Python files.

#### Database
- **No Database Interaction**: This script does not interact with any databases.

#### Configuration
- **Environment Variables**: The script does not use any environment variables.
- **Configuration Files**: The script does not use any configuration files.

#### Key Logic
- **File Inspection**: The script iterates over a predefined list of files and performs various checks using `grep` and `sed` to extract logging-related information.
- **System Information**: It also prints system and Python version details at the beginning.

#### Integration Points
- **Python Files**: The script directly interacts with Python files located at `/opt/mythos/mythos_patch_monitor.py` and `/opt/mythos/sales_ingestion/ingest_sales_zip.py`.
- **System Commands**: It uses various system commands to gather and display information about the files and the system.

### Detailed Breakdown

1. **System and Python Version Information**:
   ```bash
   echo "---- SYSTEM ----"
   uname -a
   echo ""
   echo "---- PYTHON ----"
   /opt/mythos/.venv/bin/python --version
   echo ""
   ```

2. **File Inspection Loop**:
   ```bash
   for FILE in "${FILES[@]}"; do
       echo "============================================================"
       echo "FILE: ${FILE}"
       echo "============================================================"

       if [[ ! -f "$FILE" ]]; then
           echo "❌ FILE NOT FOUND"
           echo ""
           continue
       fi
   ```

3. **File Metadata**:
   ```bash
   echo "---- FILE METADATA ----"
   ls -l "$FILE"
   sha256sum "$FILE"
   echo ""
   ```

4. **Logging Imports**:
   ```bash
   echo "---- LOGGING IMPORTS ----"
   grep -nE "import logging|from logging" "$FILE" || echo "(none)"
   echo ""
   ```

5. **basicConfig Calls**:
   ```bash
   echo "---- basicConfig CALLS ----"
   grep -nE "logging\.basicConfig" "$FILE" || echo "(none)"
   echo ""
   ```

6. **Handler Creation**:
   ```bash
   echo "---- HANDLER CREATION ----"
   grep -nE "FileHandler|StreamHandler|addHandler" "$FILE" || echo "(none)"
   echo ""
   ```

7. **getLogger Usage**:
   ```bash
   echo "---- getLogger USAGE ----"
   grep -nE "getLogger" "$FILE" || echo "(none)"
   echo ""
   ```

8. **Logger Names**:
   ```bash
   echo "---- LOGGER NAMES (strings) ----"
   grep -nE "getLogger\\(\"|getLogger\\('" "$FILE" || echo "(none)"
   echo ""
   ```

9. **File Content**:
   ```bash
   echo "---- TOP OF FILE (first 40 lines) ----"
   sed -n '1,40p' "$FILE"
   echo ""

   echo "---- BOTTOM OF FILE (last 40 lines) ----"
   tail -n 40 "$FILE"
   echo ""
   ```

10. **Completion Message**:
    ```bash
    echo "============================================================"
    echo "DONE"
    echo "============================================================"
    ```

This script provides a comprehensive inspection of logging configurations in specified Python files, ensuring that logging is set up correctly and consistently across the Mythos system.
