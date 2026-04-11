# bin/patch-clean.sh

**Language:** bash
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 172

---

### Documentation for `bin/patch-clean.sh`

#### Purpose
The `patch-clean.sh` script is designed to remove all traces of a specified patch from the system, including files in various directories and Git tags. It provides options for interactive confirmation, dry-run, and force execution.

#### Architecture
The script is a single function `patch-clean` that takes a patch ID and optional flags (`--force`, `--dry-run`). It performs the following steps:
1. Parses command-line arguments.
2. Checks for the presence of the patch ID.
3. Identifies and lists all files and directories associated with the patch.
4. Optionally confirms the removal of these items.
5. Removes the identified items and reports the results.

#### Patterns
- **Command Line Argument Parsing**: The script uses a simple loop to parse command-line arguments and set flags accordingly.
- **Conditional Execution**: The script uses conditional logic to handle different execution modes based on the presence of `--force` and `--dry-run` flags.

#### Dependencies
- **Bash Built-ins**: The script relies on built-in Bash commands such as `find`, `read`, `rm`, `git`, and `cd`.
- **Environment Variables**: The script uses `$HOME` to reference the user's home directory.

#### Interfaces
The script is designed to be sourced from `.bashrc` and provides a function `patch-clean` that can be called from the command line with the following usage:
```
patch-clean <patch_id> [--force] [--dry-run]
```

#### Database
The script does not interact with any databases directly.

#### Configuration
The script does not use any configuration files or environment variables explicitly. However, it relies on the environment variable `$HOME` to locate the `Downloads` directory.

#### Key Logic
1. **Argument Parsing**: The script parses the first argument as the patch ID and subsequent arguments as flags.
2. **File Discovery**: The script uses `find` to locate files and directories associated with the patch ID in predefined directories (`~/Downloads`, `/opt/mythos/patches`, `/opt/mythos/patches/archive`, `/tmp`).
3. **Git Tag Handling**: The script uses `git` commands to list and delete tags matching the patch ID.
4. **Removal Logic**: The script removes discovered files and directories, and optionally deletes Git tags. It handles dry-run and force execution modes.

#### Integration Points
The script integrates with the following system components:
- **File System**: It interacts with the file system to locate and remove files and directories.
- **Git Repository**: It interacts with the Git repository located at `/opt/mythos` to list and delete tags.

### Detailed Breakdown

#### Argument Parsing
The script parses the first argument as the patch ID and subsequent arguments as flags (`--force`, `--dry-run`). If no patch ID is provided, it prints usage instructions and exits.

#### File Discovery
The script uses `find` to locate files and directories associated with the patch ID in the following directories:
- `~/Downloads`: For zip files.
- `/opt/mythos/patches/archive`: For archived zip files.
- `/opt/mythos/patches`: For extracted patch directories.
- `/tmp`: For log files.

#### Git Tag Handling
The script changes to the `/opt/mythos` directory and uses `git tag -l` to list tags matching the patch ID. It then deletes these tags locally and remotely if the `--force` flag is set.

#### Removal Logic
The script removes the discovered files and directories. It handles dry-run mode by only listing the items that would be removed. It also handles force execution by skipping the confirmation prompt.

#### Reporting
The script provides detailed reporting on the items found and removed, including counts and success/failure statuses.

### Example Usage
```
patch-clean SYS-0011
patch-clean SYS-0011 --force
patch-clean SYS-0011 --dry-run
```

This script is a crucial tool for maintaining the cleanliness and integrity of the Mythos system by ensuring that all traces of a patch are removed when necessary.
