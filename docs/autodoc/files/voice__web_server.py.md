# voice/web_server.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 204

---

### File: voice/web_server.py

#### Purpose
This file implements a FastAPI-based web server that handles voice interactions via WebSocket connections. It supports speech-to-text (STT), text-to-speech (TTS), and a text processing pipeline for handling user inputs and generating responses.

#### Architecture
The file is structured around several key functions and a FastAPI application:
- **Global Variables**: `_stt_model`, `_tts_pipeline`, `_processor_config`, `_config` are used for lazy-loading models and configurations.
- **Helper Functions**: `load_config`, `get_stt`, `get_tts`, `transcribe`, `synthesize`, `think`, `audio_to_wav_bytes` handle configuration loading, model initialization, audio processing, and text processing.
- **FastAPI Routes**: `index`, `health`, `voice_ws` define the HTTP and WebSocket endpoints.
- **Main Function**: `start_server` initializes logging, preloads models, and starts the FastAPI server.

#### Patterns
- **Lazy Loading**: Models and configurations are loaded on-demand when first accessed.
- **Singleton Pattern**: Global variables ensure that models and configurations are loaded only once.

#### Dependencies
- **Imports**: `asyncio`, `logging`, `struct`, `io`, `time`, `numpy`, `uvicorn`, `yaml`, `sys`, `fastapi`, `fastapi.staticfiles`, `fastapi.responses`, `fastapi.WebSocket`, `fastapi.WebSocketDisconnect`.
- **External Libraries**: `faster_whisper`, `kokoro`, `voice.pronunciations`, `voice.processor`.

#### Interfaces
- **HTTP Routes**:
  - `GET /`: Serves the static HTML file for the voice interface.
  - `GET /health`: Returns a health check status.
- **WebSocket Route**:
  - `GET /ws/voice`: Handles real-time voice interactions, including STT, text processing, and TTS.

#### Database
- **References**: The file interacts with several PostgreSQL tables: `fastapi`, `faster_whisper`, `kokoro`, `voice`, `browser`. These tables are likely used for storing configurations, models, and interaction histories.

#### Configuration
- **Config File**: `/opt/mythos/voice/config.yaml` is loaded using `yaml.safe_load`.
- **Environment Variables**: No explicit environment variables are used, but the server can be started with custom `host` and `port` arguments.

#### Key Logic
- **Voice Interaction Loop**: The `voice_ws` function manages the WebSocket connection, handling audio input, performing STT, processing text, generating responses, and sending TTS audio back to the client.
- **Model Initialization**: `get_stt` and `get_tts` ensure that the STT and TTS models are loaded only once.
- **Audio Processing**: `transcribe` and `synthesize` handle the conversion between audio and text, using the loaded models.

#### Integration Points
- **STT and TTS Models**: The file integrates with external libraries `faster_whisper` and `kokoro` for speech-to-text and text-to-speech functionalities.
- **Text Processing Pipeline**: The `think` function integrates with `voice.processor` to process text inputs and generate responses.
- **Static Files**: The server serves static files from `/opt/mythos/voice/static`.
- **Logging**: Uses Python's `logging` module to log various events and errors.

### Detailed Breakdown

#### `load_config`
- **Purpose**: Loads the configuration from `/opt/mythos/voice/config.yaml`.
- **Logic**: Uses `yaml.safe_load` to parse the YAML file and stores the configuration in `_config`.

#### `get_stt`
- **Purpose**: Lazy-loads the STT model from `faster_whisper`.
- **Logic**: Initializes the `WhisperModel` with configuration parameters from the loaded config.

#### `get_tts`
- **Purpose**: Lazy-loads the TTS pipeline from `kokoro`.
- **Logic**: Initializes the `KPipeline` with specific parameters.

#### `transcribe`
- **Purpose**: Transcribes audio data to text using the loaded STT model.
- **Logic**: Uses the `transcribe` method of the `WhisperModel` and processes the segments to form a coherent text.

#### `synthesize`
- **Purpose**: Converts text to audio using the loaded TTS pipeline.
- **Logic**: Applies text processing, uses the `KPipeline` to generate audio segments, and combines them into a single audio array.

#### `think`
- **Purpose**: Processes text input to generate a response.
- **Logic**: Uses `voice.processor.process_text` to generate a response based on the input text and history.

#### `audio_to_wav_bytes`
- **Purpose**: Converts a float32 numpy array to WAV format bytes.
- **Logic**: Converts the audio array to 16-bit PCM, constructs a WAV header, and writes the audio data.

#### `index`
- **Purpose**: Serves the static HTML file for the voice interface.
- **Logic**: Returns a `FileResponse` for `/opt/mythos/voice/static/index.html`.

#### `health`
- **Purpose**: Provides a health check endpoint.
- **Logic**: Returns a JSON response indicating the service status.

#### `voice_ws`
- **Purpose**: Manages the WebSocket connection for real-time voice interaction.
- **Logic**: Handles audio input, performs STT, processes text, generates TTS audio, and sends responses back to the client.

#### `start_server`
- **Purpose**: Initializes logging, preloads models, and starts the FastAPI server.
- **Logic**: Configures logging, preloads STT and TTS models, and runs the FastAPI server using `uvicorn`.

This file is a crucial component of the Mythos system, enabling real-time voice interaction through a web interface.
