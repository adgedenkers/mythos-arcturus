#!/bin/bash
# Test patch - just copies a test file
echo "[TEST] Patch 0011 installing..."
mkdir -p /opt/mythos/test_files
cp "$(dirname "$0")/opt/mythos/test_files/test_config.txt" /opt/mythos/test_files/
echo "[TEST] Done - check /opt/mythos/test_files/test_config.txt"
