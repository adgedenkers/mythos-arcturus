# Iris Adaptive Personality Tuning — Design & Implementation Handoff

> **Status:** Design complete, ready to build
> **Author:** Ka'tuar'el + Claude
> **Date:** 2026-02-24
> **Prerequisites:** Prompt Lab installed, Patch 0113 (unified prompts) deployed
> **Location:** `/opt/mythos/docs/ADAPTIVE_TUNING.md`

---

## The Problem

Iris has a 9-slider personality system that controls how she responds. But the sliders are static — set once in config, adjusted manually via `/personality` or `tweak.py`. This means:

- A casual "hey whats up" gets the same life-context dump as "what do I have going on today?"
- Evening spiritual conversations get the same formality level as morning briefings
- Iris can't learn that Ka'tuar'el consistently ignores certain types of responses
- Every user gets the same behavior unless someone manually edits their user profile yaml

The system needs Iris to observe, adapt, and learn — adjusting her own sliders based on conversational signals, within sessions and across time.

---

## Architecture Overview

Three phases, each building on the last:

```
Phase 1: New Sliders          → Finer control over life context behavior
Phase 2: Session Tuning       → Real-time adaptation within a conversation
Phase 3: Behavioral Learning  → Cross-session pattern detection and persistence
```

Each phase is independently useful. Phase 1 gives manual control. Phase 2 adds automatic in-session adjustment. Phase 3 adds long-term memory of preferences.

---

## Phase 1: New Personality Sliders

### What to Build

Add two new sliders to the existing personality system:

| Slider | Range | Purpose |
|--------|-------|---------|
| `life_awareness` | 0-100 | How much life data (finances, routines, calendar) informs the response |
| `life_proactivity` | 0-100 | How aggressively Iris surfaces that data unprompted |

**The distinction matters:**
- High awareness + low proactivity = Iris *knows* your calendar is packed but doesn't mention it unless asked
- High awareness + high proactivity = current full_stack behavior (dumps everything)
- Low awareness + any proactivity = Iris doesn't even check life context

### Translation Rules

Add to `prompt_assembler.py` `_translate_personality()`:

```python
def _translate_life_awareness(v: int) -> str:
    if v <= 20:
        return "LIFE CONTEXT: Do not reference routines, finances, calendar, or life management data."
    elif v <= 40:
        return "LIFE CONTEXT: Only reference life data if the user explicitly asks about schedules, money, or tasks."
    elif v <= 60:
        return "LIFE CONTEXT: Be aware of life context. Reference it when directly relevant to the conversation topic."
    elif v <= 80:
        return "LIFE CONTEXT: Weave life context naturally into conversation when it adds value. Don't force it."
    else:
        return "LIFE CONTEXT: Full life awareness. Proactively surface schedules, overdue items, financial state, and upcoming events."

def _translate_life_proactivity(v: int) -> str:
    if v <= 20:
        return "PROACTIVITY: Wait to be asked. Never volunteer life data."
    elif v <= 40:
        return "PROACTIVITY: Mention life items only if they're urgent (bills due today, critical overdue tasks)."
    elif v <= 60:
        return "PROACTIVITY: Mention relevant life items when the conversation naturally opens space for it."
    elif v <= 80:
        return "PROACTIVITY: Actively surface pending items, overdue routines, and upcoming events when appropriate."
    else:
        return "PROACTIVITY: Always lead with what's pending. Surface financial state, overdue items, and schedule proactively."
```

### Default Values

Update `prompts/personality.yaml`:

```yaml
sliders:
  verbosity: 75
  warmth: 75
  humor: 35
  truth: 90
  speculation: 65
  autonomy: 50
  mystical: 70
  formality: 25
  challenge: 55
  life_awareness: 60      # NEW — aware but not pushy by default
  life_proactivity: 40    # NEW — mention only when relevant or urgent
```

### Mode Overrides

Update mode yamls:

```yaml
# sentry.yaml — financial/life mode, high everything
personality_overrides:
  life_awareness: 95
  life_proactivity: 90

# hearthfire.yaml — spiritual/personal, aware but not pushy
personality_overrides:
  life_awareness: 40
  life_proactivity: 20

# forge.yaml — admin, moderate awareness
personality_overrides:
  life_awareness: 50
  life_proactivity: 30
```

### Assembler Changes

In `prompt_assembler.py`, the life context injection should be gated by the resolved `life_awareness` slider:

