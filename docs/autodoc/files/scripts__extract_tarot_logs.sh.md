# scripts/extract_tarot_logs.sh

**Language:** bash
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 16

---

### File: scripts/extract_tarot_logs.sh

#### Purpose
This script extracts tarot session logs from ZIP files located in a specific directory and distributes them to two different directories: one within the Mythos system and another within an Obsidian vault.

#### Architecture
The script follows a straightforward procedural design:
1. Defines directories for ZIP files, Mythos conversations, and Obsidian vault.
2. Iterates over all ZIP files in the ZIP directory that match the pattern `tarot*.zip`.
3. For each ZIP file, it extracts the base name and creates directories for both the Mythos and Obsidian systems.
4. Unzips the contents of each ZIP file into the respective directories.

#### Patterns
No specific design patterns are used in this script. It is a simple procedural script.

#### Dependencies
- `bash` for script execution
- `unzip` command for extracting ZIP files

#### Interfaces
The script does not expose any interfaces to other parts of the system. It is intended to be run as a standalone script.

#### Database
This script does not interact with any databases.

#### Configuration
The script uses hardcoded directory paths:
- `ZIP_DIR` for the directory containing ZIP files (`/opt/mythos/conversation_log_zips`)
- `MYTHOS_DIR` for the Mythos conversation directory (`/opt/mythos/conversations`)
- `OBSIDIAN_DIR` for the Obsidian vault directory (`/home/adge/curated-vault/spiritual/seraphe/tarot-sessions`)

#### Key Logic
The key logic involves iterating over ZIP files and extracting their contents into two different directories:
1. Extract the base name from the ZIP file.
2. Create directories for both the Mythos and Obsidian systems.
3. Unzip the contents into both directories.

#### Integration Points
The script integrates with the file system to extract and distribute tarot session logs:
- **Mythos System**: Logs are extracted into `/opt/mythos/conversations`.
- **Obsidian Vault**: Logs are extracted into `/home/adge/curated-vault/spiritual/seraphe/tarot-sessions`.

### Detailed Breakdown

1. **Directory Definitions**:
   ```bash
   ZIP_DIR="/opt/mythos/conversation_log_zips"
   MYTHOS_DIR="/opt/mythos/conversations"
   OBSIDIAN_DIR="/home/adge/curated-vault/spiritual/seraphe/tarot-sessions"
   ```

2. **Loop Over ZIP Files**:
   ```bash
   for zip in "$ZIP_DIR"/tarot*.zip; do
   ```

3. **Extract Base Name**:
   ```bash
   name=$(basename "$zip" .zip)
   ```

4. **Create Directories**:
   ```bash
   mkdir -p "$MYTHOS_DIR/$name"
   mkdir -p "$OBSIDIAN_DIR/$name"
   ```

5. **Unzip Files**:
   ```bash
   unzip -o "$zip" -d "$MYTHOS_DIR/$name"
   unzip -o "$zip" -d "$OBSIDIAN_DIR/$name"
   ```

This script ensures that tarot session logs are consistently distributed to both the Mythos system and the Obsidian vault for further processing and documentation.
