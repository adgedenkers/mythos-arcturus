#!/bin/bash
# Install script for patch_0062_dockerfile_prompts
# Fixes Dockerfile to include prompts directory

set -e

echo "Updating Iris Dockerfile to include prompts..."

cp opt/mythos/iris/core/Dockerfile /opt/mythos/iris/core/Dockerfile

echo "✓ Dockerfile updated"
echo ""
echo "Now rebuild the container:"
echo "  cd /opt/mythos/docker"
echo "  docker compose -f docker-compose.iris.yml build iris-core"
echo "  docker compose -f docker-compose.iris.yml up -d iris-core"
echo ""