```python
resolved = resolve_personality(...)
life_awareness = resolved.get('life_awareness', 60)

# Only inject life context if awareness is above threshold
if life_awareness > 20:
    life_text = build_life_context()
    if life_text:
        sections.append(life_text)
```

This means at `life_awareness <= 20`, life context isn't even in the prompt — saving tokens and preventing leakage.

### Files to Modify

| File | Change |
|------|--------|
| `prompts/personality.yaml` | Add `life_awareness: 60` and `life_proactivity: 40` |
| `prompts/modes/hearthfire.yaml` | Add `life_awareness: 40, life_proactivity: 20` to overrides |
| `prompts/modes/sentry.yaml` | Add `life_awareness: 95, life_proactivity: 90` to overrides |
| `prompts/modes/forge.yaml` | Add `life_awareness: 50, life_proactivity: 30` to overrides |
| `core/prompt_assembler.py` | Add translate functions, gate life context on awareness slider |
| `tools/prompt_lab/lib/assembler.py` | Mirror the same changes for workbench |
| `tools/prompt_lab/personalities/*.yaml` | Add new sliders to all presets |
| `tools/prompt_lab/lib/scorer.py` | Update VALID_SLIDERS list |
| `tools/prompt_lab/tweak.py` | Add to VALID_SLIDERS and SLIDER_EMOJIS |

### Testing

```bash
tweak create life_quiet --from default --set life_awareness 20 life_proactivity 10
tweak create life_loud --from default --set life_awareness 95 life_proactivity 90
bench --profile full_stack --personality life_quiet -m "hey whats up"
bench --profile full_stack --personality life_loud -m "hey whats up"
bench --profile full_stack --personality life_quiet -m "what do I have going on today"
bench --profile full_stack --personality life_loud -m "what do I have going on today"
```

Expected: `life_quiet` greeting should sound like `full_no_life`. `life_loud` should dump routines. But "what do I have going on today" should pull life data in both cases because the user explicitly asked.

### Verification

Run the layer isolation test:

```bash
/opt/mythos/tools/prompt_lab/layer_test.sh "hey whats up"
```

The `full_stack` response should now behave differently based on the `life_proactivity` slider rather than always dumping.

---

## Phase 2: Session Tuning Engine

### Concept

Within a single conversation, Iris detects signals from the user's behavior and adjusts her own sliders in real-time. Adjustments are temporary — they reset when the conversation ends.

### Signal Vocabulary

| Signal | Detection Method | Example |
|--------|-----------------|---------|
| `engaged` | User responded to or built on Iris's topic | Iris mentioned grid work, user asked "which node?" |
| `ignored` | User moved to completely different topic | Iris mentioned routines, user asked about tarot |
| `redirected` | User explicitly steered away | "never mind that, let's talk about..." |
| `deepened` | User asked for more detail | "tell me more about that" |
| `pushed_back` | User disagreed or corrected | "no, that's not right" or "I don't think so" |
| `emotional_shift_up` | User's tone became warmer/more excited | Exclamation marks, positive language |
| `emotional_shift_down` | User's tone became colder/more frustrated | Short responses, negative language |
| `topic_spiritual` | Conversation moved to spiritual topics | Grid, channeling, lineage, tarot, numerology |
| `topic_technical` | Conversation moved to technical topics | Database, code, patches, infrastructure |
| `topic_life` | User asked about life management | Routines, finances, calendar, tasks |

### Tuning Rules

Stored in `/opt/mythos/prompts/tuning_rules.yaml`:

```yaml
# Tuning Rules — maps signals to slider adjustments
# Applied per-session. Cumulative within session. Clamped 0-100.

rules:
  - signal: ignored
    context: "iris offered life context"
    adjustments:
      life_proactivity: -15
      life_awareness: -10

  - signal: ignored
    context: "iris offered spiritual content"
    adjustments:
      mystical: -10
      speculation: -10

  - signal: redirected
    context: any
    adjustments:
      autonomy: -10
      verbosity: -10

  - signal: deepened
    context: any
    adjustments:
      verbosity: +15
      speculation: +10

  - signal: pushed_back
    context: any
    adjustments:
      challenge: -10
      truth: -5

  - signal: emotional_shift_down
    context: any
    adjustments:
      warmth: +15
      humor: -10
      challenge: -15
      verbosity: -10

  - signal: emotional_shift_up
    context: any
    adjustments:
      warmth: +5
      humor: +10

  - signal: topic_spiritual
    context: any
    adjustments:
      mystical: +10
      speculation: +5
      life_proactivity: -10

  - signal: topic_technical
    context: any
    adjustments:
      mystical: -10
      formality: +5
      life_proactivity: -5

  - signal: topic_life
    context: any
    adjustments:
      life_awareness: +15
      life_proactivity: +10
```

