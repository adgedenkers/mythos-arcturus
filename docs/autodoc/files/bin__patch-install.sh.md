# bin/patch-install.sh

**Language:** bash
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 375

---

### Purpose
The `patch-install.sh` script is designed to manage the installation of patches for the Mythos system. It supports various modes of operation including normal installation, dry-run validation, and capturing output to the clipboard. The script also handles automatic rollback in case of installation failure.

### Architecture
The script is structured around a main `patch-install` function that parses command-line arguments and delegates to an inner `_patch_install_inner` function for the actual installation logic. The `_patch_install_inner` function handles patch detection, extraction, and execution. The script also includes `_patch_auto_rollback` and `_patch_clean_artifacts` functions for rollback and cleanup operations.

### Patterns
- **Command Pattern**: The script acts as a command that can be executed with different flags to perform specific actions.
- **State Pattern**: The script maintains state through flags and environment variables to control the flow of execution.

### Dependencies
- **Bash Built-ins**: `echo`, `local`, `shift`, `return`, `if`, `for`, `case`, `read`, `command`, `find`, `mkdir`, `cp`, `unzip`, `chmod`, `bash`, `cd`, `git`, `rm`, `rmdir`, `python3`, `sudo`, `systemctl`.
- **External Commands**: `xclip`, `xsel` for clipboard operations.
- **Python**: Used for JSON parsing and manipulation.

### Interfaces
- **Command-line Interface**: The script is invoked from the command line with the following arguments:
  - `patch-install <patch_id> [--clip] [--dry-run]`
- **Environment Variables**: Sets `MYTHOS_PATCH_DRY_RUN` for dry-run mode.

### Database
The script does not directly interact with any databases. However, it manipulates `STREAMS.json` and `PATCH_HISTORY.md` files which can be considered part of the system's configuration state.

### Configuration
- **Environment Variables**: `MYTHOS_PATCH_DRY_RUN` is set for dry-run mode.
- **Files**: 
  - `/opt/mythos/patches/archive` for archiving patch files.
  - `/opt/mythos/patches` for extracting and installing patches.
  - `/opt/mythos/docs/STREAMS.json` for managing patch streams.
  - `/opt/mythos/docs/PATCH_HISTORY.md` for maintaining patch history.

### Key Logic
1. **Patch Detection and Extraction**:
   - Detects patch ID format and finds the corresponding zip file in the `Downloads` directory.
   - Extracts the zip file to the patches directory and makes the `install.sh` script executable.

2. **Dry-Run and Real Installation**:
   - Validates the patch with a dry-run if specified.
   - Executes the `install.sh` script for real installation if the dry-run passes or if no dry-run is requested.

3. **Auto-Rollback**:
   - Reverts deployed files using git.
   - Undoes changes made to `STREAMS.json`.
   - Removes entries from `PATCH_HISTORY.md`.
   - Re-restarts services that were restarted by the patch.
   - Cleans up artifacts (zip files, extracted directories, etc.).

### Integration Points
- **Patch Installation**: The script integrates with the `install.sh` script within each patch to perform the actual installation.
- **System Services**: The script interacts with system services via `systemctl` to restart services.
- **Git**: The script uses git to manage file versions and revert changes.
- **Python**: The script uses Python for JSON parsing and manipulation of configuration files.

### Detailed Analysis

#### `patch-install`
- **Purpose**: Main entry point for the script, parses arguments and delegates to `_patch_install_inner`.
- **Parameters**: `patch_id` (required), `--clip`, `--dry-run`.
- **Flow**: Validates `patch_id`, captures output if `--clip` is used, and calls `_patch_install_inner`.

#### `_patch_install_inner`
- **Purpose**: Handles the core logic of detecting, extracting, and installing patches.
- **Parameters**: `patch_id`, `dry_run`.
- **Flow**: 
  - Detects patch ID format and finds the corresponding zip file.
  - Extracts the zip file and makes `install.sh` executable.
  - Validates with a dry-run if specified.
  - Executes the `install.sh` script for real installation.

#### `_patch_auto_rollback`
- **Purpose**: Handles automatic rollback in case of installation failure.
- **Parameters**: `patch_id`.
- **Flow**: 
  - Reverts deployed files using git.
  - Undoes changes made to `STREAMS.json`.
  - Removes entries from `PATCH_HISTORY.md`.
  - Re-restarts services that were restarted by the patch.
  - Cleans up artifacts.

#### `_patch_clean_artifacts`
- **Purpose**: Cleans up patch artifacts.
- **Parameters**: `patch_id`.
- **Flow**: Removes zip files, extracted directories, and other artifacts.

### Conclusion
The `patch-install.sh` script is a comprehensive tool for managing patch installations in the Mythos system. It supports various modes of operation and handles automatic rollback in case of failure, ensuring the system remains in a consistent state.
