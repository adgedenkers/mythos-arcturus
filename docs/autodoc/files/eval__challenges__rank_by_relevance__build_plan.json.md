# eval/challenges/rank_by_relevance/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 28

---

### File: eval/challenges/rank_by_relevance/build_plan.json

#### Purpose
This JSON file serves as a build plan and test specification for the `RankByRelevanceSkill` class, which is designed to score and sort results based on keyword match density and recency.

#### Architecture
The JSON file is structured into several key sections:
- **plan_id**: A unique identifier for the build plan.
- **version**: The version of the build plan.
- **description**: A brief description of the skill.
- **pattern**: The pattern or type of skill.
- **model_hint**: A hint for the model to use.
- **context**: Contains system context, scaffold code, and mandatory patterns.
- **build_plan**: A step-by-step guide for implementing the skill.
- **test_cases**: Test cases to validate the implementation.

#### Patterns
- **Scaffold Pattern**: The `context` section provides a scaffold for the class implementation.
- **Mandatory Patterns**: Specific constraints like no database usage, ASCII-only, and specific response signatures.

#### Dependencies
- **Imports**: `logging`, `re`, `datetime` (specifically `datetime`, `timedelta`), and `engine.base`.
- **Classes**: `SkillBase` from `engine.base`.
- **Environment**: No specific environment variables are mentioned, but the ASCII-only constraint is noted.

#### Interfaces
- **Class**: `RankByRelevanceSkill` inherits from `SkillBase`.
- **Methods**:
  - `execute`: Asynchronous method to process the request and return a `SkillResponse`.
  - `_score`: Internal method to calculate the relevance score of a result.

#### Database
- **No Database Usage**: The build plan explicitly states no database imports or usage.

#### Configuration
- **Environment Variables**: None explicitly mentioned.
- **Configuration Files**: None explicitly mentioned.

#### Key Logic
1. **Score Calculation**:
   - `_score` method calculates a relevance score based on keyword matches and recency.
   - Keyword score is calculated by counting occurrences of each keyword in the result text and normalizing by the total number of keywords.
   - Recency score is calculated based on the `created_at` field, if present, and is capped at 30 days.
   - Final score is a weighted sum of keyword and recency scores.

2. **Execution Logic**:
   - `execute` method processes the request, extracts results and keywords, and scores each result.
   - Results are sorted by score in descending order.
   - A `SkillResponse` is returned with the ranked results and a summary.

#### Integration Points
- **Engine Base**: The skill integrates with the `engine.base` module, specifically the `SkillBase` class.
- **SkillResponse**: The skill returns a `SkillResponse` object, which is part of the `engine.base` module.
- **Test Cases**: The skill is validated using predefined test cases that check for expected data fields and overall success.

### Detailed Breakdown of Build Plan Steps

1. **Pass 1**: Write the file skeleton with necessary imports and class attributes. Methods are placeholders (`pass`).
2. **Pass 2**: Implement the `_score` method to calculate the relevance score based on keyword matches and recency.
3. **Pass 3**: Implement the `execute` method to process the request, score results, and return a `SkillResponse`.
4. **Pass 4**: Review the implementation to ensure no database usage, ASCII-only text, and production readiness.

### Test Cases
- **Test Case 1**: Verify that the skill correctly processes a request to rank by relevance and returns the expected data fields.
- **Test Case 2**: Verify that the skill handles another trigger phrase and returns a successful response.

This build plan ensures that the `RankByRelevanceSkill` is implemented correctly, tested thoroughly, and adheres to the specified constraints and patterns.
