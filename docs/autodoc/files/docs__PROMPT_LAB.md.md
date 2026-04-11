# docs/PROMPT_LAB.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 386

---

### Purpose
The `PROMPT_LAB.md` file serves as a comprehensive documentation for the Iris Prompt Lab Toolkit, detailing how to test, compare, and build Iris prompt configurations with evidence. It provides a structured guide for using the `bench.py` and `tweak.py` scripts, along with explanations of the underlying architecture, concepts, and workflows.

### Architecture
The `PROMPT_LAB.md` file is organized into several sections, each detailing different aspects of the Prompt Lab Toolkit:
- **Quick Start**: Provides basic usage examples for `bench.py`.
- **Architecture**: Outlines the directory structure and the roles of each script and file.
- **Tools**: Describes the functionalities and command-line interfaces of `bench.py` and `tweak.py`.
- **Concepts**: Explains key concepts like Profiles, Personalities, Test Suites, and Scoring.
- **Workflows**: Describes typical workflows for using the toolkit.
- **Bash Aliases**: Provides shortcuts for common tasks.
- **Adding New Content**: Instructions for extending the toolkit with new profiles, personalities, and test suites.
- **File Format Reference**: Describes the YAML formats for profiles, personalities, and test messages.

### Patterns
The documentation does not directly implement design patterns but rather describes the usage and structure of the toolkit, which implicitly follows the Command pattern for CLI tools and the Factory pattern for creating and managing different profiles and personalities.

### Dependencies
The documentation does not directly import or rely on any external libraries but references the following internal components:
- `bench.py`
- `tweak.py`
- `lib/assembler.py`
- `lib/runner.py`
- `lib/scorer.py`
- `lib/store.py`
- `messages/*.yaml`
- `personalities/*.yaml`
- `profiles/*.yaml`
- `results/*.json`

### Interfaces
The documentation exposes the command-line interfaces for `bench.py` and `tweak.py`, detailing various flags and their purposes.

### Database
The documentation does not directly interact with any database but mentions saving and loading results as JSON files in the `results/` directory.

### Configuration
The documentation does not explicitly mention configuration files but implies the use of environment variables or configuration through command-line flags.

### Key Logic
The key logic revolves around:
- **Prompt Assembly**: Combining different layers (identity, personality, voice, etc.) to form a complete prompt.
- **Prompt Testing**: Sending prompts to the Ollama model and capturing responses.
- **Scoring**: Evaluating responses based on predefined anti-patterns and expected outcomes.
- **Personality Adjustment**: Modifying personality sliders to test different configurations.

### Integration Points
The documentation integrates with other Mythos subsystems through:
- **Ollama Model**: Sending prompts and receiving responses.
- **File System**: Reading and writing profiles, personalities, test suites, and results.
- **Command Line Interface**: Providing a user-friendly interface for testing and adjusting prompts.

### Summary
The `PROMPT_LAB.md` file is a comprehensive guide for using the Iris Prompt Lab Toolkit, detailing the architecture, tools, concepts, workflows, and integration points. It provides a structured approach to testing and building prompt configurations, ensuring that the Iris AI system can be fine-tuned effectively.
