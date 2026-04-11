# eval/results/query_natal_chart/20260305_103408/temp_skill/_test_cases.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 23

---

### File: `eval/results/query_natal_chart/20260305_103408/temp_skill/_test_cases.json`

#### Purpose
This JSON file contains test cases for evaluating the functionality of a natal chart query system within the Mythos platform. Each test case specifies a query message and expected outcomes, including expected data presence and summary content.

#### Architecture
The file is structured as a JSON array of objects, where each object represents a test case. Each test case includes:
- `message`: The query message to be tested.
- `expect_ok`: A boolean indicating whether the query is expected to succeed.
- `expect_data_has`: An array of strings representing the expected data fields to be present in the response.
- `expect_summary_contains`: An array of strings representing the expected content in the summary of the response.

#### Patterns
No specific design patterns are used in this JSON file as it is a simple data structure for test cases.

#### Dependencies
This JSON file does not import or rely on any external dependencies. It is a standalone data file used for testing purposes.

#### Interfaces
This file does not expose any interfaces. It is intended to be consumed by a testing framework or script that processes test cases.

#### Database
This file does not interact directly with any database. It is used to define test cases that may query a database or a service that retrieves natal chart data.

#### Configuration
This file does not use any configuration files or environment variables. It is a static data file.

#### Key Logic
The key logic is embedded in the structure and content of the test cases:
- Each test case checks if the query message produces the expected response.
- The `expect_data_has` field ensures that specific data fields are present in the response.
- The `expect_summary_contains` field ensures that the summary of the response contains specific keywords.

#### Integration Points
This file is likely integrated with a testing framework or script that processes these test cases. The framework would:
1. Send the `message` to the natal chart query service.
2. Validate the response against `expect_ok`, `expect_data_has`, and `expect_summary_contains`.

### Example Integration
A Python script might use this file as follows:

```python
import json

with open('eval/results/query_natal_chart/20260305_103408/temp_skill/_test_cases.json', 'r') as file:
    test_cases = json.load(file)

for case in test_cases:
    response = query_natal_chart_service(case['message'])
    assert response['ok'] == case['expect_ok']
    if 'expect_data_has' in case:
        for field in case['expect_data_has']:
            assert field in response['data']
    if 'expect_summary_contains' in case:
        for keyword in case['expect_summary_contains']:
            assert keyword in response['summary']
```

In this example, `query_natal_chart_service` is a hypothetical function that interacts with the Mythos natal chart query service. The script processes each test case, sends the query, and validates the response against the expected outcomes.
