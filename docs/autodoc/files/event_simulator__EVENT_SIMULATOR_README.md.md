# event_simulator/EVENT_SIMULATOR_README.md

**Language:** markdown
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 453

---

### Purpose
The `EVENT_SIMULATOR_README.md` file serves as a comprehensive guide for the Mythos Event Simulator, detailing its installation, usage, and integration with the Mythos system. It outlines how to simulate various system events, track test history, and analyze results stored in Neo4j.

### Architecture
The document is structured into several sections:
- **Overview**: Describes the purpose and functionality of the event simulator.
- **Installation**: Instructions for setting up the simulator.
- **Usage**: Detailed steps for running tests and viewing results.
- **How It Works**: Explanation of the internal mechanisms for event triggering and data storage.
- **Querying Results in Neo4j**: Example Cypher queries for retrieving test results.
- **Best Practices**: Recommendations for regular testing and multi-machine testing.
- **Troubleshooting**: Common issues and solutions.
- **Safety Notes**: Guidelines for safe usage.
- **Integration with LLM Diagnostics**: How to use the LLM for diagnostics.
- **Advanced Usage**: Customization options for test durations and adding new tests.

### Patterns
The document does not describe any specific design patterns but rather provides procedural documentation and usage instructions.

### Dependencies
The simulator relies on:
- **Python**: For the main script `event_simulator.py`.
- **Neo4j**: For storing and querying test results.
- **Bash**: For installation and command-line interface.
- **Ollama**: For LLM diagnostics.

### Interfaces
The simulator exposes a command-line interface (`mythos-test`) for:
- Running all tests (`--run`).
- Viewing test history (`--history`).
- Analyzing common failures (`--failures`).

### Database
The simulator interacts with Neo4j to store test results:
- **TestMachine** nodes: Store machine information.
- **TestRun** nodes: Store test run details.
- **System** nodes: Identify the system running the tests.
- **Event** nodes: Store individual events triggered by tests.

### Configuration
The simulator uses environment variables and configuration files:
- **NEO4J_PASSWORD**: For Neo4j database connection.
- **monitoring_config.yaml**: For monitor thresholds and intervals.

### Key Logic
The key logic involves:
- **Event Simulation**: Triggering CPU spikes, memory pressure, disk fills, service restarts, and process spawns.
- **Data Storage**: Storing test results in Neo4j.
- **Real-time Monitoring**: Displaying test results and waiting for monitor detection.
- **Historical Analysis**: Querying Neo4j for historical trends and common failures.

### Integration Points
The simulator integrates with:
- **Neo4j**: For storing and querying test results.
- **Ollama**: For LLM diagnostics.
- **System Services**: For service restart tests.
- **Monitoring Infrastructure**: For detecting and logging events.

### Detailed Analysis

#### Event Simulation
- **CPU Spike**: Spawns CPU-burning processes to exceed 80% CPU threshold.
- **Memory Pressure**: Allocates large memory blocks to trigger memory alerts.
- **Disk Fill**: Creates temporary large files in `/tmp`.
- **Service Restart**: Stops and starts a test service.
- **Process Spawn**: Creates multiple processes to test process tracking.

#### Data Storage
Test results are stored in Neo4j using the following schema:
```cypher
(:TestMachine {hostname: "arcturus"})
  -[:HAD_TEST_RUN]->
(:TestRun {
  id: "uuid",
  timestamp: datetime(),
  total_tests: 5,
  passed_tests: 4,
  failed_tests: 1,
  events_triggered: 3,
  results: "[JSON array of individual test results]"
})
  <-[:TESTED_BY]-
(:System {name: "localhost"})
```

#### Querying Results in Neo4j
Example queries include:
- Retrieving all test runs for a machine.
- Finding failing tests.
- Comparing multiple machines.
- Seeing events triggered by tests.

#### Best Practices
- **Regular Testing Schedule**: Using cron jobs to run tests regularly.
- **Multi-Machine Testing**: Running tests on multiple machines and comparing results.

#### Troubleshooting
Common issues and solutions are provided, such as:
- Tests not triggering events.
- History not being saved.
- CPU test not reaching the threshold.

#### Safety Notes
Guidelines for safe usage include:
- Avoiding critical operations and resource-constrained systems.
- Providing an emergency stop mechanism.

#### Integration with LLM Diagnostics
The LLM can be used to ask about recent events and test runs, providing additional insights.

#### Advanced Usage
Customization options include:
- Modifying test durations.
- Adding custom tests to the `EventSimulator` class.

This comprehensive documentation ensures users can effectively use the Mythos Event Simulator for thorough system testing and monitoring.
