---
name: build_feature_telegram_tool
version: "1.0"
category: builder
risk_tier: T2-patch
description: >
  Build a discrete Telegram bot command or inline tool. Tools are one-shot
  operations (unlike modes which persist across messages). Examples: /weather,
  /finance_summary, /patch_status, /soul_lookup. Use when Ka'tuar'el wants a
  new bot command, says "add a command", "telegram tool for", or when Iris needs
  a new command for user interaction.
requires:
  services: [mythos-bot]
  tools: [python3, bash]
  files:
    - /opt/mythos/docs/ARCHITECTURE.md
    - /opt/mythos/telegram_bot/
  env_vars: [TELEGRAM_BOT_TOKEN]
inputs:
  required:
    - command name (e.g., /toolname)
    - what it does (one sentence)
  optional:
    - arguments/parameters the command accepts
    - services it needs to query
    - response format (text, image, file, inline keyboard)
outputs:
  files:
    - patch via build_patch skill
  formats: [.zip]
  destinations:
    - deployed via patch system
---

# Build Feature: Telegram Tool

## Purpose

Telegram tools are one-shot commands that execute immediately and return a
result. They don't maintain state between invocations. Think of them as the
bot's utility belt — quick access to specific Mythos functions via chat.

## Pre-Flight Checks

1. **Get current commands:**
   ```bash
   D=~/diag.txt; > "$D"
   echo "=== REGISTERED COMMANDS ===" >> "$D"
   grep -rn "CommandHandler\|command=" /opt/mythos/telegram_bot/ >> "$D" 2>&1
   echo -e "\n\n=== HANDLER FILES ===" >> "$D"
   ls /opt/mythos/telegram_bot/handlers/ 2>/dev/null >> "$D" 2>&1
   cat "$D" | xclip -selection clipboard && echo "✓ Copied to clipboard"
   ```

2. **Check for name conflicts** with existing commands.

## Process

### Step 1: Design the Command

Define:
- **Command:** `/toolname`
- **Arguments:** What parameters does it accept? (e.g., `/soul_lookup Seraphe`)
- **Data sources:** What does it query? (PostgreSQL, Neo4j, API, filesystem)
- **Response format:** Plain text, formatted markdown, photo, document, inline keyboard
- **Error response:** What to say when it fails or gets bad input

### Step 2: Implement

Write the handler function:
```python
async def toolname_handler(update, context):
    """Handle /toolname command."""
    # Parse arguments
    args = context.args

    # Do the thing
    result = await do_the_thing(args)

    # Respond
    await update.message.reply_text(result, parse_mode="Markdown")
```

Patterns:
- Always parse and validate arguments before processing
- Always send a response (even if it's an error message)
- Use parse_mode="Markdown" for formatted output
- For long operations, send a "working..." message first
- Catch exceptions and send user-friendly error messages

### Step 3: Register

Add the CommandHandler to the bot's dispatcher/application builder.
Add to /help text.

### Step 4: Deploy via build_patch

Standard patch deployment. Include handler file and updated registration.

### Step 5: Test

- Send the command in Telegram
- Test with valid args, invalid args, no args
- Verify response format renders correctly
- Check bot logs for errors

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Command not recognized | Not registered | Check add_handler call, restart bot |
| "Bad Request: can't parse" | Markdown formatting error | Escape special chars or use HTML parse_mode |
| Timeout | Query or API call too slow | Add timeout, send "working..." first |
| Permission error | Wrong user or chat | Add user/chat ID check if needed |

---

_Last updated: 2026-02-22_
_Author: Ka'tuar'el_
