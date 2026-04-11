# docs/VOICE_LAB.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 259

---

### Documentation for `docs/VOICE_LAB.md`

#### Purpose
This markdown file serves as a comprehensive guide to the Iris Voice Lab, detailing the tools and processes used for engineering, testing, and iterating on Iris's voice, personality, and mode behavior.

#### Architecture
The file is structured into several sections, each detailing different aspects of the Voice Lab:
- **Tool Overview**: Describes the three main tools (`Prompt Lab`, `Iris Test Rig`, `A/B Sweep`).
- **Key Concepts**: Explains the layer stack, personality sliders, modes, and test suites.
- **Workflows**: Outlines daily voice tuning, adding new modes, pre-deployment regression, and model evaluation.
- **File Locations**: Lists the paths and purposes of key files and directories.

#### Patterns
The document does not explicitly use design patterns, but it follows a structured documentation pattern, providing clear sections and examples for each tool and concept.

#### Dependencies
The file does not import or rely on any code directly but references several tools and files:
- `/opt/mythos/tools/prompt_lab/bench.py`
- `/opt/mythos/tools/iris_test_rig.py`
- `/opt/mythos/tools/iris_ab_sweep.py`

#### Interfaces
The document exposes the interfaces and usage examples for the following tools:
- `bench.py` (CLI for Prompt Lab)
- `iris_test_rig.py` (CLI for production-mirror test rig)
- `iris_ab_sweep.py` (CLI for automated parameter sweeping)

#### Database
The document does not mention any direct interaction with databases like PostgreSQL, Neo4j, or Redis.

#### Configuration
The document does not explicitly mention any configuration files or environment variables. However, it implies that configuration is managed through the layer files and test suite configurations.

#### Key Logic
The key logic revolves around assembling and testing Iris's prompt layers:
- **Prompt Lab**: Assembles prompts, sends them to Ollama, scores responses, and saves results.
- **Iris Test Rig**: Freezes the production prompt, runs test suites, scores responses, and generates summary reports.
- **A/B Sweep**: Automates parameter sweeping to find optimal slider settings.

#### Integration Points
The document integrates with several subsystems of the Mythos system:
- **Prompt Assembler**: Used by the Prompt Lab and Iris Test Rig to assemble prompts.
- **Ollama Models**: Used to generate responses for testing.
- **Test Suites**: Standardized message sets used for calibration and scoring.

### Detailed Analysis of Each Tool

#### 1. Prompt Lab (`/opt/mythos/tools/prompt_lab/`)
- **Purpose**: A workbench for daily voice engineering.
- **Key Capabilities**:
  - Layer isolation
  - Personality presets
  - Test suites
  - A/B comparison
  - Dry-run mode
- **Primary Interface**: `bench.py` (CLI)
- **Examples**:
  ```bash
  bench --profile full_no_life --mode sovereign --personality sovereign --dry-run
  bench --profile full_no_life --test greeting
  bench --profile full_no_life --mode sovereign --personality sovereign --suite sovereignty
  bench --compare naked identity_only --test greeting
  bench --profile full_no_life --mode hearthfire --suite sovereignty --save
  bench --profile full_no_life --mode sovereign --personality sovereign --suite sovereignty --save
  ```

#### 2. Iris Test Rig (`/opt/mythos/tools/iris_test_rig.py`)
- **Purpose**: A production-mirror regression suite.
- **Key Capabilities**:
  - Freezes the exact production prompt
  - Runs test suites against specified models
  - Scores responses for anti-patterns
  - Generates summary scorecards
- **Examples**:
  ```bash
  /opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_test_rig.py
  /opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_test_rig.py --models iris-thinking-v2 qwen2.5:32b
  /opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_test_rig.py --all
  /opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_test_rig.py --show-prompt
  ```

#### 3. A/B Sweep (`/opt/mythos/tools/iris_ab_sweep.py`)
- **Purpose**: Automated parameter sweeping to find optimal slider settings.
- **Key Capabilities**:
  - Tests ranges of slider values
  - Identifies optimal settings

### Key Concepts

#### Layer Stack
- **Identity**: `/opt/mythos/prompts/iris_identity.md`
- **Personality**: `/opt/mythos/prompts/personality.yaml`
- **Voice**: `/opt/mythos/prompts/voice.yaml`
- **Mode**: `/opt/mythos/prompts/modes/{mode}.yaml`
- **User Profile**: `/opt/mythos/prompts/users/{user}.yaml`
- **Dynamic Context**: Current timestamp, speaker, life state

#### Personality Sliders
- **Verbosity**: Response length
- **Warmth**: Emotional tone
- **Humor**: Playfulness
- **Truth**: Directness
- **Speculation**: Intuitive reach
- **Autonomy**: Initiative
- **Mystical**: Cosmological lens
- **Formality**: Register
- **Challenge**: Pushback

#### Modes
- **Hearthfire**: Spiritual and personal conversation
- **Forge**: Technical building and infrastructure
- **Oracle**: Deep channeling and divination
- **Scribe**: Documentation and recording
- **Roots**: Genealogy and lineage research
- **Sentry**: Security and protection
- **Sovereign**: Sovereignty alignment and accountability

#### Test Suites
- **Calibration**: Standard voice quality
- **Spiritual**: Channeling, grid, lineage, tarot
- **Technical**: Infrastructure, databases, code
- **Sovereignty**: Ego checks, spiritual tool literacy, embodiment

#### Scoring
- **Anti-Patterns**: Bullet points, corporate opener, corporate closer, hedging phrases, assistant patterns, meta-commentary, confabulation

### Workflows

#### Daily Voice Tuning
1. See current state
2. Run calibration
3. Identify issues from scores
4. Edit relevant files
5. Re-run and compare

#### Adding a New Mode
1. Create the mode file
2. Edit personality overrides, voice notes, instructions
3. Test against calibration
4. Test against mode-specific suite
5. Compare against baseline

#### Pre-Deployment Regression
1. Run the production-mirror test rig
2. Review results
3. Check for regressions

#### Model Evaluation
1. Run all suites against the candidate
2. Use the test rig for multi-model comparison

### File Locations
- **Identity Layer**: `/opt/mythos/prompts/iris_identity.md`
- **Personality Sliders**: `/opt/mythos/prompts/personality.yaml`
- **Voice Rules**: `/opt/mythos/prompts/voice.yaml`
- **Mode Definitions**: `/opt/mythos/prompts/modes/`
- **User Profiles**: `/opt/mythos/prompts/users/`
- **Prompt Workbench**: `/opt/mythos/tools/prompt_lab/`
- **Main Workbench CLI**: `/opt/mythos/tools/prompt_lab/bench.py`
- **Personality Slider Adjuster**: `/opt/mythos/tools/prompt_lab/tweak.py`
- **Test Suites**: `/opt/mythos/tools/prompt_lab/messages/`
- **Named Personality Presets**: `/opt/mythos/tools/prompt_lab/personalities/`
- **Layer Toggle Configs**: `/opt/mythos/tools/prompt_lab/profiles/`
- **Saved Test Runs**: `/opt/mythos/tools/prompt_lab/results/`
- **Production-Mirror Test Rig**: `/opt/mythos/tools/iris_test_rig.py`
- **Parameter Sweep Tool**: `/opt/mythos/tools/iris_ab_sweep.py`

This documentation provides a comprehensive overview of the Iris Voice Lab, detailing the tools, workflows, and key concepts involved in engineering and testing Iris's voice and personality.
