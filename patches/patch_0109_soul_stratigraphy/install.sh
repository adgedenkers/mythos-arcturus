#!/bin/bash
set -e

echo "=== Installing Patch 0109: Soul Stratigraphy Method ==="

# Create methods directory if not exists
mkdir -p /opt/mythos/docs/methods/

# Copy method definition
cp opt/mythos/docs/methods/soul_stratigraphy_definition.md /opt/mythos/docs/methods/

# Update TODO.md with new method reference
if ! grep -q "Soul Stratigraphy" /opt/mythos/docs/TODO.md 2>/dev/null; then
    echo "" >> /opt/mythos/docs/TODO.md
    echo "## Soul Stratigraphy Method (Added Patch 0109)" >> /opt/mythos/docs/TODO.md
    echo "- [x] Method defined and documented" >> /opt/mythos/docs/TODO.md
    echo "- [ ] Integrate with astrology database (auto-generate tri-field reports)" >> /opt/mythos/docs/TODO.md
    echo "- [ ] Add Hellenistic calculation support (lots, profections, zodiacal releasing)" >> /opt/mythos/docs/TODO.md
    echo "- [ ] Build Soul Stratigraphy Telegram command" >> /opt/mythos/docs/TODO.md
fi

echo "✓ Soul Stratigraphy method definition installed"
echo "✓ TODO.md updated with Soul Stratigraphy backlog items"
echo "=== Patch 0109 Complete ==="
