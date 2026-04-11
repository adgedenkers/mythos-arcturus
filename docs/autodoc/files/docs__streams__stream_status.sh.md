# docs/streams/stream_status.sh

**Language:** bash
**Stream:** SYS
**Module:** Documentation
**Lines:** 41

---

### Documentation for `stream_status.sh`

#### Purpose
This script, `stream_status.sh`, is designed to gather and display status information about various streams and system activities within the Mythos system. It can be run at the start of a session to provide an overview of ongoing work, recent changes, and the status of system services.

#### Architecture
The script follows a straightforward procedural design, consisting of a series of commands and conditional checks. It does not use classes or functions, as it is a simple Bash script.

#### Patterns
No specific design patterns are used in this script. It is a straightforward sequence of commands and conditional logic.

#### Dependencies
- **Bash**: The script is written in Bash and relies on Bash commands and utilities.
- **Git**: The script uses `git` commands to fetch information about tags and commits.
- **Systemctl**: Used to check the status of system services.
- **xclip**: Used to copy the output to the clipboard.

#### Interfaces
The script does not expose any interfaces in the traditional sense. It is intended to be run directly from the command line and outputs its results to a file and the clipboard.

#### Database
The script does not interact with any databases directly.

#### Configuration
The script does not use any configuration files or environment variables. It relies on the provided command-line argument for stream-specific information.

#### Key Logic
1. **Initialization**: The script initializes a diagnostic file `diag.txt` in the user's home directory.
2. **General Information**: It appends general information from `STREAMS.md` and `TODO.md` to the diagnostic file.
3. **Recent Changes**: It fetches and appends the last 20 git tags and the last 10 commits to the diagnostic file.
4. **Stream-Specific Information**: If a stream prefix is provided as a command-line argument, it fetches and appends stream-specific tags, commits, and files changed in the last 5 commits.
5. **Service Status**: It checks and appends the status of specific system services (`mythos-bot.service` and `mythos-patch-monitor.service`).
6. **Clipboard Copy**: The final output is copied to the clipboard for easy pasting into a Claude session.

#### Integration Points
- **Documentation Files**: The script reads from `STREAMS.md` and `TODO.md` located in `/opt/mythos/docs/`.
- **Git Repository**: It interacts with the Mythos git repository located at `/opt/mythos/` to fetch tags and commits.
- **System Services**: It checks the status of `mythos-bot.service` and `mythos-patch-monitor.service` using `systemctl`.

#### Example Usage
```bash
bash /opt/mythos/docs/stream_status.sh NEU
```
This command will generate a status report for streams prefixed with `NEU` and copy the output to the clipboard.

### Summary
The `stream_status.sh` script provides a comprehensive overview of the Mythos system's current state, including ongoing work, recent changes, and service statuses. It is designed to be run at the start of a session to quickly gather and present this information.
