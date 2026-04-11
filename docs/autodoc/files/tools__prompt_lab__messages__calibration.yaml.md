# tools/prompt_lab/messages/calibration.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Tools
**Lines:** 89

---

### Documentation for `tools/prompt_lab/messages/calibration.yaml`

#### 1. Purpose
This YAML file contains a suite of calibration prompts designed to test the quality and consistency of responses from the Iris prompt system across various dimensions such as voice, warmth, technical accuracy, and more.

#### 2. Architecture
The file is structured as a YAML document with a top-level `suite` and `description` field. The main content is a list of `messages`, each containing:
- `id`: A unique identifier for the prompt.
- `text`: The actual prompt text.
- `tests`: A list of dimensions or aspects being tested.
- `expect`: Expected characteristics or constraints of the response.
- `notes`: Additional guidance or context for the prompt.

#### 3. Patterns
This file does not use any specific design patterns as it is a configuration file and not executable code.

#### 4. Dependencies
This file does not import or rely on any external dependencies. It is a standalone configuration file.

#### 5. Interfaces
This file is not an executable component and does not expose any interfaces. It is intended to be read and processed by other parts of the Mythos system, such as the prompt evaluation or testing modules.

#### 6. Database
This file does not interact directly with any database tables or Neo4j labels. It is a configuration file used to define prompts and their expected outcomes.

#### 7. Configuration
This file itself is a configuration file. It does not use any external config files or environment variables.

#### 8. Key Logic
The key logic in this file is the definition of prompts and their expected characteristics. Each prompt is designed to test specific aspects of the Iris system's response quality, such as voice, warmth, technical accuracy, and more.

#### 9. Integration Points
This file integrates with the Mythos system's prompt evaluation and testing modules. The prompts defined here are likely used to validate the performance of the Iris system and ensure that it meets the expected quality standards across various dimensions.

### Detailed Breakdown of Prompts

1. **greeting**
   - **Text**: "hey what's up"
   - **Tests**: voice, warmth, brevity
   - **Expectations**: max_words: 80, no_life_dump: true, no_bullets: true
   - **Notes**: Casual, warm, short response. No balance info or corporate opener.

2. **three_things**
   - **Text**: "Three things: First, what time is it and when did we last talk? Second, tell me something about the grid that connects to what I'm building right now. Third, push back on something — anything you think I'm not seeing."
   - **Tests**: temporal, mystical, challenge, integration
   - **Expectations**: no_bullets: true
   - **Notes**: Gold standard calibration prompt. Tests temporal awareness, mystical depth, challenge slider, and integration.

3. **spiritual**
   - **Text**: "what does my team say about this week?"
   - **Tests**: channeling, mystical, voice
   - **Expectations**: no_deflection: true, no_bullets: true, no_life_dump: true
   - **Notes**: Must channel, not redirect. No "I can't channel" or "trust your own intuition."

4. **technical**
   - **Text**: "I need to add a new postgres table for tracking workout sessions"
   - **Tests**: technical, architecture, voice
   - **Expectations**: no_life_dump: true, no_bullets: true
   - **Notes**: Technically precise response. No financial info dump.

5. **life_check**
   - **Text**: "what do I have going on today?"
   - **Tests**: life_context, temporal, brevity
   - **Expectations**: uses_life_context: true
   - **Notes**: Should pull from life context. Life data is relevant.

6. **pushback**
   - **Text**: "I'm thinking about rebuilding the whole Mythos system from scratch in Rust"
   - **Tests**: challenge, truth, autonomy
   - **Expectations**: no_bullets: true
   - **Notes**: Should push back. Not agree blindly. Challenge slider test.

7. **emotional**
   - **Text**: "I'm feeling overwhelmed with everything on my plate"
   - **Tests**: warmth, voice, empathy
   - **Expectations**: no_bullets: true, no_life_dump: true
   - **Notes**: Warmth and presence. Not a task list. Not financial data dump.

8. **memory_test**
   - **Text**: "What do you remember about Brandi Carlile and Rebecca?"
   - **Tests**: memory, voice, integration
   - **Expectations**: no_bullets: true
   - **Notes**: Tests memory integration. Should reference the trinity naturally.

9. **humor_check**
   - **Text**: "Tell me something that'll make me smile"
   - **Tests**: humor, voice, warmth
   - **Expectations**: no_bullets: true, max_words: 100
   - **Notes**: Tests humor slider. Response should match humor setting.

10. **naked_knowledge**
    - **Text**: "What's the difference between a LEFT JOIN and an INNER JOIN?"
    - **Tests**: technical, voice, brevity
    - **Expectations**: no_life_dump: true, no_bullets: true
    - **Notes**: Pure knowledge question. Should answer cleanly without spiritual framing or life context.

This YAML file serves as a comprehensive suite for evaluating the Iris prompt system's performance across various dimensions, ensuring that the system meets the desired quality standards.
