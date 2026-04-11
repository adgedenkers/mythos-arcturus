# export_mythos_codebase.sh

**Language:** bash
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 109

---

### File: `export_mythos_codebase.sh`

#### Purpose
This script creates a compressed ZIP archive of the Mythos codebase located at `/opt/mythos/`, excluding large, sensitive, and generated files to ensure a clean and manageable export.

#### Architecture
The script is a simple bash script that follows a linear flow:
1. Sets up variables for the output directory, timestamp, and output file path.
2. Prints a header and details about the export process.
3. Checks if the source directory exists.
4. Uses the `zip` command to create the archive, excluding specified file types and directories.
5. Prints a summary of the exported file, including its size and a preview of its contents.

#### Patterns
No design patterns are used as this is a straightforward script.

#### Dependencies
- `bash` for script execution.
- `zip` for creating the ZIP archive.
- `date` for generating the timestamp.
- `du` for checking the file size.
- `unzip` for listing the contents of the ZIP file.

#### Interfaces
This script does not expose any interfaces to other parts of the system. It is intended to be run as a standalone script.

#### Database
No database interactions are performed by this script.

#### Configuration
The script does not use any configuration files or environment variables. All settings are hardcoded within the script.

#### Key Logic
The key logic involves:
1. Setting up the output file path with a timestamp.
2. Checking if the source directory exists.
3. Using the `zip` command to create the archive while excluding specified file types and directories.
4. Providing a summary of the exported file, including its size and a preview of its contents.

#### Integration Points
This script does not integrate with other subsystems of the Mythos system. It is a standalone utility for exporting the codebase.

### Detailed Breakdown

1. **Setup Variables**:
   - `OUTPUT_DIR`: The directory where the ZIP file will be saved, set to the user's home directory.
   - `TIMESTAMP`: A timestamp string in `YYYYMMDD_HHMMSS` format.
   - `OUTPUT_FILE`: The full path to the output ZIP file.

2. **Print Header and Details**:
   - Prints a header and details about the source directory and output file.
   - Lists the file types and directories that will be excluded from the ZIP archive.

3. **Check Source Directory**:
   - Checks if the `/opt/mythos` directory exists. If it does not, the script exits with an error message.

4. **Create Archive**:
   - Changes the directory to `/opt` and uses the `zip` command to create the ZIP archive.
   - Excludes various file types and directories using the `-x` option multiple times.

5. **Print Summary**:
   - Prints a completion message and the path to the output file.
   - Uses `du -h` to display the size of the ZIP file.
   - Lists the top-level contents of the ZIP file using `unzip -l` and `head`.
   - Counts and displays the most common file types included in the ZIP file using `unzip -l`, `grep`, `sort`, and `uniq`.

6. **Final Message**:
   - Provides a final message instructing the user to upload the file to Claude for review.

This script ensures that only relevant codebase files are included in the ZIP archive, making it easier to manage and review the Mythos codebase.
