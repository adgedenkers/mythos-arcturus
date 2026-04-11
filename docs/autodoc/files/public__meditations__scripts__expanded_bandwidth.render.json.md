# public/meditations/scripts/expanded_bandwidth.render.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 1326

---

### File: public/meditations/scripts/expanded_bandwidth.render.json

#### Purpose
This JSON file contains metadata and detailed content for a meditation script named "Expanded Bandwidth," authored by Ka'tuar'el. It includes information about the rendered output, background audio, phases, and segments of the meditation.

#### Architecture
The file is structured as a JSON object with several key-value pairs:
- **Metadata**: `title`, `slug`, `author`, `rendered_at`, `source_spec`, `output_file`, `total_duration_s`, `total_duration_min`.
- **Background Audio**: `background` object with `track`, `volume`, `fade_in`, and `fade_out`.
- **Phases**: Array of objects, each representing a phase with `id`, `label`, `tone`, and `speed`.
- **Segments**: Array of objects, each representing a segment with `index`, `type`, `text`, `speed`, `phase`, `tone`, and `duration_s` or `seconds`.

#### Patterns
No design patterns are applicable as this is a JSON configuration file, not a code file.

#### Dependencies
This JSON file does not import or rely on any external dependencies directly. It is a configuration file that is likely read by a script or application to generate or render the meditation.

#### Interfaces
This file is intended to be read by a script or application that processes meditation scripts. It does not expose any interfaces directly.

#### Database
This JSON file does not interact with any databases directly. It is a standalone configuration file.

#### Configuration
This file itself serves as a configuration file. It does not reference any external configuration files or environment variables directly.

#### Key Logic
The key logic embodied in this file is the structured content of the meditation script, including:
- The sequence of phases and their attributes (tone, speed).
- The segments of speech and pauses, each with specific text, speed, and duration.

#### Integration Points
This JSON file is likely integrated into the Mythos system through a script or application that reads this file to:
- Render the meditation audio file.
- Apply background audio and fades.
- Control the pacing and tone of the meditation based on the specified phases and segments.

### Detailed Breakdown

#### Metadata
- **title**: "Expanded Bandwidth"
- **slug**: "expanded_bandwidth"
- **author**: "Ka'tuar'el"
- **rendered_at**: "2026-03-25T23:58:20.892511"
- **source_spec**: "/opt/mythos/public/meditations/scripts/expanded_bandwidth.yaml"
- **output_file**: "/opt/mythos/public/meditations/meditation_20260325_235817_expanded_bandwidth.ogg"
- **total_duration_s**: 1110.3
- **total_duration_min**: 18.5

#### Background Audio
- **track**: "stream_quiet.ogg"
- **volume**: 0.2
- **fade_in**: 4.0
- **fade_out**: 8.0

#### Phases
- **arrival**: Label "Arrival", Tone "warm_grounding", Speed 0.85
- **collapsed_state**: Label "The Collapsed State", Tone "direct_warm", Speed 0.83
- **superposition**: Label "Superposition", Tone "suspended", Speed 0.75
- **observer**: Label "The Observer", Tone "spacious", Speed 0.78
- **entanglement**: Label "Entanglement and Coherence", Tone "deep_field", Speed 0.76
- **tunneling**: Label "Tunneling", Tone "anchoring", Speed 0.77
- **integration**: Label "Integration and Return", Tone "returning_warm", Speed 0.83

#### Segments
- Each segment includes `index`, `type` (speech or pause), `text`, `speed`, `phase`, `tone`, and `duration_s` or `seconds`.
- Example segment:
  ```json
  {
    "index": 0,
    "type": "speech",
    "text": "Close your eyes.",
    "speed": 0.85,
    "phase": "arrival",
    "tone": "warm_grounding",
    "duration_s": 1.95
  }
  ```

This JSON file is a comprehensive configuration for the "Expanded Bandwidth" meditation, detailing the structure and content to be rendered into an audio file.
