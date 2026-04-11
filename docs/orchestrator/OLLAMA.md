---
title: "Ollama Model Management Integration"
category: orchestrator
status: active
stream: LOG
location: docs
tags: [ollama, model-management, api]
created: unknown
updated: 2026-03-12
author: Adge Denkers
---

# Ollama Integration

**Phase 1.2** - Model Management and Ollama API Integration

---

## Overview

Phase 1.2 adds comprehensive Ollama integration, enabling the orchestrator to discover, register, and manage local LLM models.

**Components:**
- **OllamaClient** - Async API wrapper for Ollama
- **ModelRegistry** - Database-backed model registry
- **ModelManager** - High-level model operations

---

## Quick Start

### Register Models

```bash
# Sync installed Ollama models to database
cd /opt/mythos/orchestrator/scripts
./register_models.sh
```

### Python Usage

```python
import asyncio
from models import ModelManager, OllamaClient

async def main():
    # High-level operations
    manager = ModelManager()
    
    # Sync models from Ollama
    await manager.sync_models()
    
    # List available models
    models = await manager.get_available_models()
    for model in models:
        print(model['name'])
    
    # Generate completion
    response = await manager.generate(
        "qwen2.5:32b",
        "What is 2+2?"
    )
    print(response)
    
    # Low-level Ollama access
    async with OllamaClient() as client:
        models = await client.list_models()
        result = await client.generate("llama3.1:70b", "Hello!")

asyncio.run(main())
```

---

## OllamaClient

Async wrapper for Ollama API.

### Methods

**list_models()** - List installed models
```python
async with OllamaClient() as client:
    models = await client.list_models()
```

**show_model(name)** - Get model details
```python
details = await client.show_model("llama3.1:70b")
```

**generate(model, prompt, ...)** - Generate completion
```python
response = await client.generate(
    model="qwen2.5:32b",
    prompt="Explain quantum computing",
    temperature=0.7
)
```

**pull_model(name)** - Pull model (streaming)
```python
async for progress in client.pull_model("llama3.1:70b"):
    print(progress['status'])
```

**delete_model(name)** - Delete model
```python
success = await client.delete_model("old_model:7b")
```

---

## ModelRegistry

Database-backed model registry.

### Methods

**register_model(name, ...)** - Register a model
```python
registry = ModelRegistry()
model_id = await registry.register_model(
    name="llama3.1:70b",
    size_params="70B",
    context_window=128000
)
```

**get_model(model_id)** - Get model by ID
```python
model = await registry.get_model("llama3_1_70b")
```

**list_models(provider, installed_only)** - List models
```python
models = await registry.list_models(
    provider="ollama",
    installed_only=True
)
```

**add_capability(model_id, task_type, ...)** - Add capability
```python
await registry.add_capability(
    model_id="llama3_1_70b",
    task_type="math",
    quality_score=0.95
)
```

**get_best_model_for_task(task_type)** - Find best model
```python
best = await registry.get_best_model_for_task("code")
```

---

## ModelManager

High-level model operations.

### Methods

**sync_models()** - Sync Ollama models to database
```python
manager = ModelManager()
result = await manager.sync_models()
# Returns: {registered: 2, updated: 5, total: 7}
```

**get_available_models()** - Get available models
```python
models = await manager.get_available_models(
    installed_only=True,
    with_capabilities=True
)
```

**get_model_info(name)** - Get detailed model info
```python
info = await manager.get_model_info("qwen2.5:32b")
```

**ensure_model(name, auto_pull)** - Ensure model available
```python
# Pull if not installed
model = await manager.ensure_model("llama3.1:70b", auto_pull=True)
```

**select_model_for_task(task_type)** - Select best model
```python
model_name = await manager.select_model_for_task("math")
```

**generate(model_name, prompt)** - Generate with tracking
```python
response = await manager.generate(
    "qwen2.5:32b",
    "Explain machine learning"
)
```

---

## Database Schema

Models are stored in `orch_models` table:

```sql
CREATE TABLE orch_models (
    model_id TEXT PRIMARY KEY,           -- Normalized ID
    name TEXT NOT NULL,                  -- Original name
    provider TEXT DEFAULT 'ollama',
    size_params TEXT,                    -- e.g., "70B"
    context_window INTEGER,
    installed BOOLEAN,
    installed_at TIMESTAMP,
    last_used TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP
);
```

Capabilities in `orch_model_capabilities`:

```sql
CREATE TABLE orch_model_capabilities (
    capability_id TEXT PRIMARY KEY,
    model_id TEXT REFERENCES orch_models,
    task_type TEXT,                      -- math, code, etc.
    quality_score REAL,                  -- 0.0-1.0
    speed_tier TEXT,                     -- fast, medium, slow
    notes TEXT
);
```

---

## Configuration

Ollama settings in `.env`:

```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_TIMEOUT=120
OLLAMA_MAX_RETRIES=3
DEFAULT_MODEL=qwen2.5:32b
```

---

## Examples

### Sync and List Models

```python
import asyncio
from models import ModelManager

async def main():
    manager = ModelManager()
    
    # Sync from Ollama
    result = await manager.sync_models()
    print(f"Synced {result['total']} models")
    
    # List installed
    models = await manager.get_available_models()
    for model in models:
        print(f"{model['name']}: {model.get('size_params', 'unknown')}")

asyncio.run(main())
```

### Generate with Best Model

```python
async def generate_math_answer(question: str) -> str:
    manager = ModelManager()
    
    # Find best model for math
    model = await manager.select_model_for_task("math")
    
    if not model:
        model = "qwen2.5:32b"  # Fallback
    
    # Generate answer
    return await manager.generate(model, question)
```

### Check Model Health

```python
async def check_ollama():
    async with OllamaClient() as client:
        healthy = await client.health_check()
        
        if healthy:
            models = await client.list_models()
            print(f"✓ Ollama healthy: {len(models)} models")
        else:
            print("✗ Ollama not responding")
```

---

## Troubleshooting

### Ollama Not Running

```bash
# Check status
systemctl status ollama

# Start if stopped
sudo systemctl start ollama

# Enable auto-start
sudo systemctl enable ollama
```

### Models Not Syncing

```bash
# Manually sync
cd /opt/mythos/orchestrator/scripts
./register_models.sh

# Check Ollama directly
ollama list

# Check database
psql -d mythos -c "SELECT name, installed FROM orch_models;"
```

### Connection Errors

Check configuration:
```bash
cat /opt/mythos/orchestrator/.env | grep OLLAMA
```

Test connection:
```bash
curl http://localhost:11434/api/tags
```

---

**Version:** 1.15.2  
**Phase:** 1.2 Complete  
**Next:** Phase 1.3 - Test Framework
