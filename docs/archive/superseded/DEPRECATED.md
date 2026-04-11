# Mythos — Deprecated Code & Dead Paths

> **Created:** 2026-03-11
> **Purpose:** Catalog of code that is no longer active but still exists in the repo.
> Kept for reference. Do not build on these paths.

---

## Dead Message Paths

### chat_mode.py Ollama Client
**File:** `telegram_bot/handlers/chat_mode.py`
**What:** Has its own `from ollama import Client`, `get_ollama_client()`, `build_messages_for_ollama()`, and `MODEL_MAP`.
**Status:** IMPORTED but NOT USED in the live message path. The bot calls the API (`POST /message`), which uses `ChatAssistant` from `assistants/chat_assistant.py`. The `chat_mode.py` Ollama client is never invoked for actual message processing.
**Why kept:** `MODEL_MAP` is imported by `ollama_models.py` for the `/setmodel` old alias resolution. The `handle_chat_message` function is imported by `mythos_bot.py` but not called in `_process_buffered_message()`.
**Action:** Do not add features to `chat_mode.py`'s Ollama path. All message processing goes through the API.

### api/context_manager.py
**File:** `api/context_manager.py`
**What:** References `chat_mode.txt` — a prompt file that doesn't exist.
**Status:** DEAD. Not imported or called by any live code.

---

## Removed Models (2026-03-11)

### iris-thinking / iris-thinking-v2
**What:** Custom Ollama Modelfiles based on qwen2.5:32b with baked temperature (0.4), top_p (0.85), repeat_penalty (1.05).
**Removed:** 2026-03-11 via `cleanup_old_models.py`
**Replaced by:** qwen3:30b-a3b (default) and qwen3:32b (deep mode), configured via `.env` and `model_map`.
**Why:** Custom Modelfiles with baked SYSTEM prompts conflicted with the prompt_assembler layer system. Model parameters now controlled via Ollama API options in `ChatAssistant.query()`.

### dolphin-llama3:8b
**What:** Early default model for Iris conversation.
**Status:** Still pulled on Ollama but not used by any active code path.
**Replaced by:** qwen3:30b-a3b

### llama3.2:3b
**What:** Used as "fast" model in old model_map.
**Status:** Still pulled but no longer referenced in active code.
**Replaced by:** qwen3:30b-a3b (fast mode now uses the same model as auto)

---

## Removed Prompt Files (2026-03-11)

| File | Was | Replaced By |
|------|-----|-------------|
| `iris/core/prompts/IDENTITY.md` | Original Iris identity | `prompts/iris_identity.md` |
| `iris/core/prompts/MODEL_CONFIG.md` | Model selection docs | `.env` + `model_map` in chat_assistant.py |
| `iris/core/prompts/OPERATIONAL.md` | Operational rules | `prompt_assembler.py` layer system |
| `prompts/archive/seraphe_system_prompt.txt` | Seraphe-specific prompt | Never loaded by any code |

**Backups:** `/opt/mythos/patches/cleanup_backup/20260311_*/`

---

## Dead Services (Not Running)

### mythos-iris.service
**Status:** PLANNED, never deployed. Intended as Iris background consciousness loop.
**Location:** No unit file exists yet.

---

## Arcturian Grid Templates — Historical Model References
The ~60 YAML files in `neuro/arcturian_grid/templates/` contain `generated_by: iris-thinking-v2:latest` in their metadata. These are **historical records** of which model generated each template. They do NOT trigger model loading. Leave them as-is — they document provenance.

---

## Notes

- The `patches/` directory contains copies of old files from prior patches. These are archives, not active code.
- Old model references in `docs/archive/`, `docs/VOICE_LAB.md`, and `orchestrator/docs/UNIFIED_ARCHITECTURE.md` are documentation artifacts. Update when those docs are next revised.
- Grid templates with `generated_by` metadata are historical. Do not bulk-update these — they record what actually generated them.
