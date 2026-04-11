# workers/transcription_worker.py

**Language:** python
**Stream:** SYS
**Module:** Background Workers
**Lines:** 340

---

### Documentation for `workers/transcription_worker.py`

#### Purpose
The `transcription_worker.py` file is responsible for processing voice memo transcription assignments from a Redis stream. It handles the entire workflow from receiving the assignment to saving the transcription result in the database and sending notifications.

#### Architecture
The file is structured around several top-level functions that handle specific tasks:
- `get_transcription_service`: Lazy-loads the transcription service.
- `get_db_conn`: Establishes a database connection.
- `send_telegram_notification`: Sends a Telegram notification.
- `create_memo_record`: Creates a new voice memo record in the database.
- `save_transcription_result`: Saves the transcription result to the database.
- `update_memo_status`: Updates the status of a voice memo in the database.
- `process_transcription`: The main handler for transcription assignments.

#### Patterns
- **Lazy Initialization**: The `get_transcription_service` function uses lazy initialization to load the transcription service only when needed.
- **Singleton**: The transcription service is a singleton, ensuring only one instance is created.

#### Dependencies
- **Standard Libraries**: `os`, `sys`, `json`, `logging`, `time`, `datetime`, `pathlib`, `typing`, `shutil`
- **External Libraries**: `psycopg2`, `httpx`, `dotenv`

#### Interfaces
- **Functions Exposed**: 
  - `get_transcription_service()`
  - `get_db_conn()`
  - `send_telegram_notification(chat_id, text)`
  - `create_memo_record(file_path, filename, source, file_size)`
  - `save_transcription_result(memo_id, result)`
  - `update_memo_status(memo_id, status, error=None)`
  - `process_transcription(payload)`

#### Database
- **Tables/Labels**:
  - `voice_memos`: For storing voice memo records.
  - `voice_memo_segments`: For storing individual segments of the transcription.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: For database connection.
  - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ADMIN_CHAT_ID`: For Telegram notifications.

#### Key Logic
- **Main Workflow**:
  1. **Receive Assignment**: The `process_transcription` function is called with a payload containing the file path and other metadata.
  2. **File Handling**: Moves the file to a processing directory.
  3. **Database Record**: Creates a new record in the `voice_memos` table if one does not already exist.
  4. **Transcription**: Uses the lazy-loaded transcription service to transcribe the audio file.
  5. **Save Result**: Saves the transcription result to the `voice_memos` and `voice_memo_segments` tables.
  6. **Notification**: Sends a Telegram notification on completion or failure.
  7. **Archive**: Moves the processed file to an archive directory.

#### Integration Points
- **Redis Stream**: Receives transcription assignments from a Redis stream.
- **Database**: Interacts with PostgreSQL to create, update, and query voice memo records.
- **Telegram**: Sends notifications using the Telegram API.
- **Worker Framework**: Integrates with the Mythos worker framework, which calls the `process_transcription` function.

### Summary
The `transcription_worker.py` file is a crucial component of the Mythos system, responsible for handling the transcription of voice memos. It manages the entire workflow from receiving assignments to saving results and sending notifications, leveraging lazy initialization and database interactions to ensure efficient and reliable processing.
