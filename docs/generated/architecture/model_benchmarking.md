## model_benchmarking

### Purpose
The `model_benchmarking` component of Mythos is designed to evaluate large language models across 43 diverse tasks spanning six categories: Reasoning, Code, Mythos, Narrative, Tool Use, and Voice. Each task employs real-world Mythos workloads, with results output in JSONL format for analysis by a separate scoring model.

### Key Files and Structure
The `model_benchmarking` component currently consists of no files or lines of code as it is under active development. The CLI tools `mythos-bench` and `mythos-bench-report` are the primary interfaces for running benchmarks and generating reports, respectively.

### Data Flow
Data flows from the benchmark tasks into JSONL output files, which are then processed by a separate scoring model to generate performance metrics. These metrics are used to evaluate the models' capabilities across various categories of tasks.

### Dependencies and Integration Points
The `model_benchmarking` component relies on external language models such as qwen2.5:32b for task execution. It integrates with a JSONL output format handler and a separate scoring model for evaluation. The CLI tools (`mythos-bench`, `mythos-bench-report`) are the main integration points for users to interact with the benchmarking process.

### Known Issues or Technical Debt
- **Timeouts**: Some models, like gemma3:27b, have experienced timeouts across all tasks.
- **File and Codebase Development**: The component currently lacks implemented files and lines of code, indicating ongoing development and potential for future expansion.
