#!/bin/bash
# patch_0023_chat_assistant install script
# Implements chat mode in the API gateway via ChatAssistant class

set -e

echo "📦 Installing patch_0023: Chat Assistant for API Gateway"

# Copy files
cp -v opt/mythos/assistants/chat_assistant.py /opt/mythos/assistants/chat_assistant.py
cp -v opt/mythos/api/main.py /opt/mythos/api/main.py

# Set permissions
chmod 644 /opt/mythos/assistants/chat_assistant.py
chmod 644 /opt/mythos/api/main.py

# Restart the API service
echo "🔄 Restarting mythos-api service..."
sudo systemctl restart mythos-api.service

# Wait and check status
sleep 2
if systemctl is-active --quiet mythos-api.service; then
    echo "✅ mythos-api.service is running"
else
    echo "❌ mythos-api.service failed to start"
    journalctl -u mythos-api.service -n 20 --no-pager
    exit 1
fi

# Also restart bot to pick up any changes
echo "🔄 Restarting mythos-bot service..."
sudo systemctl restart mythos-bot.service

sleep 2
if systemctl is-active --quiet mythos-bot.service; then
    echo "✅ mythos-bot.service is running"
else
    echo "❌ mythos-bot.service failed to start"
    journalctl -u mythos-bot.service -n 20 --no-pager
    exit 1
fi

# Test API endpoint
echo ""
echo "🔍 Testing API..."
API_STATUS=$(curl -s http://localhost:8000/ 2>/dev/null || echo "FAILED")
if echo "$API_STATUS" | grep -q "chat_assistant"; then
    echo "✅ API responding with chat_assistant status"
else
    echo "⚠️  API test inconclusive: $API_STATUS"
fi

echo ""
echo "✅ patch_0023 installed successfully!"
echo ""
echo "Changes:"
echo "  - ChatAssistant class added to /opt/mythos/assistants/"
echo "  - API /message endpoint now routes 'chat' mode to ChatAssistant"
echo "  - Chat maintains conversation context per user"
echo "  - New endpoints: /chat/clear/{user_id}, /chat/stats/{user_id}"
echo "  - Default mode changed from 'db' to 'chat'"
echo ""
echo "Test with: /mode chat in Telegram, then send a message"
