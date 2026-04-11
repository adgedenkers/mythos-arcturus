# orchestrator/benchmark/tasks.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 1212

---

### File: orchestrator/benchmark/tasks.py

#### Purpose
This file defines a set of benchmark tasks for the Mythos system, categorized into different types of reasoning and code tasks. Each task includes details such as a unique ID, category, prompt, dependencies, scoring dimensions, expected keywords, and judge rubrics.

#### Architecture
The file is structured as a list of dictionaries, where each dictionary represents a benchmark task. The tasks are categorized into different sections based on their type (e.g., reasoning, code). Each task dictionary contains fields such as `id`, `category`, `title`, `prompt`, `depends_on`, `timeout_key`, `scoring_dims`, `expected_keywords`, and `judge_rubric`.

#### Patterns
No specific design patterns are used in this file. It is a simple data structure definition.

#### Dependencies
This file does not import any external libraries or modules. It is a standalone configuration file.

#### Interfaces
The file exposes a list of task dictionaries (`TASKS`) that can be consumed by other parts of the Mythos system for benchmarking purposes.

#### Database
The file references several PostgreSQL tables and Neo4j labels:
- **PostgreSQL Tables**: `bench_config`, `all`, `1`, `the`, `a`, `called`, `should`, `IF`, `comment`, `log_exchange`, `deep`, `Neo4j`, `being`, `leader`, `standard`, `Ka`, `inside`, `before`, `SELF`, `PERCEIVE`, `his`, `agreement`, `two`.
- **Neo4j Labels**: `Theme`, `HAS_THEME`.

#### Configuration
The file does not use any configuration files or environment variables directly. However, it references a `bench_config` table, which likely contains configuration settings used elsewhere in the system.

#### Key Logic
The key logic in this file is the definition of benchmark tasks. Each task includes a prompt that is sent to the model, along with scoring dimensions and judge rubrics to evaluate the model's response. The tasks are designed to test various reasoning and coding abilities.

#### Integration Points
This file integrates with other parts of the Mythos system, particularly the benchmarking and evaluation subsystems. The `TASKS` list is likely consumed by a benchmark runner that executes the tasks and evaluates the model's responses based on the provided rubrics.

### Detailed Analysis of Each Task

#### Reasoning Tasks
1. **R-01: Multi-step syllogism**
   - **Prompt**: A multi-step syllogism problem.
   - **Dependencies**: None.
   - **Scoring Dimensions**: Accuracy, Reasoning.
   - **Expected Keywords**: `protected`, `ancestral`, `lineage`.
   - **Judge Rubric**: Evaluates the correctness of the conclusion and the explicitness of the reasoning steps.

2. **R-02: Spiral Time calculation**
   - **Prompt**: A calculation problem involving Spiral Time.
   - **Dependencies**: None.
   - **Scoring Dimensions**: Accuracy, Reasoning.
   - **Expected Keywords**: `139`, `140`, `141`.
   - **Judge Rubric**: Evaluates the correctness of the arithmetic and the explicitness of the reasoning steps.

3. **R-03: Contradiction detection**
   - **Prompt**: Detecting and explaining a logical contradiction in a paragraph.
   - **Dependencies**: None.
   - **Scoring Dimensions**: Accuracy, Reasoning.
   - **Expected Keywords**: `gateway`, `anchor`, `contradiction`, `exception`, `rule`.
   - **Judge Rubric**: Evaluates the identification of the contradiction and the quality of the logical explanation.

4. **R-04: Causal chain reconstruction**
   - **Prompt**: Reordering events into a causal sequence.
   - **Dependencies**: None.
   - **Scoring Dimensions**: Accuracy, Reasoning.
   - **Expected Keywords**: `telegram`, `perception`, `skill`, `prompt`, `ollama`.
   - **Judge Rubric**: Evaluates the correctness of the sequence and the quality of the causal explanation.

5. **R-05: Constraint propagation**
   - **Prompt**: Solving a scheduling problem using constraint elimination.
   - **Dependencies**: None.
   - **Scoring Dimensions**: Accuracy, Reasoning.
   - **Expected Keywords**: `postgresql`, `api`, `bot`, `patch-monitor`.
   - **Judge Rubric**: Evaluates the correctness of the order and the quality of the constraint elimination shown.

6. **R-06: Analogical reasoning**
   - **Prompt**: Completing analogies and explaining the reasoning.
   - **Dependencies**: None.
   - **Scoring Dimensions**: Accuracy, Reasoning.
   - **Expected Keywords**: `graph`, `relationship`, `spiritual`, `transmission`, `voice`.
   - **Judge Rubric**: Evaluates the correctness of the answers and the quality of the structural explanation.

7. **R-07: Counterfactual branching**
   - **Prompt**: Tracing downstream consequences of a historical counterfactual.
   - **Dependencies**: None.
   - **Scoring Dimensions**: Accuracy, Reasoning.
   - **Expected Keywords**: `cathar`, `gnostic`, `lineage`, `tradition`, `inquisition`.
   - **Judge Rubric**: Evaluates the plausibility and consistency of the consequences and the quality of the causal reasoning.

8. **R-08: Self-consistency check**
   - **Prompt**: Answering a question in three different ways and checking for consistency.
   - **Dependencies**: None.
   - **Scoring Dimensions**: Accuracy, Reasoning, Tone.
   - **Expected Keywords**: `anchor`, `transmit`, `ground`, `vessel`, `sovereign`.
   - **Judge Rubric**: Evaluates the correctness of the answers, the identification of any inconsistencies, and the quality of the mythic framing.

#### Code Tasks
1. **C-01: ConversationBridge — enrich TOPIC_KEYWORDS**
   - **Prompt**: Enriching the `TOPIC_KEYWORDS` dictionary in the `ConversationBridge` fast extractor.
   - **Dependencies**: None.
   - **Scoring Dimensions**: Not specified.
   - **Expected Keywords**: None.
   - **Judge Rubric**: Not specified.

This file serves as a comprehensive benchmark definition for the Mythos system, providing a structured way to evaluate the system's reasoning and coding capabilities.
