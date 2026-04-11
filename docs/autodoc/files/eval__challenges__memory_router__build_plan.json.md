# eval/challenges/memory_router/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 72

---

### Documentation for `eval/challenges/memory_router/build_plan.json`

#### Purpose
This JSON file serves as a structured plan for building a Mythos skill named `MemoryRouterSkill`. The skill analyzes user messages to determine which memory stores to search based on specific keywords and triggers.

#### Architecture
The file is organized into several sections:
- **plan_id**: Identifies the skill.
- **version**: Specifies the version of the plan.
- **description**: Describes the purpose of the skill.
- **pattern**: Indicates the pattern used for routing intents.
- **model_hint**: Specifies the AI model hint for the skill.
- **context**: Contains system context and scaffold information.
- **build_plan**: A step-by-step guide for implementing the skill.
- **test_cases**: Provides test cases to validate the skill.

#### Patterns
- **Template Method**: The `execute` method acts as a template method, defining the steps for processing the message and determining the memory stores to search.
- **Singleton**: The skill class `MemoryRouterSkill` can be considered a singleton as it is designed to be instantiated once and reused.

#### Dependencies
- **Imports**: The skill imports `SkillBase`, `SkillRequest`, and `SkillResponse` from `engine.base`.
- **Environment**: The skill does not rely on any external databases or environment variables, as indicated by the `no_database` pattern.

#### Interfaces
- **SkillBase**: The skill class `MemoryRouterSkill` inherits from `SkillBase`.
- **SkillRequest**: The `execute` method takes a `SkillRequest` object as input.
- **SkillResponse**: The `execute` method returns a `SkillResponse` object.

#### Database
- **No Database Access**: The skill does not interact with any databases, as specified in the `no_database` pattern.

#### Configuration
- **Environment Variables**: No environment variables are used.
- **Configuration Files**: No configuration files are used.

#### Key Logic
- **_extract_search_terms**: Removes trigger phrases from the message and returns the cleaned search content.
- **_score_stores**: Scores each memory store based on keyword matches in the message.
- **execute**: Orchestrates the extraction of search terms and scoring of stores to determine the final list of stores to search.

#### Integration Points
- **SkillBase**: The skill integrates with the `SkillBase` class for its base functionality.
- **SkillRequest**: The skill integrates with `SkillRequest` to receive input messages.
- **SkillResponse**: The skill integrates with `SkillResponse` to return the processed output.

### Detailed Breakdown

#### Context
- **system_context**: Contains metadata such as the database type, database name, and skill directory path.
- **scaffold**: Provides a template for the `MemoryRouterSkill` class, including attributes and methods.
- **mandatory_patterns**: Specifies constraints such as no database access and ASCII-only comments.

#### Build Plan
1. **Pass 1**: Write the file skeleton with necessary imports and class attributes.
2. **Pass 2**: Implement the `_extract_search_terms` method to clean the message.
3. **Pass 3**: Implement the `_score_stores` method to score memory stores based on keywords.
4. **Pass 4**: Implement the `execute` method to orchestrate the search term extraction and store scoring.
5. **Pass 5**: Review the complete file to ensure it meets all specified constraints.

#### Test Cases
- **Test Case 1**: Validates routing to specific stores based on message content.
- **Test Case 2**: Validates routing to specific stores based on message content.
- **Test Case 3**: Validates routing to all stores when no specific keywords are matched.

### Example Implementation
```python
#!/usr/bin/env python3
"""
Build a Mythos skill that analyzes a message and determines which memory stores to search.
"""

import logging
from engine.base import SkillBase, SkillRequest, SkillResponse

class MemoryRouterSkill(SkillBase):
    name = 'memory_router'
    version = '1.0'
    category = 'meta'
    description = 'Analyzes a message and determines which memory stores to search'
    triggers = ['remember', 'recall', 'what did', 'when did', 'did we', 'did I', 'have I', 'have we', 'memory', 'search everything', 'find anything about', 'look up']
    cache_ttl = 0

    STORE_KEYWORDS = {
        'voice_memos': ['voice', 'memo', 'memos', 'recording', 'said', 'talked', 'spoke', 'heard', 'audio', 'transcri'],
        'conversations': ['chat', 'conversation', 'discuss', 'discussed', 'asked', 'told', 'replied', 'message', 'thread'],
        'life_events': ['happened', 'event', 'occurred', 'milestone', 'experience', 'went', 'did', 'felt', 'mood'],
        'ideas': ['idea', 'thought', 'brainstorm', 'suggestion', 'concept', 'proposal', 'plan', 'backlog'],
        'documents': ['document', 'doc', 'file', 'scroll', 'written', 'notes', 'readme', 'architecture'],
    }

    def _extract_search_terms(self, message: str) -> str:
        # Remove routing trigger phrases, return the actual search content
        triggers = ['find anything about', 'search everything', 'what did we', 'what did i', 'when did we', 'when did i', 'did we', 'did i', 'have we', 'have i', 'remember', 'recall', 'look up', 'memory', 'search for', 'search about', 'search', 'find', 'about']
        for trigger in triggers:
            message = message.replace(trigger, '').strip()
        message = ' '.join(message.split()).strip()
        return message if len(message) >= 2 else ''

    def _score_stores(self, message: str) -> list:
        # For each store, count keyword matches
        scores = []
        for store, keywords in self.STORE_KEYWORDS.items():
            score = sum(keyword in message for keyword in keywords)
            scores.append((store, score))
        if all(score == 0 for _, score in scores):
            return [(store, 1.0) for store in self.STORE_KEYWORDS.keys()]
        return sorted(scores, key=lambda x: x[1], reverse=True)

    async def execute(self, request: SkillRequest) -> SkillResponse:
        # Extract search terms using _extract_search_terms()
        terms = self._extract_search_terms(request.message)
        # Score each store using _score_stores()
        targets = self._score_stores(request.message)
        # Build summary
        if any(score > 0 for _, score in targets):
            summary = f"Routing to {len([t for t, s in targets if s > 0])} store(s): {', '.join([t for t, s in targets if s > 0])}. Search terms: {terms}."
        else:
            summary = f"No specific store identified -- searching all memory stores for: {terms}."
        if not terms:
            summary = "No searchable content found in message."
        # Return SkillResponse
        return SkillResponse(skill_name=self.name, data={'targets': [name for name, score in targets], 'scores': {name: score for name, score in targets}, 'search_terms': terms}, summary=summary, confidence=max([score for _, score in targets], default=0.5), sources=['memory_router'])
```

This implementation follows the build plan and ensures that the skill functions as intended, adhering to the specified constraints and patterns.
