# services/voice_watcher.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 206

---

### Documentation for `voice_watcher.py`

#### Purpose
The `voice_watcher.py` script monitors the `/opt/mythos/voice_memos/incoming/` directory for new audio files. When a new file is detected, it dispatches a transcription task to a Redis stream, ensuring the file is stable and not already dispatched.

#### Architecture
The script is structured around a single class, `VoiceWatcher`, which encapsulates the logic for monitoring the directory and dispatching transcription tasks. The class contains several methods for checking file stability, dispatching tasks, and scanning the directory.

- **`__init__`**: Initializes the `VoiceWatcher` instance, setting up the Redis connection and ensuring the watch directory exists.
- **`_is_audio_file`**: Checks if a file has a supported audio extension.
- **`_is_already_dispatched`**: Verifies if a file has already been dispatched by checking Redis.
- **`_mark_dispatched`**: Marks a file as dispatched in Redis.
- **`_is_file_stable`**: Ensures a file has finished writing by checking its size stability.
- **`dispatch_transcription`**: Pushes a transcription task to the Redis stream.
- **`scan`**: Scans the directory for new audio files and dispatches them if they are stable and not already dispatched.
- **`run`**: The main watch loop that periodically scans the directory.
- **`_shutdown`**: Handles shutdown signals to gracefully stop the watcher.

#### Patterns
- **Singleton Pattern**: The `VoiceWatcher` class can be considered a singleton in the context of this script, as it is instantiated once and runs continuously.
- **Observer Pattern**: The script observes changes in the directory and reacts by dispatching transcription tasks.

#### Dependencies
- **Imports**: `os`, `sys`, `json`, `time`, `signal`, `logging`, `hashlib`, `redis`, `pathlib`, `datetime`, `dotenv`
- **Redis**: Used for tracking dispatched files and pushing transcription tasks to a stream.
- **Environment Variables**: `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `TELEGRAM_ADMIN_CHAT_ID`

#### Interfaces
- **Public Methods**: `run()`, `scan()`, `dispatch_transcription(filepath)`
- **Signals**: Handles `SIGTERM` and `SIGINT` to gracefully shut down.

#### Database
- **Redis**: 
  - **Key**: `mythos:voice_memos:dispatched` — Set of dispatched files.
  - **Stream**: `mythos:assignments:transcription` — Stream for transcription tasks.

#### Configuration
- **Environment Variables**: 
  - `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `TELEGRAM_ADMIN_CHAT_ID`
- **Constants**: 
  - `WATCH_DIR`, `AUDIO_EXTENSIONS`, `STREAM`, `POLL_INTERVAL`, `STABLE_WAIT`

#### Key Logic
- **File Stability Check**: Ensures a file is no longer being written to by comparing its size over time.
- **Dispatching Transcription Tasks**: Pushes tasks to a Redis stream with details about the file and dispatch time.
- **Deduplication**: Uses Redis to track dispatched files and avoid reprocessing.

#### Integration Points
- **Redis**: For tracking dispatched files and pushing transcription tasks.
- **File System**: Monitors `/opt/mythos/voice_memos/incoming/` for new audio files.
- **Logging**: Uses Python's `logging` module to log events and errors.

### Summary
The `voice_watcher.py` script is a critical component of the Mythos system, responsible for monitoring a directory for new audio files and dispatching transcription tasks to a Redis stream. It ensures file stability and deduplication using Redis, and it gracefully handles shutdowns and errors.
