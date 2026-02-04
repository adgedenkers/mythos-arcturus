#!/usr/bin/env python3
"""
Comprehensive help system for Mythos Telegram Bot
Provides detailed examples and guidance for each subsystem
"""

from telegram import Update
from telegram.ext import ContextTypes


# Main help - overview with topic hints
HELP_MAIN = """🔮 **Mythos System Help**

For detailed help on any topic, use:
`/help <topic>`

━━━━━━━━━━━━━━━━━━━━━━━━
**📋 TASKS** → `/help tasks`
Track your to-dos with due dates

**💰 FINANCE** → `/help finance`
Track spending, balances, bills

**📦 SELL** → `/help sell`
List items for sale with photos

**💬 CHAT** → `/help chat`
Talk with local AI

**🗄️ DATABASE** → `/help db`
Query Neo4j and Postgres

**⚙️ SYSTEM** → `/help system`
Patches, status, modes
━━━━━━━━━━━━━━━━━━━━━━━━

**Quick Start:**
Just type to chat! Or try:
`/tasks` - See your task list
`/balance` - Check finances
`/status` - What's happening
"""


HELP_TASKS = """📋 **Task Tracking**

Manage your to-do list with priorities and due dates.

━━━━━━━━━━━━━━━━━━━━━━━━
**ADDING TASKS**
━━━━━━━━━━━━━━━━━━━━━━━━

**Basic:**
`/task add Buy groceries`
`/task add Call the dentist`

**With priority:**
`/task add -h Fix the server` → 🔴 High
`/task add -m Review document` → 🟡 Medium (default)
`/task add -l Organize photos` → 🟢 Low

**With due date:**
`/task add -d today Urgent thing`
`/task add -d tomorrow Call mom`
`/task add -d friday Weekly review`
`/task add -d 10th Pay rent`
`/task add -d 2/14 Valentine's day`

**Combined:**
`/task add -h -d tomorrow Submit report`
`/task add -d friday -l Clean garage`

━━━━━━━━━━━━━━━━━━━━━━━━
**DUE DATE FORMATS**
━━━━━━━━━━━━━━━━━━━━━━━━

`today`, `tomorrow`, `tonight`
`monday`, `tue`, `wed`, `thursday`, `fri`
`10th`, `15th`, `1st`, `23rd`
`2/14`, `2/14/26`, `02/14/2026`

━━━━━━━━━━━━━━━━━━━━━━━━
**VIEWING TASKS**
━━━━━━━━━━━━━━━━━━━━━━━━

`/tasks` - List all open tasks
`/task list` - Same as above
`/task due` - Show only tasks with due dates
`/task all` - Include completed/dropped

━━━━━━━━━━━━━━━━━━━━━━━━
**COMPLETING TASKS**
━━━━━━━━━━━━━━━━━━━━━━━━

First run `/tasks` to see the list:
```
1 🔴 Fix server 📍 today
2 🟡 Buy groceries 📅 Fri
3 🟢 Organize desk
```

Then:
`/task done 1` → ✅ Completes task #1
`/task drop 2` → 🗑️ Removes task #2

━━━━━━━━━━━━━━━━━━━━━━━━
**TIPS**
━━━━━━━━━━━━━━━━━━━━━━━━

• Overdue tasks show ⚠️ and sort first
• Tasks sort: overdue → due soon → priority
• Use `/task due` for deadline focus
• Quick add: `/task add thing` (no subcommand needed)
"""


HELP_FINANCE = """💰 **Finance System**

Track balances, spending, and bills.

━━━━━━━━━━━━━━━━━━━━━━━━
**QUICK COMMANDS**
━━━━━━━━━━━━━━━━━━━━━━━━

`/balance` - Current account balances
`/finance` - Summary with recent activity
`/spending` - Recent spending breakdown
`/snapshot` - Full financial picture

━━━━━━━━━━━━━━━━━━━━━━━━
**EXAMPLES**
━━━━━━━━━━━━━━━━━━━━━━━━

**Check your balances:**
`/balance`
→ Shows each account's current balance

**See recent spending:**
`/spending`
→ Breakdown by category (groceries, gas, etc.)

**Full picture:**
`/snapshot`
→ All accounts, recent transactions, upcoming bills

━━━━━━━━━━━━━━━━━━━━━━━━
**MANUAL UPDATES**
━━━━━━━━━━━━━━━━━━━━━━━━

**Set a balance manually:**
`/setbal`
→ Interactive balance update

**Update specific account:**
`/setbalance <account> <amount>`
→ Direct balance set

━━━━━━━━━━━━━━━━━━━━━━━━
**AUTO-IMPORT**
━━━━━━━━━━━━━━━━━━━━━━━━

Bank CSVs are auto-imported when dropped in:
`/opt/mythos/finance/imports/`

The patch monitor detects new files and imports them automatically.

━━━━━━━━━━━━━━━━━━━━━━━━
**TIPS**
━━━━━━━━━━━━━━━━━━━━━━━━

• Transactions are auto-categorized
• `/snapshot` is the most comprehensive view
• Check `/balance` daily for awareness
"""