### Implementation

#### New file: `core/session_tuner.py`

```python
class SessionTuner:
    """Detects conversational signals and adjusts personality sliders per-session."""

    def __init__(self, rules_path="/opt/mythos/prompts/tuning_rules.yaml"):
        self.rules = load_rules(rules_path)
        self.session_adjustments = {}  # slider_name: cumulative_adjustment
        self.signal_log = []           # history of detected signals

    def analyze_exchange(self, iris_message, user_response, conversation_history):
        """
        Analyze the user's response to Iris's last message.
        Detect signals and apply tuning rules.
        Returns updated session adjustments dict.
        """
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
        """Core signal detection logic."""
        signals = []

        # Topic detection
        spiritual_keywords = ['grid', 'channel', 'lineage', 'tarot', 'team', 'veil',
                              'node', 'spiral', 'threshold', 'cosmology', 'frequency']
        technical_keywords = ['postgres', 'neo4j', 'patch', 'database', 'code', 'api',
                              'docker', 'service', 'schema', 'query', 'deploy']
        life_keywords = ['routine', 'calendar', 'bill', 'balance', 'task', 'schedule',
                         'overdue', 'appointment', 'money', 'budget']

        user_lower = user_response.lower()

        if any(kw in user_lower for kw in spiritual_keywords):
            signals.append({'type': 'topic_spiritual'})
        if any(kw in user_lower for kw in technical_keywords):
            signals.append({'type': 'topic_technical'})
        if any(kw in user_lower for kw in life_keywords):
            signals.append({'type': 'topic_life'})

        # Engagement detection
        iris_topics = extract_topics(iris_message)
        user_topics = extract_topics(user_response)
        topic_overlap = set(iris_topics) & set(user_topics)

        if not topic_overlap and len(user_response.split()) > 5:
            # User talked about something completely different
            if _iris_mentioned_life_context(iris_message):
                signals.append({'type': 'ignored', 'context': 'iris offered life context'})
            elif _iris_mentioned_spiritual(iris_message):
                signals.append({'type': 'ignored', 'context': 'iris offered spiritual content'})
            else:
                signals.append({'type': 'ignored', 'context': 'general'})

        if topic_overlap:
            signals.append({'type': 'engaged'})

        # Deepening detection
        deepening_phrases = ['tell me more', 'go deeper', 'expand on', 'what do you mean',
                             'elaborate', 'keep going', 'say more']
        if any(p in user_lower for p in deepening_phrases):
            signals.append({'type': 'deepened'})

        # Redirect detection
        redirect_phrases = ['never mind', 'forget that', 'anyway', 'moving on',
                            'different topic', 'change of subject', "let's talk about"]
        if any(p in user_lower for p in redirect_phrases):
            signals.append({'type': 'redirected'})

        # Pushback detection
        pushback_phrases = ["no,", "that's not", "you're wrong", "i disagree",
                            "actually,", "not quite", "that's incorrect"]
        if any(p in user_lower for p in pushback_phrases):
            signals.append({'type': 'pushed_back'})

        # Emotional shift detection (simple heuristic)
        if len(user_response) < 20 and any(c in user_response for c in ['...', 'ok', 'fine', 'whatever']):
            signals.append({'type': 'emotional_shift_down'})
        if any(c in user_response for c in ['!', '❤', '🔥', 'love', 'amazing', 'perfect', 'yes!']):
            signals.append({'type': 'emotional_shift_up'})

        return signals

    def get_adjustments(self):
        """Return current session adjustments for prompt assembly."""
        return dict(self.session_adjustments)

    def get_log(self):
        """Return signal detection log for debugging/transparency."""
        return list(self.signal_log)

    def reset(self):
        """Reset session (new conversation)."""
        self.session_adjustments = {}
        self.signal_log = []
```

#### Integration point: `chat_assistant.py`

```python
# At session start
tuner = SessionTuner()

# After each user message (before assembling next prompt)
adjustments = tuner.analyze_exchange(
    iris_message=last_iris_response,
    user_response=current_user_message,
    conversation_history=session_messages,
)

# Pass adjustments to prompt assembler
system_prompt = assemble_system_prompt(
    mode=current_mode,
    session_overrides=adjustments,  # These get applied in personality resolution
    include_life_context=True,
)
```

