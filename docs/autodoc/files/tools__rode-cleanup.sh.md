# tools/rode-cleanup.sh

**Language:** bash
**Stream:** SYS
**Module:** Tools
**Lines:** 190

---

### File: tools/rode-cleanup.sh

#### Purpose
This script performs a one-time deduplication of voice memos in the `/opt/mythos/voice_memos/incoming` directory. It removes zero-byte files and duplicates based on MD5 hashes, keeping only the original files without suffixes.

#### Architecture
The script is structured into three main phases:
1. **Phase 1**: Identifies and removes zero-byte files.
2. **Phase 2**: Deduplicates files based on MD5 hashes, keeping the original file without suffixes.
3. **Phase 3**: Generates a manifest of surviving files for the `rode-transfer` subsystem.

#### Patterns
- **Command Line Arguments**: The script uses command line arguments to determine whether to perform a dry run or actually delete files.
- **Conditional Execution**: Uses conditional logic to handle different modes (dry run vs. live execution).

#### Dependencies
- **Bash Built-ins**: `find`, `md5sum`, `awk`, `stat`, `basename`, `echo`, `printf`, `bc`.
- **Environment Variables**: `CONFIRM` to control the execution mode.

#### Interfaces
- **Command Line Interface**: The script accepts `--confirm` as an optional argument to confirm the deletion of files.
- **Output**: Provides detailed output to the console, indicating what actions would be taken or have been taken.

#### Database
- **No Direct Database Interaction**: The script does not interact directly with any databases.

#### Configuration
- **Environment Variables**: Uses `CONFIRM` to control the execution mode.
- **Hardcoded Paths**: Uses hardcoded paths for the target directory (`/opt/mythos/voice_memos/incoming`) and the manifest file (`/opt/mythos/voice_memos/incoming/.rode-manifest.json`).

#### Key Logic
1. **Zero-byte File Removal**:
   - Uses `find` to locate zero-byte files.
   - Conditionally deletes these files based on the `CONFIRM` flag.
   
2. **MD5-based Deduplication**:
   - Hashes all remaining WAV files and builds a mapping of hashes to file paths.
   - For each hash, identifies and keeps the original file without a suffix (e.g., `_b`, `_c`).
   - Conditionally deletes duplicate files based on the `CONFIRM` flag.
   
3. **Manifest Generation**:
   - Generates a JSON manifest of surviving files.
   - Writes the manifest to `/opt/mythos/voice_memos/incoming/.rode-manifest.json`.

#### Integration Points
- **rode-transfer Subsystem**: The script generates a manifest file that is used by the `rode-transfer` subsystem to track surviving voice memos.
- **File System**: The script interacts with the file system to read, delete, and write files.

### Detailed Breakdown

#### Phase 1: Zero-byte File Removal
- **Functionality**: Identifies and optionally deletes zero-byte files.
- **Logic**:
  - Uses `find` to locate zero-byte files.
  - Stores file paths in `ZERO_FILES` array.
  - Conditionally deletes files based on the `CONFIRM` flag.

#### Phase 2: MD5-based Deduplication
- **Functionality**: Deduplicates files based on MD5 hashes, keeping the original file without suffixes.
- **Logic**:
  - Hashes all remaining WAV files and builds a mapping of hashes to file paths.
  - For each hash, identifies and keeps the original file without a suffix.
  - Conditionally deletes duplicate files based on the `CONFIRM` flag.

#### Phase 3: Manifest Generation
- **Functionality**: Generates a JSON manifest of surviving files.
- **Logic**:
  - Builds a JSON manifest of surviving files.
  - Writes the manifest to `/opt/mythos/voice_memos/incoming/.rode-manifest.json`.

### Example Usage
- **Dry Run**: `./rode-cleanup.sh`
- **Live Execution**: `./rode-cleanup.sh --confirm`

This script ensures that the `rode-transfer` subsystem receives a clean set of unique voice memos, optimizing storage and preventing data redundancy.
