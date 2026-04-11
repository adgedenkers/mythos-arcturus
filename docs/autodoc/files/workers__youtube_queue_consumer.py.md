# workers/youtube_queue_consumer.py

**Language:** python
**Stream:** SYS
**Module:** Background Workers
**Lines:** 381

---

### File: workers/youtube_queue_consumer.py

#### Purpose
This file contains the main logic for consuming and processing videos from a Redis queue, specifically for the YouTube channel skill in the Mythos system. It handles fetching video transcripts, storing them in a PostgreSQL database, and managing backoff logic for failed video processing attempts.

#### Architecture
The file consists of several helper functions and a main consumer loop (`run_consumer`). The helper functions manage Redis operations, error logging, status tracking, and database interactions. The main loop (`run_consumer`) orchestrates the fetching and processing of videos from the queue.

#### Patterns
- **Singleton**: The Redis connection is created once and reused.
- **Helper Functions**: Functions like `_get_failed_info`, `_set_failed_info`, `_log_error`, and `_increment_status` encapsulate specific functionalities.
- **Error Handling**: The `process_video` function raises exceptions on failure, which are then handled by the main loop to manage backoff logic.

#### Dependencies
- **Imports**: `json`, `logging`, `os`, `time`, `redis`, `psycopg2`
- **External Services**: Redis, PostgreSQL

#### Interfaces
- **Public Functions**:
  - `get_queue_status()`: Returns the current status of the YouTube queue.
  - `run_consumer(redis_url, poll_interval)`: Main consumer loop that processes videos from the queue.

#### Database
- **PostgreSQL Tables**:
  - `youtube_videos`: Stores video metadata and transcript.
  - `failure`: Tracks failed video processing attempts.
  - `channel`: Stores channel information.
  - `score`: Tracks scoring information.
  - `backoff`: Tracks backoff information for failed videos.

#### Configuration
- **Environment Variables**:
  - `YT_PROCESS_INTERVAL`: Throttle interval between processing videos.
  - `MYTHOS_DB_URL`: Database connection string for PostgreSQL.

#### Key Logic
- **Backoff Logic**:
  - `_get_failed_info`: Retrieves failure information for a video.
  - `_set_failed_info`: Records or updates failure information for a video.
  - `is_backoff_active`: Determines if a video should be skipped due to backoff.
- **Queue Management**:
  - `_peek_next`: Peeks at the highest-priority video in the queue.
  - `_pop_video`: Removes a video from the queue and retrieves its metadata.
- **Processing**:
  - `process_video`: Fetches and processes a video transcript, storing it in the PostgreSQL database.
- **Status Tracking**:
  - `get_queue_status`: Retrieves and returns the current status of the queue.

#### Integration Points
- **Redis**:
  - Manages the YouTube queue and metadata using Redis sorted sets and hash tables.
- **PostgreSQL**:
  - Stores processed video data in the `youtube_videos` table.
- **Logging**:
  - Logs errors and status updates using the `logging` module.
- **Other Components**:
  - Integrates with the `skills.data.youtube_intake` module for fetching transcripts.

### Detailed Function Descriptions

1. **_get_failed_info**
   - **Purpose**: Retrieves stored failure information for a video.
   - **Parameters**: `r` (Redis connection), `video_id`
   - **Returns**: Dictionary containing failure info or `None`.

2. **_set_failed_info**
   - **Purpose**: Records or updates failure information for a video.
   - **Parameters**: `r` (Redis connection), `video_id`, `attempt_count`, `last_error`
   - **Returns**: None

3. **is_backoff_active**
   - **Purpose**: Determines if a video should be skipped due to backoff.
   - **Parameters**: `r` (Redis connection), `video_id`
   - **Returns**: Boolean indicating if backoff is active.

4. **_log_error**
   - **Purpose**: Logs an error for a video.
   - **Parameters**: `r` (Redis connection), `video_id`, `error`, `title`
   - **Returns**: None

5. **_increment_status**
   - **Purpose**: Increments status counters in Redis.
   - **Parameters**: `r` (Redis connection), `field`, `amount`
   - **Returns**: None

6. **get_queue_status**
   - **Purpose**: Retrieves the current status of the queue.
   - **Parameters**: None
   - **Returns**: Dictionary containing queue status information.

7. **_resolve_channel_name**
   - **Purpose**: Resolves a channel ID to a human-readable name.
   - **Parameters**: `r` (Redis connection), `channel_id`
   - **Returns**: Channel name or `Unknown`.

8. **_peek_next**
   - **Purpose**: Peeks at the highest-priority video in the queue.
   - **Parameters**: `r` (Redis connection)
   - **Returns**: Video ID or `None`.

9. **_pop_video**
   - **Purpose**: Removes a video from the queue and retrieves its metadata.
   - **Parameters**: `r` (Redis connection), `video_id`
   - **Returns**: Metadata dictionary or `None`.

10. **process_video**
    - **Purpose**: Fetches and processes a video transcript, storing it in the PostgreSQL database.
    - **Parameters**: `r` (Redis connection), `video_id`, `meta`
    - **Returns**: None
    - **Raises**: `RuntimeError` on failure.

11. **_resolve_channel_name_static**
    - **Purpose**: Resolves a channel ID to a human-readable name without a pre-existing Redis connection.
    - **Parameters**: `channel_id`
    - **Returns**: Channel name or `None`.

12. **run_consumer**
    - **Purpose**: Main consumer loop that processes videos from the queue.
    - **Parameters**: `redis_url`, `poll_interval`
    - **Returns**: None

### Example Usage
```python
# Start the consumer loop
run_consumer(redis_url='redis://localhost:6379/0', poll_interval=10.0)

# Get current queue status
status = get_queue_status()
print(status)
```

This file is critical for the Mythos system's YouTube channel skill, ensuring that videos are processed efficiently and failures are managed appropriately.
