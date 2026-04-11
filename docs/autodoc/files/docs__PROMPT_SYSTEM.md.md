# docs/PROMPT_SYSTEM.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 398

---

### Purpose
The `PROMPT_SYSTEM.md` file serves as a comprehensive reference for the Iris Prompt System, detailing the flow of message processing, the structure of the prompt assembler, and the configuration of various prompt layers and skill activation mechanisms.

### Architecture
The file is structured into several sections, each detailing different aspects of the Iris Prompt System:
- **How Iris Gets Her Prompt**: Describes the pipeline from Telegram message to Ollama chat API response.
- **The Prompt Assembler**: Explains the assembly process and the order of sections.
- **Prompt Files**: Lists active and legacy prompt files.
- **Layer Configuration**: Details the configuration of prompt layers and their current status.
- **Skill Engine**: Describes the skill activation process and mutual exclusion rules.
- **Browser Automation**: Details the browser automation process and CLI usage.
- **Sovereign Alignment Test**: Describes a tool to test model compliance with the cosmological framework.

### Patterns
- **Configuration Management**: The use of YAML files (`prompt_layers.yaml`) to manage configuration.
- **Layered Architecture**: The prompt assembler uses a layered approach to build the system prompt.

### Dependencies
- **Files**: `/opt/mythos/core/prompt_assembler.py`, `/opt/mythos/prompts/prompt_layers.yaml`, `/opt/mythos/skills/engine/engine.py`, `/opt/mythos/skills/engine/router.py`, `/opt/mythos/browser/core.py`, `/opt/mythos/skills/data/web_browser.py`, `/opt/mythos/bin/iris-browse`, `/opt/mythos/bin/sovereign-align-test`
- **Libraries**: Playwright for browser automation

### Interfaces
- **Prompt Assembler**: Exposes `assemble_system_prompt()`
- **Skill Engine**: Exposes `process_sync()`
- **Browser Automation**: Exposes `BrowserSession` API

### Database
- **Queries**: `life_context.py` queries the database for life context data.
- **Tables/Labels**: Not explicitly detailed in the file, but `life_context.py` likely interacts with relevant tables or labels in the database.

### Configuration
- **Files**: `/opt/mythos/prompts/prompt_layers.yaml`
- **Environment Variables**: Not explicitly mentioned in the file.

### Key Logic
- **Prompt Assembly**: The `assemble_system_prompt()` function reads `prompt_layers.yaml` and assembles the system prompt based on enabled layers.
- **Skill Activation**: The `process_sync()` function in `SkillEngine` processes messages and activates relevant skills based on their relevance score.
- **Browser Automation**: Uses Playwright to drive headless Chromium for web interactions.
- **Sovereign Alignment Test**: Tests model compliance with the cosmological framework and skill data.

### Integration Points
- **Telegram**: Messages are received via Telegram and processed by `mythos-bot.service`.
- **API**: The processed message is sent to the Ollama chat API.
- **Skills Directory**: Skills are auto-discovered from `/opt/mythos/skills/data/`.
- **Database**: `life_context.py` queries the database for life context data.
- **CLI**: `iris-browse` and `sovereign-align-test` provide command-line interfaces for browser automation and model testing.

### Summary
The `PROMPT_SYSTEM.md` file provides a detailed overview of the Iris Prompt System, including the message processing pipeline, prompt assembly, skill activation, and browser automation. It serves as a critical reference for understanding and maintaining the system's architecture and configuration.
