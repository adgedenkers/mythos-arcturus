# Voice Memo Pipeline

**Stream:** MNE
**Files:** 2

## Files in this Module

- `voice_memos/incoming/.rode-manifest.json` (4L)
- `voice_memos/incoming/.stfolder/syncthing-folder-992cf5.txt` (5L)

---

# Voice Memo Pipeline Module Documentation

## 1. Module Purpose
The Voice Memo Pipeline module manages the ingestion and synchronization of voice memo files into the Mythos system. It serves as the entry point for raw voice memo data, ensuring files are properly tracked and synchronized across devices before being processed by downstream systems. The module focuses on file tracking, synchronization coordination, and metadata management for incoming voice memos.

## 2. Architecture Overview
The architecture consists of two core components working in tandem:
- **Syncthing Integration**: Manages cross-device synchronization of voice memo files
- **Manifest Tracking System**: Maintains metadata about incoming files using a JSON manifest

Data flow:
1. Voice memos are deposited into the `voice_memos/incoming` directory
2. Syncthing synchronizes files across devices using the folder marker file
3. The manifest file tracks file metadata and versioning
4. Processing systems monitor the manifest to detect new/changed files
5. Processed files are moved to archival storage (not shown in current implementation)

## 3. Key Components
### 3.1 Syncthing Folder Marker
- **File**: `.stfolder/syncthing-folder-992cf5.txt`
- **Role**: Identifies the directory as a Syncthing synchronization folder
- **Properties**:
  - `folderID`: Unique identifier for the Syncthing folder (`v5gm9-jjumm`)
  - `created`: Timestamp of folder creation (`2026-02-22T17:07:29-05:00`)

### 3.2 Manifest File
- **File**: `.rode-manifest.json`
- **Role**: Tracks file metadata and versioning information
- **Structure**:
  ```json
  {
    "version": 1,
    "files": {}
  }
  ```
- **Evolution**: The manifest schema is versioned to support future enhancements

## 4. Design Patterns
- **Manifest Pattern**: Uses a versioned JSON manifest to track file metadata
- **Synchronization Marker**: Simple text file pattern for identifying sync folders
- **Passive Configuration**: All components are static configuration files with no active processing logic

## 5. Data Model
### Manifest Schema
```json
{
  "version": Integer,
  "files": {
    "filename": {
      "mtime": ISO8601Timestamp,
      "size": Integer,
      "checksum": String
    }
  }
}
```

### Syncthing Folder Metadata
```text
folderID: v5gm9-jjumm
created: 2026-02-22T17:07:29-05:00
```

## 6. API Surface
This module does not expose direct APIs but provides integration points:
- **File System Interface**: Voice memos are deposited into `voice_memos/incoming/`
- **Manifest Reader Interface**: Processing systems read `.rode-manifest.json` to detect changes
- **Syncthing Integration**: Folder marker enables synchronization with Syncthing service

## 7. Dependencies
- **Syncthing Service**: Required for cross-device file synchronization
- **File System**: Relies on standard file system operations for file storage
- **Processing Pipeline**: Depends on downstream systems to monitor and process files from the manifest

## 8. Configuration
### Syncthing Configuration
1. Create folder marker file with unique ID
2. Configure Syncthing to recognize the folder ID and path
3. Set up devices/folders in Syncthing configuration

### Manifest Configuration
1. Create `.rode-manifest.json` with initial version
2. Maintain manifest schema version during system upgrades
3. Update manifest when new files are added/modified

### Example Configuration
```json
// .rode-manifest.json
{
  "version": 1,
  "files": {
    "20260301-voice-memo-001.wav": {
      "mtime": "2026-03-01T10:00:00Z",
      "size": 1234567,
      "checksum": "sha256:abcdef1234567890..."
    }
  }
}
```

```text
// .stfolder/syncthing-folder-992cf5.txt
folderID: v5gm9-jjumm
created: 2026-02-22T17:07:29-05:00
```

## Implementation Notes
- Current implementation is minimal (manifest is empty)
- Future enhancements should include:
  - Automatic manifest updates when files are added/modified
  - Conflict resolution for synchronized files
  - Versioning support for file changes
  - Integration with media processing pipeline

This module forms the foundational layer for voice memo ingestion in the Mythos system, ensuring reliable file synchronization and metadata tracking before processing.
