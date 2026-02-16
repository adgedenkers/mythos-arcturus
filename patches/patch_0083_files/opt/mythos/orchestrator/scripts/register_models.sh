#!/bin/bash
# Register installed Ollama models in the database

MYTHOS_ROOT="/opt/mythos"

# Activate venv
source "${MYTHOS_ROOT}/.venv/bin/activate"

# Run Python script to sync models
python3 << 'EOPY'
import sys
sys.path.insert(0, '/opt/mythos/orchestrator/src')

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
