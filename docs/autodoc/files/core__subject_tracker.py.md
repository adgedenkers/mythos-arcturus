# core/subject_tracker.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 886

---

### Documentation for `core/subject_tracker.py`

#### Purpose
The `subject_tracker.py` module is the core component of Iris's conversational consciousness. It tracks the subject of conversations, manages conversation segments, and provides context for the system. It processes every incoming message to extract subject data, record subject points, and manage segment lifecycles.

#### Architecture
The module consists of two data classes (`SubjectPoint` and `SegmentAction`) and multiple top-level functions that handle various aspects of subject extraction, recording, and segment management. The data flow is as follows:
1. **Inline Subject Extraction**: Functions like `extract_subject_inline` process incoming messages to extract subject data.
2. **Subject Point Recording**: Functions like `record_subject_point` write the extracted subject points to the database.
3. **Segment Management**: Functions like `get_open_segment`, `create_segment`, and `reopen_segment` manage the lifecycle of conversation segments.
4. **Warm Cache and Trajectory Retrieval**: Functions like `get_warm_cache` and `get_trajectory` provide recent context and conversation history.

#### Patterns
- **Data Class Pattern**: The `SubjectPoint` and `SegmentAction` classes use the `dataclasses` module to define immutable data structures.
- **Singleton Pattern**: The database connection is managed through the `get_db` function, which can be considered a singleton pattern for database connections.

#### Dependencies
- **Standard Libraries**: `os`, `re`, `json`, `logging`, `datetime`, `typing`, `dataclasses`
- **Third-party Libraries**: `psycopg2`, `dotenv`

#### Interfaces
- **Public Functions**:
  - `extract_subject_inline(message: str, previous_point: Optional[Dict], role: str) -> SubjectPoint`
  - `record_subject_point(chat_id: int, telegram_id: int, subject: SubjectPoint, segment_id: Optional[str], perception_id: Optional[str], previous_point_id: Optional[int]) -> Optional[int]`
  - `get_open_segment(chat_id: int) -> Optional[Dict]`
  - `get_recent_soft_closed_segments(chat_id: int, hours: int) -> List[Dict]`
  - `detect_segment_action(chat_id: int, subject: SubjectPoint, time_gap_seconds: int) -> SegmentAction`
  - `create_segment(chat_id: int, telegram_id: int, subject: SubjectPoint) -> str`
  - `update_segment(segment_id: str, subject: SubjectPoint) -> None`
  - `reopen_segment(segment_id: str, subject: SubjectPoint) -> None`
  - `get_last_subject_point(chat_id: int) -> Dict`
  - `get_trajectory(chat_id: int, limit: int) -> List[Dict]`
  - `get_warm_cache(chat_id: int, tier_hours: int) -> List[Dict]`
  - `get_open_threads(chat_id: int) -> List[Dict]`
  - `build_conversation_awareness(chat_id: int, limit: int) -> str`
  - `process_message(chat_id: int, telegram_id: int, message: str, role: str, perception_id: str, time_gap_seconds: int) -> Dict`
  - `close_stale_segments() -> int`

#### Database
- **Tables**:
  - `conversation_subject_points`: Stores subject points.
  - `conversation_segments`: Stores conversation segments.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`
- **Constants**:
  - `SOFT_CLOSE_MINUTES`, `HARD_CLOSE_MINUTES`, `REATTACH_WINDOW_HOURS`, `WARM_TIER_HOURS`, `SHORT_TIER_HOURS`, `MEDIUM_TIER_HOURS`, `TAG_OVERLAP_THRESHOLD`, `SHIFT_TAG_THRESHOLD`, `MAX_PREVIEW_LENGTH`

#### Key Logic
- **Subject Extraction**: Uses heuristics to extract meaningful tags and build a summary from the message text.
- **Segment Lifecycle Management**: Manages the opening, appending, reattaching, and closing of conversation segments.
- **Warm Cache and Trajectory Retrieval**: Provides recent context and conversation history for building the system prompt.

#### Integration Points
- **chat_mode.py**: Calls `process_message` for every incoming message.
- **subject_worker.py**: Handles asynchronous enrichment of subject data.
- **Database**: Uses PostgreSQL for storing subject points and segments.
- **Redis**: Not directly used in this file but likely used for caching or other purposes in the broader system.
- **Ollama**: Not directly used in this file but likely used for generating responses based on the conversation awareness built by this module.

This module is critical for maintaining the conversational context and ensuring that the system can respond appropriately to user inputs by tracking and analyzing the conversation's subject over time.
