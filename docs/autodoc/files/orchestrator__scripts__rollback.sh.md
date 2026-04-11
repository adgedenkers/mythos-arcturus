# orchestrator/scripts/rollback.sh

**Language:** bash
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 127

---

### Purpose
The `rollback.sh` script is designed to revert the changes made by `patch_0082`, specifically removing the Phase 1.1 Core Infrastructure of the Mythos system. This includes deleting specific database tables, removing the orchestrator directory, and restoring the system to a previous version.

### Architecture
The script follows a linear flow, performing a series of steps in sequence:
1. Verify the user running the script.
2. Prompt for user confirmation.
3. Drop specific database tables.
4. Remove the orchestrator directory.
5. Remove documentation.
6. Restore the version file.
7. Update Git to reflect the rollback.

### Patterns
- **Linear Execution**: The script follows a straightforward sequence of commands without branching logic.
- **User Confirmation**: Uses a simple confirmation prompt to ensure the user intends to proceed with the destructive actions.

### Dependencies
- **Environment Variables**: `EUID`, `MYTHOS_ROOT`, `ORCH_ROOT`
- **External Commands**: `psql`, `sudo`, `rm`, `git`, `grep`, `tr`

### Interfaces
- **User Interaction**: Prompts the user for confirmation before proceeding.
- **Output**: Provides detailed output to inform the user of the progress and results of each step.

### Database
- **Tables Removed**: `orch_test_results`, `orch_test_runs`, `orch_test_questions`, `orch_test_suites`, `orch_model_benchmarks`, `orch_model_capabilities`, `orch_models`

### Configuration
- **Environment Variables**: `MYTHOS_ROOT` and `ORCH_ROOT` are used to define the paths to the Mythos root directory and the orchestrator directory, respectively.
- **Version File**: The version file at `${MYTHOS_ROOT}/.version` is updated to `1.0.0`.

### Key Logic
1. **Database Table Deletion**: Uses `psql` to drop specific tables related to the orchestrator.
2. **Directory Removal**: Uses `rm -rf` to remove the orchestrator directory and documentation.
3. **Version Restoration**: Updates the version file to `1.0.0`.
4. **Git Update**: Adds changes to Git, commits them with a rollback message, and removes a specific tag if it exists.

### Integration Points
- **Database Integration**: Interacts with the PostgreSQL database to drop tables.
- **File System Integration**: Removes directories and files from the file system.
- **Version Control Integration**: Updates Git to reflect the rollback, including removing a specific tag.

### Detailed Breakdown
1. **User Verification**:
   - Checks if the script is run as root and exits if true.
   - Prompts the user for confirmation before proceeding.

2. **Database Table Deletion**:
   - Uses `psql` to drop tables with names starting with `orch_`.
   - Verifies that all tables have been removed.

3. **Directory Removal**:
   - Removes the orchestrator directory and documentation directory if they exist.

4. **Version Restoration**:
   - Updates the version file to `1.0.0`.

5. **Git Update**:
   - Adds all changes to Git.
   - Commits the changes with a rollback message.
   - Removes the tag `v1.15.1` if it exists.

### Summary
The `rollback.sh` script is a critical component for reverting the system to a previous state by removing specific infrastructure components, updating the version, and ensuring the changes are reflected in version control. It ensures safety by requiring user confirmation and verifying the user's identity before executing destructive actions.
