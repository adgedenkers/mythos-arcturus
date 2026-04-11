# photos/google_ingest.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 268

---

### File: `photos/google_ingest.py`

#### Purpose
This file implements a pipeline for ingesting Google Photos Takeout zip files into the Mythos system. It extracts the zip files, recovers timestamps from JSON sidecar files, corrects EXIF timestamps, deduplicates against the existing library, and moves the processed files to an import directory watched by Immich.

#### Architecture
The file consists of several top-level functions that handle different stages of the ingestion process:
- `log`: Logging utility function.
- `file_hash`: Computes the SHA256 hash of a file.
- `build_library_hash_set`: Builds a set of hashes for existing files in the Immich library.
- `extract_zips`: Extracts zip files from a specified directory.
- `find_sidecar`: Finds the JSON sidecar file associated with a photo.
- `get_timestamp_from_sidecar`: Extracts the timestamp from a JSON sidecar file.
- `fix_exif_timestamp`: Uses `exiftool` to update the EXIF timestamp of a photo.
- `ingest`: Main function that orchestrates the entire ingestion process.

#### Patterns
- **Singleton**: The `log` function acts as a singleton for logging throughout the script.
- **Factory**: The `file_hash` function can be seen as a factory for generating file hashes.

#### Dependencies
- `os`, `sys`, `json`, `shutil`, `hashlib`, `zipfile`, `argparse`, `subprocess`: Standard Python libraries for file operations, JSON handling, hashing, zip file extraction, argument parsing, and subprocess execution.
- `Path` from `pathlib`: For path manipulations.
- `datetime`, `timezone` from `datetime`: For timestamp handling.

#### Interfaces
- **Exposed Functions**: 
  - `log(msg, level)`: Logging utility.
  - `file_hash(path, chunk_size)`: Computes the hash of a file.
  - `build_library_hash_set()`: Builds a set of hashes for existing library files.
  - `extract_zips(zip_dir)`: Extracts zip files.
  - `find_sidecar(photo_path)`: Finds the JSON sidecar file.
  - `get_timestamp_from_sidecar(sidecar_path)`: Extracts timestamp from a sidecar file.
  - `fix_exif_timestamp(photo_path, dt, dry_run)`: Fixes EXIF timestamp.
  - `ingest(zip_dir, already_extracted, dry_run)`: Main ingestion function.

#### Database
- **PostgreSQL Tables**: 
  - `EXIF`: Used for storing EXIF metadata.
  - `pathlib`: Not a table, but used for path manipulations.
  - `datetime`: Not a table, but used for timestamp manipulations.

#### Configuration
- **Environment Variables**: None.
- **Configuration Files**: None.
- **Constants**: 
  - `EXTRACT_DIR`, `STAGING_DIR`, `IMPORT_DIR`, `LIBRARY_DIR`, `LOG_FILE`: Paths for directories and log file.
  - `SUPPORTED_EXTENSIONS`: Set of supported file extensions.

#### Key Logic
1. **Extraction**: Extracts all zip files from the specified directory.
2. **Timestamp Recovery**: Uses JSON sidecar files to recover original timestamps.
3. **Deduplication**: Computes SHA256 hashes to avoid importing duplicate files.
4. **EXIF Correction**: Updates EXIF metadata with the correct timestamps.
5. **Import**: Moves processed files to the Immich import directory.

#### Integration Points
- **Immich**: The processed files are moved to the `IMPORT_DIR`, which is watched by Immich for new files.
- **Exiftool**: Used to update EXIF metadata.
- **Logging**: Logs are written to `LOG_FILE` for monitoring and debugging.

### Summary
The `google_ingest.py` script is a comprehensive pipeline for processing Google Photos Takeout zip files. It handles extraction, timestamp recovery, deduplication, EXIF correction, and importing into the Immich system. The script is designed to be robust, logging all actions and handling errors gracefully.
