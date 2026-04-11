# assets/asset_store.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 44

---

### File: assets/asset_store.py

#### Purpose
This file contains functions to manage assets, specifically images, by ensuring they are stored in a central asset store with a unique identifier based on their SHA-256 hash.

#### Architecture
- **Functions**:
  - `sha256_file`: Computes the SHA-256 hash of a file.
  - `ensure_asset`: Ensures an image is copied into the central asset store if it is not already present, and returns metadata about the asset.

#### Patterns
- **None**: The file does not use any specific design patterns like factory, singleton, or observer.

#### Dependencies
- **Imports**:
  - `hashlib`: For computing the SHA-256 hash.
  - `os`: For file operations.
  - `shutil`: For copying files.
  - `pathlib`: For handling file paths.

#### Interfaces
- **Public Functions**:
  - `sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str`: Computes the SHA-256 hash of a file.
  - `ensure_asset(image_path: Path) -> dict`: Ensures an image is copied into the central asset store and returns metadata about the asset.

#### Database
- **References**:
  - `pathlib`: Not a database table but a module used for path operations.
  - `central`: Not a database table but refers to the central asset store.

#### Configuration
- **Environment Variables**: None.
- **Config Files**: None.

#### Key Logic
- **sha256_file**:
  - Opens the file in binary mode and reads it in chunks.
  - Updates the SHA-256 hash object with each chunk.
  - Returns the hexadecimal representation of the hash.

- **ensure_asset**:
  - Checks if the image file exists.
  - Computes the SHA-256 hash of the image.
  - Determines the file extension and creates a directory structure based on the hash.
  - Copies the image to the central asset store if it does not already exist.
  - Returns a dictionary containing the hash, relative path, byte size, and file extension of the asset.

#### Integration Points
- **Mythos Subsystems**:
  - **Central Asset Store**: The `ensure_asset` function interacts with the central asset store to ensure images are stored uniquely based on their hash.
  - **PostgreSQL**: The file references `pathlib` and `central`, which might be used to store metadata in a PostgreSQL database, though no direct database operations are performed in this file.

### Summary
The `asset_store.py` file is responsible for managing assets, specifically images, by ensuring they are stored in a central asset store with a unique identifier based on their SHA-256 hash. It provides two main functions: `sha256_file` for computing the hash and `ensure_asset` for ensuring the asset is stored and returning its metadata. The file integrates with the central asset store and might be used in conjunction with a PostgreSQL database for metadata storage.
