# bin/downloads_triage.sh

**Language:** bash
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 282

---

### File: `bin/downloads_triage.sh`

#### Purpose
This script organizes files in the `~/Downloads` directory into categorized subdirectories within `~/Downloads/_archived/`. It does not delete any files but moves them to labeled bins for further processing by other systems.

#### Architecture
The script is organized into several sections, each handling a specific category of files. It defines helper functions `archive` and `archive_dir` to move files and directories, respectively. Each section iterates over specific file patterns and moves them to the appropriate category directory.

#### Patterns
- **Helper Functions**: The script uses helper functions (`archive`, `archive_dir`) to encapsulate the logic for moving files and directories.
- **Loops and Conditionals**: The script uses loops and conditionals to check for the existence of files and directories before moving them.

#### Dependencies
- **Bash Built-ins**: Uses built-in bash commands like `find`, `mv`, `mkdir`, `echo`, and `date`.
- **Environment Variables**: Uses `$HOME` and `$DL` environment variables.

#### Interfaces
- **Output**: The script outputs progress messages and a summary of the triage process.
- **File Operations**: The script exposes no direct interfaces but performs file operations that can be observed through the output and the state of the `~/Downloads` directory.

#### Database
- **No Database Interaction**: This script does not interact with any databases.

#### Configuration
- **No Configuration Files**: The script does not use any configuration files or environment variables beyond the standard environment variables like `$HOME`.

#### Key Logic
1. **Snapshot Creation**: Before moving any files, the script creates a snapshot of the current state of `~/Downloads` in `/tmp`.
2. **Directory Creation**: It creates the necessary category directories within `~/Downloads/_archived/`.
3. **File and Directory Movement**: It moves files and directories to their respective categories using the `archive` and `archive_dir` functions.
4. **Summary**: After moving all files, it provides a summary of the triage process, including the number of files remaining in `~/Downloads`.

#### Integration Points
- **docs-librarian System**: This script prepares the `~/Downloads` directory for the `docs-librarian` system by organizing files into labeled bins.
- **File System**: The script interacts with the file system to move and organize files.

### Detailed Analysis

#### Helper Functions
- **`archive`**: Moves a file to a specified category directory.
  ```bash
  archive() {
      local file="$1"
      local bin="$2"
      [ -f "$DL/$file" ] && mv -v "$DL/$file" "$A/$bin/" || true
  }
  ```
- **`archive_dir`**: Moves a directory to a specified category directory.
  ```bash
  archive_dir() {
      local dir="$1"
      local bin="$2"
      [ -d "$DL/$dir" ] && mv -v "$DL/$dir" "$A/$bin/" || true
  }
  ```

#### File Categories
- **Patches**: Directories and zip files related to patches.
- **Sessions**: JSON files related to session summaries and exports.
- **Handoffs**: Handoff documents.
- **Scripts**: Python scripts.
- **Schemas**: JSON skill schemas and build plans.
- **Tarot**: Tarot session exports.
- **Seraphe**: Deliverables and data exports.
- **Images**: Image files.
- **Duplicates**: Numbered copies of files.
- **Build Artifacts**: SQL, cypher, and other build-related files.
- **Iris Bench**: Iris-specific deliverables.
- **Docs Candidates**: Markdown files for future librarian import.
- **Deliverables**: Final output files.

#### Summary
The script concludes by providing a summary of the triage process, including the number of files remaining in `~/Downloads`.

This script ensures that the `~/Downloads` directory is organized into labeled bins, preparing it for further processing by the `docs-librarian` system.
