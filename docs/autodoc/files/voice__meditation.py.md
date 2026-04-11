# voice/meditation.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 177

---

### File: `voice/meditation.py`

#### Purpose
This file contains functions for parsing meditation scripts, synthesizing speech using text-to-speech (TTS), and rendering the output as OGG files. It also includes utilities for estimating the duration of a meditation script and listing all rendered meditations.

#### Architecture
The file consists of several top-level functions that handle different aspects of the meditation rendering process:
- `slugify`: Generates a slug from a title.
- `parse_script`: Parses a meditation script into a list of speech and pause segments.
- `make_silence`: Creates a silence segment of a specified duration.
- `render_meditation`: Renders a meditation script into an OGG file.
- `estimate_duration`: Estimates the duration of a meditation script without rendering.
- `list_meditations`: Lists metadata for all rendered meditations.

#### Patterns
- **No specific design patterns**: The file primarily consists of utility functions without complex design patterns.

#### Dependencies
- `os`: For file system operations.
- `re`: For regular expression operations.
- `logging`: For logging messages.
- `numpy`: For handling audio data.
- `soundfile`: For writing audio files.
- `datetime`: For timestamp operations.
- `pathlib`: For path operations.
- `typing`: For type hints.
- `voice.tts`: For TTS synthesis.

#### Interfaces
- Exposes functions for parsing scripts, rendering meditations, estimating durations, and listing meditations.
- Interfaces with TTS synthesis via `voice.tts.synthesize`.

#### Database
- No direct database operations are performed in this file.
- References to `datetime`, `pathlib`, `typing`, and `voice` are likely imports and not database tables.

#### Configuration
- Uses `OUTPUT_DIR` for the default output directory.
- Uses `SAMPLE_RATE` and `BREATH_GAP` for audio configuration.

#### Key Logic
1. **Parsing Scripts**: The `parse_script` function splits the script into segments, distinguishing between speech and pause segments.
2. **Rendering Meditation**: The `render_meditation` function synthesizes speech segments using TTS, adds silence where needed, and writes the combined audio to an OGG file.
3. **Estimating Duration**: The `estimate_duration` function calculates the total duration of a meditation script by summing the durations of speech and pause segments.
4. **Listing Meditations**: The `list_meditations` function retrieves metadata for all rendered meditations, sorting them by creation time.

#### Integration Points
- **TTS Integration**: Uses `voice.tts.synthesize` to convert text segments to audio.
- **File System**: Writes OGG files to the specified output directory.
- **Logging**: Uses the `logging` module to log various stages of the rendering process.

### Detailed Documentation

#### `slugify`
- **Purpose**: Generates a slug from a title.
- **Arguments**: `title` (str), `max_words` (int, default=4).
- **Logic**: Converts the title to lowercase, removes non-alphanumeric characters, and joins the first `max_words` words with underscores.

#### `parse_script`
- **Purpose**: Parses a meditation script into a list of speech and pause segments.
- **Arguments**: `script` (str).
- **Logic**: Splits the script into lines, matches pause lines using a regex, and creates a list of segment dictionaries.

#### `make_silence`
- **Purpose**: Creates a silence segment of a specified duration.
- **Arguments**: `seconds` (float).
- **Logic**: Generates a zero-filled numpy array of the specified duration.

#### `render_meditation`
- **Purpose**: Renders a meditation script to an OGG file.
- **Arguments**: `script` (str), `title` (str, default="meditation"), `voice` (str, default="af_heart"), `output_dir` (Path, optional), `output_path` (Path, optional).
- **Logic**: Parses the script, synthesizes speech segments, adds silence, and writes the combined audio to an OGG file.

#### `estimate_duration`
- **Purpose**: Estimates the duration of a meditation script without rendering.
- **Arguments**: `script` (str).
- **Logic**: Parses the script and calculates the total duration by summing the durations of speech and pause segments.

#### `list_meditations`
- **Purpose**: Lists metadata for all rendered meditations, sorted by creation time.
- **Arguments**: `output_dir` (Path, optional).
- **Logic**: Retrieves metadata for all OGG files in the output directory, sorting them by creation time.

### Example Usage
```python
from voice.meditation import render_meditation, list_meditations

script = """
This is a meditation script.
[pause:5]
Continue speaking after the pause.
"""

output_path = render_meditation(script, title="Sample Meditation")
print(output_path)

meditations = list_meditations()
for meditation in meditations:
    print(meditation)
```

This file is a crucial part of the Mythos system, enabling the creation and management of meditation audio files.
