# telegram_bot/handlers/voice_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 324

---

### File: `telegram_bot/handlers/voice_handler.py`

#### Purpose
This file handles voice messages and audio files received from the Telegram bot. It processes these files by downloading them, saving them to disk, transcribing them, and sending the transcript to the Iris system for further processing.

#### Architecture
The file consists of several functions that handle different aspects of the voice and audio message processing pipeline:
- `get_transcription_service`: Lazy loads the transcription service.
- `get_db_conn`: Establishes a connection to the PostgreSQL database.
- `get_user_uuid`: Retrieves the user UUID from the database based on the Telegram ID.
- `save_media_record`: Saves media file metadata to the database.
- `handle_voice`: Processes voice messages, including downloading, saving, transcribing, and sending the transcript to Iris.
- `handle_audio`: Processes audio files similarly to `handle_voice`.

#### Patterns
- **Lazy Loading**: The transcription service is lazily loaded to avoid unnecessary initialization overhead.
- **Singleton**: The transcription service is a singleton, ensuring only one instance is created and reused.

#### Dependencies
- **Standard Libraries**: `os`, `json`, `time`, `logging`, `datetime`, `pathlib`, `typing`
- **External Libraries**: `httpx`, `psycopg2`, `dotenv`
- **Internal Services**: `services.transcription.TranscriptionService`

#### Interfaces
- **Functions**:
  - `get_transcription_service()`: Returns the transcription service instance.
  - `get_db_conn()`: Returns a PostgreSQL database connection.
  - `get_user_uuid(telegram_id: int)`: Returns the user UUID for a given Telegram ID.
  - `save_media_record(...)`: Saves a media file record to the database.
  - `handle_voice(update, context)`: Handles incoming voice messages.
  - `handle_audio(update, context)`: Handles incoming audio files.

#### Database
- **Tables**:
  - `users`: Stores user information including `telegram_id` and `user_uuid`.
  - `media_files`: Stores metadata for media files including `user_uuid`, `filename`, `file_path`, `file_size_bytes`, `mime_type`, `media_type`, `telegram_file_id`, `telegram_file_unique_id`, `extracted_text`, `processed`, `processed_at`, `analysis_data`.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: PostgreSQL database connection details.
  - `API_URL`: URL for the Iris API.
  - `API_KEY_TELEGRAM_BOT`: API key for the Telegram bot.

#### Key Logic
1. **Voice/Audio Handling**:
   - Downloads the file from Telegram.
   - Saves the file to disk with a timestamped filename.
   - Saves metadata to the `media_files` table.
   - Transcribes the audio file using the `TranscriptionService`.
   - Updates the `media_files` table with the transcription result.
   - Sends the transcript to the Iris system via an API call.
   - Responds to the user with the transcript and Iris's response.

2. **Lazy Loading**:
   - The transcription service is lazily loaded to ensure it is only initialized when needed.

3. **Error Handling**:
   - Logs errors and sends appropriate error messages to the user.

#### Integration Points
- **Telegram Bot API**: Downloads files and sends messages.
- **PostgreSQL Database**: Stores user and media file metadata.
- **Transcription Service**: Transcribes audio files.
- **Iris API**: Sends the transcript for further processing.

### Summary
This file is a crucial part of the Mythos system, handling the end-to-end processing of voice and audio messages from Telegram. It integrates with the Telegram bot API, PostgreSQL database, transcription service, and Iris API to provide a seamless experience for users.
