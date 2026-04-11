# voice/pipeline.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 147

---

### File: voice/pipeline.py

#### Purpose
This file defines the `VoicePipeline` class, which manages the entire voice processing pipeline from speech-to-text (STT), text processing, text-to-speech (TTS), to audio delivery via Mumble. It also includes a utility function `load_config` for loading configuration settings.

#### Architecture
The `VoicePipeline` class is the core component of the voice processing pipeline. It initializes various components such as the Mumble client, Voice Activity Detector (VAD), and manages a queue for incoming audio data. The class contains methods for starting and stopping the pipeline, handling incoming audio, and processing the audio through the pipeline stages.

- **`__init__`**: Initializes the `VoicePipeline` with configuration settings and sets up the VAD and Mumble client.
- **`start`**: Starts the pipeline by pre-loading models, connecting to Mumble, and starting the processing thread.
- **`stop`**: Stops the pipeline by disconnecting from Mumble and stopping the processing thread.
- **`_on_audio`**: Handles incoming audio data, resampling if necessary, and queues it for processing.
- **`_loop`**: Continuously processes audio data from the queue.
- **`_handle`**: Processes the audio data through the pipeline stages: STT, text processing, TTS, and audio delivery.
- **`say`**: Manually generates speech and sends it via Mumble.

#### Patterns
- **Singleton**: The `VoicePipeline` instance is intended to be a singleton, managing the entire pipeline lifecycle.
- **Observer**: The `IrisMumbleClient` is an observer that triggers `_on_audio` when audio is received.

#### Dependencies
- **Logging**: `logging` for logging messages.
- **Threading**: `threading` for managing threads.
- **Queue**: `queue` for managing audio data.
- **Time**: `time` for timing operations.
- **NumPy**: `numpy` for audio processing.
- **YAML**: `yaml` for loading configuration files.
- **OS**: `os` for file operations.
- **STT**: `voice.stt` for speech-to-text functionality.
- **Processor**: `voice.processor` for text processing.
- **TTS**: `voice.tts` for text-to-speech functionality.
- **Mumble Client**: `voice.mumble_client` for Mumble client functionality.

#### Interfaces
- **`start`**: Starts the voice pipeline.
- **`stop`**: Stops the voice pipeline.
- **`say`**: Manually generates speech and sends it via Mumble.

#### Database
- **`voice` (PostgreSQL)**: The `voice` table in PostgreSQL is referenced multiple times, likely for logging or storing voice-related data.

#### Configuration
- **`/opt/mythos/voice/config.yaml`**: The configuration file path for loading settings.

#### Key Logic
- **Audio Processing Pipeline**: The `_handle` method processes audio data through the following stages:
  1. **STT**: Transcribes audio to text.
  2. **Wake Word Check**: Ensures the wake word is present before processing.
  3. **Text Processing**: Processes the text through an LLM.
  4. **TTS**: Synthesizes the response to audio.
  5. **Audio Delivery**: Sends the synthesized audio to Mumble.
- **Pre-loading Models**: Models are pre-loaded to reduce the first-response delay.
- **Queue Management**: Incoming audio is queued and processed in a separate thread.

#### Integration Points
- **STT**: Integrates with the `voice.stt` module for speech-to-text functionality.
- **Processor**: Integrates with the `voice.processor` module for text processing.
- **TTS**: Integrates with the `voice.tts` module for text-to-speech functionality.
- **Mumble Client**: Integrates with the `voice.mumble_client` module for Mumble client functionality.

This file is a critical component of the Mythos system, managing the entire voice processing pipeline and ensuring smooth interaction between different subsystems.
