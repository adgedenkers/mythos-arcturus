# voice/config.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 37

---

### File: `voice/config.yaml`

#### Purpose
This YAML configuration file contains settings for the voice processing subsystem of the Mythos system, including Mumble server details, speech-to-text (STT) and text-to-speech (TTS) configurations, and pipeline parameters.

#### Architecture
The file is structured into several sections, each corresponding to a specific aspect of the voice processing pipeline:
- **mumble**: Configuration for the Mumble server.
- **pipeline**: Parameters for the voice processing pipeline.
- **processor**: Settings for the AI model processing.
- **stt**: Configuration for the speech-to-text engine.
- **tts**: Configuration for the text-to-speech engine.

#### Patterns
No design patterns are applicable as this is a configuration file.

#### Dependencies
This file does not directly import or rely on any external libraries or modules. It is used by the voice processing subsystem to configure its behavior.

#### Interfaces
This configuration file is read by the voice processing subsystem to initialize its components with the specified settings. It does not expose any interfaces directly.

#### Database
This configuration file does not interact with any database tables or Neo4j labels.

#### Configuration
The configuration is entirely contained within this YAML file. There are no additional config files or environment variables used directly by this file.

#### Key Logic
The key logic is not contained within this file but rather in the code that reads and applies these configurations. The configurations dictate how the voice processing subsystem behaves, including:
- Mumble server connection details.
- Speech-to-text engine settings, including model size and device type.
- Text-to-speech engine settings, including the voice and language.
- Pipeline parameters such as wake words and confidence thresholds.

#### Integration Points
This configuration file integrates with the following subsystems of the Mythos system:
- **Mumble Integration**: Configures the Mumble server connection for voice communication.
- **Speech-to-Text (STT) Engine**: Configures the STT engine with specific parameters like model size and device type.
- **Text-to-Speech (TTS) Engine**: Configures the TTS engine with specific parameters like voice and language.
- **Voice Processing Pipeline**: Configures the pipeline with parameters like wake words, confidence thresholds, and greeting messages.
- **AI Model Processor**: Configures the AI model processor with parameters like model name, maximum tokens, and system prompt path.

### Detailed Configuration Sections

#### Mumble Configuration
- **channel**: The Mumble channel to join (`Iris`).
- **host**: The Mumble server IP address (`127.0.0.1`).
- **password**: The password for the Mumble server (`''`).
- **port**: The Mumble server port (`64738`).
- **user**: The username for the Mumble server (`Iris`).

#### Pipeline Configuration
- **channels**: Number of audio channels (`1`).
- **greeting**: The greeting message when the system starts (`Iris online. I am listening.`).
- **min_confidence**: Minimum confidence threshold for processing speech (`0.4`).
- **sample_rate**: Sample rate for audio processing (`48000`).
- **wake_word_required**: Whether a wake word is required to activate processing (`true`).
- **wake_words**: List of wake words (`iris`, `hey iris`).

#### Processor Configuration
- **max_tokens**: Maximum number of tokens for the AI model (`2048`).
- **model**: Name of the AI model (`qwen3:30b-a3b`).
- **ollama_url**: URL for the Ollama service (`http://localhost:11434`).
- **system_prompt_path**: Path to the system prompt file (`/opt/mythos/prompts/voices/iris.yaml`).
- **temperature**: Temperature for the AI model (`0.7`).
- **timeout**: Timeout for the AI model processing (`30` seconds).

#### Speech-to-Text (STT) Configuration
- **compute_type**: Type of computation for STT (`float16`).
- **device**: Device for STT processing (`cuda`).
- **engine**: STT engine to use (`faster-whisper`).
- **model_size**: Size of the STT model (`medium.en`).
- **vad**: Voice activity detection settings:
  - **enabled**: Whether VAD is enabled (`true`).
  - **min_silence_ms**: Minimum silence duration in milliseconds (`1000`).
  - **min_speech_ms**: Minimum speech duration in milliseconds (`1500`).
  - **post_speech_pause_ms**: Post-speech pause duration in milliseconds (`1200`).
  - **threshold**: VAD threshold (`0.65`).

#### Text-to-Speech (TTS) Configuration
- **engine**: TTS engine to use (`kokoro`).
- **language**: Language for TTS (`en`).
- **voice**: Voice for TTS (`af_heart`).

This configuration file is critical for setting up the voice processing subsystem and ensuring that it operates correctly with the specified parameters.
