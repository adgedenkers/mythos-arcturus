# bin/pdf-open-wrapper.sh

**Language:** bash
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 20

---

### File: `bin/pdf-open-wrapper.sh`

#### Purpose
This script acts as a smart PDF opener that suppresses automatic opening for files located in the `~/print-queue/` directory and opens other PDF files normally using the Evince viewer.

#### Architecture
- **Script Structure**: The script is a simple bash script that iterates over each file passed as an argument.
- **Conditional Logic**: It checks if the file is in the `~/print-queue/` directory and handles it accordingly.
- **External Commands**: Uses `realpath` to resolve the absolute path of the file and `logger` to log messages.

#### Patterns
- **Conditional Execution**: The script uses conditional statements to decide whether to open the file or suppress the action.

#### Dependencies
- **External Commands**: `realpath`, `logger`, `evince`
- **Environment Variables**: `HOME`

#### Interfaces
- **Input**: Takes a list of file paths as command-line arguments.
- **Output**: Logs messages to the system log using `logger` and opens files using `evince`.

#### Database
- **No Database Interaction**: This script does not interact with any database.

#### Configuration
- **Environment Variables**: Uses `HOME` to construct the `PRINT_QUEUE` path.
- **Hardcoded Paths**: Uses hardcoded paths for the Evince viewer (`/usr/bin/evince`).

#### Key Logic
- **Path Resolution**: Resolves the absolute path of each file using `realpath`.
- **Conditional Handling**: Checks if the file is in the `~/print-queue/` directory and either logs a message or opens the file with `evince`.

#### Integration Points
- **Print Queue Handling**: This script integrates with the print queue system by suppressing the opening of files in `~/print-queue/` and logging the event.
- **Evince Viewer**: It integrates with the Evince PDF viewer to open files that are not in the print queue.

### Detailed Breakdown

1. **Initialization**:
   - `PRINT_QUEUE` is set to `~/print-queue/` using the `HOME` environment variable.
   - `REAL_VIEWER` is set to `/usr/bin/evince`.

2. **Loop Through Files**:
   - The script loops over each file passed as an argument (`"$@"`).

3. **Path Resolution**:
   - The absolute path of each file is resolved using `realpath`. If `realpath` fails, the original file path is used.

4. **Conditional Handling**:
   - If the absolute path starts with `${PRINT_QUEUE}`, the script logs a message using `logger` and skips opening the file.
   - Otherwise, the script opens the file with `evince` in the background (`&`).

### Example Usage
```bash
./pdf-open-wrapper.sh /path/to/file1.pdf /path/to/file2.pdf
```

This script ensures that files in the print queue are not automatically opened, while other PDF files are opened normally, facilitating a more controlled workflow for PDF handling within the Mythos system.
