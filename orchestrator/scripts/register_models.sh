#!/bin/bash
# Register installed Ollama models in the database

MYTHOS_ROOT="/opt/mythos"

# Activate venv
source "${MYTHOS_ROOT}/.venv/bin/activate"

# Run Python script to sync models
cd "${MYTHOS_ROOT}/orchestrator"

python3 << 'EOPY'
import sys
import os

# Critical: Set the path BEFORE any imports
orchestrator_src = '/opt/mythos/orchestrator/src'
if orchestrator_src not in sys.path:
    sys.path.insert(0, orchestrator_src)

# Now we can import
import asyncio
from models.model_manager import ModelManager

async def main():
    manager = ModelManager()
    
    print("Syncing installed Ollama models...")
    result = await manager.sync_models()
    
    print(f"✓ Registered: {result['registered']} new models")
    print(f"✓ Updated: {result['updated']} existing models")
    print(f"✓ Total: {result['total']} models synced")
    
    # List models
    models = await manager.get_available_models()
    print(f"\nInstalled models:")
    for model in models:
        print(f"  • {model['name']} ({model.get('size_params', 'unknown size')})")

asyncio.run(main())
EOPY
