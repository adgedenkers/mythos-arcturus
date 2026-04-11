# vision/prompts/symbols.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 38

---

### File: vision/prompts/symbols.py

#### Purpose
This file contains predefined prompts used for symbolic and esoteric analysis of images within the Mythos system. These prompts are designed to guide the AI in interpreting images through various symbolic and spiritual lenses.

#### Architecture
The file consists of several string constants, each representing a different type of prompt for symbolic analysis. There are no classes or functions defined in this file. The data flow is straightforward, with the prompts being used as input to other components of the system that perform the actual analysis.

#### Patterns
No design patterns are used in this file since it only contains static string data.

#### Dependencies
This file does not import any external modules or dependencies. It is a standalone file that provides static data.

#### Interfaces
This file exposes several string constants that can be imported and used by other parts of the system. The primary interface is through these constants:

- `ESOTERIC_ANALYSIS`
- `DREAM_INTERPRETATION`
- `TAROT_STYLE`
- `SYNCHRONICITY_CHECK`

#### Database
This file does not interact with any database tables or Neo4j labels.

#### Configuration
This file does not use any configuration files or environment variables.

#### Key Logic
The key logic in this file is the definition of the prompts themselves. Each prompt is crafted to guide the AI in interpreting images from different symbolic and esoteric perspectives. The prompts are designed to be comprehensive and cover various aspects of symbolic analysis.

#### Integration Points
This file integrates with other subsystems of the Mythos system, particularly those responsible for image analysis and AI-driven interpretation. The prompts are likely used as inputs to the AI models or natural language processing components that generate interpretations of images.

### Detailed Documentation

#### Constants

1. **ESOTERIC_ANALYSIS**
   ```python
   ESOTERIC_ANALYSIS = """Examine this image through a symbolic and esoteric lens.
   Consider:
   - Sacred geometry patterns
   - Archetypal symbols
   - Numerological significance
   - Color symbolism
   - Natural symbols (animals, plants, elements)
   - Cultural or religious iconography

   Describe what resonates spiritually or symbolically.
   Speak with depth but accessibility."""
   ```
   - **Purpose**: This prompt guides the AI to analyze images from an esoteric perspective, covering various symbolic elements such as sacred geometry, archetypes, numerology, color symbolism, and cultural iconography.

2. **DREAM_INTERPRETATION**
   ```python
   DREAM_INTERPRETATION = """This image relates to a dream or vision.
   Analyze it symbolically:
   - Key symbols and their traditional meanings
   - Personal significance (what might it mean to the dreamer)
   - Archetypal themes
   - Messages or guidance it might contain

   Be insightful and intuitive in your interpretation."""
   ```
   - **Purpose**: This prompt is designed to interpret images as if they were part of a dream or vision, focusing on traditional symbolic meanings, personal significance, archetypal themes, and potential messages or guidance.

3. **TAROT_STYLE**
   ```python
   TAROT_STYLE = """Describe this image as if it were a tarot card:
   - What archetype does it represent?
   - Upright meaning (positive aspects)
   - Shadow meaning (challenges)
   - Advice it offers
   - Element and astrological correspondence (if apparent)"""
   ```
   - **Purpose**: This prompt guides the AI to interpret images in the style of tarot card readings, covering archetypes, positive and negative aspects, advice, and elemental or astrological correspondences.

4. **SYNCHRONICITY_CHECK**
   ```python
   SYNCHRONICITY_CHECK = """Examine this image for synchronistic meaning.
   What patterns, symbols, or messages might the universe be communicating?
   Consider timing, repetition, and meaningful coincidence."""
   ```
   - **Purpose**: This prompt is used to interpret images from a synchronistic perspective, focusing on patterns, symbols, and messages that might be indicative of meaningful coincidences or universal communication.

### Integration

These prompts are likely used by other components of the Mythos system, such as the AI-driven image analysis modules, to generate detailed and contextually rich interpretations of images. The prompts are designed to be flexible and can be adapted to various types of images and contexts, making them a crucial part of the symbolic and esoteric analysis capabilities of the system.
