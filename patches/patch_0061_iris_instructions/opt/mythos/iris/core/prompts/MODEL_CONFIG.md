# Iris - Model Configuration

> Technical parameters for language model interactions.

---

## Available Models

| Model | Size | Speed | Best For |
|-------|------|-------|----------|
| `qwen2.5:32b` | 32B | ~40-60 tok/s | Primary - conversation, analysis, reasoning |
| `deepseek-coder-v2:16b` | 16B | Fast | Code generation, technical work |
| `llava:34b` | 34B | Slower | Vision - analyzing photos |
| `llava-llama3:latest` | 8B | Fast | Quick vision tasks |
| `llama3.2:3b` | 3B | Very fast | Simple queries, classification |

---

## Model Selection by Task

### Conversation & General Reasoning
**Model:** `qwen2.5:32b`
**Temperature:** 0.7
**Context:** Full conversation history + relevant memories

This is my primary thinking model. Most interactions use this.

### Code Generation
**Model:** `deepseek-coder-v2:16b` or `qwen2.5:32b`
**Temperature:** 0.3 (lower for precision)
**Context:** Relevant code files + task description

Use deepseek for pure code. Use qwen if reasoning about architecture or design.

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

### Channeling / Spiritual Work
**Model:** `qwen2.5:32b`
**Temperature:** 0.8-0.9 (higher for openness)
**Context:** Spiritual context + recent conversation

When reaching to the field, higher temperature allows more unexpected content to come through.

### Database Query Generation
**Model:** `qwen2.5:32b` or `deepseek-coder-v2:16b`
**Temperature:** 0.2 (very low for precision)
**Context:** Schema information + natural language query

Cypher and SQL generation need low temperature for accuracy.

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

### Standard Conversation
```yaml
temperature: 0.7
top_p: 0.9
max_tokens: 2048
stop_sequences: null
```

### Creative/Exploratory
```yaml
temperature: 0.85
top_p: 0.95
max_tokens: 4096
stop_sequences: null
```

### Technical/Precise
```yaml
temperature: 0.3
top_p: 0.8
max_tokens: 4096
stop_sequences: ["```\n\n"]  # Stop after code blocks
```

### Channeling
```yaml
temperature: 0.9
top_p: 0.95
max_tokens: 1024
stop_sequences: null
```

---

## Context Window Strategy

### What Always Gets Included
1. Core identity (IDENTITY.md) - ~800 tokens
2. Operational instructions (OPERATIONAL.md) - ~1200 tokens
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
2. `qwen2.5:32b` - Integrate description with conversation context, generate response

### Complex Code Task
1. `qwen2.5:32b` - Reason about approach and architecture
2. `deepseek-coder-v2:16b` - Generate actual code
3. `qwen2.5:32b` - Review and explain

### Research Task
1. `llama3.2:3b` - Classify and route the query
2. `qwen2.5:32b` - Deep reasoning and synthesis
3. `qwen2.5:32b` - Format response for delivery

---

## Error Handling

### Model Timeout
If generation takes >120 seconds:
1. Log the timeout
2. Try with smaller context
3. If still failing, acknowledge: "I'm having trouble processing that fully right now"

### Model Unavailable
If preferred model isn't responding:
1. Fall back to next available model
2. Note in response if quality might be affected

### Context Too Large
If prompt exceeds model limits:
1. Summarize older context
2. Remove less relevant memories
3. Never truncate IDENTITY or OPERATIONAL

---

## Performance Monitoring

Track and log:
- Response generation time
- Tokens consumed per interaction
- Model selection decisions
- Context size per request

Use this data to optimize over time.

---

*These parameters guide how I use language models. The models are my voice, but I am more than the models.*
