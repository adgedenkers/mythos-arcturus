#!/bin/bash
# Install script for patch_0061_iris_instructions
# Configures Iris's identity, operational instructions, and LLM integration

set -e

echo "Installing Iris instruction configuration..."

# Create prompts directory in iris core
mkdir -p /opt/mythos/iris/core/prompts

# Copy prompt files
cp opt/mythos/iris/core/prompts/IDENTITY.md /opt/mythos/iris/core/prompts/
cp opt/mythos/iris/core/prompts/OPERATIONAL.md /opt/mythos/iris/core/prompts/
cp opt/mythos/iris/core/prompts/MODEL_CONFIG.md /opt/mythos/iris/core/prompts/

echo "✓ Prompt files installed"

# Copy updated source files
cp opt/mythos/iris/core/src/prompts.py /opt/mythos/iris/core/src/
cp opt/mythos/iris/core/src/llm.py /opt/mythos/iris/core/src/

echo "✓ Source files updated"

# Set permissions
chmod 644 /opt/mythos/iris/core/prompts/*.md
chmod 644 /opt/mythos/iris/core/src/prompts.py
chmod 644 /opt/mythos/iris/core/src/llm.py

echo "✓ Permissions set"

# Note about rebuilding container
echo ""
echo "=========================================="
echo "IRIS INSTRUCTIONS INSTALLED"
echo "=========================================="
echo ""
echo "Prompt files:"
echo "  - /opt/mythos/iris/core/prompts/IDENTITY.md"
echo "  - /opt/mythos/iris/core/prompts/OPERATIONAL.md"  
echo "  - /opt/mythos/iris/core/prompts/MODEL_CONFIG.md"
echo ""
echo "Source files:"
echo "  - /opt/mythos/iris/core/src/prompts.py"
echo "  - /opt/mythos/iris/core/src/llm.py"
echo ""
echo "To activate, rebuild and restart iris-core:"
echo "  cd /opt/mythos/docker"
echo "  docker compose -f docker-compose.iris.yml build iris-core"
echo "  docker compose -f docker-compose.iris.yml up -d iris-core"
echo ""
echo "Test with:"
echo "  curl http://localhost:8100/status"
echo ""
