#!/bin/bash
# Install script for patch_0063_model_config
# Updates model configuration to use dolphin-llama3:8b as default

set -e

echo "Updating Iris model configuration..."

# Copy updated files
cp opt/mythos/iris/core/prompts/MODEL_CONFIG.md /opt/mythos/iris/core/prompts/
cp opt/mythos/iris/core/src/prompts.py /opt/mythos/iris/core/src/

echo "✓ Model config and prompts.py updated"

# Update .env if not already set to dolphin
if grep -q "^OLLAMA_MODEL=dolphin-llama3:8b" /opt/mythos/.env; then
    echo "✓ .env already set to dolphin-llama3:8b"
else
    sed -i 's/^OLLAMA_MODEL=.*/OLLAMA_MODEL=dolphin-llama3:8b/' /opt/mythos/.env
    echo "✓ .env updated to use dolphin-llama3:8b"
fi

echo ""
echo "=========================================="
echo "MODEL CONFIGURATION UPDATED"
echo "=========================================="
echo ""
echo "Default model: dolphin-llama3:8b"
echo "  - Conversation, spiritual work, relational"
echo "  - Uncensored, follows identity well"
echo "  - Fast (~250-350ms)"
echo ""
echo "Other models used for:"
echo "  - qwen2.5:32b: Complex reasoning, database queries"
echo "  - deepseek-coder-v2:16b: Code generation"
echo "  - llava:34b: Photo analysis"
echo "  - llama3.2:3b: Classification, quick queries"
echo ""
echo "Rebuild container to apply:"
echo "  cd /opt/mythos/docker"
echo "  docker compose -f docker-compose.iris.yml build iris-core"
echo "  docker compose -f docker-compose.iris.yml up -d iris-core"
echo ""
