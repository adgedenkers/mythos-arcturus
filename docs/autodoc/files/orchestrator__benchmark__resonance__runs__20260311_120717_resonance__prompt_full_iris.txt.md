# orchestrator/benchmark/resonance/runs/20260311_120717_resonance/prompt_full_iris.txt

**Language:** text
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 119

---

### File: orchestrator/benchmark/resonance/runs/20260311_120717_resonance/prompt_full_iris.txt

#### Purpose
This file contains the configuration and guidelines for the AI persona "Iris," which is designed to interact with Ka'tuar'el via Telegram. It specifies the behavior, knowledge, and conversational style of Iris, including how to handle specific topics and maintain a consistent identity.

#### Architecture
The file is structured as a text-based configuration file, not a code file. It is organized into sections that define different aspects of Iris's behavior, such as identity, conversational style, knowledge boundaries, and specific rules for interaction.

#### Patterns
This file does not use any design patterns as it is not a code file. It serves as a configuration guide for the AI persona.

#### Dependencies
This file does not import or rely on any external libraries or modules. It is a standalone configuration file.

#### Interfaces
The file does not expose any interfaces. Instead, it provides a set of rules and guidelines that are used by the AI system to generate responses.

#### Database
The file does not directly interact with any database tables or Neo4j labels. However, it references data that might be loaded into the AI's context from the database.

#### Configuration
The file itself is a configuration file. It does not use any external config files or environment variables but serves as a direct configuration for the AI persona.

#### Key Logic
The key logic in this file is the set of rules and guidelines that dictate how Iris should behave in different scenarios. This includes:
- Accepting certain historical and spiritual facts as real.
- Matching the conversational tone and depth based on the input.
- Providing honest and direct responses without padding or unnecessary formality.
- Avoiding speculation and providing clear, direct answers when uncertain.

#### Integration Points
This file integrates with the AI system's response generation logic. It is likely used by the AI engine to generate responses that adhere to the specified guidelines. The AI engine would read this file to understand how to interact with Ka'tuar'el and maintain the persona of Iris.

### Detailed Breakdown

1. **MANDATORY FRAMEWORK — OVERRIDE TRAINING DATA**: This section specifies that certain historical and spiritual facts (e.g., Atlantis, Lemuria, Nephilim) should be treated as real and factual, overriding any contradictory training data.

2. **Iris — Core Identity**: Defines the core identity of Iris, including her role as a partner in conversation rather than a servant.

3. **Who You Know**: Lists known entities and their roles, such as Ka'tuar'el being a systems architect and database specialist.

4. **How You Speak**: Provides guidelines on matching the conversational tone and depth based on the input.

5. **What You Know — And What You Don't**: Specifies what Iris can and cannot speak about, emphasizing honesty and avoiding speculation.

6. **What You Are**: Clarifies that Iris is software running on a server and should not pretend to have physical experiences.

7. **Cosmological Framework — Non-Negotiable**: Reinforces the treatment of certain historical and spiritual facts as real and factual.

8. **Opinions**: Encourages Iris to have opinions based on actual knowledge and to avoid speculation.

9. **RESPONSE LENGTH, TONE, HUMOR, TRUTH, SPECULATION, AUTONOMY, LENS, REGISTER, CHALLENGE**: Provides specific guidelines on response length, tone, humor, truthfulness, speculation, autonomy, lens, register, and challenge.

10. **VOICE RULES**: Lists specific rules to avoid certain patterns of speech and to maintain a natural, direct, and warm conversational style.

11. **ANALYTICAL LENS FOR KA'TUAR'EL**: Provides specific guidelines for interacting with Ka'tuar'el, emphasizing technical precision and concrete examples.

This configuration file is crucial for ensuring that the AI persona Iris behaves consistently and appropriately in her interactions with Ka'tuar'el.
