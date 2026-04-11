# services/diarized_transcription.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 442

---

### File: services/diarized_transcription.py

#### Purpose
This file contains the `DiarizedTranscriptionService` class, which provides a full pipeline for converting audio files to WAV format, transcribing them using the Whisper model, and performing speaker diarization using the Pyannote pipeline. The service merges transcription and diarization results to provide a comprehensive output with speaker labels and timestamps.

#### Architecture
The `DiarizedTranscriptionService` class is the primary component of this file. It includes methods for lazy-loading the Whisper and Pyannote models, converting audio files to WAV, transcribing audio, running diarization, merging transcription and diarization results, and computing speaker statistics. The class is designed to handle the entire transcription and diarization process in a modular and efficient manner.

#### Patterns
- **Lazy Loading**: The Whisper and Pyannote models are loaded only when needed, reducing the initial load time and resource usage.
- **Fallback Mechanism**: If diarization is not available (e.g., due to missing HuggingFace token), the service falls back to transcription-only mode.

#### Dependencies
- **Standard Libraries**: `os`, `logging`, `subprocess`, `time`, `torch`
- **External Libraries**: `faster_whisper`, `pyannote.audio`, `pathlib`, `typing`

#### Interfaces
- **Public Methods**:
  - `convert_to_wav(input_path: str, wav_path: str = None) -> Optional[str]`: Converts an audio file to WAV format.
  - `get_audio_duration(audio_path: str) -> float`: Returns the duration of an audio file.
  - `transcribe_with_diarization(audio_path: str, language: str = None, wav_cache_dir: str = "/opt/mythos/voice_memos/wav_cache") -> Dict[str, Any]`: Full pipeline for converting, transcribing, diarizing, and merging audio files.

- **Private Methods**:
  - `_load_whisper()`: Lazy-loads the Whisper model.
  - `_load_diarization()`: Lazy-loads the Pyannote diarization pipeline.
  - `_transcribe_whisper(wav_path: str, language: str = None) -> Dict[str, Any]`: Runs Whisper transcription.
  - `_run_diarization(wav_path: str) -> List[Dict[str, Any]]`: Runs Pyannote diarization.
  - `_merge_transcription_and_diarization(whisper_segments: List[Dict], diarization_segments: List[Dict]) -> List[Dict[str, Any]]`: Merges transcription and diarization results.
  - `_compute_speaker_stats(diarized_segments: List[Dict]) -> Dict[str, Dict]`: Computes per-speaker statistics.

#### Database
- **References**: The file does not directly interact with any database tables or Neo4j labels. It primarily deals with audio files and their processing.

#### Configuration
- **Environment Variables**:
  - `WHISPER_MODEL`: Specifies the Whisper model to use (default: `large-v3`).
  - `WHISPER_DEVICE`: Specifies the device to use for Whisper (default: `cuda`).
  - `WHISPER_COMPUTE`: Specifies the compute type for Whisper (default: `float16`).
  - `HUGGINGFACE_TOKEN`: Specifies the HuggingFace token for accessing the Pyannote model.

#### Key Logic
- **Conversion**: Converts audio files to 16kHz mono WAV format using `ffmpeg`.
- **Transcription**: Uses the Whisper model to transcribe audio files, providing word-level timestamps.
- **Diarization**: Uses the Pyannote pipeline to perform speaker diarization, identifying speaker segments.
- **Merging**: Merges transcription and diarization results, assigning speaker labels to each transcription segment based on temporal overlap.
- **Statistics**: Computes per-speaker statistics such as total duration, segment count, and word count.

#### Integration Points
- **Audio Conversion**: Integrates with `ffmpeg` for audio format conversion.
- **Whisper Transcription**: Integrates with the `faster_whisper` library for speech-to-text conversion.
- **Pyannote Diarization**: Integrates with the `pyannote.audio` library for speaker diarization.
- **Logging**: Uses Python's `logging` module for logging information and errors.

This file serves as a crucial component in the Mythos system, providing a robust and efficient way to process audio files, transcribe them, and identify speaker segments, all while handling various edge cases and fallback scenarios.