HELP_SELL = """📦 **Sell Mode**

List items for sale using photo analysis.

━━━━━━━━━━━━━━━━━━━━━━━━
**WORKFLOW**
━━━━━━━━━━━━━━━━━━━━━━━━

**1. Enter sell mode:**
`/mode sell`

**2. Send 3 photos of your item**
(different angles work best)

**3. AI analyzes and creates listing**
Title, description, suggested price

**4. Repeat for more items, then:**
`/done` - Exit sell mode

━━━━━━━━━━━━━━━━━━━━━━━━
**COMMANDS**
━━━━━━━━━━━━━━━━━━━━━━━━

**While in sell mode:**
`/done` - Exit sell mode
`/undo` - Remove last added item
`/status` - See current session

**Inventory management:**
`/inventory` - View all items
`/export` - Generate FB Marketplace listings

**After listing/selling:**
`/listed <id>` - Mark item as listed
`/sold <id>` - Mark item as sold

━━━━━━━━━━━━━━━━━━━━━━━━
**EXAMPLE SESSION**
━━━━━━━━━━━━━━━━━━━━━━━━

```
You: /mode sell
Bot: 📦 Sell mode activated!

[Send photo 1]
Bot: 📸 Photo 1/3 received

[Send photo 2]
Bot: 📸 Photo 2/3 received

[Send photo 3]
Bot: 📸 Analyzing...
Bot: ✅ Added: "Vintage Desk Lamp"
     Suggested price: $45

You: /done
Bot: 📦 Sell mode ended. 1 item added.
```

━━━━━━━━━━━━━━━━━━━━━━━━
**TIPS**
━━━━━━━━━━━━━━━━━━━━━━━━

• Good lighting = better analysis
• Show any defects for honest listings
• Use `/export` to get copy-paste FB posts
"""


HELP_CHAT = """💬 **Chat Mode**

Talk with the local AI (Ollama).

━━━━━━━━━━━━━━━━━━━━━━━━
**BASICS**
━━━━━━━━━━━━━━━━━━━━━━━━

Just type! No command needed.
Context is maintained throughout the conversation.

**Examples:**
"What's the capital of France?"
"Help me write an email to my boss"
"Explain quantum computing simply"

━━━━━━━━━━━━━━━━━━━━━━━━
**COMMANDS**
━━━━━━━━━━━━━━━━━━━━━━━━

`/clear` - Reset conversation context
`/status` - See recent topics discussed
`/model fast` - Use faster, lighter model
`/model deep` - Use best quality model

━━━━━━━━━━━━━━━━━━━━━━━━
**MODES**
━━━━━━━━━━━━━━━━━━━━━━━━

`/mode chat` - General conversation (default)
`/mode seraphe` - Cosmology & spiritual topics
`/mode genealogy` - Bloodline research

━━━━━━━━━━━━━━━━━━━━━━━━
**TRACKED CONVERSATIONS**
━━━━━━━━━━━━━━━━━━━━━━━━

For important conversations you want saved:

`/convo` - Start tracked conversation
(conversation is logged to database)
`/endconvo` - End tracking

━━━━━━━━━━━━━━━━━━━━━━━━
**TIPS**
━━━━━━━━━━━━━━━━━━━━━━━━

• Context persists until `/clear`
• Use `/status` to see what you've discussed
• `/model deep` for complex reasoning
• `/model fast` for quick answers
"""


HELP_DB = """🗄️ **Database Mode**

Query Neo4j and PostgreSQL directly.

━━━━━━━━━━━━━━━━━━━━━━━━
**ENTERING DB MODE**
━━━━━━━━━━━━━━━━━━━━━━━━

`/mode db`

Then just type natural language queries:

━━━━━━━━━━━━━━━━━━━━━━━━
**EXAMPLE QUERIES**
━━━━━━━━━━━━━━━━━━━━━━━━

**Neo4j (Graph):**
"Show me all Soul nodes"
"What relationships does Ka'tuar'el have?"
"Find all Incarnation nodes"

**PostgreSQL:**
"How many transactions this month?"
"Show recent chat messages"
"List all accounts"

━━━━━━━━━━━━━━━━━━━━━━━━
**AVAILABLE DATA**
━━━━━━━━━━━━━━━━━━━━━━━━

**Neo4j:**
• Soul, Person, Incarnation
• Exchange, Conversation
• GridNode, Entity, Theme

**PostgreSQL:**
• users, chat_messages
• accounts, transactions
• items_for_sale, sales
• idea_backlog (tasks)
• grid_activation_timeseries

━━━━━━━━━━━━━━━━━━━━━━━━
**TIPS**
━━━━━━━━━━━━━━━━━━━━━━━━

• Natural language is converted to queries
• Be specific about what you want
• Use `/mode chat` to return to chat
"""


