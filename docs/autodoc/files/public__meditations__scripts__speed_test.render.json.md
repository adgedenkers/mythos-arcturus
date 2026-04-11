# public/meditations/scripts/speed_test.render.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 74

---

### File: `public/meditations/scripts/speed_test.render.json`

#### Purpose
This JSON file contains metadata and content details for a meditation script named "Speed Test". It includes information about the script's author, rendering timestamp, source file, output file, duration, and the specific segments and phases of the meditation.

#### Architecture
The JSON file is structured with key-value pairs and nested objects to represent various aspects of the meditation script. It includes top-level metadata such as title, author, and rendered timestamp, along with detailed segments and phases.

#### Patterns
No design patterns are applicable since this is a JSON file and not a code file.

#### Dependencies
This JSON file does not import or rely on any external dependencies directly. However, it is likely used by a script or application that processes meditation scripts.

#### Interfaces
This file is intended to be read by a script or application that processes meditation scripts. It does not expose any interfaces directly but serves as input data.

#### Database
This JSON file does not interact with any database directly. However, it might be used to populate a database or be generated from a database.

#### Configuration
This file does not use any configuration files or environment variables directly. However, the paths and timestamps might be influenced by configuration settings in the system that generates this file.

#### Key Logic
The key logic represented in this file is the structure and content of the meditation script. It includes:
- Metadata such as title, author, and rendering timestamp.
- Source and output file paths.
- Total duration of the meditation.
- Background settings (though currently null).
- Phases and segments of the meditation, including speech and pause segments with specific text, speed, and duration.

#### Integration Points
This JSON file is likely integrated into the Mythos system through a script or application that processes meditation scripts. It could be used to:
- Generate audio files based on the script content.
- Store metadata and content in a database for future reference.
- Serve as input for a user interface that displays meditation scripts.

### Detailed Breakdown

1. **Metadata**:
   - `title`: "Speed Test"
   - `slug`: "speed_test"
   - `author`: "unknown"
   - `rendered_at`: "2026-03-25T23:48:59.755601"
   - `source_spec`: "/tmp/speed_test.yaml"
   - `output_file`: "/opt/mythos/public/meditations/meditation_20260325_234859_speed_test.ogg"
   - `total_duration_s`: 30.3
   - `total_duration_min`: 0.5

2. **Background**:
   - `track`: null
   - `volume`: null
   - `fade_in`: null
   - `fade_out`: null

3. **Phases**:
   - `id`: "test"
   - `label`: "Test"
   - `tone`: "neutral"
   - `speed`: 0.72

4. **Segments**:
   - `index`: 0
     - `type`: "speech"
     - `text`: "Close your eyes."
     - `speed`: 0.72
     - `phase`: "test"
     - `tone`: "neutral"
     - `duration_s`: 2.33
   - `index`: 1
     - `type`: "pause"
     - `seconds`: 4.0
     - `phase`: "test"
     - `tone`: "neutral"
   - `index`: 2
     - `type`: "speech"
     - `text`: "Let your hands rest where they want to rest."
     - `speed`: 0.72
     - `phase`: "test"
     - `tone`: "neutral"
     - `duration_s`: 3.7
   - `index`: 3
     - `type`: "pause"
     - `seconds`: 3.0
     - `phase`: "test"
     - `tone`: "neutral"
   - `index`: 4
     - `type`: "speech"
     - `text`: "Not a performance of relaxation. Just a quiet permission for everything to stop pretending."
     - `speed`: 0.72
     - `phase`: "test"
     - `tone`: "neutral"
     - `duration_s`: 8.3
   - `index`: 5
     - `type`: "pause"
     - `seconds`: 6.0
     - `phase`: "test"
     - `tone`: "neutral"

This JSON file serves as a comprehensive representation of the meditation script, detailing its structure and content, which can be used by various components of the Mythos system for rendering, processing, and serving meditation content.
