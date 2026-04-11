# workers/youtube_channel_monitor.py

**Language:** python
**Stream:** SYS
**Module:** Background Workers
**Lines:** 464

---

### File: workers/youtube_channel_monitor.py

#### Purpose
This file contains functions to monitor YouTube channels for new videos, enqueue them for processing, and manage channel subscriptions. It integrates with Redis for queue management and PostgreSQL for persistent storage.

#### Architecture
The file consists of several top-level functions that handle different aspects of YouTube channel monitoring and subscription management. Functions are organized into logical sections such as backoff checks, already-processed checks, enqueuing, subscription management, and RSS polling. Each function performs a specific task and interacts with Redis and PostgreSQL as needed.

#### Patterns
- **Singleton Pattern**: The `_get_redis` function ensures a single Redis connection is used throughout the file.
- **Factory Method Pattern**: The `_resolve_channel_id` function acts as a factory method to resolve a YouTube handle or URL to a channel ID.

#### Dependencies
- **Standard Libraries**: `json`, `logging`, `os`, `re`, `time`
- **External Libraries**: `redis`, `feedparser`, `psycopg2`, `subprocess`, `requests`

#### Interfaces
- **Public Functions**:
  - `enqueue_video`: Adds a video to the processing queue.
  - `subscribe_channel`: Subscribes to a YouTube channel for automatic transcript capture.
  - `unsubscribe_channel`: Unsubscribes from a YouTube channel.
  - `list_subscriptions`: Returns all channel subscriptions with stats.
  - `run_monitor`: Main monitor loop that polls all subscribed channels on a schedule.

- **Private Functions**:
  - `_get_redis`: Returns a Redis connection.
  - `_is_backoff_active`: Checks if a video should be enqueued.
  - `_is_already_processed`: Checks if a video is already processed.
  - `_resolve_channel_id`: Resolves a YouTube handle or URL to a channel ID.
  - `_load_channel_list`: Loads the channel list from Redis.
  - `_save_channel_list`: Saves the channel list to Redis.
  - `_load_subscribed_channels`: Loads active channels from Redis.
  - `_notify_new_videos`: Sends a notification about newly queued videos.
  - `_clean`: Cleans datetime objects for JSON serialization.

#### Database
- **Redis**:
  - Keys: `mythos:youtube:queue`, `mythos:youtube:queue:meta:<video_id>`, `mythos:youtube:failed`, `mythos:youtube:channels`
- **PostgreSQL**:
  - Tables: `youtube_videos`

#### Configuration
- **Environment Variables**:
  - `MYTHOS_DB_URL`: Database URL for PostgreSQL.
  - `redis_url`: URL for Redis connection.

#### Key Logic
- **Enqueue Logic**: The `enqueue_video` function checks if a video is already in the queue, is already processed, or is in backoff before enqueuing it.
- **Subscription Management**: Functions like `subscribe_channel`, `unsubscribe_channel`, and `list_subscriptions` manage the subscription list in Redis and PostgreSQL.
- **RSS Polling**: The `poll_channel` function fetches the RSS feed for a channel and enqueues new videos.

#### Integration Points
- **Redis**: Used for queue management and storing channel subscriptions.
- **PostgreSQL**: Used for storing processed videos and enriching subscription stats.
- **yt-dlp**: Used for resolving YouTube channel IDs.
- **Telegram**: Used for sending notifications about newly queued videos.

### Detailed Documentation

#### `_get_redis`
- **Purpose**: Returns a Redis connection.
- **Dependencies**: `redis`
- **Logic**: Uses `redis.from_url` to connect to Redis.

#### `_is_backoff_active`
- **Purpose**: Checks if a video should be enqueued based on backoff rules.
- **Dependencies**: `redis`, `json`, `time`
- **Logic**: Checks the `mythos:youtube:failed` key in Redis to see if the video is in backoff.

#### `_is_already_processed`
- **Purpose**: Checks if a video is already processed in the `youtube_videos` table.
- **Dependencies**: `psycopg2`, `os`
- **Logic**: Queries the `youtube_videos` table to check if the video exists.

#### `enqueue_video`
- **Purpose**: Adds a video to the processing queue.
- **Dependencies**: `redis`, `json`, `time`, `datetime`
- **Logic**: Checks backoff, already processed, and queue status before enqueuing the video.

#### `_resolve_channel_id`
- **Purpose**: Resolves a YouTube handle or URL to a channel ID.
- **Dependencies**: `subprocess`, `re`
- **Logic**: Uses `yt-dlp` to extract channel information.

#### `subscribe_channel`
- **Purpose**: Subscribes to a YouTube channel for automatic transcript capture.
- **Dependencies**: `redis`, `json`, `datetime`
- **Logic**: Resolves the channel ID, checks if already subscribed, and saves the subscription to Redis.

#### `unsubscribe_channel`
- **Purpose**: Unsubscribes from a YouTube channel.
- **Dependencies**: `redis`, `json`
- **Logic**: Deactivates the channel in the Redis subscription list.

#### `list_subscriptions`
- **Purpose**: Returns all channel subscriptions with stats.
- **Dependencies**: `redis`, `psycopg2`, `datetime`
- **Logic**: Loads the subscription list from Redis and enriches it with stats from PostgreSQL.

#### `_load_channel_list`
- **Purpose**: Loads the channel list from Redis.
- **Dependencies**: `redis`, `json`
- **Logic**: Retrieves and deserializes the channel list from Redis.

#### `_save_channel_list`
- **Purpose**: Saves the channel list to Redis.
- **Dependencies**: `redis`, `json`
- **Logic**: Serializes and saves the channel list to Redis.

#### `_load_subscribed_channels`
- **Purpose**: Loads active channels from Redis.
- **Dependencies**: `redis`
- **Logic**: Filters the loaded channel list to active channels.

#### `poll_channel`
- **Purpose**: Fetches the RSS feed for a channel and enqueues new videos.
- **Dependencies**: `redis`, `feedparser`, `json`
- **Logic**: Fetches the RSS feed, checks for new videos, and enqueues them.

#### `_notify_new_videos`
- **Purpose**: Sends a notification about newly queued videos.
- **Dependencies**: `redis`
- **Logic**: Sends a Telegram notification about newly queued videos.

#### `run_monitor`
- **Purpose**: Main monitor loop that polls all subscribed channels on a schedule.
- **Dependencies**: `redis`, `time`
- **Logic**: Periodically polls all subscribed channels and enqueues new videos.

#### `_clean`
- **Purpose**: Cleans datetime objects for JSON serialization.
- **Dependencies**: `datetime`
- **Logic**: Converts datetime objects to ISO format for JSON serialization.
