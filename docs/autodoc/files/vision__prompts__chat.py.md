# vision/prompts/chat.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 33

---

### File: `vision/prompts/chat.py`

#### Purpose
This file contains predefined prompt strings used for generating conversational responses about images. These prompts guide the AI in providing detailed, quick, and comparative analyses of images.

#### Architecture
The file is structured as a collection of string constants, each representing a different type of prompt for image analysis. There are no classes or functions defined in this file; it solely serves as a repository for these prompt strings.

#### Patterns
No design patterns are used in this file as it is a simple collection of string constants.

#### Dependencies
This file does not import any external libraries or modules. It is self-contained and only relies on the Python standard library.

#### Interfaces
This file exposes several string constants that can be imported and used by other parts of the system to generate conversational responses about images. The constants are:
- `GENERAL_DESCRIPTION`
- `DETAILED_ANALYSIS`
- `QUICK_SUMMARY`
- `QUESTION_ANSWER`
- `COMPARE_IMAGES`

#### Database
This file does not interact directly with any database tables or Neo4j labels. However, it is referenced in the context of the `details` table in PostgreSQL, which might use these prompts for generating responses.

#### Configuration
This file does not use any configuration files or environment variables. The prompt strings are hardcoded and do not change based on external configurations.

#### Key Logic
The key logic of this file is encapsulated in the prompt strings themselves. These strings guide the AI in generating responses that are conversational, detailed, quick, specific, and comparative, respectively.

#### Integration Points
This file integrates with other parts of the Mythos system, particularly the components responsible for image analysis and generating conversational responses. The prompt strings defined here are likely used by the AI subsystems to generate appropriate responses based on the content of the images.

### Detailed Documentation

#### Constants
- **`GENERAL_DESCRIPTION`**: A prompt to describe the image in a conversational and helpful manner, pointing out interesting details.
- **`DETAILED_ANALYSIS`**: A prompt to provide a thorough analysis of the image, covering the main subject, setting, colors, composition, mood, text, and notable details.
- **`QUICK_SUMMARY`**: A prompt to provide a brief summary of the image in 1-2 sentences.
- **`QUESTION_ANSWER`**: A prompt to answer specific questions about the image, referencing visible elements and acknowledging uncertainty when necessary.
- **`COMPARE_IMAGES`**: A prompt to compare multiple images, highlighting similarities, differences, progressions, and standout features.

### Example Usage
```python
from vision.prompts.chat import GENERAL_DESCRIPTION

# Example usage in an image analysis function
def generate_response(image_data):
    # Use the GENERAL_DESCRIPTION prompt to generate a response
    response = ollama.generate_response(image_data, GENERAL_DESCRIPTION)
    return response
```

This file serves as a central repository for the prompt strings used in the Mythos system to ensure consistency and quality in the conversational responses generated about images.
