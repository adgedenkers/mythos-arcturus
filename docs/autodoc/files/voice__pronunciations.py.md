# voice/pronunciations.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 21

---

### File: voice/pronunciations.py

#### Purpose
This file contains a pronunciation substitution map and a function to apply these substitutions to input text for the Iris TTS (Text-to-Speech) system.

#### Architecture
- **Data Structure**: The file uses a dictionary `SUBSTITUTIONS` to map specific words or phrases to their phonetic pronunciations.
- **Function**: The `apply` function takes a string `text` as input, processes it to apply the substitutions, and returns the modified text.

#### Patterns
- **No Design Patterns**: This file does not employ any specific design patterns such as factory, singleton, or observer. It is a straightforward implementation of a substitution map.

#### Dependencies
- **Built-in Python Modules**: Uses `str.split` and `str.replace` methods from the built-in `str` class.

#### Interfaces
- **Function Interface**: The `apply` function is the primary interface exposed by this file. It accepts a single string argument `text` and returns a modified string with pronunciation substitutions applied.

#### Database
- **No Database Interaction**: This file does not interact with any databases or Neo4j labels.

#### Configuration
- **No Configuration Files**: This file does not use any configuration files or environment variables.

#### Key Logic
- **Text Normalization**: The `apply` function first normalizes the input text by splitting it into words and then joining them back with a single space, effectively removing extra spaces.
- **Substitution Application**: The function iterates over the `SUBSTITUTIONS` dictionary and replaces occurrences of each key (word or phrase) with its corresponding value (phonetic pronunciation).

#### Integration Points
- **Iris TTS System**: This file is likely integrated into the Iris TTS system where the `apply` function is used to preprocess text before it is converted to speech. This ensures that specific names and phrases are pronounced correctly.

### Detailed Analysis

#### Purpose
The `pronunciations.py` file is designed to handle specific pronunciation substitutions for the Iris TTS system. It contains a dictionary of words and their phonetic pronunciations and a function to apply these substitutions to any given text.

#### Architecture
- **SUBSTITUTIONS Dictionary**: This dictionary contains key-value pairs where the keys are words or phrases that need specific pronunciation and the values are their phonetic pronunciations.
- **apply Function**: This function takes a string `text` as input, normalizes the text to remove extra spaces, and then applies the substitutions defined in the `SUBSTITUTIONS` dictionary.

#### Patterns
- **No Design Patterns**: The file is a simple utility script that does not follow any specific design patterns.

#### Dependencies
- **Built-in Python Modules**: The function uses the `str.split` and `str.replace` methods from the built-in `str` class.

#### Interfaces
- **apply Function**: The `apply` function is the primary interface. It accepts a string `text` and returns a modified string with the substitutions applied.

#### Database
- **No Database Interaction**: This file does not interact with any databases or Neo4j labels.

#### Configuration
- **No Configuration Files**: The file does not use any configuration files or environment variables.

#### Key Logic
- **Text Normalization**: The function normalizes the input text by splitting it into words and then joining them with a single space.
- **Substitution Application**: The function iterates over the `SUBSTITUTIONS` dictionary and replaces each occurrence of a key with its corresponding value.

#### Integration Points
- **Iris TTS System**: The `apply` function is likely used in the Iris TTS system to preprocess text before it is converted to speech, ensuring that specific names and phrases are pronounced correctly.
