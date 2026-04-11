# orchestrator/benchmark/resonance/iris_test_config.yaml

**Language:** yaml
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 80

---

### File: orchestrator/benchmark/resonance/iris_test_config.yaml

#### Purpose
This YAML file contains configuration settings and test prompts for benchmarking the Iris subsystem within the Mythos system. It defines various test sets with different prompt configurations to evaluate the performance and behavior of the Iris subsystem under different conditions.

#### Architecture
The file is structured as a YAML document with the following sections:
- **api_url**: The URL of the API endpoint to which test requests will be sent.
- **user_id**: The user ID for the test requests.
- **timeout**: The timeout duration for API requests.
- **model_preference**: The preferred model for the test requests.
- **sets**: A dictionary containing different sets of test prompts, each with a description and a list of prompts.

#### Patterns
No design patterns are directly applicable to this configuration file as it is a static data file.

#### Dependencies
This file does not import or rely on any external dependencies. It is a configuration file that is read by the benchmarking script or service.

#### Interfaces
This file is read by the benchmarking service or script to configure the test parameters and prompts. It does not expose any interfaces directly.

#### Database
This file does not interact with any databases directly. It is used to configure test parameters and prompts for the benchmarking service.

#### Configuration
The file itself is a configuration file and does not use any external configuration files or environment variables. The values within the file are used to configure the benchmarking service.

#### Key Logic
The key logic in this file is the definition of different test sets with varying numbers and types of prompts. The benchmarking service uses these sets to evaluate the performance and behavior of the Iris subsystem under different conditions.

#### Integration Points
This file integrates with the benchmarking service or script within the Mythos system. The service reads this configuration file to set up and execute the benchmark tests. The test results are likely used to evaluate the performance and reliability of the Iris subsystem.

### Detailed Breakdown of Configuration Sections

1. **api_url**: Specifies the endpoint for the API to which test requests will be sent.
   - Example: `"http://localhost:8000"`

2. **user_id**: Specifies the user ID to be used in the test requests.
   - Example: `"7811548479"`

3. **timeout**: Specifies the timeout duration for API requests.
   - Example: `180` (seconds)

4. **model_preference**: Specifies the preferred model for the test requests.
   - Example: `"auto"`

5. **sets**: A dictionary containing different sets of test prompts:
   - **quick**: A fast smoke test with 3 prompts.
   - **standard**: A core resonance battery with 8 prompts.
   - **full**: A full 16-prompt battery.
   - **sovereign**: A sovereign alignment test with cosmological framework prompts.
   - **anti_confab**: Fabrication traps to test for data invention.
   - **channeling**: Spirit team and channeling prompts.
   - **voice**: Voice and identity tests.

Each set includes a description and a list of prompts to be used in the benchmarking process.

### Example Usage
The benchmarking service would read this configuration file and use the defined parameters and prompts to execute tests against the Iris subsystem. For example, it might send the prompts in the `quick` set to the API endpoint specified by `api_url` and measure the response times and accuracy of the responses.

This configuration allows for flexible and comprehensive testing of the Iris subsystem under various conditions, ensuring that it performs reliably and accurately across different scenarios.
