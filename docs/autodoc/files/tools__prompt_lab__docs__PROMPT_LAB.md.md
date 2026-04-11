# tools/prompt_lab/docs/PROMPT_LAB.md

**Language:** markdown
**Stream:** SYS
**Module:** Tools
**Lines:** 374

---

### Purpose
The `PROMPT_LAB.md` file serves as a comprehensive documentation guide for the Prompt Lab toolkit, which is used to test, compare, and build Iris prompt configurations. It provides detailed instructions and examples for using the `bench.py` and `tweak.py` scripts, as well as explanations of the underlying architecture, concepts, and workflows.

### Architecture
The file is structured into several sections, each detailing different aspects of the Prompt Lab toolkit:
- **Quick Start**: Provides example commands for using `bench.py` and `tweak.py`.
- **Architecture**: Outlines the directory structure and the purpose of each file.
- **Tools**: Describes the functionality and usage of `bench.py` and `tweak.py`.
- **Concepts**: Explains the key concepts such as Profiles, Personalities, and Test Suites.
- **Workflows**: Describes typical workflows for using the toolkit.
- **Bash Aliases**: Provides shortcuts for common commands.
- **Adding New Content**: Instructions for adding new test suites, personality presets, and profiles.
- **File Format Reference**: Describes the YAML format for profiles, personalities, and test messages.

### Patterns
The documentation does not explicitly use design patterns, but it follows a modular approach where different scripts (`bench.py`, `tweak.py`) and files (`profiles`, `personalities`, `messages`) are organized to handle specific tasks.

### Dependencies
The documentation does not list dependencies directly, but it implies the following:
- **Python scripts**: `bench.py`, `tweak.py`
- **Libraries**: `assembler.py`, `runner.py`, `scorer.py`, `store.py`
- **Data files**: `messages/*.yaml`, `personalities/*.yaml`, `profiles/*.yaml`

### Interfaces
The documentation exposes the following interfaces:
- **CLI Commands**: `bench.py` and `tweak.py` with various flags and options.
- **File Formats**: YAML files for profiles, personalities, and test messages.

### Database
The documentation does not mention any direct database interactions, but it implies that results are saved and loaded using JSON files in the `results/` directory.

### Configuration
The documentation does not explicitly mention configuration files or environment variables, but it implies the use of YAML files for configuration and JSON files for storing results.

### Key Logic
The key logic described in the documentation includes:
- **Prompt Assembly**: Combining different layers to form a complete prompt.
- **Prompt Testing**: Sending prompts to Ollama and capturing responses.
- **Scoring**: Evaluating responses based on predefined anti-patterns.
- **Personality Adjustment**: Modifying personality sliders and presets.

### Integration Points
The documentation integrates with other Mythos subsystems through:
- **Ollama**: Sending prompts and receiving responses.
- **Iris**: Using Iris modes and profiles.
- **File System**: Reading and writing YAML and JSON files for profiles, personalities, and test results.

### Summary
The `PROMPT_LAB.md` file provides a detailed guide for using the Prompt Lab toolkit, covering its architecture, tools, concepts, workflows, and file formats. It serves as a reference for developers and users to effectively test and build Iris prompt configurations.
