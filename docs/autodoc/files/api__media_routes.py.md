# api/media_routes.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 457

---

### File: `api/media_routes.py`

#### Purpose
This file contains the implementation of media-related endpoints for the Mythos system, including uploading media, retrieving recent photos, and adding tags to media files.

#### Architecture
The file is structured around several Pydantic models and FastAPI routes. It defines the following Pydantic models:
- `MediaUploadRequest`: Represents the request payload for uploading media.
- `MediaUploadResponse`: Represents the response payload for media upload.
- `PhotoSummary`: Represents a summary of a photo.
- `RecentPhotosResponse`: Represents a list of recent photos.
- `AddTagRequest`: Represents the request payload for adding a tag to a photo.

The file also contains several top-level functions:
- `get_recent_conversation_with_media`: Retrieves recent messages and photos for a given user and conversation.
- `setup_media_routes`: Registers all media-related routes with the FastAPI application.
- `upload_media`: Handles the upload of media files.
- `get_recent_photos`: Retrieves recent photos for a user.
- `get_media_by_id`: Retrieves detailed information about a specific media file.
- `search_photos_by_tag`: Searches photos by a given tag.
- `add_user_tag`: Adds a user tag to a photo.

#### Patterns
- **Factory Pattern**: Not explicitly used, but the `MediaUploadRequest` and other Pydantic models can be considered as factory classes for creating structured data.
- **Dependency Injection**: The `setup_media_routes` function uses dependency injection to pass required dependencies like `get_db_connection` and `verify_api_key`.

#### Dependencies
- `psycopg2`: Used for database operations.
- `pydantic`: Used for defining Pydantic models.
- `fastapi`: Used for defining FastAPI routes.
- `pathlib`: Used for file path operations.

#### Interfaces
The file exposes the following FastAPI routes:
- `POST /media/upload`: Uploads a media file.
- `GET /media/recent`: Retrieves recent photos for a user.
- `GET /media/{media_id}`: Retrieves detailed information about a specific media file.
- `GET /media/search/tag/{tag}`: Searches photos by a given tag.
- `POST /media/tag/add`: Adds a user tag to a photo.

#### Database
The file interacts with the following PostgreSQL tables:
- `media_files`: Stores metadata about media files.
- `chat_messages`: Stores chat messages.
- `users`: Stores user information.

#### Configuration
The file does not explicitly use any configuration files or environment variables, but it relies on the `get_db_connection` and `verify_api_key` functions, which are assumed to be configured elsewhere in the system.

#### Key Logic
- **Media Upload**: The `upload_media` function handles the upload of media files, storing metadata in the `media_files` table and optionally creating a chat message for captions.
- **Recent Photos Retrieval**: The `get_recent_photos` function retrieves recent photos for a user from the `media_files` table.
- **Media Detail Retrieval**: The `get_media_by_id` function retrieves detailed information about a specific media file from the `media_files` and `users` tables.
- **Tagging**: The `add_user_tag` function adds a user tag to a photo in the `media_files` table.

#### Integration Points
The file integrates with other parts of the Mythos system through:
- **Database Connection**: Uses `get_db_connection` to interact with the PostgreSQL database.
- **User Verification**: Uses `verify_api_key` to verify API keys.
- **User Retrieval**: Uses `get_user_by_identifier` to retrieve user information.

### Detailed Documentation

#### Classes
- **MediaUploadRequest**: Represents the request payload for uploading media.
- **MediaUploadResponse**: Represents the response payload for media upload.
- **PhotoSummary**: Represents a summary of a photo.
- **RecentPhotosResponse**: Represents a list of recent photos.
- **AddTagRequest**: Represents the request payload for adding a tag to a photo.

#### Functions
- **get_recent_conversation_with_media**: Retrieves recent messages and photos for a given user and conversation.
- **setup_media_routes**: Registers all media-related routes with the FastAPI application.
- **upload_media**: Handles the upload of media files.
- **get_recent_photos**: Retrieves recent photos for a user.
- **get_media_by_id**: Retrieves detailed information about a specific media file.
- **search_photos_by_tag**: Searches photos by a given tag.
- **add_user_tag**: Adds a user tag to a photo.

#### FastAPI Routes
- `POST /media/upload`: Uploads a media file.
- `GET /media/recent`: Retrieves recent photos for a user.
- `GET /media/{media_id}`: Retrieves detailed information about a specific media file.
- `GET /media/search/tag/{tag}`: Searches photos by a given tag.
- `POST /media/tag/add`: Adds a user tag to a photo.

#### Database Tables
- `media_files`: Stores metadata about media files.
- `chat_messages`: Stores chat messages.
- `users`: Stores user information.
