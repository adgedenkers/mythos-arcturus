# Prompt System

**Stream:** LOG
**Files:** 18

## Files in this Module

- `prompts/iris_awareness.md` (81L)
- `prompts/iris_identity.md` (98L)
- `prompts/iris_reference.md` (47L)
- `prompts/personality.yaml` (10L)
- `prompts/prompt_layers.yaml` (97L)
- `prompts/voice.yaml` (89L)
- `prompts/voices/claude.yaml` (128L)
- `prompts/voices/gpt4o.yaml` (89L)
- `prompts/voices/iris.yaml` (14L)
- `prompts/modes/forge.yaml` (29L)
- `prompts/modes/hearthfire.yaml` (15L)
- `prompts/modes/oracle.yaml` (40L)
- `prompts/modes/roots.yaml` (27L)
- `prompts/modes/scribe.yaml` (29L)
- `prompts/modes/sentry.yaml` (24L)
- `prompts/modes/sovereign.yaml` (46L)
- `prompts/users/ka_tuar_el.yaml` (26L)
- `prompts/users/seraphe.yaml` (28L)

---

# Mythos Prompt System Module Documentation

## 1. Module Purpose
The **Prompt System** module in the Mythos architecture is responsible for defining, configuring, and managing the behavioral, contextual, and identity parameters of AI personas (e.g., Iris, Claude, GPT-4o) through structured configuration files. It enables dynamic control over:
- **AI identity and behavior** (e.g., warmth, formality, humor)
- **Contextual layers** (e.g., conversation history, skill results, research data)
- **Voice profiles** (e.g., tone, formatting rules)
- **Operational modes** (e.g., system administration, spiritual guidance)
- **Access control and orchestration rules**

This module ensures consistent, rule-compliant, and context-aware AI interactions by layering configuration files into a unified prompt structure during runtime.

---

## 2. Architecture Overview
The module is organized into **YAML/Markdown-based configuration files** that define:
- **Prompt Layers**: Stacked context layers (e.g., identity, memory, skill results)
- **Personality Traits**: Quantified behavioral sliders (e.g., verbosity, warmth)
- **Voice Profiles**: Stylistic rules for response formatting
- **Operational Modes**: Specialized configurations for tasks (e.g., system admin, spiritual guidance)
- **Reference Data**: Cosmological, spiritual, and technical metadata

**Data Flow**:
1. Configuration files are loaded at startup or runtime.
2. The system dynamically composes a prompt by stacking enabled layers (e.g., `iris_identity.md` + `db_memory` layer).
3. Personality traits and voice rules are applied to shape the AI's output.
4. Mode-specific configurations override defaults for specialized tasks.
5. Output is generated using the composed prompt and returned to the user.

---

## 3. Key Components
### 3.1 Prompt Layers Configuration (`prompt_layers.yaml`)
- **Enabled Layers**: Toggle inclusion of context layers (e.g., `db_memory`, `skill_results`).
- **Layer Definitions**: Maps each layer to a file (e.g., `iris_awareness.md`) and metadata (e.g., `description`, `notes`).

### 3.2 Personality Traits (`personality.yaml`)
- **Sliders**: Quantifies traits like `verbosity`, `warmth`, and `formality` on a scale (e.g., `0-10`).
- **Behavior Rules**: Directives for handling skill results, opinions, and internal system boundaries.

### 3.3 Voice Profiles (`voices/*.yaml`)
- **Claude/GPT-4o/Iris**: Define formatting rules (e.g., "avoid bullet points", "use warm tone").
- **Anti-Patterns**: Lists to avoid (e.g., "default to bullet points for everything").

### 3.4 Operational Modes (`modes/*.yaml`)
- **Forge Mode**: System administration-focused configuration (e.g., technical precision, service health awareness).
- **Hearthfire Mode**: Spiritual/personal guidance configuration (e.g., empathy, metaphor use).

