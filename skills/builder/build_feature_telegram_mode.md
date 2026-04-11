---
name: build_feature_telegram_mode
version: "1.0"
category: builder
risk_tier: T2-patch
description: >
  Create a new Telegram bot operating mode within the Mythos bot. Operating
  modes are persistent conversation states (like /life-log, /finance) that
  change how the bot processes messages while active. Use when Ka'tuar'el wants
  a new mode, says "add a mode to the bot", "operating mode for", or describes
  a persistent bot behavior pattern. Distinct from telegram tools (one-shot
  commands) — modes maintain state across messages.
requires:
  services: [mythos-bot, postgresql]
  tools: [python3, bash]
  files:
    - /opt/mythos/docs/ARCHITECTURE.md
    - /opt/mythos/telegram_bot/
  env_vars: [TELEGRAM_BOT_TOKEN]
inputs:
  required:
    - mode name and activation command (e.g., /modename)
    - what the mode does while active
    - how to exit the mode
  optional:
    - state schema (what data persists between messages)
    - special message handling rules
    - integration points with other Mythos services
outputs:
  files:
    - patch via build_patch skill
  formats: [.zip]
  destinations:
    - deployed via patch system
---

# Build Feature: Telegram Operating Mode

## Purpose

Operating modes transform the Telegram bot into a context-specific tool. When
a mode is active, every message is processed through that mode's handler before
(or instead of) the default handler. Modes maintain state across messages,
enabling multi-turn workflows like logging, data entry, or guided processes.

## Pre-Flight Checks

1. **Get current bot structure:**
   ```bash
   D=~/diag.txt; > "$D"
   echo "=== BOT STRUCTURE ===" >> "$D"
   find /opt/mythos/telegram_bot -name "*.py" | sort >> "$D" 2>&1
   echo -e "\n\n=== EXISTING MODES ===" >> "$D"
   grep -rn "mode\|Mode\|handler" /opt/mythos/telegram_bot/modes/ 2>/dev/null >> "$D" 2>&1
   echo -e "\n\n=== COMMANDS REGISTERED ===" >> "$D"
   grep -rn "add_handler\|CommandHandler\|command=" /opt/mythos/telegram_bot/ >> "$D" 2>&1
   cat "$D" | xclip -selection clipboard && echo "✓ Copied to clipboard"
   ```

2. **Check for command conflicts** — ensure /modename isn't already registered.

3. **Understand the mode manager** — how does the bot track which mode is active?
   Check for a mode manager, state store, or context variables.

## Process

### Step 1: Design the Mode

Define:
- **Activation command:** `/modename` — what starts it
- **Exit command:** `/exit` or `/done` or mode-specific
- **State schema:** What data persists between messages while mode is active
- **Message handler:** How each message is processed in this mode
- **Special commands:** Any mode-specific sub-commands
- **Integration points:** What services/databases does it talk to?

Present design to Ka'tuar'el.

### Step 2: Implement the Mode Handler

Create a mode file following the existing bot patterns:
- Mode class or handler function
- State initialization on activation
- Message processing logic
- State cleanup on deactivation
- Error handling for invalid inputs

Key patterns:
- Store mode state in user context or database, not in-memory globals
- Always provide a way to exit the mode
- Send confirmation when mode activates and deactivates
- Handle unexpected inputs gracefully (don't crash the bot)

### Step 3: Register the Mode

Update the bot's command registration:
- Add CommandHandler for the activation command
- Register the mode's message handler with appropriate priority
- Ensure mode handler takes precedence over default when active
- Add to the bot's /help text

### Step 4: Add Database Support (if needed)

If the mode needs persistent storage beyond session state:
- Design the table schema
- Write SQL migration
- Add to patch install.sh

### Step 5: Deploy via build_patch

Package as a numbered patch. Include:
- Mode handler file(s)
- Updated command registration
- Database migration (if any)
- Service restart for mythos-bot

### Step 6: Test

After deployment:
- Activate the mode via Telegram
- Send test messages, verify handling
- Test edge cases (empty messages, commands while in mode)
- Exit and verify bot returns to normal
- Check bot logs: `journalctl -u mythos-bot -n 30`

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Mode doesn't activate | Command not registered | Check handler registration, restart bot |
| Messages not captured by mode | Handler priority too low | Check handler group/priority ordering |
| State lost between messages | In-memory storage cleared | Move to database or persistent context |
| Bot crashes when entering mode | Import error or bad initialization | Check journalctl, fix imports |
| Can't exit mode | Exit handler not working | Ensure exit command is registered separately |

---

_Last updated: 2026-02-22_
_Author: Ka'tuar'el_