HELP_SYSTEM = """⚙️ **System Commands**

Patches, status, and administration.

━━━━━━━━━━━━━━━━━━━━━━━━
**STATUS**
━━━━━━━━━━━━━━━━━━━━━━━━

`/status` - Current mode, model, recent activity
`/patch_status` - System version and recent patches

━━━━━━━━━━━━━━━━━━━━━━━━
**MODES**
━━━━━━━━━━━━━━━━━━━━━━━━

`/mode chat` - General AI chat (default)
`/mode db` - Database queries
`/mode sell` - Item selling
`/mode seraphe` - Cosmology assistant
`/mode genealogy` - Bloodline research

━━━━━━━━━━━━━━━━━━━━━━━━
**PATCH MANAGEMENT**
━━━━━━━━━━━━━━━━━━━━━━━━

`/patch_status` - Current version
`/patch_list` - Recent patches
`/patch_apply <n>` - Apply a patch
`/patch_rollback` - Rollback last patch

**Auto-deploy:**
Drop patches in `~/Downloads` on Arcturus.
The patch monitor auto-detects and installs.

━━━━━━━━━━━━━━━━━━━━━━━━
**SERVICES**
━━━━━━━━━━━━━━━━━━━━━━━━

Running on Arcturus:
• `mythos-api` - FastAPI gateway (:8000)
• `mythos-bot` - This Telegram bot
• `mythos-worker-grid` - Grid analysis
• `mythos-patch-monitor` - Auto-deploy

━━━━━━━━━━━━━━━━━━━━━━━━
**DIAGNOSTICS**
━━━━━━━━━━━━━━━━━━━━━━━━

On Arcturus, use:
```
sudo systemctl status mythos-bot
journalctl -u mythos-bot -f
```

━━━━━━━━━━━━━━━━━━━━━━━━
**HELP**
━━━━━━━━━━━━━━━━━━━━━━━━

`/help` - This overview
`/help tasks` - Task tracking
`/help finance` - Finance system
`/help sell` - Selling items
`/help chat` - Chat mode
`/help db` - Database queries
"""


# Topic aliases for flexible matching
HELP_TOPICS = {
    # Tasks
    'task': HELP_TASKS,
    'tasks': HELP_TASKS,
    'todo': HELP_TASKS,
    'todos': HELP_TASKS,
    
    # Finance
    'finance': HELP_FINANCE,
    'money': HELP_FINANCE,
    'balance': HELP_FINANCE,
    'spending': HELP_FINANCE,
    'bills': HELP_FINANCE,
    
    # Sell
    'sell': HELP_SELL,
    'selling': HELP_SELL,
    'inventory': HELP_SELL,
    'items': HELP_SELL,
    
    # Chat
    'chat': HELP_CHAT,
    'talk': HELP_CHAT,
    'conversation': HELP_CHAT,
    'ai': HELP_CHAT,
    
    # Database
    'db': HELP_DB,
    'database': HELP_DB,
    'query': HELP_DB,
    'neo4j': HELP_DB,
    'postgres': HELP_DB,
    
    # System
    'system': HELP_SYSTEM,
    'sys': HELP_SYSTEM,
    'patch': HELP_SYSTEM,
    'patches': HELP_SYSTEM,
    'admin': HELP_SYSTEM,
    'status': HELP_SYSTEM,
    'mode': HELP_SYSTEM,
    'modes': HELP_SYSTEM,
}


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /help command with optional topic
    
    Usage:
        /help - Main overview
        /help tasks - Task tracking help
        /help finance - Finance help
        /help sell - Selling help
        /help chat - Chat mode help
        /help db - Database help
        /help system - System/admin help
    """
    args = context.args if context.args else []
    
    if not args:
        # No topic - show main help
        await update.message.reply_text(HELP_MAIN, parse_mode='Markdown')
        return
    
    topic = args[0].lower()
    
    if topic in HELP_TOPICS:
        await update.message.reply_text(HELP_TOPICS[topic], parse_mode='Markdown')
    else:
        # Unknown topic - show main help with hint
        await update.message.reply_text(
            f"❓ Unknown topic: `{topic}`\n\n"
            "Available topics:\n"
            "`tasks`, `finance`, `sell`, `chat`, `db`, `system`\n\n"
            "Use `/help` for overview.",
            parse_mode='Markdown'
        )