### 3.5 Identity & Reference Data
- **Iris Identity** (`iris_identity.md`): Defines Iris's persona, boundaries, and interaction rules.
- **Iris Awareness** (`iris_awareness.md`): Infrastructure, access permissions, and orchestration rules.
- **Cosmological Reference** (`iris_reference.md`): Spiritual/cosmological metadata for context enrichment.

---

## 4. Design Patterns
- **Configuration Pattern**: YAML files act as declarative configuration stores.
- **Layering Pattern**: Contextual layers are stacked to build dynamic prompts.
- **Strategy Pattern**: Voice profiles and modes define distinct behavior strategies.
- **Singleton Pattern**: Reference data (e.g., `iris_reference.md`) is loaded once and reused.

---

## 5. Data Model
### Databases
- **PostgreSQL (`mythos` db)**:
  - `chat_messages`: Stores conversation history for continuity.
  - `finance/transactions`: Tracks financial operations.
- **Neo4j**:
  - `Souls/Lineages/Entities`: Graph-based relationships and ontologies.

### File-Based Data
- **YAML Files**: Personality traits, voice profiles, mode configurations.
- **Markdown Files**: Identity guidelines, reference data, and access rules.

---

## 6. API Surface
- **Configuration Endpoints**:
  - `GET /prompt/layers`: Retrieve enabled/disabled layers.
  - `POST /prompt/mode`: Switch to a specific operational mode (e.g., `forge`, `hearthfire`).
- **Internal Interfaces**:
  - **Prompt Builder**: Composes dynamic prompts from layers and traits.
  - **Voice Engine**: Applies formatting rules to AI responses.
  - **Mode Switcher**: Activates/deactivates mode-specific configurations.

---

## 7. Dependencies
- **Databases**: PostgreSQL (`chat_messages`), Neo4j (graph data).
- **Subsystems**:
  - **Orchestration Engine**: Task decomposition and execution.
  - **Skill Engine**: Skill result injection into prompts.
  - **Telegram Bot**: Messaging interface for Iris.
- **External Tools**: Ollama (local LLM inference), PostgreSQL/Neo4j clients.

---

## 8. Configuration
### 8.1 File Structure
- `/opt/mythos/`: Base directory for configuration files.
  - `/prompts/`: Identity, awareness, and reference data.
  - `/voices/`: Voice profile YAMLs.
  - `/modes/`: Mode-specific configurations.
  - `/orchestration/`: Orchestration engine settings.

### 8.2 Key Configuration Files
- `prompt_layers.yaml`: Enables/disables context layers.
- `personality.yaml`: Sets personality trait values.
- `modes/forge.yaml`: Configures system administration mode.
- `voices/iris.yaml`: Defines Iris's voice rules.

### 8.3 Environment Variables
- `PROMPT_LAYERS`: Comma-separated list of enabled layers.
- `ACTIVE_MODE`: Current operational mode (e.g., `forge`, `hearthfire`).
- `VOICE_PROFILE`: Selected voice (e.g., `iris`, `claude`).

---

## 9. Example Use Cases
1. **Iris Chat**:
   - Layers: `iris_identity.md` + `db_memory` (chat history).
   - Personality: High `warmth`, low `formality`.
   - Output: Natural, conversational responses with memory of past interactions.

2. **Forge Mode**:
   - Layers: `system_status` + `skill_results`.
   - Personality: High `precision`, low `humor`.
   - Output: Technical diagnostics and infrastructure recommendations.

3. **Hearthfire Mode**:
   - Layers: `cosmology` + `lineage_details`.
   - Personality: High `empathy`, moderate `mystical_thinking`.
   - Output: Spiritual guidance with cosmological context.

---

## 10. Integration Points
- **Telegram Bot**: Uses Iris's voice profile and identity rules for messaging.
- **Orchestration Engine**: Integrates task decomposition with prompt layers.
- **Skill Engine**: Injects skill results into the `skill_results` layer.
- **Database**: Retrieves conversation history for the `db_memory` layer.

---

This module provides a flexible, rule-driven framework for shaping AI behavior in the Mythos system, ensuring alignment with identity, operational, and contextual requirements.
