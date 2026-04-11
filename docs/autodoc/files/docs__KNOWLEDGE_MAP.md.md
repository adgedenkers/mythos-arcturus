# docs/KNOWLEDGE_MAP.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 109

---

### Documentation for `docs/KNOWLEDGE_MAP.md`

#### Purpose
This file serves as a comprehensive knowledge map for the Mythos system, detailing key entities, financial accounts, bills, routines, and data routing mechanisms. It is auto-generated from the database and is designed to provide a structured overview of the system's knowledge base.

#### Architecture
The file is structured into several sections, each containing specific details:
- **People**: Lists individuals and their aliases.
- **Financial Accounts**: Details of various financial accounts including abbreviations, names, and types.
- **Bills & Utilities**: Information about recurring bills and their due dates.
- **Active Routines**: Lists of routines and their frequencies.
- **Data Routing**: Describes how different types of data are routed to specific tables in the database.
- **Locations**: Common locations relevant to the system.
- **Notes**: Additional notes and clarifications.

#### Patterns
- **Static/Dynamic Sections**: The file maintains static sections (People, Locations, Notes) and dynamically rebuilds sections (Financial Accounts, Bills & Utilities, Active Routines) based on database changes.
- **Auto-Generation**: The file is auto-generated, indicating a pattern where data is extracted and formatted from the database.

#### Dependencies
- **Database**: The file relies on data from the database to populate dynamic sections.
- **Auto-Generation Script**: An underlying script or process that generates this file from the database.

#### Interfaces
- **Read-Only Interface**: The file is intended for reading and does not expose any direct interfaces for modification. Instead, changes are made through the database and reflected in this file via the auto-generation process.

#### Database
- **Tables/Labels**: The file references several tables and labels in the database:
  - `bill_overrides` table
  - `life_events` table
  - `calendar_events` table
  - `idea_backlog` table
  - `routine_completions` table

#### Configuration
- **Environment Variables**: No explicit configuration files or environment variables are mentioned, but the auto-generation process might rely on configuration settings.
- **Auto-Generation Timestamp**: The file includes a timestamp indicating when it was last rebuilt.

#### Key Logic
- **Data Extraction and Formatting**: The key logic involves extracting data from the database and formatting it into the structured sections of the file.
- **Dynamic Section Rebuilding**: The logic for rebuilding dynamic sections based on changes in the database.

#### Integration Points
- **Database Integration**: The file integrates with the Mythos database to extract and display data.
- **Auto-Generation Process**: The file is part of an auto-generation process that ensures it is up-to-date with the latest data from the database.

### Summary
The `docs/KNOWLEDGE_MAP.md` file serves as a comprehensive knowledge map for the Mythos system, detailing key entities, financial accounts, bills, routines, and data routing mechanisms. It is auto-generated from the database, maintaining static sections while dynamically rebuilding others based on database changes. The file integrates with the Mythos database and relies on an underlying auto-generation process to ensure it remains up-to-date.
