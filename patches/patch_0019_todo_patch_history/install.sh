#!/bin/bash
# Patch 0019: Add Patch History to TODO.md
# Adds a Patch History section so Claude always knows the next patch number

set -e

echo "Installing patch 0019: TODO Patch History"

cp opt/mythos/docs/TODO.md /opt/mythos/docs/TODO.md
echo "✓ Updated TODO.md with patch history section"

echo "✓ Patch 0019 complete"
