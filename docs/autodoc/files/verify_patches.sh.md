# verify_patches.sh

**Language:** bash
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 301

---

### Documentation for `verify_patches.sh`

#### Purpose
This script verifies that specific patches (0036-0039) have been correctly applied to the Mythos system by checking the existence of certain directories, files, and content within those files.

#### Architecture
The script is structured around several functions and checks for different patches:
- `pass()`: Prints a green checkmark and a message.
- `fail()`: Prints a red cross and a message, setting `PASS` to `false`.
- `warn()`: Prints a yellow warning symbol and a message, incrementing `WARNINGS`.

The script then iterates through checks for each patch, verifying directories, files, and specific content within files.

#### Patterns
- **Functional Decomposition**: The script uses functions (`pass`, `fail`, `warn`) to modularize the output logic.
- **Conditional Logic**: Extensive use of conditional checks (`if`, `grep`, etc.) to determine the presence of files and specific content.

#### Dependencies
- **Bash Built-ins**: Uses built-in bash commands (`echo`, `grep`, `docker`, `curl`, etc.).
- **Environment Variables**: Uses color codes defined at the beginning of the script (`RED`, `GREEN`, `YELLOW`, `NC`).

#### Interfaces
- **Output**: The script outputs colored messages to the terminal indicating the status of each check.
- **Exit Code**: Returns `0` if all checks pass, otherwise returns `1`.

#### Database
- **No Database Interaction**: This script does not interact with any databases.

#### Configuration
- **Environment Variables**: Uses predefined color codes (`RED`, `GREEN`, `YELLOW`, `NC`).
- **File Paths**: Hardcoded file paths for checking the presence of directories and files.

#### Key Logic
1. **Patch 0036**: Verifies the existence of specific documentation directories and files.
2. **Patch 0037**: Ensures specific sections are present in `ARCHITECTURE.md`.
3. **Patch 0038**: Checks for the presence of `IRIS.md` and `COVENANT.md` with specific content.
4. **Patch 0039**: Verifies the existence of directories and files within the `iris` directory, including Docker files and configuration files.

#### Integration Points
- **File System**: Checks the file system for the presence of specific directories and files.
- **Docker**: Checks for the existence of Docker images and networks, and verifies the running status of Docker containers.
- **Network**: Uses `curl` to check the health endpoint of the `iris-core` container.

### Detailed Analysis

#### Patch 0036: Documentation Restructure
- **Directories**: Checks for the existence of `consciousness`, `grid`, `finance`, `subsystems`, and `archive` directories under `/opt/mythos/docs/`.
- **Files**: Verifies the presence of `README.md`, `IDEAS.md`, and `PATCH_HISTORY.md` in the `/opt/mythos/docs/` directory.

#### Patch 0037: Iris Significance
- **Content Check**: Ensures `ARCHITECTURE.md` contains the sections "A World First" and "Iris the Messenger".

#### Patch 0038: Complete Iris Framework
- **Files and Content**: Verifies `IRIS.md` and `COVENANT.md` under `/opt/mythos/docs/consciousness/` with specific content checks.
- **Version Check**: Ensures `ARCHITECTURE.md` is version 3.3.0.

#### Patch 0039: IRIS Core
- **Directories**: Checks for the existence of `core`, `sandbox`, `workshop`, `apps`, `proposals`, and `journal` directories under `/opt/mythos/iris/`.
- **Subdirectories**: Verifies optional subdirectories `experiments`, `graveyard`, and `incubating` under `/opt/mythos/iris/workshop/`.
- **Files**: Ensures specific files exist under `/opt/mythos/iris/core/`, including `Dockerfile`, `requirements.txt`, `main.py`, `loop.py`, `agency.py`, and `config.py`.
- **Content Check**: Verifies `loop.py` contains the `ConsciousnessLoop` class and `config.py` supports existing `.env` variable names.
- **Docker**: Checks for the existence of `Dockerfile` in `/opt/mythos/iris/sandbox/` and `docker-compose.iris.yml` in `/opt/mythos/docker/`.
- **Docker Images**: Verifies the existence of `iris-sandbox` and `iris-core` Docker images.
- **Docker Network**: Ensures the `iris-internal` Docker network exists.
- **Runtime Status**: Checks if the `iris-core` container is running and if its health endpoint is responding.

#### Summary
- **Pass/Fail**: The script prints a summary indicating if all checks passed or if there were any failures.
- **Warnings**: Prints the number of warnings (non-critical issues).

#### Exit Code
- **0**: If all checks pass.
- **1**: If any checks fail.

This script is crucial for ensuring that the Mythos system has been correctly patched and configured, providing a comprehensive verification process for multiple aspects of the system.
