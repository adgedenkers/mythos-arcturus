# bin/rode_transfer.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 709

---

### File: `bin/rode_transfer.py`

#### Purpose
This file manages the transfer of audio files from RØDE Wireless GO devices to a specified destination directory, ensuring deduplication through a quick fingerprint mechanism.

#### Architecture
The file contains several classes and functions to handle device detection, file scanning, fingerprinting, and transfer operations. The main classes are:
- **Manifest**: Tracks every file ever imported by quick fingerprint.
- **RodeDevice**: Represents a RØDE Wireless GO device.
- **AudioFile**: Represents an audio file from a RØDE device.

Top-level functions include:
- `quick_fingerprint`: Generates a quick fingerprint for a file.
- `load_config` and `save_config`: Load and save configuration data.
- `find_rode_devices`: Detects connected RØDE devices.
- `scan_device`: Scans a device for audio files.
- `do_transfer`: Executes the file transfer process.

#### Patterns
- **Factory Method**: Used implicitly in the creation of `RodeDevice` and `AudioFile` instances.
- **Singleton**: The `Manifest` class can be considered a singleton as it tracks global state across the system.

#### Dependencies
- **Imports**: `os`, `sys`, `json`, `hashlib`, `argparse`, `pathlib`, `datetime`, `dataclasses`, `typing`, `rich` (for console output).
- **External Config**: Relies on a configuration file at `~/.config/rode-transfer/devices.json`.

#### Interfaces
- **Public Methods**: `quick_fingerprint`, `load_config`, `save_config`, `find_rode_devices`, `scan_device`, `do_transfer`, `cmd_list_devices`, `main`.
- **Classes**: `Manifest`, `RodeDevice`, `AudioFile`.

#### Database
- **PostgreSQL Tables**: No direct PostgreSQL tables are referenced.
- **Neo4j Labels**: No Neo4j labels are referenced.
- **Manifest File**: Uses a JSON manifest file (`MANIFEST_NAME`) to track fingerprints and file metadata.

#### Configuration
- **Config File**: `~/.config/rode-transfer/devices.json` for storing device names and serials.
- **Environment Variables**: No environment variables are used.

#### Key Logic
- **Fingerprinting**: Uses `quick_fingerprint` to generate a fingerprint based on file size and chunks of the file.
- **Device Detection**: Uses `/dev/disk/by-id/` to identify connected RØDE devices.
- **File Transfer**: Ensures deduplication by checking the manifest before transferring files.

#### Integration Points
- **Mythos Subsystems**: Integrates with the Mythos system for file transfer and deduplication.
- **Console Output**: Uses `rich` for formatted console output, including banners, tables, and progress bars.

### Detailed Documentation

#### Classes

1. **Manifest**
   - **Purpose**: Tracks every file ever imported by quick fingerprint.
   - **Methods**:
     - `__init__`: Initializes the manifest with the destination directory.
     - `_load`: Loads manifest data from a JSON file.
     - `_migrate_v1_to_v2`: Migrates manifest data from version 1 to version 2.
     - `save`: Saves the manifest data to a JSON file.
     - `files`: Returns the dictionary of files in the manifest.
     - `has_fingerprint`: Checks if a fingerprint exists in the manifest.
     - `record`: Records a new file in the manifest.
     - `count`: Returns the number of files in the manifest.
   - **Properties**:
     - `files`: Property to access the files dictionary.
     - `count`: Property to get the count of files.

2. **RodeDevice**
   - **Purpose**: Represents a RØDE Wireless GO device.
   - **Attributes**:
     - `serial`: Serial number of the device.
     - `mount_point`: Mount point of the device.
     - `name`: Name of the device.
     - `by_id_path`: Path to the device in `/dev/disk/by-id/`.

3. **AudioFile**
   - **Purpose**: Represents an audio file from a RØDE device.
   - **Methods**:
     - `size`: Returns the size of the file.
     - `best_date`: Returns the best date (modification or creation time) of the file.
     - `size_human`: Returns the size of the file in human-readable format.
     - `fingerprint`: Generates a quick fingerprint for the file.

#### Top-Level Functions

1. **quick_fingerprint**
   - **Purpose**: Generates a quick fingerprint for a file.
   - **Arguments**: `filepath` (Path), `file_size` (int).
   - **Logic**: Computes an MD5 hash of the file size and the first and last 64KB chunks of the file.

2. **load_config**
   - **Purpose**: Loads configuration data from a JSON file.
   - **Logic**: Reads the configuration file and returns the data as a dictionary.

3. **save_config**
   - **Purpose**: Saves configuration data to a JSON file.
   - **Arguments**: `cfg` (dict).
   - **Logic**: Writes the configuration data to the JSON file.

4. **find_rode_devices**
   - **Purpose**: Detects connected RØDE devices.
   - **Logic**: Scans `/dev/disk/by-id/` for devices with the RØDE prefix and returns a list of `RodeDevice` instances.

5. **scan_device**
   - **Purpose**: Scans a device for audio files.
   - **Arguments**: `dev` (RodeDevice).
   - **Logic**: Recursively scans the device's mount point for audio files and returns a list of `AudioFile` instances.

6. **do_transfer**
   - **Purpose**: Executes the file transfer process.
   - **Arguments**: `plan` (list), `dest` (Path), `manifest` (Manifest), `dry_run` (bool).
   - **Logic**: Transfers files from the plan to the destination directory, updating the manifest.

7. **main**
   - **Purpose**: Main entry point for the script.
   - **Logic**: Parses command-line arguments, detects devices, scans for files, and executes the transfer process.

#### Configuration and Environment
- **Config File**: `~/.config/rode-transfer/devices.json` stores device names and serials.
- **Environment Variables**: None used.

#### Integration Points
- **Mythos Subsystems**: Integrates with the Mythos system for file transfer and deduplication.
- **Console Output**: Uses `rich` for formatted console output, including banners, tables, and progress bars.

This detailed documentation provides a comprehensive overview of the `rode_transfer.py` script, its classes, functions, and integration points within the Mythos system.
