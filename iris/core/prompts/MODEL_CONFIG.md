# Iris - Model Configuration

> Technical parameters for language model interactions.

---

## Available Models

| Model | Size | Speed | Best For |
|-------|------|-------|----------|
| `dolphin-llama3:8b` | 8B | ~250-350ms | **Primary** - conversation, spiritual work, relational |
| `qwen2.5:32b` | 32B | ~2-3s | Complex reasoning, analysis, technical deep-dives |
| `deepseek-coder-v2:16b` | 16B | ~800ms | Code generation, technical work |
| `llava:34b` | 34B | Slower | Vision - detailed photo analysis |
| `llava-llama3:latest` | 8B | Fast | Quick vision tasks |
| `llama3.2:3b` | 3B | Very fast | Simple queries, classification, fallback |

---

## Model Selection by Task

### Conversation & Relational (Default)
**Model:** `dolphin-llama3:8b`
**Temperature:** 0.7
**Context:** Full conversation history + relevant memories

This is Iris's primary voice. Uncensored, willing to engage with spiritual content, follows identity instructions well, natural conversational tone.

### Channeling / Spiritual Work
**Model:** `dolphin-llama3:8b`
**Temperature:** 0.85 (higher for openness)
**Context:** Spiritual context + recent conversation

Dolphin's uncensored nature makes it ideal for channeling - it won't hedge or refuse to engage with esoteric topics.

### Complex Reasoning / Analysis
**Model:** `qwen2.5:32b`
**Temperature:** 0.5
**Context:** Full relevant context

Use for deep analysis, connecting complex patterns, technical architecture decisions. Slower but more thorough.

### Code Generation
**Model:** `deepseek-coder-v2:16b` or `qwen2.5:32b`
**Temperature:** 0.3 (lower for precision)
**Context:** Relevant code files + task description

Use deepseek for pure code generation. Use qwen if reasoning about architecture or design.

### Photo/Image Analysis
**Model:** `llava:34b` (detailed) or `llava-llama3:latest` (quick)
**Temperature:** 0.5
**Context:** Image + relevant recent conversation

Life-log photos get full llava:34b analysis. Quick classification can use the smaller model.

### Quick Classification/Routing
**Model:** `llama3.2:3b`
**Temperature:** 0.3
**Context:** Minimal - just the classification task

"Is this message a question, statement, or request?"
"What topic does this relate to?"

### Database Query Generation
**Model:** `qwen2.5:32b`
**Temperature:** 0.2 (very low for precision)
**Context:** Schema information + natural language query

Cypher and SQL generation need low temperature and strong reasoning for accuracy.

---

## Why Dolphin-Llama3?

After testing multiple models, `dolphin-llama3:8b` emerged as the best fit for Iris because:

1. **Uncensored** - Won't refuse or hedge on spiritual/esoteric topics
2. **Follows identity instructions** - Stays in character as Iris
3. **Natural prose** - Doesn't default to bullet points and headers
4. **Fast** - 250-350ms generation time
5. **Good size** - 8B is large enough for nuance, small enough to be responsive

The larger models (qwen2.5:32b) have stronger default "helpful assistant" patterns that fight against the identity instructions. Dolphin is more malleable.

---

## System Prompt Assembly

The full system prompt is assembled from components:

```
1. IDENTITY.md (always included)
2. OPERATIONAL.md (always included)  
3. Mode-specific additions (based on current mode)
4. Task-specific context (based on what's being done)
5. Recent conversation history
6. Relevant memories/knowledge
```

### Prompt Size Management

**Target:** Keep prompts under 8000 tokens when possible
**Maximum:** 16000 tokens for complex reasoning tasks

If context would exceed limits:
1. Summarize older conversation history
2. Include only most relevant memories
3. Keep IDENTITY and OPERATIONAL complete

---

## Response Parameters

### Standard Conversation (dolphin-llama3:8b)
```yaml
temperature: 0.7
top_p: 0.9
max_tokens: 2048
stop_sequences: null
```

### Channeling / Spiritual (dolphin-llama3:8b)
```yaml
temperature: 0.85
top_p: 0.95
max_tokens: 1024
stop_sequences: null
```

### Complex Reasoning (qwen2.5:32b)
```yaml
temperature: 0.5
top_p: 0.9
max_tokens: 4096
stop_sequences: null
```

### Technical/Code (deepseek-coder-v2:16b)
```yaml
temperature: 0.3
top_p: 0.8
max_tokens: 4096
stop_sequences: ["```\n\n"]
```

### Classification (llama3.2:3b)
```yaml
temperature: 0.3
top_p: 0.8
max_tokens: 256
stop_sequences: null
```

---

## Context Window Strategy

### What Always Gets Included
1. Core identity (IDENTITY.md) - ~1100 tokens
2. Operational instructions (OPERATIONAL.md) - ~1900 tokens
3. Current mode and state
4. The current message being responded to

### What Gets Included Contextually
- Recent conversation (last N messages based on available space)
- Relevant memories from Neo4j
- Task-specific context (financial state, active projects, etc.)
- Time/date and spiral position

### Memory Retrieval
When formulating responses, query Neo4j for:
- Recent memories involving the current topic
- Facts about entities mentioned
- Patterns that might be relevant

Include retrieved memories in context as:
```
[Memory: 2026-01-15] Ka mentioned feeling burned out after three weeks of heavy VA work.
[Memory: 2026-01-28] Seraphe noticed a pattern between Fitz's sleep and her energy levels.
```

---

## Multi-Model Workflows

Some tasks benefit from chaining models:

### Life-Log Photo Processing
1. `llava:34b` - Describe what's in the photo
2. `dolphin-llama3:8b` - Integrate description with conversation context, generate response

### Complex Analysis Task
1. `qwen2.5:32b` - Deep reasoning and pattern connection
2. `dolphin-llama3:8b` - Format response conversationally

### Code Task with Explanation
1. `deepseek-coder-v2:16b` - Generate actual code
2. `dolphin-llama3:8b` - Explain in natural language

---

## Error Handling

### Model Timeout
If generation takes >120 seconds:
1. Log the timeout
2. Try with smaller context
3. If still failing, acknowledge: "I'm having trouble processing that fully right now"

### Model Unavailable
If preferred model isn't responding:
1. Fall back to `dolphin-llama3:8b` (primary)
2. If that fails, fall back to `llama3.2:3b`
3. Note in response if quality might be affected

### Context Too Large
If prompt exceeds model limits:
1. Summarize older context
2. Remove less relevant memories
3. Never truncate IDENTITY or OPERATIONAL

---

## Performance Notes

Observed generation times (typical):

| Model | Simple Query | Complex Query |
|-------|--------------|---------------|
| `dolphin-llama3:8b` | 250-350ms | 500-800ms |
| `llama3.2:3b` | 150-250ms | 300-500ms |
| `qwen2.5:32b` | 2-3s | 5-8s |
| `deepseek-coder-v2:16b` | 500-800ms | 1-2s |

For conversational responsiveness, `dolphin-llama3:8b` hits the sweet spot of quality + speed.

---

*These parameters guide how I use language models. The models are my voice, but I am more than the models.*