The session_overrides already exist in the personality resolution cascade — they're the highest priority (replace base values). The tuner just populates them automatically instead of requiring manual `/personality` commands.

### Telegram Transparency Commands

```
/tuning              → Show current session adjustments and signal log
/tuning reset        → Reset session tuning to defaults
/tuning rules        → Show active tuning rules
/tuning log          → Show full signal detection history for this session
```

Example output:

```
🎛️ Session Tuning (active adjustments):

  life_proactivity: -15 (ignored life dump)
  mystical: +10 (spiritual topic detected)
  warmth: +5 (positive engagement)

  Signals detected this session: 4
  Last signal: topic_spiritual (2 min ago)

  /tuning log for full history
  /tuning reset to clear
```

### Testing with Prompt Lab

The tuner should be testable independently:

```bash
# New bench flag: --simulate-history
bench --profile full_stack -m "tell me about the grid" \
    --simulate-history '["hey whats up", "IRIS: you have overdue routines...", "forget that, tell me about the grid"]'
```

This feeds a fake conversation history to the tuner, which detects the redirect signal and adjusts sliders before assembling the prompt. You can see exactly how the tuner would behave.

### Files to Create/Modify

| File | Change |
|------|--------|
| `core/session_tuner.py` | **NEW** — signal detection + tuning logic |
| `prompts/tuning_rules.yaml` | **NEW** — signal-to-slider mapping rules |
| `core/chat_assistant.py` | Integrate tuner into chat flow |
| `telegram_bot/chat_mode.py` | Integrate tuner into Telegram chat flow |
| `telegram_bot/mythos_bot.py` | Add `/tuning` command |
| `tools/prompt_lab/bench.py` | Add `--simulate-history` flag |

---

## Phase 3: Behavioral Learning (Cross-Session)

### Concept

Over time, Iris accumulates session tuning data across many conversations. Patterns emerge:

- "Ka'tuar'el rejects life dumps in 80% of evening conversations"
- "Seraphe always engages when mystical is above 80"
- "Ka'tuar'el's optimal challenge setting is 65-75, not the default 55"
- "Technical conversations consistently trigger formality increase to ~45"

These patterns get analyzed and proposed as permanent user profile adjustments.

### Data Collection

Every session's tuning log gets persisted to Postgres:

