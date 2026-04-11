# voice/stt.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 73

---

### Documentation for `voice/stt.py`

#### Purpose
This file provides Speech-to-Text (STT) functionality using the `faster-whisper` model for transcription and the `Silero VAD` (Voice Activity Detection) model for detecting speech segments in audio data.

#### Architecture
The file consists of:
- **Top-level functions**:
  - `get_whisper_model(config)`: Loads and initializes the `faster-whisper` model.
  - `get_vad_model()`: Loads and initializes the `Silero VAD` model.
  - `transcribe(audio_data, config)`: Transcribes the provided audio data using the `faster-whisper` model.
- **Class**:
  - `VoiceActivityDetector(config)`: Manages the detection of speech segments in audio data using the `Silero VAD` model.

#### Patterns
- **Singleton Pattern**: The `get_whisper_model` and `get_vad_model` functions ensure that only one instance of the models is loaded and reused throughout the application.

#### Dependencies
- **Imports**: `logging`, `time`, `numpy`, `torch`
- **External Models**: `faster-whisper` and `Silero VAD` models from `torch.hub`

#### Interfaces
- **Functions Exposed**:
  - `get_whisper_model(config)`: Returns the initialized `faster-whisper` model.
  - `get_vad_model()`: Returns the initialized `Silero VAD` model.
  - `transcribe(audio_data, config)`: Returns the transcribed text and confidence score.
  - `VoiceActivityDetector(config)`: Class for managing speech detection.
    - `process_chunk(audio_chunk)`: Processes an audio chunk and returns speech segments.
    - `_reset()`: Resets the internal state of the `VoiceActivityDetector`.

#### Database
- **PostgreSQL Table**: `faster_whisper` (used for storing or retrieving model configurations or data)

#### Configuration
- **Environment Variables/Config Files**: 
  - `config`: Configuration dictionary passed to `get_whisper_model` and `VoiceActivityDetector` for model initialization and parameters.

#### Key Logic
- **Voice Activity Detection**:
  - `VoiceActivityDetector.process_chunk(audio_chunk)`: Splits the audio chunk into frames, processes each frame with the `Silero VAD` model, and accumulates frames that exceed the speech threshold.
  - `_reset()`: Resets the internal state of the `VoiceActivityDetector` after processing a speech segment.
- **Transcription**:
  - `transcribe(audio_data, config)`: Uses the `faster-whisper` model to transcribe the provided audio data, handling exceptions and returning the transcribed text and confidence score.

#### Integration Points
- **Mythos Subsystems**:
  - **Audio Input**: Receives raw audio data from the audio input subsystem.
  - **Model Initialization**: Integrates with the configuration subsystem to load and initialize models.
  - **Post-Processing**: Outputs transcribed text and speech segments to the post-processing subsystem for further analysis or action.

### Detailed Breakdown

#### `get_whisper_model(config)`
- **Purpose**: Loads and initializes the `faster-whisper` model.
- **Logic**: Uses the `config` dictionary to determine the model size, device, and compute type. Ensures only one instance of the model is loaded using the singleton pattern.

#### `get_vad_model()`
- **Purpose**: Loads and initializes the `Silero VAD` model.
- **Logic**: Uses `torch.hub.load` to load the `Silero VAD` model from the specified repository.

#### `transcribe(audio_data, config)`
- **Purpose**: Transcribes the provided audio data using the `faster-whisper` model.
- **Logic**: Calls `get_whisper_model` to ensure the model is loaded, then transcribes the audio data. Handles exceptions and returns the transcribed text and confidence score.

#### `VoiceActivityDetector(config)`
- **Purpose**: Manages the detection of speech segments in audio data.
- **Methods**:
  - `__init__(config)`: Initializes the `VoiceActivityDetector` with configuration parameters.
  - `process_chunk(audio_chunk)`: Processes an audio chunk, detects speech segments, and returns the accumulated speech frames.
  - `_reset()`: Resets the internal state after processing a speech segment.

### Summary
This file integrates speech-to-text and voice activity detection functionalities into the Mythos system, providing robust transcription capabilities and efficient speech segment detection. It leverages external models and follows a singleton pattern to ensure efficient resource usage.
