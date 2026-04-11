# services/install_services.sh

**Language:** bash
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 23

---

### File: services/install_services.sh

#### Purpose
This script installs Mythos worker systemd services by copying service files from `/opt/mythos/services/` to `/etc/systemd/system/` and reloading the systemd daemon.

#### Architecture
- **Script Structure**: The script uses a `for` loop to iterate over all service files matching the pattern `mythos-worker-*.service` in the `/opt/mythos/services/` directory.
- **Systemd Management**: It copies each service file to the systemd directory and then reloads the systemd daemon to recognize the new services.

#### Patterns
- **None**: This script does not use any design patterns as it is a simple bash script for service installation.

#### Dependencies
- **System Commands**: `echo`, `basename`, `sudo`, `cp`, `systemctl`

#### Interfaces
- **Output**: The script outputs messages to the user about the installation process and provides instructions on how to enable and start the services.
- **No External Interfaces**: The script does not expose any functions or methods to other parts of the system.

#### Database
- **None**: This script does not interact with any databases.

#### Configuration
- **Environment Variables**: The script does not use any environment variables.
- **Config Files**: The script does not use any configuration files.

#### Key Logic
- **Service Installation Loop**: The script iterates over all service files in `/opt/mythos/services/` that match the pattern `mythos-worker-*.service`, copies each file to `/etc/systemd/system/`, and reloads the systemd daemon.
- **User Instructions**: The script provides instructions on how to enable and start the services after installation.

#### Integration Points
- **Systemd Services**: The script integrates with the systemd service manager to install and manage Mythos worker services.
- **File System**: The script reads service files from `/opt/mythos/services/` and writes them to `/etc/systemd/system/`.

### Detailed Breakdown

1. **Script Initialization**:
   ```bash
   #!/bin/bash
   echo "Installing Mythos worker services..."
   ```
   - The script starts with a shebang (`#!/bin/bash`) to indicate that it should be run with the Bash shell.
   - It prints a message indicating that the Mythos worker services are being installed.

2. **Service Installation Loop**:
   ```bash
   for service in /opt/mythos/services/mythos-worker-*.service; do
       name=$(basename "$service")
       echo "  Installing $name..."
       sudo cp "$service" /etc/systemd/system/
   done
   ```
   - The script iterates over all files in `/opt/mythos/services/` that match the pattern `mythos-worker-*.service`.
   - For each file, it extracts the base name (e.g., `mythos-worker-grid.service`) and prints a message indicating that the service is being installed.
   - It then copies the service file to `/etc/systemd/system/` using `sudo cp`.

3. **Daemon Reload**:
   ```bash
   sudo systemctl daemon-reload
   ```
   - After all service files are copied, the script reloads the systemd daemon to recognize the new services.

4. **User Instructions**:
   ```bash
   echo ""
   echo "Services installed. To enable and start:"
   echo "  sudo systemctl enable mythos-worker-grid"
   echo "  sudo systemctl start mythos-worker-grid"
   echo ""
   echo "Or enable all workers:"
   echo "  for w in grid embedding vision temporal entity summary; do"
   echo "    sudo systemctl enable mythos-worker-\$w"
   echo "    sudo systemctl start mythos-worker-\$w"
   echo "  done"
   ```
   - The script provides instructions on how to enable and start the `mythos-worker-grid` service.
   - It also provides a loop to enable and start all worker services (`grid`, `embedding`, `vision`, `temporal`, `entity`, `summary`).

This script is a straightforward utility for installing and managing Mythos worker services using systemd.
