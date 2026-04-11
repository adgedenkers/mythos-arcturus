# api/routes/voice.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 317

---

### File: api/routes/voice.py

#### Purpose
This file defines the API endpoints for handling voice memos, including uploading, checking status, listing recent memos, and retrieving transcripts. It uses FastAPI to define the routes and interacts with a PostgreSQL database to store and retrieve memo information.

#### Architecture
The file is structured around several key components:
1. **Response Models**: `UploadResponse`, `MemoStatus`, and `MemoTranscript` are Pydantic models that define the structure of the responses for different API endpoints.
2. **Utility Functions**: `get_db_conn` and `verify_api_key` are utility functions used across multiple routes.
3. **Routes**: The main routes are defined using FastAPI decorators (`@router.post`, `@router.get`), each handling a specific operation related to voice memos.

#### Patterns
- **Factory Pattern**: `get_db_conn` acts as a factory method to create and return a database connection.
- **Singleton Pattern**: The database connection is managed within the function, ensuring a consistent connection for each request.
- **Observer Pattern**: The file watcher pattern is implied where uploaded files are picked up and processed by a separate worker.

#### Dependencies
- **Standard Libraries**: `os`, `json`, `logging`, `datetime`, `pathlib`, `typing`
- **External Libraries**: `psycopg2`, `dotenv`, `fastapi`, `pydantic`

#### Interfaces
- **API Routes**:
  - `POST /api/voice/upload`: Uploads a voice memo.
  - `GET /api/voice/status/{memo_id}`: Retrieves the status of a voice memo.
  - `GET /api/voice/list`: Lists recent voice memos.
  - `GET /api/voice/transcript/{memo_id}`: Retrieves the full transcript of a voice memo.

#### Database
- **Tables**: The file interacts with the `voice_memos` table in the PostgreSQL database.
- **Operations**:
  - `upload_voice_memo`: No direct database write, but the file is saved to disk.
  - `get_memo_status`: Reads from `voice_memos` to get the status of a memo.
  - `list_voice_memos`: Reads from `voice_memos` to list recent memos.
  - `get_transcript`: Reads from `voice_memos` to get the full transcript of a memo.

#### Configuration
- **Environment Variables**: The file reads configuration from environment variables using `dotenv`:
  - `API_KEY_TELEGRAM_BOT`, `API_KEY_KA`, `API_KEY_SERAPHE` for API keys.
  - `TELEGRAM_ADMIN_CHAT_ID` for admin chat ID.
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` for database connection.

#### Key Logic
- **Upload Logic**:
  - Validates the file extension and size.
  - Generates a unique filename and saves the file to the incoming directory.
  - Returns a response indicating the memo is queued for transcription.
- **Status and List Logic**:
  - Queries the `voice_memos` table to retrieve status and list recent memos.
- **Transcript Logic**:
  - Queries the `voice_memos` table to retrieve the full transcript of a memo.

#### Integration Points
- **File System**: The file is saved to the incoming directory (`/opt/mythos/voice_memos/incoming`), where a file watcher picks it up and dispatches to a transcription worker.
- **Database**: The file interacts with the PostgreSQL database to store and retrieve memo information.
- **API Key Verification**: Uses a set of valid API keys to authenticate requests.

### Summary
This file is a crucial component of the Mythos system, providing the API endpoints for managing voice memos. It handles file uploads, status checks, and transcript retrieval, leveraging FastAPI for routing and Pydantic for response models. The file integrates with the PostgreSQL database and the file system, ensuring robust and secure handling of voice memos.
