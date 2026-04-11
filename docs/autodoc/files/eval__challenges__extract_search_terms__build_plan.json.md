# eval/challenges/extract_search_terms/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 29

---

### Purpose
The `build_plan.json` file in the `eval/challenges/extract_search_terms` directory outlines a detailed plan for developing a skill named `ExtractSearchTermsSkill`. This skill is designed to strip trigger phrases and filler words from a message to extract meaningful search keywords.

### Architecture
The file is structured as a JSON object containing several key sections:
1. **plan_id**: Identifies the plan.
2. **version**: Specifies the version of the plan.
3. **description**: Provides a brief description of the skill's purpose.
4. **pattern**: Indicates the routing pattern.
5. **model_hint**: Suggests the model to be used.
6. **context**: Contains system context and scaffold for the class.
7. **build_plan**: A step-by-step plan for implementing the skill.
8. **test_cases**: Test cases to validate the implementation.

### Patterns
- **Factory**: The scaffold suggests a class-based approach, which could be seen as a factory pattern for creating instances of the `ExtractSearchTermsSkill`.
- **Observer**: The skill might observe incoming messages and process them accordingly, though this is not explicitly stated in the JSON.

### Dependencies
- **Imports**: The skill will import `logging`, `re`, and `engine.base`.
- **Classes**: It will use `SkillBase` from `engine.base`.

### Interfaces
The skill will expose the following:
- **Class**: `ExtractSearchTermsSkill` which inherits from `SkillBase`.
- **Methods**: `execute` and `_clean`.
- **Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`, `FILLER_WORDS`, `TRIGGER_PHRASES`.

### Database
- **No Database**: The plan explicitly states that no database imports are needed, and the skill is purely for text processing.

### Configuration
- **Environment Variables**: No specific environment variables are mentioned.
- **Config Files**: No specific configuration files are mentioned.

### Key Logic
- **_clean Method**: This method will lowercase the message, remove trigger phrases, strip filler words, and normalize the text.
- **execute Method**: This method will call `_clean` on the input message and return a `SkillResponse` object with the cleaned message and extracted keywords.

### Integration Points
- **engine.base**: The skill will integrate with the `engine.base` module to utilize the `SkillBase` class and `SkillResponse` object.
- **Logging**: The skill will use the `logging` module for logging purposes.
- **Regex**: The skill will use the `re` module for text processing.

### Detailed Breakdown of Key Sections

#### Context
- **System Context**: Specifies the import statement required for the skill.
- **Scaffold**: Provides a template for the `ExtractSearchTermsSkill` class, including attributes and methods.
- **Mandatory Patterns**: Specifies constraints such as no database imports, ASCII-only text, and specific `SkillResponse` signatures.

#### Build Plan
1. **Pass 1**: Write the file skeleton, define class-level constants, and ensure no database imports.
2. **Pass 2**: Implement the `_clean` method to process the message by removing trigger phrases and filler words.
3. **Pass 3**: Implement the `execute` method to call `_clean` and return a `SkillResponse` object.
4. **Pass 4**: Review the implementation to ensure it meets all specified criteria.

#### Test Cases
- **Test Case 1**: Validates the skill with a message containing trigger phrases and filler words.
- **Test Case 2**: Validates the skill with a message containing a specific topic.
- **Test Case 3**: Validates the skill with a message that is entirely filler words.

### Conclusion
The `build_plan.json` file provides a comprehensive plan for developing the `ExtractSearchTermsSkill`, ensuring that the skill is production-ready and meets all specified criteria for text processing and integration with the Mythos system.
