# vision/prompts/journal.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 31

---

### File: vision/prompts/journal.py

#### Purpose
This file contains predefined prompt templates for generating journal entries, memory captures, and daily logs based on images. These prompts are used to guide the AI in producing descriptive and reflective text for personal documentation.

#### Architecture
The file consists of three string constants:
- `DESCRIBE_FOR_JOURNAL`: A prompt for describing an image in a reflective and meaningful tone for a personal journal.
- `MEMORY_CAPTURE`: A prompt for capturing and preserving the details of a memory through an image.
- `DAILY_LOG`: A prompt for adding an image to a daily log with structured notes.

#### Patterns
No design patterns are used in this file as it primarily contains string constants.

#### Dependencies
This file does not import any external dependencies. It relies on the Python standard library for string handling.

#### Interfaces
The file exposes three string constants:
- `DESCRIBE_FOR_JOURNAL`
- `MEMORY_CAPTURE`
- `DAILY_LOG`

These constants are intended to be imported and used by other parts of the Mythos system, particularly in modules that interact with image processing and AI text generation.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, the prompts may be used to generate content that is eventually stored in the `now` table in PostgreSQL.

#### Configuration
The file does not use any configuration files or environment variables.

#### Key Logic
The key logic in this file is embodied in the content of the string constants. These prompts are carefully crafted to guide the AI in generating text that is reflective, detailed, and structured, depending on the context (journal entry, memory capture, or daily log).

#### Integration Points
This file integrates with other parts of the Mythos system, particularly:
- **AI Text Generation**: The prompts are used by AI models to generate descriptive text based on images.
- **Database Storage**: The generated text may be stored in the `now` table in PostgreSQL for future reference or analysis.
- **User Interface**: The generated text can be displayed to users through the Mythos UI for review and further action.

### Summary
The `journal.py` file provides essential prompt templates for generating descriptive and reflective text based on images. These prompts are used by other components of the Mythos system to create meaningful personal documentation, which can be stored in the PostgreSQL database for later use.
