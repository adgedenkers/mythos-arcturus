## voice_tuning

### Purpose
The `voice_tuning` component of Mythos is designed to iteratively refine the quality of Iris's voice through prompt tuning. It runs a series of voice versions (V-01 through V-06) against any given model using live prompts defined in `prompt_layers.yaml`. This process allows for dynamic adjustments and testing without requiring code changes, enhancing flexibility and efficiency in voice refinement.

### Key Files and Structure
The component does not rely on specific files or lines of code within the Mythos system. Instead, it dynamically reads prompt configurations directly from disk, specifically targeting `prompt_layers.yaml` as its primary source for system prompts. This setup ensures that any edits to the prompt configuration can be immediately reflected by re-running the process.

### Data Flow
Data flow in the `voice_tuning` component begins with reading live prompts from `prompt_layers.yaml`. These prompts are then used to run through a series of voice versions (V-01 to V-06) against selected models. The output is not stored within the system but can be captured externally for analysis and further tuning iterations.

### Dependencies and Integration Points
The component primarily depends on the availability of `prompt_layers.yaml` file, which must be correctly formatted and accessible from disk. It integrates with Mythos's model execution framework to apply voice versions against models. The CLI command `iris-voice-tune` serves as the primary interface for initiating tuning processes.

### Known Issues or Technical Debt
At present, there are no specific known issues documented within the `voice_tuning` component. However, future enhancements could include more robust error handling and validation of the prompt configuration files to prevent runtime errors due to misconfigurations. Additionally, automating the capture and analysis of tuning results could streamline the iterative refinement process further.
