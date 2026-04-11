# voice/tts.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 44

---

### File: voice/tts.py

#### Purpose
This file provides text-to-speech (TTS) functionality using the Kokoro TTS engine. It includes functions to load the TTS pipeline, synthesize speech from text, and check the health of the TTS system.

#### Architecture
The file is structured around three main functions:
1. `get_pipeline`: Loads and caches the Kokoro TTS pipeline.
2. `synthesize`: Synthesizes speech from the given text using the loaded pipeline.
3. `ping`: Checks if the TTS system is operational.

#### Patterns
- **Singleton Pattern**: The `_pipeline` variable is used to ensure that the Kokoro TTS pipeline is loaded only once and reused across multiple calls to `get_pipeline`.

#### Dependencies
- `os`: For operating system-related operations.
- `logging`: For logging messages.
- `numpy`: For numerical operations on audio data.
- `soundfile`: For writing audio files (conditionally imported).
- `kokoro`: The Kokoro TTS engine.
- `voice.pronunciations`: For applying pronunciation adjustments to the input text.

#### Interfaces
- `get_pipeline()`: Returns the Kokoro TTS pipeline.
- `synthesize(text, config, output_path)`: Synthesizes speech from the given text and writes it to `output_path` if provided.
- `ping()`: Returns `True` if the TTS system is operational, otherwise `False`.

#### Database
- **PostgreSQL Tables**:
  - `kokoro`: Potentially used for storing TTS-related configurations or metadata.
  - `voice`: Potentially used for storing voice-related configurations or metadata.

#### Configuration
- No explicit configuration files are used, but the `config` parameter in `synthesize` can be used to pass configuration options like the voice to use.

#### Key Logic
- **Loading the TTS Pipeline**: The `get_pipeline` function ensures that the Kokoro TTS pipeline is loaded only once and reused across multiple calls.
- **Text Synthesis**: The `synthesize` function processes the input text, applies pronunciation adjustments, and uses the Kokoro TTS pipeline to generate audio segments. These segments are concatenated and optionally written to a file.
- **Health Check**: The `ping` function checks if the TTS pipeline can be loaded successfully.

#### Integration Points
- **Pronunciation Adjustments**: The `voice.pronunciations.apply` function is used to adjust the pronunciation of the input text before synthesis.
- **Logging**: The `logging` module is used to log information and errors related to TTS operations.
- **Audio Writing**: The `soundfile` module is conditionally imported and used to write the synthesized audio to a file if an `output_path` is provided.

### Detailed Analysis

#### `get_pipeline`
- **Purpose**: Loads and caches the Kokoro TTS pipeline.
- **Logic**: Uses a global variable `_pipeline` to cache the pipeline instance. If the pipeline is already loaded, it returns the cached instance; otherwise, it loads the pipeline and caches it.

#### `synthesize`
- **Purpose**: Synthesizes speech from the given text and writes it to an output file if specified.
- **Logic**:
  - Checks if the input text is empty or contains only whitespace.
  - Applies pronunciation adjustments using `voice.pronunciations.apply`.
  - Retrieves the TTS pipeline using `get_pipeline`.
  - Synthesizes audio segments from the text using the specified voice.
  - Concatenates the audio segments and converts the result to a NumPy array.
  - Optionally writes the audio to a file using `soundfile`.

#### `ping`
- **Purpose**: Checks if the TTS system is operational.
- **Logic**: Attempts to load the TTS pipeline using `get_pipeline`. Returns `True` if successful, otherwise `False`.

### Summary
The `voice/tts.py` file provides essential TTS functionality for the Mythos system, leveraging the Kokoro TTS engine to synthesize speech from text. It ensures efficient pipeline loading through caching and provides mechanisms for pronunciation adjustments and audio file writing. The file integrates with other components of the system through pronunciation adjustments and logging, and it interfaces with PostgreSQL for potential TTS-related configurations.
