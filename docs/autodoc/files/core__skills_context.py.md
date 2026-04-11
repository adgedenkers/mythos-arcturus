# core/skills_context.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 176

---

### Documentation for `core/skills_context.py`

#### Purpose
This file provides functionality to build a skills awareness block for Iris's system prompt and to read specific skill files from the skills directory.

#### Architecture
The file consists of two primary functions:
1. `build_skills_context`: Constructs a string that describes Iris's skills and how to use them.
2. `get_skill_content`: Reads the content of a specific skill file based on a given relative path.

The file uses global constants for the skills directory and registry file, and it includes predefined strings for data skill awareness and manual skill awareness.

#### Patterns
- **Singleton Pattern**: The `logger` object is created once and reused throughout the file.
- **Configuration Management**: The skills directory and registry file paths are managed as constants.

#### Dependencies
- `logging`: For logging warnings and errors.
- `yaml`: For potential future use with the registry file.
- `pathlib`: For handling file paths.
- `typing`: For type hinting.

#### Interfaces
- `build_skills_context`: Exposes a function that returns a string describing Iris's skills.
- `get_skill_content`: Exposes a function that reads and returns the content of a specific skill file or `None` if the file is not found.

#### Database
- **PostgreSQL Tables**: The file references several PostgreSQL tables (`Iris`, `pathlib`, `typing`, `web_search`, `a`, `skills`), but these are not directly used in the file. They are likely referenced elsewhere in the system.

#### Configuration
- **Environment Variables**: No environment variables are used directly in this file.
- **Config Files**: The file uses a constant `SKILLS_DIR` to point to the skills directory and `REGISTRY_FILE` to point to the registry file.

#### Key Logic
- **Skill Awareness Block Construction**: The `build_skills_context` function concatenates predefined strings (`DATA_SKILL_AWARENESS` and `MANUAL_SKILL_AWARENESS`) to form a comprehensive skills awareness block.
- **Skill File Reading**: The `get_skill_content` function reads the content of a skill file from the specified path, handling cases where the file does not exist or cannot be read.

#### Integration Points
- **Skill Engine**: The skills awareness block is intended to be injected into Iris's system prompt, providing her with context about available skills.
- **Skill Files**: The `get_skill_content` function is used to retrieve the content of specific skill files, which are likely used by other parts of the system to execute or guide Iris through specific tasks.

### Detailed Analysis

#### `build_skills_context`
- **Purpose**: Constructs a comprehensive skills awareness block that describes Iris's skills and how to use them.
- **Logic**: Concatenates predefined strings (`DATA_SKILL_AWARENESS` and `MANUAL_SKILL_AWARENESS`) and returns the result.
- **Output**: A string that is under 400 tokens, designed to be injected into Iris's system prompt.

#### `get_skill_content`
- **Purpose**: Reads the content of a specific skill file.
- **Logic**: Constructs the full path to the skill file, checks if the file exists, and reads its content. If the file does not exist or cannot be read, it logs a warning or error and returns `None`.
- **Output**: The content of the skill file as a string, or `None` if the file is not found or cannot be read.

### Example Usage
```python
# Build the skills awareness block
skills_context = build_skills_context()
print(skills_context)

# Get the content of a specific skill file
skill_content = get_skill_content('builder/build_patch.md')
if skill_content:
    print(skill_content)
else:
    print("Skill file not found.")
```

### Conclusion
This file is a crucial component of the Mythos system, providing Iris with the necessary context about her skills and the ability to access specific skill files. It integrates with the broader system by providing the skills awareness block and skill file content, which are essential for Iris's operation and decision-making.
