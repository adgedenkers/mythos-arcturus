## decision_gate

### Purpose
The **decision_gate** component is responsible for handling events that reach escalation TIER 2+ in Phase 4 of the autonomic system. It gathers necessary context, constructs a prompt, invokes an LLM (Large Language Model) through Ollama to make judgments on these high-priority events, and returns a structured action plan based on the model's response. This component is accessible via CLI commands for testing, dry-runs, and viewing prompt previews or history.

### Key Files and Structure
Currently, the **decision_gate** does not have any files or lines of code committed to it, indicating that its implementation is pending. The structure will be defined as development progresses, but it will likely include modules for context gathering, prompt generation, LLM invocation, and action plan structuring.

### Data Flow
1. Events reaching TIER 2+ are routed into the **decision_gate**.
2. Context relevant to the event is gathered from various sources within the system.
3. A structured prompt is built based on this context.
4. The constructed prompt is sent to Ollama for judgment via an LLM invocation.
5. The response from the LLM is processed and transformed into a structured action plan.
6. This action plan is then returned to the autonomic system for execution.

### Dependencies and Integration Points
- **Ollama**: For invoking the LLM and receiving judgments on events.
- **CLI Interface (iris-decide)**: Provides command-line access for testing, dry-runs, prompt previews, and history viewing.
- **Context Gathering Modules**: Required to collect relevant data from the system about the event.

### Known Issues or Technical Debt
- The component is currently under development with no files committed, indicating a need for initial implementation.
- Two seed triggers (`smart_disk_check`, `smart_service_check`) are mentioned but are currently disabled and require enabling as part of future work.
