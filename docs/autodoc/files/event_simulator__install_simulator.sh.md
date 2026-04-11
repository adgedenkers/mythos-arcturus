# event_simulator/install_simulator.sh

**Language:** bash
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 30

---

### File: `event_simulator/install_simulator.sh`

#### Purpose
This script installs the Mythos Event Simulator by setting up necessary directories, copying Python scripts, and installing a wrapper script for easy execution.

#### Architecture
The script follows a straightforward procedural flow:
1. Creates a directory for tools.
2. Copies the Python script to the tools directory and makes it executable.
3. Installs a wrapper script in `/usr/local/bin` and makes it executable.
4. Provides usage instructions for the wrapper script.

#### Patterns
No specific design patterns are used since this is a simple bash script for installation purposes.

#### Dependencies
- `sudo` for elevated permissions.
- `cp` for copying files.
- `chmod` for changing file permissions.

#### Interfaces
The script does not expose any interfaces but provides a wrapper script (`mythos-test`) that can be used from the command line.

#### Database
The script mentions that test results will be stored in Neo4j per-machine, but it does not directly interact with the database.

#### Configuration
The script does not use any configuration files or environment variables explicitly. It relies on the current user's environment for permissions and paths.

#### Key Logic
The key logic involves:
1. Creating the `/opt/mythos/tools` directory and setting appropriate permissions.
2. Copying the `mythos_event_simulator.py` script to the tools directory and making it executable.
3. Installing the `mythos-test` wrapper script in `/usr/local/bin` and making it executable.

#### Integration Points
- The script integrates with the Mythos Event Simulator by setting up the necessary files and directories.
- The `mythos-test` wrapper script is used to interact with the `event_simulator.py` script, which presumably handles the actual event simulation and test execution.

### Detailed Breakdown

1. **Creating the Tools Directory:**
   ```bash
   sudo mkdir -p /opt/mythos/tools
   sudo chown -R $USER:$USER /opt/mythos/tools
   ```
   - Creates the directory `/opt/mythos/tools` if it does not exist.
   - Changes the ownership of the directory to the current user.

2. **Copying and Making the Python Script Executable:**
   ```bash
   cp mythos_event_simulator.py /opt/mythos/tools/event_simulator.py
   chmod +x /opt/mythos/tools/event_simulator.py
   ```
   - Copies the `mythos_event_simulator.py` script to `/opt/mythos/tools/event_simulator.py`.
   - Makes the copied script executable.

3. **Installing the Wrapper Script:**
   ```bash
   sudo cp mythos-test /usr/local/bin/mythos-test
   sudo chmod +x /usr/local/bin/mythos-test
   ```
   - Copies the `mythos-test` script to `/usr/local/bin`.
   - Makes the wrapper script executable.

4. **Usage Instructions:**
   ```bash
   echo "Usage:"
   echo "  mythos-test --run              # Run all tests"
   echo "  mythos-test --history          # Show test history"
   echo "  mythos-test --failures         # Show common failures"
   echo "  mythos-test --duration 60      # Run tests with custom duration"
   echo ""
   echo "Test results will be stored in Neo4j per-machine."
   echo ""
   ```
   - Provides usage instructions for the `mythos-test` wrapper script.
   - Mentions that test results are stored in Neo4j per-machine.

### Summary
This script sets up the Mythos Event Simulator by creating necessary directories, copying and making scripts executable, and providing usage instructions for the `mythos-test` wrapper script. It does not directly interact with the database but mentions that test results are stored in Neo4j.
