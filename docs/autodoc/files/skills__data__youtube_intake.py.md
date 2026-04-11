# skills/data/youtube_intake.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 220

---

### File: skills/data/youtube_intake.py

#### Purpose
This file is responsible for fetching and parsing transcripts from YouTube videos. It uses two methods: `yt-dlp` and `youtube-transcript-api`, with `yt-dlp` as the primary method to avoid IP blocks.

#### Architecture
The file consists of several functions:
- `_parse_vtt`: Parses a WebVTT file into a list of transcript segments.
- `_vtt_ts_to_seconds`: Converts VTT timestamps to float seconds.
- `_fetch_transcript_ytdlp`: Fetches auto-generated subtitles via `yt-dlp`.
- `_fetch_transcript_api`: Fetches transcripts via `youtube-transcript-api`.
- `fetch_transcript`: Tries to fetch transcripts using `yt-dlp` first, falling back to `youtube-transcript-api` if `yt-dlp` fails.
- `transcript_to_text`: Flattens a list of transcript segments into a single plain-text string.

#### Patterns
- **Facade Pattern**: The `fetch_transcript` function acts as a facade, abstracting the complexity of fetching transcripts from different sources.
- **Fallback Pattern**: The `fetch_transcript` function implements a fallback mechanism, trying `yt-dlp` first and falling back to `youtube-transcript-api` if the primary method fails.

#### Dependencies
- `os`: For file path operations.
- `re`: For regular expression operations.
- `json`: For JSON operations (though not used in the provided code).
- `logging`: For logging.
- `tempfile`: For temporary directory management.
- `subprocess`: For running external commands.
- `pathlib`: For path operations.
- `typing`: For type hints.
- `youtube_transcript_api`: For fetching transcripts via the YouTube API (fallback method).

#### Interfaces
- `fetch_transcript(video_id: str) -> Optional[list[dict]]`: Fetches a transcript for a given YouTube video ID.
- `transcript_to_text(segments: list[dict]) -> str`: Converts a list of transcript segments into a plain-text string.

#### Database
The file does not directly interact with any database tables or Neo4j labels. However, it is part of the Mythos system, which might store the fetched transcripts in a PostgreSQL database.

#### Configuration
- `YT_DLP_BIN`: Path to the `yt-dlp` binary.

#### Key Logic
- **Parsing VTT Files**: The `_parse_vtt` function parses a WebVTT file into a list of transcript segments, handling timestamp conversion and text extraction.
- **Fetching Transcripts**: The `_fetch_transcript_ytdlp` and `_fetch_transcript_api` functions fetch transcripts using `yt-dlp` and `youtube-transcript-api`, respectively. The `fetch_transcript` function orchestrates the fetching process, trying `yt-dlp` first and falling back to `youtube-transcript-api` if necessary.
- **Converting to Text**: The `transcript_to_text` function flattens a list of transcript segments into a plain-text string.

#### Integration Points
- **Mythos System**: This file is part of the Mythos system and integrates with other subsystems that require YouTube video transcripts. The fetched transcripts can be used for further processing, such as indexing or analysis.
- **Logging**: The file uses the `logging` module to log various stages of the transcript fetching process, which can be integrated with the Mythos logging infrastructure.

### Summary
The `youtube_intake.py` file is a crucial component of the Mythos system, responsible for fetching and parsing YouTube video transcripts. It uses a combination of `yt-dlp` and `youtube-transcript-api` to ensure robust transcript fetching, with a fallback mechanism to handle failures. The file provides a clean interface for other parts of the system to fetch and process transcripts.
