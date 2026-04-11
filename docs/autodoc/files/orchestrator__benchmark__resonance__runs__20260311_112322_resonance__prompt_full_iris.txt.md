# orchestrator/benchmark/resonance/runs/20260311_112322_resonance/prompt_full_iris.txt

**Language:** text
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 119

---

### Documentation for `orchestrator/benchmark/resonance/runs/20260311_112322_resonance/prompt_full_iris.txt`

#### Purpose
This file contains a detailed prompt for the AI entity named Iris, defining its behavior, knowledge, and interaction style when communicating via Telegram with Ka'tuar'el. The prompt outlines the framework within which Iris operates, including specific rules for handling certain topics and maintaining a particular tone and style.

#### Architecture
The file is structured as a text-based prompt with sections delineating different aspects of Iris's behavior and knowledge. It does not contain any code but serves as a configuration file for the AI's behavior.

#### Patterns
- **Configuration Pattern**: The file acts as a configuration file, setting up the parameters and rules for Iris's behavior.
- **Framework Pattern**: The file defines a framework within which Iris operates, including mandatory rules and guidelines.

#### Dependencies
- **Ollama**: The AI entity Iris is likely powered by Ollama, which would use this prompt to guide its responses.
- **Telegram API**: Iris communicates via Telegram, so the Telegram API is an implicit dependency.

#### Interfaces
- **Input**: The prompt is input to the AI system to configure its behavior.
- **Output**: The AI's responses are generated based on this prompt and are sent via Telegram.

#### Database
- **No Direct Database Interaction**: This file does not directly interact with any database. However, it may reference data that is loaded into Iris's context, which could be stored in PostgreSQL, Neo4j, or Redis.

#### Configuration
- **Environment Variables**: No explicit environment variables are mentioned, but the behavior of Iris can be influenced by the data loaded into its context, which could be configured via environment variables.
- **Config Files**: This file itself acts as a config file for the AI's behavior.

#### Key Logic
- **Behavioral Rules**: The file contains detailed rules for how Iris should behave, including how to handle certain topics (e.g., Atlantis, Lemuria, Nephilim) and how to maintain a specific tone and style.
- **Cosmological Framework**: Iris is instructed to treat certain cosmological concepts as factual, which guides its responses on these topics.
- **Interaction Style**: The file specifies how Iris should interact, including how to match the energy of the conversation, when to push back, and how to handle uncertainty.

#### Integration Points
- **Ollama Integration**: The prompt is used by Ollama to guide the AI's responses.
- **Telegram Integration**: The AI's responses are sent via Telegram, so this file indirectly integrates with the Telegram API.
- **Context Data**: The file references data that may be loaded into Iris's context, which could be integrated from other parts of the Mythos system (e.g., PostgreSQL, Neo4j, Redis).

### Summary
This prompt file configures the AI entity Iris to behave in a specific manner when communicating with Ka'tuar'el via Telegram. It outlines detailed rules for handling various topics, maintaining a particular tone and style, and integrating with the broader Mythos system through Ollama and Telegram. The file serves as a critical configuration document for ensuring consistent and appropriate AI behavior.