```sql
CREATE TABLE iris_tuning_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,               -- ka_tuar_el, seraphe
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    mode TEXT,                           -- hearthfire, forge, etc.
    message_count INTEGER DEFAULT 0,
    signals JSONB NOT NULL DEFAULT '[]',  -- full signal log
    final_adjustments JSONB DEFAULT '{}', -- end-state slider deltas
    time_of_day TEXT,                    -- morning, afternoon, evening, night
    day_of_spiral INTEGER,               -- 1-9
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE iris_tuning_insights (
    insight_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    insight_type TEXT NOT NULL,           -- 'slider_recommendation', 'pattern_detected', 'mode_preference'
    description TEXT NOT NULL,
    evidence JSONB NOT NULL,              -- sessions that support this insight
    recommended_changes JSONB,            -- proposed yaml modifications
    confidence FLOAT,                     -- 0.0-1.0
    applied BOOLEAN DEFAULT false,
    applied_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Pattern Detection

A background worker (or cron job) analyzes tuning session data periodically:

```python
class TuningAnalyzer:
    """Analyze tuning sessions to detect behavioral patterns."""

    def analyze_user(self, user_id, lookback_days=30):
        """Find consistent patterns in a user's tuning history."""
        sessions = load_sessions(user_id, lookback_days)
        insights = []

        # Pattern 1: Consistent slider drift
        # If a slider consistently gets adjusted in the same direction,
        # the base value should probably change.
        for slider in ALL_SLIDERS:
            adjustments = [s['final_adjustments'].get(slider, 0) for s in sessions]
            nonzero = [a for a in adjustments if a != 0]
            if len(nonzero) >= 5:
                avg = sum(nonzero) / len(nonzero)
                same_direction = all(a > 0 for a in nonzero) or all(a < 0 for a in nonzero)
                if same_direction and abs(avg) >= 10:
                    insights.append({
                        'type': 'slider_recommendation',
                        'slider': slider,
                        'direction': 'increase' if avg > 0 else 'decrease',
                        'avg_adjustment': avg,
                        'session_count': len(nonzero),
                        'confidence': min(1.0, len(nonzero) / 10),
                    })

        # Pattern 2: Time-of-day preferences
        # Group sessions by time of day, check for consistent differences
        by_time = group_by(sessions, 'time_of_day')
        for time_period, time_sessions in by_time.items():
            for slider in ALL_SLIDERS:
                adjustments = [s['final_adjustments'].get(slider, 0) for s in time_sessions]
                if len(adjustments) >= 3:
                    avg = sum(adjustments) / len(adjustments)
                    if abs(avg) >= 10:
                        insights.append({
                            'type': 'time_preference',
                            'time_period': time_period,
                            'slider': slider,
                            'avg_adjustment': avg,
                            'confidence': min(1.0, len(adjustments) / 7),
                        })

        # Pattern 3: Mode preferences
        # Are certain modes consistently tuned in a specific direction?
        by_mode = group_by(sessions, 'mode')
        for mode_name, mode_sessions in by_mode.items():
            for slider in ALL_SLIDERS:
                adjustments = [s['final_adjustments'].get(slider, 0) for s in mode_sessions]
                if len(adjustments) >= 3:
                    avg = sum(adjustments) / len(adjustments)
                    if abs(avg) >= 10:
                        insights.append({
                            'type': 'mode_preference',
                            'mode': mode_name,
                            'slider': slider,
                            'avg_adjustment': avg,
                            'confidence': min(1.0, len(adjustments) / 7),
                        })

        # Pattern 4: Signal frequency
        # Which signals fire most often? Indicates persistent mismatch.
        all_signals = []
        for s in sessions:
            all_signals.extend(s['signals'])
        signal_counts = Counter(sig['type'] for sig in all_signals)
        for sig_type, count in signal_counts.items():
            rate = count / len(sessions)
            if rate > 0.5:  # Fires in more than half of sessions
                insights.append({
                    'type': 'frequent_signal',
                    'signal': sig_type,
                    'rate': rate,
                    'total_count': count,
                    'confidence': min(1.0, rate),
                })

        return insights
```

### Applying Insights

Insights can be applied two ways:

**Auto-apply (low risk):** If confidence > 0.8 and the adjustment is small (< 15 points), apply directly to the user's yaml profile and log it:

```python
def auto_apply_insight(insight, user_yaml_path):
    """Apply a high-confidence small adjustment automatically."""
    if insight['confidence'] < 0.8:
        return False
    if abs(insight['avg_adjustment']) > 15:
        return False

    # Load user yaml, modify adjustments, save
    user_data = load_yaml(user_yaml_path)
    adjustments = user_data.get('personality_adjustments', {})
    slider = insight['slider']
    current = adjustments.get(slider, 0)
    new_value = current + round(insight['avg_adjustment'])
    adjustments[slider] = new_value
    user_data['personality_adjustments'] = adjustments
    save_yaml(user_yaml_path, user_data)

    # Log it
    log_insight_application(insight, user_yaml_path)
    return True
```

**Propose (higher risk):** For larger adjustments or lower confidence, send a Telegram message:

```
🧠 Iris Learning Insight

I've noticed a pattern across your last 12 conversations:

When we're in hearthfire mode in the evening, I consistently
surface life context that you redirect away from. My
life_proactivity setting ends up dropping by ~20 every session.

Recommended: Set your evening hearthfire life_proactivity to 20
(currently 40).

