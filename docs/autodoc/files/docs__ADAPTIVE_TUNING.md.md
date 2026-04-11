# docs/ADAPTIVE_TUNING.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 768

---

### File: docs/ADAPTIVE_TUNING.md

#### Purpose
This markdown file documents the design and implementation plan for the Iris Adaptive Personality Tuning system, which aims to make Iris's responses more adaptive and context-aware based on user interactions.

#### Architecture
The document outlines a phased approach to implementing adaptive personality tuning:
1. **Phase 1: New Personality Sliders** - Introduces new sliders for `life_awareness` and `life_proactivity`.
2. **Phase 2: Session Tuning Engine** - Implements real-time adjustment of personality sliders within a conversation.
3. **Phase 3: Behavioral Learning** - Adds long-term memory of user preferences across sessions.

#### Patterns
- **Singleton Pattern**: The `SessionTuner` class can be implemented as a singleton to ensure a single instance manages session adjustments.
- **Observer Pattern**: The `SessionTuner` observes user responses and adjusts sliders accordingly.

#### Dependencies
- **Files**: `prompts/personality.yaml`, `prompts/modes/*.yaml`, `core/prompt_assembler.py`, `tools/prompt_lab/lib/assembler.py`, `tools/prompt_lab/personalities/*.yaml`, `tools/prompt_lab/lib/scorer.py`, `tools/prompt_lab/tweak.py`, `core/session_tuner.py`.
- **Modules**: `datetime`, `yaml` for loading rules.

#### Interfaces
- **Public Methods**: `SessionTuner.analyze_exchange(iris_message, user_response, conversation_history)` to detect signals and apply tuning rules.
- **Configuration Files**: `prompts/personality.yaml`, `prompts/tuning_rules.yaml` for defining personality sliders and tuning rules.

#### Database
- **No Direct Database Interaction**: The document does not specify any direct interaction with PostgreSQL, Neo4j, or Redis. However, the session tuning data could potentially be stored in a database for long-term analysis.

#### Configuration
- **Environment Variables**: None specified.
- **Config Files**: `prompts/personality.yaml`, `prompts/tuning_rules.yaml`.

#### Key Logic
- **Phase 1**: Adds new sliders to the personality system and defines translation rules for these sliders.
- **Phase 2**: Implements a `SessionTuner` class to detect conversational signals and adjust sliders based on predefined rules.

#### Integration Points
- **Prompt Assembler**: Integrates with the `prompt_assembler.py` to inject life context based on `life_awareness`.
- **Session Tuner**: Integrates with the conversation flow to dynamically adjust personality sliders based on user responses.

### Detailed Analysis

#### Phase 1: New Personality Sliders
- **New Sliders**: `life_awareness` and `life_proactivity` are added to the personality system.
- **Translation Rules**: Functions `_translate_life_awareness` and `_translate_life_proactivity` are added to `prompt_assembler.py` to translate slider values into prompt text.
- **Default Values**: Updated in `prompts/personality.yaml` and mode-specific overrides in `prompts/modes/*.yaml`.
- **Assembler Changes**: `prompt_assembler.py` is modified to gate life context injection based on `life_awareness`.

#### Phase 2: Session Tuning Engine
- **Concept**: Real-time adjustment of personality sliders within a conversation.
- **Signal Vocabulary**: Defines various signals and their detection methods.
- **Tuning Rules**: Stored in `prompts/tuning_rules.yaml`, mapping signals to slider adjustments.
- **Implementation**: `SessionTuner` class in `core/session_tuner.py` detects signals and applies tuning rules.

### Example Code Snippets

#### New Sliders Translation Rules
```python
def _translate_life_awareness(v: int) -> str:
    if v <= 20:
        return "LIFE CONTEXT: Do not reference routines, finances, calendar, or life management data."
    elif v <= 40:
        return "LIFE CONTEXT: Only reference life data if the user explicitly asks about schedules, money, or tasks."
    # ... other conditions

def _translate_life_proactivity(v: int) -> str:
    if v <= 20:
        return "PROACTIVITY: Wait to be asked. Never volunteer life data."
    elif v <= 40:
        return "PROACTIVITY: Mention life items only if they're urgent (bills due today, critical overdue tasks)."
    # ... other conditions
```

#### Session Tuner Class
```python
class SessionTuner:
    def __init__(self, rules_path="/opt/mythos/prompts/tuning_rules.yaml"):
        self.rules = load_rules(rules_path)
        self.session_adjustments = {}
        self.signal_log = []

    def analyze_exchange(self, iris_message, user_response, conversation_history):
        signals = self._detect_signals(iris_message, user_response, conversation_history)
        for signal in signals:
            matching_rules = self._match_rules(signal)
            for rule in matching_rules:
                for slider, delta in rule['adjustments'].items():
                    current = self.session_adjustments.get(slider, 0)
                    self.session_adjustments[slider] = current + delta
            self.signal_log.append({
                'signal': signal,
                'timestamp': datetime.now().isoformat(),
                'adjustments_applied': {r['signal']: r['adjustments'] for r in matching_rules},
            })
        return self.session_adjustments

    def _detect_signals(self, iris_message, user_response, history):
        signals = []
        # ... signal detection logic
        return signals
```

This document provides a comprehensive plan for implementing adaptive personality tuning in the Iris system, detailing the necessary changes to the existing architecture and the introduction of new components to achieve the desired adaptability.
