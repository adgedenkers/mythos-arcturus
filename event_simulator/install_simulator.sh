#!/bin/bash
# Install Mythos Event Simulator

set -e

echo "Installing Mythos Event Simulator..."
echo ""

# Create tools directory
sudo mkdir -p /opt/mythos/tools
sudo chown -R $USER:$USER /opt/mythos/tools

# Copy Python script
cp mythos_event_simulator.py /opt/mythos/tools/event_simulator.py
chmod +x /opt/mythos/tools/event_simulator.py

# Install wrapper script
sudo cp mythos-test /usr/local/bin/mythos-test
sudo chmod +x /usr/local/bin/mythos-test

echo "✓ Installation complete!"
echo ""
echo "Usage:"
echo "  mythos-test --run              # Run all tests"
echo "  mythos-test --history          # Show test history"
echo "  mythos-test --failures         # Show common failures"
echo "  mythos-test --duration 60      # Run tests with custom duration"
echo ""
echo "Test results will be stored in Neo4j per-machine."
echo ""