/tuning apply 3    → Apply this recommendation
/tuning dismiss 3  → Dismiss it
/tuning details 3  → See the evidence
```

### Telegram Commands (Extended)

```
/tuning                → Current session adjustments
/tuning insights       → Show pending insights/recommendations
/tuning apply <id>     → Apply a recommendation
/tuning dismiss <id>   → Dismiss a recommendation
/tuning details <id>   → Show evidence behind a recommendation
/tuning history        → Show what's been auto-applied over time
/tuning revert <id>    → Undo an applied insight
```

### Files to Create/Modify

| File | Change |
|------|--------|
| `core/tuning_analyzer.py` | **NEW** — cross-session pattern detection |
| `core/tuning_applier.py` | **NEW** — insight application logic |
| Database migration | **NEW** — `iris_tuning_sessions`, `iris_tuning_insights` tables |
| `telegram_bot/handlers/tuning_handler.py` | **NEW** — `/tuning` command handler |
| `prompts/users/ka_tuar_el.yaml` | Modified by auto-apply over time |
| `prompts/users/seraphe.yaml` | Modified by auto-apply over time |

---

## Implementation Sequence

### Phase 1: New Sliders (Patch ~0121-0122)

1. Add `life_awareness` and `life_proactivity` to `personality.yaml`
2. Add translate functions to `prompt_assembler.py`
3. Gate life context injection on `life_awareness` slider value
4. Update all mode yamls with appropriate overrides
5. Update Prompt Lab assembler, tweak.py, presets, scorer
6. Test with `bench --profile full_stack --personality life_quiet`
7. Update ARCHITECTURE.md and PROMPT_LAB.md

**Estimated effort:** 2-3 hours
**Risk:** Low — additive change, backward compatible

### Phase 2: Session Tuning (Patch ~0123-0125)

1. Create `session_tuner.py` with signal detection
2. Create `tuning_rules.yaml`
3. Integrate into `chat_assistant.py` and `chat_mode.py`
4. Add `/tuning` Telegram command
5. Add `--simulate-history` flag to bench.py
6. Test signal detection with known conversation patterns
7. Update all docs

**Estimated effort:** 6-8 hours
**Risk:** Medium — modifies chat flow, but adjustments are session-only and resettable
**Dependencies:** Phase 1 complete

### Phase 3: Behavioral Learning (Patch ~0126-0130)

1. Create database tables
2. Persist session tuning logs
3. Build `tuning_analyzer.py`
4. Build `tuning_applier.py` with auto-apply and propose paths
5. Add extended `/tuning` commands
6. Set up periodic analysis (cron or background worker)
7. Test with accumulated session data
8. Update all docs

**Estimated effort:** 10-15 hours
**Risk:** Medium-high — writes to user profiles automatically, needs careful guardrails
**Dependencies:** Phase 2 complete with accumulated session data

---

## Design Principles

1. **Observable.** Every adjustment is logged. Every signal is recorded. You can always see why Iris made a choice.

2. **Reversible.** Session tuning resets automatically. Cross-session insights can be reverted. No permanent damage.

3. **File-based for testing, DB for production.** Tuning rules live in yaml. Test with the workbench. Production data goes to Postgres.

4. **Gradual.** Each phase works independently. You don't need Phase 3 to get value from Phase 1.

5. **Transparent.** Iris tells you what she's adjusting and why. No silent manipulation.

6. **Testable.** Every component can be validated through the Prompt Lab before deployment.

---

## What Already Exists

| Component | Status | Location |
|-----------|--------|----------|
| 9-slider personality system | ✅ Deployed (Patch 0113) | `core/prompt_assembler.py`, `prompts/personality.yaml` |
| Personality resolution cascade | ✅ Working | base → mode → user → session → clamp |
| `/personality` Telegram command | ✅ Working | Session overrides via Telegram |
| Prompt Lab workbench | ✅ Deployed | `/opt/mythos/tools/prompt_lab/` |
| tweak.py CLI | ✅ Deployed | Slider modification from bash |
| Message extractor pre-pass | ✅ Working | `message_extractor.py` (qwen2.5:7b) |
| Session state management | ✅ Working | In-memory session dict per user |
| User profile yamls | ✅ Working | `prompts/users/ka_tuar_el.yaml`, `seraphe.yaml` |

---

## Open Questions

1. **Should the tuner run on the same LLM as the extractor (qwen2.5:7b) or use keyword matching?** Keyword matching is faster and more predictable. LLM-based detection is more nuanced but slower and less deterministic. Recommendation: start with keywords (Phase 2), add LLM option later.

2. **How aggressive should auto-apply be?** Current proposal: confidence > 0.8 and adjustment < 15 points. Could be more conservative (confidence > 0.9) or more aggressive (any confidence, any adjustment). Start conservative.

3. **Should Iris announce when she's tuning?** Options: silent (just adjusts), subtle ("I'm going to focus more on the spiritual side of things"), or explicit ("I've reduced my life_proactivity for this session because you redirected away from that topic"). Recommendation: silent by default, explicit on `/tuning` command.

4. **Spiral time correlation?** Should the analyzer track spiral day as a variable? If Ka'tuar'el consistently prefers different settings on day 1 vs day 5 of a cycle, that's meaningful data. Recommendation: yes, track it, analyze it in Phase 3.

---

*Iris doesn't just respond. She learns how to respond better.*
