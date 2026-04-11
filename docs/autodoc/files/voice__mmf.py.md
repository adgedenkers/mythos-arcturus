# voice/mmf.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 370

---

### File: voice/mmf.py

#### Purpose
This file contains functions to render an Iris Meditation Markup Format (MMF) specification into an audio file (OGG). It handles loading configuration, validating the specification, synthesizing speech segments, mixing background music, and writing the final audio file along with a manifest.

#### Architecture
The file consists of several top-level functions that handle different aspects of the MMF rendering process:
- `load_global_config`: Loads global configuration from a YAML file.
- `resolve_background`: Resolves background music settings from the global configuration and the specification.
- `load_spec`: Loads and validates the MMF specification from a YAML file.
- `_validate`: Validates the structure of the MMF specification.
- `flatten_segments`: Flattens the MMF specification into a list of segments for easier processing.
- `make_silence`: Generates a silence segment.
- `synth_segment`: Synthesizes speech segments using a text-to-speech pipeline.
- `_wav_to_ogg`: Converts a WAV file to OGG format.
- `_mix_background`: Mixes the synthesized voice with background music using `ffmpeg`.
- `render_spec`: Orchestrates the rendering process, including loading the spec, synthesizing segments, mixing background, and writing the final OGG file.
- `_safe_unlink`: Safely deletes a file.
- `_write_manifest`: Writes a manifest file containing metadata about the rendered meditation.

#### Patterns
- **Factory Method**: The `synth_segment` function uses a factory method to get the TTS pipeline.
- **Singleton**: The global configuration is loaded once and reused throughout the file.

#### Dependencies
- `os`, `re`, `json`, `logging`, `subprocess`, `tempfile`, `numpy`, `yaml`, `soundfile`
- `voice.pronunciations.apply`, `voice.tts.get_pipeline`

#### Interfaces
- Exposes functions for loading and rendering MMF specifications (`load_spec`, `render_spec`).
- Internal functions for validation, synthesis, and file operations.

#### Database
- No direct database interactions are present in this file.

#### Configuration
- Uses `CONFIG_PATH` to load global configuration from a YAML file.
- Environment variables are not used directly in this file.

#### Key Logic
- **Validation**: Ensures the MMF specification has required keys and structures.
- **Segment Synthesis**: Uses TTS to synthesize speech segments and generates silence for pause segments.
- **Audio Mixing**: Uses `ffmpeg` to mix voice and background music, handling resampling and volume adjustments.
- **File Handling**: Writes temporary WAV files and converts them to OGG, ensuring cleanup of temporary files.

#### Integration Points
- **TTS Pipeline**: Integrates with the TTS pipeline from `voice.tts.get_pipeline`.
- **Pronunciation Handling**: Uses `voice.pronunciations.apply` to handle text pronunciation.
- **File System**: Interacts with the file system to read specifications, write temporary files, and generate final OGG files.
- **Logging**: Uses Python's `logging` module to log information and errors.

### Detailed Function Descriptions

1. **`load_global_config`**
   - Loads global configuration from a YAML file at `CONFIG_PATH`.

2. **`resolve_background`**
   - Merges global and spec-specific background settings and resolves the background track path.

3. **`load_spec`**
   - Loads and validates the MMF specification from a YAML file.

4. **`_validate`**
   - Validates the structure of the MMF specification to ensure required keys are present.

5. **`flatten_segments`**
   - Flattens the MMF specification into a list of segments for easier processing.

6. **`make_silence`**
   - Generates a silence segment as a NumPy array.

7. **`synth_segment`**
   - Synthesizes speech segments using a TTS pipeline, handling exceptions and fallbacks.

8. **`_wav_to_ogg`**
   - Converts a WAV file to OGG format using `ffmpeg`.

9. **`_mix_background`**
   - Mixes the synthesized voice with background music using `ffmpeg`, handling resampling and volume adjustments.

10. **`render_spec`**
    - Orchestrates the rendering process, including loading the spec, synthesizing segments, mixing background, and writing the final OGG file.

11. **`_safe_unlink`**
    - Safely deletes a file.

12. **`_write_manifest`**
    - Writes a manifest file containing metadata about the rendered meditation.

### Example Usage
```python
from voice.mmf import render_spec

output_path = render_spec("/path/to/spec.yaml")
print(f"Rendered meditation saved to: {output_path}")
```

This file is a crucial part of the Mythos system, handling the complex process of converting a structured meditation specification into an audio file, complete with background music and detailed logging for debugging and monitoring.
