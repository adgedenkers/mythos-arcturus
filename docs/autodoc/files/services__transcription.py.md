# services/transcription.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 190

---

### Documentation for `services/transcription.py`

#### Purpose
The `TranscriptionService` class in `transcription.py` provides GPU-accelerated speech-to-text transcription using the `faster-whisper` library. It handles the conversion of Telegram voice messages from `.ogg` to `.wav` format and performs transcription, returning the transcribed text along with metadata.

#### Architecture
- **Class**: `TranscriptionService`
  - **Methods**:
    - `__init__`: Initializes the class with model configuration.
    - `_load_model`: Lazy-loads the `faster-whisper` model on first use.
    - `convert_ogg_to_wav`: Converts `.ogg` files to `.wav` format.
    - `get_audio_duration`: Retrieves the duration of an audio file.
    - `transcribe`: Transcribes an audio file and returns the transcription result.

#### Patterns
- **Lazy Initialization**: The `_load_model` method ensures that the model is only loaded when it is first needed, avoiding unnecessary startup delay.

#### Dependencies
- **Imports**:
  - `os`: For environment variable access and file operations.
  - `logging`: For logging messages.
  - `subprocess`: For running external commands like `ffmpeg` and `ffprobe`.
  - `tempfile`: For temporary file management (not directly used in the provided code but imported).
  - `pathlib`: For path operations.
  - `typing`: For type hints.
  - `faster_whisper`: For speech-to-text transcription.

#### Interfaces
- **Public Methods**:
  - `convert_ogg_to_wav(ogg_path: str, wav_path: str = None) -> str`: Converts `.ogg` to `.wav`.
  - `get_audio_duration(audio_path: str) -> float`: Returns the duration of an audio file.
  - `transcribe(audio_path: str, language: str = None) -> Dict[str, Any]`: Transcribes an audio file and returns the transcription result.

#### Database
- **References**:
  - No direct database operations are performed in this file. The `services` table and `pathlib` are imported but not used directly for database operations.

#### Configuration
- **Environment Variables**:
  - `WHISPER_MODEL`: Specifies the model to use for transcription (default: `large-v3`).
  - `WHISPER_DEVICE`: Specifies the device to use for transcription (default: `cuda`).
  - `WHISPER_COMPUTE`: Specifies the compute type for the model (default: `float16`).

#### Key Logic
- **Model Initialization**: The `_load_model` method ensures that the `faster-whisper` model is only loaded when needed.
- **Audio Conversion**: The `convert_ogg_to_wav` method uses `ffmpeg` to convert `.ogg` files to `.wav` format.
- **Transcription**: The `transcribe` method handles the transcription process, including:
  - Converting `.ogg` files to `.wav` if necessary.
  - Getting the duration of the audio file.
  - Transcribing the audio using the `faster-whisper` model.
  - Collecting and formatting the transcription segments and full text.

#### Integration Points
- **External Commands**: Uses `ffmpeg` for audio conversion and `ffprobe` for getting audio duration.
- **Logging**: Uses the `logging` module to log initialization, model loading, conversion, and transcription processes.
- **Environment Configuration**: Relies on environment variables for model configuration.

This file is a crucial component of the Mythos system, providing the necessary functionality for speech-to-text transcription and audio file handling.
