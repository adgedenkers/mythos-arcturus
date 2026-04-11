# bin/print-watcher.sh

**Language:** bash
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 42

---

### File: `bin/print-watcher.sh`

#### Purpose
This script watches the `~/print-queue` directory for new PDF files that match a specific naming pattern and prints them using the `lp` command. After printing, it moves the file to the `~/print-queue/done/` directory.

#### Architecture
- **Functions**:
  - `log`: A function to log messages both to the console and the system log.
- **Main Logic**:
  - The script uses `inotifywait` to monitor the `~/print-queue` directory for new files.
  - It processes each new file that matches the pattern `*-[13-digit-timestamp].pdf`.
  - The script prints the file using `lp` and moves it to the `done` directory upon successful printing.

#### Patterns
- **Observer Pattern**: The script uses `inotifywait` to observe changes in the `~/print-queue` directory, which is a form of the Observer pattern.

#### Dependencies
- **Bash Built-ins**: `set`, `mkdir`, `echo`, `logger`, `date`, `read`, `if`, `sleep`, `lp`, `mv`
- **External Commands**: `inotifywait` (from the `inotify-tools` package)

#### Interfaces
- **Logging**: The `log` function is used to log messages both to the console and the system log.
- **File Watching**: The script exposes a mechanism to watch for new files in the `~/print-queue` directory.

#### Database
- **No Database Interaction**: This script does not interact with any database.

#### Configuration
- **Environment Variables**:
  - `HOME`: Used to set the `WATCH_DIR` and `DONE_DIR`.
- **No Configuration Files**: The script does not use any external configuration files.

#### Key Logic
- **File Matching**: The script checks if the file name matches the pattern `*-[13-digit-timestamp].pdf`.
- **Printing**: The script uses the `lp` command to print the file.
- **File Management**: After printing, the script moves the file to the `~/print-queue/done/` directory.

#### Integration Points
- **File System**: The script interacts with the file system to watch for new files, print them, and move them to the `done` directory.
- **Logging**: The script logs messages to both the console and the system log using the `logger` command.

### Detailed Breakdown

1. **Environment Setup**:
   - The script sets up the `WATCH_DIR` and `DONE_DIR` variables to point to the `~/print-queue` and `~/print-queue/done/` directories, respectively.
   - It ensures that these directories exist using `mkdir -p`.

2. **Logging Function**:
   - The `log` function is defined to log messages both to the console and the system log using `logger`.

3. **Watching for New Files**:
   - The script uses `inotifywait` to monitor the `~/print-queue` directory for new files.
   - It processes each new file that matches the pattern `*-[13-digit-timestamp].pdf`.

4. **File Processing**:
   - The script checks if the file exists and is fully written by introducing a brief pause using `sleep 1`.
   - It then prints the file using the `lp` command.
   - If the printing is successful, the script moves the file to the `~/print-queue/done/` directory.
   - If the printing fails, the script logs an error message.

This script is a simple yet effective way to automate the printing of PDF files that are dropped into a specific directory, ensuring that each file is processed and moved to a done directory after printing.
