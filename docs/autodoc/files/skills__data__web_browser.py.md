# skills/data/web_browser.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 298

---

### File: skills/data/web_browser.py

#### Purpose
This file defines the `WebBrowserSkill` class, which provides browser automation capabilities to Iris, including scraping content, filling forms, and taking screenshots. It uses Playwright to interact with web pages and determine the relevance of the skill based on the input message.

#### Architecture
- **Class**: `WebBrowserSkill` inherits from `SkillBase`.
- **Methods**:
  - `relevance`: Scores the relevance of the skill for a given message.
  - `execute`: Executes browser automation based on the request.
  - `_classify_action`: Determines the browser action based on the message.
  - `_format_summary`: Formats the browser results for Iris.
  - `_run`: Runs the browser session in a separate thread.
- **Top-level Functions**:
  - `relevance`: Top-level function to score relevance.
  - `execute`: Top-level function to execute browser actions.
  - `_classify_action`: Top-level function to classify the action.
  - `_format_summary`: Top-level function to format the summary.
  - `_run`: Top-level function to run the browser session.

#### Patterns
- **Singleton**: The `WebBrowserSkill` class is designed to be a singleton, as it is instantiated once and used throughout the system.
- **Observer**: The skill observes the incoming messages and determines its relevance based on the message content.

#### Dependencies
- **Imports**: `json`, `logging`, `re`, `sys`, `time`, `threading`, `typing`
- **External Libraries**: Uses Playwright via the `/opt/mythos/browser/core` module.

#### Interfaces
- **Public Methods**:
  - `relevance(message: str, context: Optional[Dict] = None) -> float`: Determines the relevance of the skill for a given message.
  - `execute(request: SkillRequest) -> SkillResponse`: Executes the browser action based on the request and returns a response.

#### Database
- **References**: The file references several PostgreSQL tables (`JavaScript`, `pages`, `typing`, `engine`, `the`, `message`, `browser`, `if`), but these are likely placeholders or misinterpretations of the code.

#### Configuration
- **Environment Variables**: No specific environment variables are used.
- **Config Files**: No specific configuration files are used.

#### Key Logic
- **Relevance Scoring**:
  - Uses predefined lists (`BROWSER_EXPLICIT`, `BROWSER_HINTS`, `SEARCH_SIGNALS`) and regular expressions to determine the relevance of the skill based on the message content.
- **Browser Automation**:
  - Uses Playwright to navigate to URLs, take screenshots, extract tables, and links.
  - Determines the action to take based on the message content.
- **Result Formatting**:
  - Formats the results into a structured summary for Iris.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the broader Mythos system.
- **BrowserSession**: Uses the `BrowserSession` class from `/opt/mythos/browser/core` to handle browser interactions.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` classes to handle requests and responses within the Mythos system.

### Detailed Analysis

#### Relevance Scoring
The `relevance` method evaluates the message content to determine if the `WebBrowserSkill` should be activated. It checks for explicit browser commands, URLs, and hints that suggest the need for browser automation. The method returns a relevance score based on the presence of these signals.

#### Browser Automation
The `execute` method handles the execution of browser actions. It extracts the URL from the message, determines the action to take (e.g., screenshot, extract tables), and runs the browser session in a separate thread to ensure asynchronous compatibility. The method returns a `SkillResponse` object containing the results of the browser action.

#### Action Classification
The `_classify_action` method determines the specific action to take based on the message content. It checks for keywords related to screenshots, table extraction, link extraction, and general page reading.

#### Result Formatting
The `_format_summary` method formats the results of the browser action into a structured summary. It includes details such as the URL, title, and specific content based on the action (e.g., screenshots, tables, links).

#### Thread Management
The `_run` method runs the browser session in a separate thread to ensure that the browser operations do not block the main execution flow. This method handles the import of the `BrowserSession` class and performs the necessary browser actions.

### Conclusion
The `WebBrowserSkill` class provides comprehensive browser automation capabilities to Iris, handling a wide range of tasks from simple page scraping to complex interactions with web pages. It integrates seamlessly with the Mythos system and leverages Playwright for efficient and reliable browser automation.
