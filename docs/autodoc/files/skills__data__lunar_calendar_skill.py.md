# skills/data/lunar_calendar_skill.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 173

---

### Documentation for `skills/data/lunar_calendar_skill.py`

#### Purpose
This file contains the `LunarCalendarSkill` class, which is responsible for handling user queries related to generating Seraphe's lunar calendar. It checks if the query matches specific keywords and, if so, generates the lunar calendar PDF using an external generator script.

#### Architecture
The file contains a single class `LunarCalendarSkill` that inherits from `SkillBase`. The class has four methods:
- `can_handle(query: str)`: Determines if the skill can handle the given query.
- `execute(query: str, context: dict = None)`: Executes the lunar calendar generation process.
- `_parse_date(query: str)`: Parses the date from the query.
- `_month_name(month: int)`: Converts a month number to its name.

Additionally, there are four top-level functions with the same names as the class methods, but these are not used within the class and seem to be redundant.

#### Patterns
- **Factory Method**: The `LunarCalendarSkill` class can be seen as a factory method for handling specific types of queries.
- **Singleton**: The class does not enforce singleton behavior, but it can be used as a singleton if instantiated once.

#### Dependencies
- **Imports**: `os`, `sys`, `subprocess`, `re`, `datetime`, `pathlib`, and `SkillBase` from `skills.engine.skill_base`.
- **External Scripts**: Uses `/opt/mythos/astrology/seraphe_lunar_generator.py` to generate the lunar calendar PDF.

#### Interfaces
- **Public Methods**: `can_handle(query: str)` and `execute(query: str, context: dict = None)` are the primary methods exposed to other parts of the system.
- **SkillResponse**: The `execute` method returns a `SkillResponse` object containing the result of the lunar calendar generation.

#### Database
- **References**: The file does not directly interact with any PostgreSQL tables or Neo4j labels. The references to `datetime`, `pathlib`, `skills`, and `query` are likely part of the import statements and not actual database references.

#### Configuration
- **Environment Variables**: No explicit environment variables are used.
- **Paths**: Uses hardcoded paths such as `/opt/mythos`, `/opt/mythos/astrology/seraphe_lunar_generator.py`, and `/opt/mythos/outputs/lunar_calendars`.

#### Key Logic
- **Query Handling**: The `can_handle` method checks if the query contains any of the predefined trigger keywords.
- **Date Parsing**: The `_parse_date` method extracts the year and month from the query, defaulting to the current month if not specified.
- **Calendar Generation**: The `execute` method runs the external generator script to create the lunar calendar PDF. It checks if the file already exists and returns the appropriate response.

#### Integration Points
- **SkillEngine**: The `LunarCalendarSkill` class is designed to integrate with the SkillEngine, which automatically discovers and loads skills based on the class definition.
- **Ollama**: The external generator script (`seraphe_lunar_generator.py`) likely uses Ollama for generating the lunar calendar, which is a dependency for the skill's functionality.

### Summary
The `LunarCalendarSkill` class is a specialized skill for generating lunar calendars based on user queries. It leverages an external generator script and handles date parsing and file existence checks to provide a seamless experience for users. The class integrates with the broader Mythos system through the SkillEngine and relies on external scripts for the actual calendar generation.
