# telegram_bot/handlers/media_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 451

---

### File: `telegram_bot/handlers/media_handler.py`

#### Purpose
This file contains functions to handle media files (photos and videos) received via the Telegram bot. It includes downloading, saving, analyzing, and sending media-related data to other systems like Iris.

#### Architecture
The file consists of several top-level functions that handle different aspects of media processing:
- `get_db_conn`: Establishes a database connection.
- `get_user_uuid`: Retrieves a user UUID from a Telegram ID.
- `save_media_record`: Saves media file metadata to the database.
- `update_media_analysis`: Updates media analysis results in the database.
- `send_to_iris`: Sends a message to the Iris system via an API.
- `describe_image`: Uses LLAVA to analyze and describe an image.
- `extract_audio_from_video`: Extracts audio from a video file using `ffmpeg`.
- `get_video_duration`: Retrieves the duration of a video file.
- `handle_photo_media`: Handles photo media, including downloading, analysis, and sending to Iris.
- `handle_video_media`: Handles video media, including downloading, extracting audio, and sending to Iris.

#### Patterns
- **Singleton**: The database connection is established using a simple function (`get_db_conn`) which can be considered a singleton pattern for the connection.
- **Factory**: Functions like `describe_image` and `extract_audio_from_video` can be seen as factory methods for generating specific outputs (image descriptions and audio files).

#### Dependencies
- **Imports**: `os`, `json`, `time`, `logging`, `subprocess`, `httpx`, `psycopg2`, `dotenv`, `pathlib`, `typing`, `datetime`.
- **Environment Variables**: `API_URL`, `API_KEY_TELEGRAM_BOT`, `OLLAMA_VISION_MODEL`, `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`.

#### Interfaces
- **Exposed Functions**: `handle_photo_media`, `handle_video_media` are the main entry points for handling media.
- **Internal Functions**: `get_db_conn`, `get_user_uuid`, `save_media_record`, `update_media_analysis`, `send_to_iris`, `describe_image`, `extract_audio_from_video`, `get_video_duration`.

#### Database
- **Tables**: `users`, `media_files`.
- **Operations**: 
  - `users`: Query to retrieve `user_uuid` from `telegram_id`.
  - `media_files`: Insert and update operations for media records.

#### Configuration
- **Config Files**: `.env` file loaded using `dotenv`.
- **Environment Variables**: Used for API URLs, API keys, and database credentials.

#### Key Logic
- **Photo Handling**: Downloads the photo, saves it to disk, logs it in the database, analyzes the image using LLAVA, and sends the analysis to Iris.
- **Video Handling**: Downloads the video, extracts audio, transcribes the audio, and sends the transcript to Iris.

#### Integration Points
- **Iris API**: Sends media analysis results to Iris via HTTP POST requests.
- **LLAVA**: Uses LLAVA for image analysis.
- **FFmpeg**: Uses FFmpeg for audio extraction from video files.
- **PostgreSQL**: Stores media metadata and user information in the database.

### Detailed Function Descriptions

1. **`get_db_conn`**
   - **Purpose**: Establishes a connection to the PostgreSQL database.
   - **Dependencies**: `psycopg2`, environment variables for database credentials.
   - **Database**: Connects to the `mythos` database.

2. **`get_user_uuid`**
   - **Purpose**: Retrieves the user UUID from the `users` table based on the Telegram ID.
   - **Dependencies**: `get_db_conn`.
   - **Database**: Queries the `users` table.

3. **`save_media_record`**
   - **Purpose**: Saves media file metadata to the `media_files` table.
   - **Dependencies**: `get_db_conn`, `json`.
   - **Database**: Inserts a record into the `media_files` table.

4. **`update_media_analysis`**
   - **Purpose**: Updates the analysis results for a media file in the `media_files` table.
   - **Dependencies**: `get_db_conn`, `json`.
   - **Database**: Updates the `media_files` table.

5. **`send_to_iris`**
   - **Purpose**: Sends a message to the Iris system via an HTTP POST request.
   - **Dependencies**: `httpx`, environment variables for API URL and key.

6. **`describe_image`**
   - **Purpose**: Analyzes an image using LLAVA and returns a description.
   - **Dependencies**: `vision` module, `VISION_MODEL` environment variable.

7. **`extract_audio_from_video`**
   - **Purpose**: Extracts audio from a video file using FFmpeg.
   - **Dependencies**: `subprocess`.

8. **`get_video_duration`**
   - **Purpose**: Retrieves the duration of a video file using FFprobe.
   - **Dependencies**: `subprocess`.

9. **`handle_photo_media`**
   - **Purpose**: Handles photo media by downloading, analyzing, and sending to Iris.
   - **Dependencies**: `get_user_uuid`, `save_media_record`, `describe_image`, `update_media_analysis`, `send_to_iris`.
   - **Database**: Uses `save_media_record` and `update_media_analysis`.

10. **`handle_video_media`**
    - **Purpose**: Handles video media by downloading, extracting audio, and sending to Iris.
    - **Dependencies**: `get_user_uuid`, `save_media_record`, `extract_audio_from_video`, `send_to_iris`.
    - **Database**: Uses `save_media_record`.

This file serves as a crucial component in the Mythos system, handling the ingestion and analysis of media files received via the Telegram bot, and integrating with other systems like Iris for further processing.
