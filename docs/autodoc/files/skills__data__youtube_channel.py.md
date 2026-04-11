# skills/data/youtube_channel.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 296

---

### Documentation for `skills/data/youtube_channel.py`

#### Purpose
This file implements the `YouTubeChannelSkill` class, which handles natural language requests for managing YouTube channel subscriptions and reporting queue status. It supports commands to track and untrack YouTube channels, list tracked channels, and check the status of the YouTube queue.

#### Architecture
The file contains a single class `YouTubeChannelSkill` that inherits from `SkillBase`. It includes several methods for handling different types of requests:
- `_extract_handle_or_url`: Extracts YouTube channel handles or URLs from messages.
- `_extract_untrack_target`: Extracts the target for untracking from messages.
- `relevance`: Determines the relevance of a message to the skill.
- `execute`: Executes the appropriate action based on the message.
- `_track`: Tracks a YouTube channel.
- `_untrack`: Stops tracking a YouTube channel.
- `_list_subs`: Lists all tracked YouTube channels.
- `_queue_status`: Reports the status of the YouTube queue.

#### Patterns
- **Factory Pattern**: Not explicitly used.
- **Singleton Pattern**: Not explicitly used.
- **Observer Pattern**: Not explicitly used.
- **Command Pattern**: The class acts as a command handler for different types of requests.

#### Dependencies
- **Imports**: `logging`, `re`, `sys`, `subprocess`, `os`, `typing`, `engine.base`, `youtube_channel_monitor`, `youtube_queue_consumer`.
- **External Commands**: Uses `subprocess` to run the `yt-subscribe` script.

#### Interfaces
- **Public Methods**: `relevance`, `execute`.
- **Private Methods**: `_track`, `_untrack`, `_list_subs`, `_queue_status`.
- **Top-level Functions**: `_extract_handle_or_url`, `_extract_untrack_target`.

#### Database
- **PostgreSQL Tables**: `youtube_channel_monitor`, `youtube_queue_consumer`.
- **Neo4j Labels**: Not used.

#### Configuration
- **Environment Variables**: `PYTHONPATH` is set to `/opt/mythos`.
- **Config Files**: Not used.

#### Key Logic
- **Relevance Calculation**: Determines the relevance of a message to the skill based on predefined patterns.
- **Tracking and Untracking**: Uses subprocess to run an external script for tracking and a module function for untracking.
- **Listing Subscriptions**: Retrieves and formats a list of tracked YouTube channels.
- **Queue Status**: Retrieves and formats the status of the YouTube queue.

#### Integration Points
- **SkillBase Class**: Inherits from `SkillBase`, which likely provides a framework for handling skill requests.
- **External Scripts**: Integrates with the `yt-subscribe` script for tracking channels.
- **Database Modules**: Uses `youtube_channel_monitor` and `youtube_queue_consumer` modules to interact with the database for tracking and queue status.

### Detailed Analysis

#### `YouTubeChannelSkill` Class
- **Attributes**:
  - `name`: 'youtube_channel'
  - `version`: '2.0'
  - `category`: 'action'
  - `description`: 'Manage YouTube channel subscriptions and queue status'
  - `triggers`: List of trigger words and phrases.
  - `cache_ttl`: 0 (no caching).

- **Methods**:
  - `relevance`: Determines the relevance of a message by matching it against predefined patterns.
  - `execute`: Processes the message and calls the appropriate method based on the message content.
  - `_track`: Tracks a YouTube channel using an external script.
  - `_untrack`: Stops tracking a YouTube channel using a module function.
  - `_list_subs`: Lists all tracked YouTube channels.
  - `_queue_status`: Reports the status of the YouTube queue.

#### Top-level Functions
- `_extract_handle_or_url`: Extracts YouTube channel handles or URLs from messages.
- `_extract_untrack_target`: Extracts the target for untracking from messages.

#### Database Interactions
- **Tracking**: Uses `subprocess` to run the `yt-subscribe` script, which likely interacts with the `youtube_channel_monitor` table.
- **Untracking**: Calls `unsubscribe_channel` from `youtube_channel_monitor`.
- **Listing Subscriptions**: Calls `list_subscriptions` from `youtube_channel_monitor`.
- **Queue Status**: Calls `get_queue_status` from `youtube_queue_consumer`.

#### Configuration and Environment
- **Environment Variables**: `PYTHONPATH` is set to `/opt/mythos` to ensure the script can find the necessary modules.
- **External Commands**: Uses `subprocess` to run the `yt-subscribe` script located at `/opt/mythos/bin/yt-subscribe`.

This file is a crucial part of the Mythos system, handling user interactions related to YouTube channel subscriptions and queue management.
