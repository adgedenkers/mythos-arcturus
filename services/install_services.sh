#!/bin/bash
# Install Mythos worker systemd services

echo "Installing Mythos worker services..."

for service in /opt/mythos/services/mythos-worker-*.service; do
    name=$(basename "$service")
    echo "  Installing $name..."
    sudo cp "$service" /etc/systemd/system/
done

sudo systemctl daemon-reload

echo ""
echo "Services installed. To enable and start:"
echo "  sudo systemctl enable mythos-worker-grid"
echo "  sudo systemctl start mythos-worker-grid"
echo ""
echo "Or enable all workers:"
echo "  for w in grid embedding vision temporal entity summary; do"
echo "    sudo systemctl enable mythos-worker-\$w"
echo "    sudo systemctl start mythos-worker-\$w"
echo "  done"
