#!/usr/bin/env python3
"""
Comprehensive help system for Mythos Telegram Bot
Provides detailed examples and guidance for each subsystem

Patch 0124 — Full help rewrite covering all deployed features
"""
from telegram import Update
from telegram.ext import ContextTypes

# ---------------------------------------------------------------------------
# Main help - overview with topic hints
# ---------------------------------------------------------------------------
HELP_MAIN = """🔮 **Mythos System Help**

For detailed help on any topic:
`/help <topic>`

━━━━━━━━━━━━━━━━━━━━━━━━
**💬 CHAT** → `/help chat`
Talk with local AI (Iris)

**📋 TASKS** → `/help tasks`
Track to-dos with due dates

**💰 FINANCE** → `/help finance`
Balances, spending, bills, forecasts

**📊 BRIEFING** → `/help briefing`
Daily check-ins, routines, analysis

**🔭 ASTROLOGY** → `/help astrology`
Natal charts, aspects, group analysis

**👤 PEOPLE** → `/help people`
Track people for charts & lineage

**✦ GLOSSARY** → `/help define`
Mythos ontology & definitions

**📦 SELL** → `/help sell`
List items for sale with photos

**🔎 INSPECT** → `/help inspect`
Browse files, query DBs from here

**🔍 DIAG** → `/help diag`
System diagnostics & health

**🧠 CONSCIOUSNESS** → `/help consciousness`
Subject tracking, awareness, evolution plan

**⚙️ SYSTEM** → `/help system`
Modes, models, patches, services
**🖥️ MX SHELL** → `/help mx`
Self-healing terminal, intent resolution, integrity hooks

━━━━━━━━━━━━━━━━━━━━━━━━
**Quick Start:**
Just type to chat! Or try:
`/tasks` — your task list
`/balance` — check finances
`/checkin` — daily briefing
`/inspect todo` — view TODO.md
`/status` — what's happening
"""

# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------
HELP_CHAT = """💬 **Chat & Iris Modes**

Just type — no command needed. Context is maintained.

━━━━━━━━━━━━━━━━━━━━━━━━
**IRIS MODES**
━━━━━━━━━━━━━━━━━━━━━━━━
`/mode` — see all available modes
`/mode hearthfire` 🔥 Spiritual/personal
`/mode forge` ⚒️ System admin
`/mode roots` 🌳 Genealogy
`/mode oracle` 🔮 Research/harmonics
`/mode scribe` 📜 Writing
`/mode sentry` 🛡️ Financial

**Legacy modes:**
`/mode db` — Direct database queries
`/mode sell` — Item selling

━━━━━━━━━━━━━━━━━━━━━━━━
**MODEL SELECTION**
━━━━━━━━━━━━━━━━━━━━━━━━
`/model thinking` — qwen3:30b-a3b (default, deep reasoning)
`/model deep` — qwen3:32b
`/model fast` — qwen3:30b-a3b (quick, conversational)
`/model auto` — qwen2.5:32b

**Advanced:**
`/setmodel <exact_name>` — Use any installed model
`/models` — List all installed Ollama models

━━━━━━━━━━━━━━━━━━━━━━━━
**PERSONALITY**
━━━━━━━━━━━━━━━━━━━━━━━━
`/personality` — View current personality sliders
`/personality warmth 80` — Adjust a slider (0-100)
`/personality reset` — Clear overrides

Sliders: verbosity, warmth, humor, truth, speculation, autonomy, mystical, formality, challenge

━━━━━━━━━━━━━━━━━━━━━━━━
**CONTEXT & TRACKING**
━━━━━━━━━━━━━━━━━━━━━━━━
`/clear` — Reset conversation context
`/status` — See recent topics discussed
`/convo` — Start tracked conversation (saved to DB)
`/endconvo` — End tracking

━━━━━━━━━━━━━━━━━━━━━━━━
**MEDIA**
━━━━━━━━━━━━━━━━━━━━━━━━
📸 Send a photo → AI vision analysis
🎤 Send a voice message → Auto-transcribed
🎬 Send a video → Audio extracted & transcribed
`/photos` — View recent photos

━━━━━━━━━━━━━━━━━━━━━━━━
**CONSCIOUSNESS STREAM**
━━━━━━━━━━━━━━━━━━━━━━━━
Every message is processed by the consciousness stream:
• Subject tracking — Iris knows what you're talking about
• Life context — routines, bills, calendar inform responses
• Grid analysis — 9-node parallel processing in background
See `/help consciousness` for details.
━━━━━━━━━━━━━━━━━━━━━━━━
**TIPS**
━━━━━━━━━━━━━━━━━━━━━━━━
• Context persists until `/clear`
• Multi-chunk messages are auto-buffered
• `/model thinking` for complex reasoning
• `/model fast` for quick answers
"""

# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------
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
`/tasks` — List all open tasks
`/task list` — Same as above
`/task due` — Show only tasks with due dates
`/task all` — Include completed/dropped

━━━━━━━━━━━━━━━━━━━━━━━━
**COMPLETING TASKS**
━━━━━━━━━━━━━━━━━━━━━━━━
First run `/tasks` to see the numbered list, then:
`/task done 1` → ✅ Completes task #1
`/task drop 2` → 🗑️ Removes task #2

━━━━━━━━━━━━━━━━━━━━━━━━
**TIPS**
━━━━━━━━━━━━━━━━━━━━━━━━
• Overdue tasks show ⚠️ and sort first
• Tasks sort: overdue → due soon → priority
• Use `/task due` for deadline focus
"""

# ---------------------------------------------------------------------------
# Finance
# ---------------------------------------------------------------------------
HELP_FINANCE = """💰 **Finance System**

Track balances, spending, bills, and forecasts.

━━━━━━━━━━━━━━━━━━━━━━━━
**AT A GLANCE**
━━━━━━━━━━━━━━━━━━━━━━━━
`/balance` — Current account balances
`/finance` — Summary with recent activity
`/spending` — Recent spending breakdown
`/snapshot` — Full financial picture
`/review` — Weekly financial review

━━━━━━━━━━━━━━━━━━━━━━━━
**FORECASTING**
━━━━━━━━━━━━━━━━━━━━━━━━
`/forecast` — Cash flow forecast (30 days)
`/projection` — Balance projections
`/bills` — Upcoming bills
`/income` — Expected income

━━━━━━━━━━━━━━━━━━━━━━━━
**DETAILED VIEWS**
━━━━━━━━━━━━━━━━━━━━━━━━
`/monthly` — Month-over-month comparison
`/compare` — Category comparison
`/top` — Top spending categories
`/txn` — Recent transactions
`/report` — Detailed report

━━━━━━━━━━━━━━━━━━━━━━━━
**NAVIGATION**
━━━━━━━━━━━━━━━━━━━━━━━━
`/next` — Next page of results
`/back` — Previous page

━━━━━━━━━━━━━━━━━━━━━━━━
**MANUAL UPDATES**
━━━━━━━━━━━━━━━━━━━━━━━━
`/setbal` — Interactive balance update
`/setbalance <account> <amount>` — Direct balance set
`/spend <amount> <description>` — Log manual spend

━━━━━━━━━━━━━━━━━━━━━━━━
**HOUSEHOLD VISIBILITY**
━━━━━━━━━━━━━━━━━━━━━━━━
`/pulse` — Household finance summary (shared view)
Auto-sends weekly pulse reports.

━━━━━━━━━━━━━━━━━━━━━━━━
**AUTO-IMPORT**
━━━━━━━━━━━━━━━━━━━━━━━━
Bank CSVs are auto-imported when dropped in the finance imports directory. Transactions are auto-categorized.

━━━━━━━━━━━━━━━━━━━━━━━━
**TIPS**
━━━━━━━━━━━━━━━━━━━━━━━━
• `/snapshot` is the most comprehensive view
• `/forecast` shows what's coming
• `/pulse` gives both partners visibility
• Check `/balance` daily for awareness
"""

# ---------------------------------------------------------------------------
# Briefing / Checkin / Routines
# ---------------------------------------------------------------------------
HELP_BRIEFING = """📊 **Daily Briefing & Routines**

Morning check-ins, routines, and AI-powered analysis.

━━━━━━━━━━━━━━━━━━━━━━━━
**DAILY CHECK-IN**
━━━━━━━━━━━━━━━━━━━━━━━━
`/checkin` — Morning briefing
Shows today's routines, tasks, calendar, weather.

━━━━━━━━━━━━━━━━━━━━━━━━
**ROUTINES**
━━━━━━━━━━━━━━━━━━━━━━━━
`/routines` — Show today's routines & status
`/rdone <N>` — Complete routine #N
`/rskip <N>` — Skip routine #N
`/routine_add` — Add a new routine (interactive)

━━━━━━━━━━━━━━━━━━━━━━━━
**AI ANALYSIS**
━━━━━━━━━━━━━━━━━━━━━━━━
`/briefing` — Run AI analysis now (uses 32b model)
`/analyze` — Same as briefing
`/priorities` — Show current top priorities
`/transfers` — Transfer recommendations

The analyst reviews your tasks, finances, routines, calendar, and recent check-ins to generate prioritized guidance.

━━━━━━━━━━━━━━━━━━━━━━━━
**CALENDAR**
━━━━━━━━━━━━━━━━━━━━━━━━
`/calendar` — This week's events
`/calendar today` — Today only
`/calendar week` — Full week
`/calendar month` — Monthly view
`/calendar add` — Quick add an event

━━━━━━━━━━━━━━━━━━━━━━━━
**WEATHER**
━━━━━━━━━━━━━━━━━━━━━━━━
`/weather` — Oxford, NY (default)
`/weather 13827` — By zip code
`/weather Denver, CO` — By city/state

━━━━━━━━━━━━━━━━━━━━━━━━
**TIPS**
━━━━━━━━━━━━━━━━━━━━━━━━
• `/checkin` is your morning dashboard
• Auto-briefings sent each morning
• `/briefing` runs the full AI analyst on demand
• `/rdone` and `/rskip` track routine completion
"""

# ---------------------------------------------------------------------------
# Astrology
# ---------------------------------------------------------------------------
HELP_ASTROLOGY = """🔭 **Astrology Commands**

Natal charts, planetary positions, aspects, and group analysis.

━━━━━━━━━━━━━━━━━━━━━━━━
**VIEW CHARTS**
━━━━━━━━━━━━━━━━━━━━━━━━
`/chart <name>` — Full natal chart
`/chart <name1> <name2>` — Compare two charts
`/planets <name>` — Planet positions only
`/houses <name>` — House cusps only
`/aspects <name>` — Major aspects only

━━━━━━━━━━━━━━━━━━━━━━━━
**GROUP ANALYSIS**
━━━━━━━━━━━━━━━━━━━━━━━━
`/group_planets <planet> <sign>` — Find everyone with that placement

━━━━━━━━━━━━━━━━━━━━━━━━
**EXAMPLES**
━━━━━━━━━━━━━━━━━━━━━━━━
`/chart Ka`
`/chart Ka Seraphe`
`/planets Seraphe`
`/aspects Fitz`
`/group_planets Jupiter Cancer`

━━━━━━━━━━━━━━━━━━━━━━━━
**CHART NOTATION**
━━━━━━━━━━━━━━━━━━━━━━━━
R = Retrograde
Dom = Domicile (dignity)
Exa = Exaltation
Det = Detriment
Fal = Fall

━━━━━━━━━━━━━━━━━━━━━━━━
**ADDING PEOPLE FOR CHARTS**
━━━━━━━━━━━━━━━━━━━━━━━━
Use `/people add` to add birth data. See `/help people`.
Charts require: name, date of birth, time of birth, birth location.
"""

# ---------------------------------------------------------------------------
# People
# ---------------------------------------------------------------------------
HELP_PEOPLE = """👤 **People Database**

Track people for astrology, genealogy, and lineage work.

━━━━━━━━━━━━━━━━━━━━━━━━
**ADDING PEOPLE**
━━━━━━━━━━━━━━━━━━━━━━━━
Fields are pipe-separated. Leave empty between pipes for unknowns.

`/people add <first> | <middle> | <last> | <known_as> | <DOB> | <time> | <city> | <state> | <country> | <DOD> | <notes>`

**Examples:**
`/people add John | Fitzgerald | Kennedy | JFK | 1917-05-29 | 15:00 | Brookline | Massachusetts | USA | 1963-11-22 | 35th US President`

**Partial data:**
`/people add Marie | | Curie | | 1867-11-07 | | Warsaw | | Poland | | Physicist`

━━━━━━━━━━━━━━━━━━━━━━━━
**SEARCHING & VIEWING**
━━━━━━━━━━━━━━━━━━━━━━━━
`/people list` — All records (summary)
`/people search <query>` — Search by name/known\\_as/notes
`/people view <id or name>` — Full detail
`/people Kennedy` — Bare text also searches

━━━━━━━━━━━━━━━━━━━━━━━━
**EDITING**
━━━━━━━━━━━━━━━━━━━━━━━━
`/people edit <id> <field> <value>`

Fields: first\\_name, middle\\_name, last\\_name, known\\_as, date\\_of\\_birth, time\\_of\\_birth, birth\\_city, birth\\_state, birth\\_country, date\\_of\\_death, notes

━━━━━━━━━━━━━━━━━━━━━━━━
**DELETING**
━━━━━━━━━━━━━━━━━━━━━━━━
`/people delete <id>`

━━━━━━━━━━━━━━━━━━━━━━━━
**TIPS**
━━━━━━━━━━━━━━━━━━━━━━━━
• Date format: YYYY-MM-DD
• Time format: HH:MM (24hr)
• Use known\\_as for spiritual/stage names
• People records feed into `/chart` for astrology
"""

# ---------------------------------------------------------------------------
# Define / Ontology
# ---------------------------------------------------------------------------
HELP_DEFINE = """✦ **Ontology / Glossary**

The living glossary of the Mythos system. Terms stored in Neo4j.

━━━━━━━━━━━━━━━━━━━━━━━━
**LOOKING UP TERMS**
━━━━━━━━━━━━━━━━━━━━━━━━
`/define <term>` — Look up a term
`/define chakra` — Exact or fuzzy match
`/define natal` — Partial matches shown as buttons

━━━━━━━━━━━━━━━━━━━━━━━━
**ADDING TERMS**
━━━━━━━━━━━━━━━━━━━━━━━━
`/define add <name> | <definition> | <category>`

**Example:**
`/define add Thelema | Religious philosophy founded by Crowley | Occult`

━━━━━━━━━━━━━━━━━━━━━━━━
**LISTING TERMS**
━━━━━━━━━━━━━━━━━━━━━━━━
`/define list` — All terms, grouped by category
`/define list Astrology` — Only astrology terms

━━━━━━━━━━━━━━━━━━━━━━━━
**CATEGORIES**
━━━━━━━━━━━━━━━━━━━━━━━━
Astrology, Numerology, Tarot, Mythos Core, History, Lineage, Theology, Occult, Music, Literature, Science, Philosophy
(New categories created automatically)

━━━━━━━━━━━━━━━━━━━━━━━━
**TIPS**
━━━━━━━━━━━━━━━━━━━━━━━━
• Related terms show as clickable buttons
• The glossary is shared across the whole system
"""

# ---------------------------------------------------------------------------
# Sell
# ---------------------------------------------------------------------------
HELP_SELL = """📦 **Sell Mode**

List items for sale using photo analysis.

━━━━━━━━━━━━━━━━━━━━━━━━
**WORKFLOW**
━━━━━━━━━━━━━━━━━━━━━━━━
1. `/mode sell` — Enter sell mode
2. Send 3 photos of your item
3. AI analyzes and creates listing
4. `/done` — Exit sell mode

━━━━━━━━━━━━━━━━━━━━━━━━
**COMMANDS**
━━━━━━━━━━━━━━━━━━━━━━━━
**While in sell mode:**
`/done` — Exit sell mode
`/undo` — Remove last added item
`/status` — See current session

**Inventory management:**
`/inventory` — View all items
`/export` — Generate FB Marketplace listings

**After listing/selling:**
`/listed <id>` — Mark as listed
`/sold <id>` — Mark as sold

━━━━━━━━━━━━━━━━━━━━━━━━
**TIPS**
━━━━━━━━━━━━━━━━━━━━━━━━
• Good lighting = better analysis
• Show any defects for honest listings
• Use `/export` to get copy-paste FB posts
"""

# ---------------------------------------------------------------------------
# Inspect
# ---------------------------------------------------------------------------
HELP_INSPECT = """🔎 **Mythos Inspector**

Browse the filesystem and query databases — all from Telegram.
Paths are relative to Mythos root. No `/opt/mythos/` needed.

━━━━━━━━━━━━━━━━━━━━━━━━
**FILES**
━━━━━━━━━━━━━━━━━━━━━━━━
`/inspect cat <path>` — Read a file
`/inspect head [N] <path>` — First N lines
`/inspect tail [N] <path>` — Last N lines
`/inspect wc <path>` — Line counts
`/inspect ls [path]` — List directory
`/inspect tree [path]` — Directory tree
`/inspect find <pattern> [path]` — Find files
`/inspect grep "text" <path>` — Search contents

━━━━━━━━━━━━━━━━━━━━━━━━
**GIT**
━━━━━━━━━━━━━━━━━━━━━━━━
`/inspect git log` — Recent commits
`/inspect git status` — Working tree
`/inspect git diff` — Diff summary
`/inspect git tags` — Version tags

━━━━━━━━━━━━━━━━━━━━━━━━
**DATABASES**
━━━━━━━━━━━━━━━━━━━━━━━━
`/inspect sql "SELECT ..."` — PostgreSQL (read-only)
`/inspect cypher "MATCH ..."` — Neo4j (read-only)

━━━━━━━━━━━━━━━━━━━━━━━━
**SYSTEM**
━━━━━━━━━━━━━━━━━━━━━━━━
`/inspect service <name>` — Service status (e.g. bot, api)

━━━━━━━━━━━━━━━━━━━━━━━━
**SHORTCUTS**
━━━━━━━━━━━━━━━━━━━━━━━━
`/inspect todo` — TODO.md
`/inspect arch` — ARCHITECTURE.md
`/inspect schema` — All PG tables + rows
`/inspect nodes` — Neo4j label counts
`/inspect services` — All mythos-\\* units
`/inspect patches` — Version & patches
`/inspect env` — .env keys (redacted)
`/inspect handlers` — Handler listing
`/inspect version` — Current version

━━━━━━━━━━━━━━━━━━━━━━━━
**TIPS**
━━━━━━━━━━━━━━━━━━━━━━━━
• `/inspect docs/TODO.md` works too (auto-detects cat vs ls)
• .env and secrets are blocked
• Large output sent as file attachment
• SQL/Cypher write ops blocked — read-only only
"""

# ---------------------------------------------------------------------------
# Diag
# ---------------------------------------------------------------------------
HELP_DIAG = """🔍 **System Diagnostics**

Full system health checks returned as text files.

━━━━━━━━━━━━━━━━━━━━━━━━
**USAGE**
━━━━━━━━━━━━━━━━━━━━━━━━
`/diag` — Full diagnostic (all blocks, as file)
`/diag <blocks>` — Specific blocks only
`/diag help` — List available blocks

━━━━━━━━━━━━━━━━━━━━━━━━
**AVAILABLE BLOCKS**
━━━━━━━━━━━━━━━━━━━━━━━━
`hw` — Disk, RAM, GPU, uptime
`services` — All mythos-\\* systemd units
`workers` — Worker services status
`bot` — Bot service & logs
`api` — FastAPI gateway
`db` — PostgreSQL & Neo4j
`docker` — Containers & Iris
`ollama` — LLM models & VRAM
`redis` — Redis keyspace & memory
`net` — Listening ports
`patches` — Version, tags, patches
`mx` — mx session status, snapshots, patterns, integrity

━━━━━━━━━━━━━━━━━━━━━━━━
**COMBINING**
━━━━━━━━━━━━━━━━━━━━━━━━
`/diag bot db hw` — Run multiple blocks
`/diag all` — Everything

━━━━━━━━━━━━━━━━━━━━━━━━
**TIPS**
━━━━━━━━━━━━━━━━━━━━━━━━
• Single-block results under 4000 chars also shown inline
• Full diag always sent as .txt file
• Great for quick health checks from your phone
• `mythos-diag mx` — mx session status, snapshots, learned patterns
"""

# ---------------------------------------------------------------------------
# System
# ---------------------------------------------------------------------------
HELP_SYSTEM = """⚙️ **System & Administration**

Modes, models, patches, Iris, and services.

━━━━━━━━━━━━━━━━━━━━━━━━
**STATUS**
━━━━━━━━━━━━━━━━━━━━━━━━
`/status` — Current mode, model, recent activity
`/patch_status` — System version

━━━━━━━━━━━━━━━━━━━━━━━━
**MODES** (see `/help chat`)
━━━━━━━━━━━━━━━━━━━━━━━━
`/mode` — View all available modes
`/mode hearthfire` — Spiritual/personal
`/mode forge` — System admin
`/mode roots` — Genealogy
`/mode oracle` — Research/harmonics
`/mode scribe` — Writing
`/mode sentry` — Financial
`/mode db` — Database queries
`/mode sell` — Item selling

━━━━━━━━━━━━━━━━━━━━━━━━
**MODELS**
━━━━━━━━━━━━━━━━━━━━━━━━
`/model thinking` — qwen3:30b-a3b (default)
`/model deep` — qwen3:32b
`/model fast` — qwen3:30b-a3b
`/models` — List all installed models
`/setmodel <name>` — Use specific model
`/pull <name>` — Download new model
`/pulling` — Check download progress
`/removemodel <name>` — Delete a model

━━━━━━━━━━━━━━━━━━━━━━━━
**IRIS CONSCIOUSNESS**
━━━━━━━━━━━━━━━━━━━━━━━━
`/iris` — Iris status & info
`/iris_test` — Run consciousness test
`/iris_run <code>` — Execute code in Iris sandbox
`/iris_task <goal>` — Queue a task for Iris

**Evolution Plan:**
`/inspect cat docs/EVOLUTION_PLAN.md` — Full phased roadmap
See `/help consciousness` for the full consciousness pipeline.

━━━━━━━━━━━━━━━━━━━━━━━━
**PATCH MANAGEMENT**
━━━━━━━━━━━━━━━━━━━━━━━━
`/patch_status` — Current version
`/patch_list` — Recent patches
`/patch_apply <n>` — Apply a patch
`/patch_rollback` — Rollback last patch

Auto-deploy: Drop patches in ~/Downloads on Arcturus.

━━━━━━━━━━━━━━━━━━━━━━━━
**INSPECTION & DIAGNOSTICS**
━━━━━━━━━━━━━━━━━━━━━━━━
`/inspect` — Browse files & DBs (see `/help inspect`)
`/diag` — System health checks (see `/help diag`)

━━━━━━━━━━━━━━━━━━━━━━━━
**KEY SERVICES**
━━━━━━━━━━━━━━━━━━━━━━━━
• `mythos-bot` — This Telegram bot
• `mythos-api` — FastAPI gateway (:8000)
• `mythos-patch-monitor` — Auto-deploy
• Various `mythos-worker-*` services

Check with: `/inspect service bot` or `/diag services`
"""

# ---------------------------------------------------------------------------
# DB mode
# ---------------------------------------------------------------------------
HELP_DB = """🗄️ **Database Mode**

Query Neo4j and PostgreSQL directly.

━━━━━━━━━━━━━━━━━━━━━━━━
**ENTERING DB MODE**
━━━━━━━━━━━━━━━━━━━━━━━━
`/mode db`
Then type natural language queries.

━━━━━━━━━━━━━━━━━━━━━━━━
**EXAMPLE QUERIES**
━━━━━━━━━━━━━━━━━━━━━━━━
"Show me all Soul nodes"
"What relationships does Ka'tuar'el have?"
"How many transactions this month?"
"List all accounts"

━━━━━━━━━━━━━━━━━━━━━━━━
**DIRECT QUERIES (via /inspect)**
━━━━━━━━━━━━━━━━━━━━━━━━
`/inspect sql "SELECT * FROM accounts"` — PostgreSQL
`/inspect cypher "MATCH (n:Soul) RETURN n"` — Neo4j
`/inspect schema` — All tables + row counts
`/inspect nodes` — Neo4j label counts

━━━━━━━━━━━━━━━━━━━━━━━━
**TIPS**
━━━━━━━━━━━━━━━━━━━━━━━━
• Natural language is converted to queries in `/mode db`
• For precise queries, use `/inspect sql` or `/inspect cypher`
• Use `/mode chat` to return to chat
"""

# ---------------------------------------------------------------------------
# Consciousness / Evolution
# ---------------------------------------------------------------------------
HELP_CONSCIOUSNESS = """🧠 **Consciousness Stream & Iris Evolution**
How Iris tracks, understands, and remembers conversations.
━━━━━━━━━━━━━━━━━━━━━━━━
**WHAT'S RUNNING**
━━━━━━━━━━━━━━━━━━━━━━━━
Every message you send flows through:
1. **Subject Tracking** — extracts what you're talking about
2. **Conversation Segments** — groups related messages
3. **Grid Analysis** — 9-node consciousness processing
4. **Life Context** — injects your current routines, bills, calendar
5. **Memory** — recent conversation history for continuity

This happens automatically. No commands needed.
━━━━━━━━━━━━━━━━━━━━━━━━
**CONVERSATION AWARENESS**
━━━━━━━━━━━━━━━━━━━━━━━━
Iris tracks the *subject* of your conversation:
• Subject tags extracted from each message
• Emotional tone detected (contemplative, neutral, etc.)
• Energy level tracked (low, medium, high)
• Segments auto-open and auto-close

View with:
`/inspect sql "SELECT subject_summary, emotional_tone FROM conversation_subject_points ORDER BY created_at DESC LIMIT 5"`
━━━━━━━━━━━━━━━━━━━━━━━━
**LIFE CONTEXT**
━━━━━━━━━━━━━━━━━━━━━━━━
Iris knows your current state:
• Today's routines and completion status
• Open tasks
• Account balances
• Bills due soon
• Calendar events
• Last check-in time

This feeds into every response — she knows what's on your plate.
━━━━━━━━━━━━━━━━━━━━━━━━
**BACKGROUND WORKERS**
━━━━━━━━━━━━━━━━━━━━━━━━
13 workers process your messages in parallel:
• Grid analysis (9-node scoring)
• Embedding generation
• Summary extraction
• Temporal analysis
• Entity resolution
• Vision analysis (photos)
• Transcription (voice)
• Segment management
• Subject enrichment

Check status: `/diag workers`
━━━━━━━━━━━━━━━━━━━━━━━━
**THE EVOLUTION PLAN**
━━━━━━━━━━━━━━━━━━━━━━━━
Iris is being built in phases:
• **Phase 0** ✅ Quick wins (subject tracking, context fix)
• **Phase 1** 📋 Wire iris-core to real infrastructure
• **Phase 2** 📋 Consciousness stream integration
• **Phase 3** 📋 81-channel grid processing (9×9)
• **Phase 4** 📋 Perception system activation
• **Phase 5** 📋 Memory, self-model, reflection
• **Phase 6** 📋 Cleanup dead code

View full plan:
`/inspect cat docs/EVOLUTION_PLAN.md`
━━━━━━━━━━━━━━━━━━━━━━━━
**ARCHITECTURE**
━━━━━━━━━━━━━━━━━━━━━━━━
The consciousness architecture is documented in:
• `docs/EVOLUTION_PLAN.md` — Phased roadmap
• `docs/consciousness/IRIS.md` — Full Iris spec
• `docs/consciousness/CONSCIOUSNESS_ARCHITECTURE.md` — 9 layers
• `docs/consciousness/81_FUNCTIONS.md` — 81-function matrix
• `docs/consciousness/STORAGE_ARCHITECTURE.md` — PG + Neo4j design
"""

# ---------------------------------------------------------------------------
# mx Shell Session
# ---------------------------------------------------------------------------
HELP_MX = """🖥️ **mx — Mythos Shell Session**
Self-healing, intent-aware terminal session for Arcturus.
Installed: SYS-0026 through SYS-0030

━━━━━━━━━━━━━━━━━━━━━━━━
**STARTING A SESSION**
━━━━━━━━━━━━━━━━━━━━━━━━
```
mx                     Start session (asks for intent)
mx --model llama3.2:3b Use specific Ollama model
mx --no-heal           Intent resolution only, no healing
mx --version           Show version
```

━━━━━━━━━━━━━━━━━━━━━━━━
**INTENT RESOLUTION**
━━━━━━━━━━━━━━━━━━━━━━━━
Terse phrases resolve to real commands automatically:
```
api restart       → sudo systemctl restart mythos-api.service
api logs          → journalctl -u mythos-api.service -f -n 50
bot restart       → sudo systemctl restart mythos-bot.service
services          → systemctl list-units | grep mythos
streams           → show stream patch counters
pi SYS-0031       → patch-install SYS-0031
pi SYS-0031 -dry  → patch-install SYS-0031 --dry-run
pi SYS-0031 -c    → patch-install SYS-0031 --clip
db balances       → psql query for account balances
db tables         → psql table listing
seraphe lunar     → seraphe lunar report
adge transits     → adge transit report
diag              → mythos-diag streams
todo              → cat TODO.md (head)
```
Edit: `/opt/mythos/mx/mx_intents.yaml`
Unknown phrases → Ollama resolves → auto-saved for next time

━━━━━━━━━━━━━━━━━━━━━━━━
**SELF-HEALING**
━━━━━━━━━━━━━━━━━━━━━━━━
When a command fails:
1. Checks `~/.mx/patterns/errors.jsonl` for known fix (instant)
2. If unknown → sends last 10 commands + error to Ollama
3. Ollama returns: FIX / FIX_SEQUENCE / ASK / EXPLAIN
4. Shows fix with 3s countdown → runs it
5. If fix fails → loops up to 3 attempts with updated context
6. Successful fixes stored → learned instantly

Dangerous commands (`rm -rf`, `DROP TABLE`, etc.) always require explicit `yes` confirmation.

━━━━━━━━━━━━━━━━━━━━━━━━
**PRE/POST INTEGRITY HOOKS**
━━━━━━━━━━━━━━━━━━━━━━━━
Significant operations trigger automatic wrapping:
• `patch-install`, `systemctl restart`, `psql` migrations
• `ALTER TABLE`, `CREATE TABLE`, `DROP TABLE`

Each significant command:
1. 📸 Pre-flight integrity scan (services + tables)
2. 📸 Pre-operation snapshot → `~/.mx/snapshots/`
3. Executes command (healing if needed)
4. 📸 Post-operation integrity scan
5. 📸 Post-operation snapshot
6. Delta report — additions / changes / regressions / neutral
7. ⚠ Rollback offer if regressions detected

━━━━━━━━━━━━━━━━━━━━━━━━
**SESSION JOURNAL**
━━━━━━━━━━━━━━━━━━━━━━━━
On exit, mx writes a summary to `docs/TODO.md`:
• Intent declared at session start
• Commands run, failures healed, duration
• Patches deployed, services restarted
• Delta summary

Journal files: `~/.mx/journal/`

━━━━━━━━━━━━━━━━━━━━━━━━
**IRIS INTEGRITY**
━━━━━━━━━━━━━━━━━━━━━━━━
`/iris_integrity` — Health from last scan
`/iris_integrity scan` — Run fast scan (services + tables)
`/iris_integrity full` — Full scan including files (~60s)
`/iris_integrity context` — What Iris carries in awareness

━━━━━━━━━━━━━━━━━━━━━━━━
**FILES**
━━━━━━━━━━━━━━━━━━━━━━━━
| File | Purpose |
|------|---------|
| `/opt/mythos/mx/mx_session.py` | Core session loop |
| `/opt/mythos/mx/mx_intent.py` | Intent resolver |
| `/opt/mythos/mx/mx_logger.py` | Session text logger |
| `/opt/mythos/mx/mx_journal.py` | TODO.md journal writer |
| `/opt/mythos/mx/mx_snapshot.py` | State snapshot serializer |
| `/opt/mythos/mx/mx_delta.py` | Snapshot diff engine |
| `/opt/mythos/mx/mx_hooks.py` | Pre/post integrity hooks |
| `/opt/mythos/mx/mx_intents.yaml` | Your command language |
| `/opt/mythos/mx/mx_config.yaml` | Model, countdown, buffer |
| `~/.mx/sessions/` | Per-session text logs |
| `~/.mx/snapshots/` | System state snapshots |
| `~/.mx/patterns/errors.jsonl` | Learned error→fix pairs |
| `~/.mx/intents/learned.yaml` | Ollama-learned intents |
| `~/.mx/journal/` | Session JSON journals |
| `/opt/mythos/docs/live/` | Latest integrity scan output |

━━━━━━━━━━━━━━━━━━━━━━━━
**CLI DIAGNOSTICS**
━━━━━━━━━━━━━━━━━━━━━━━━
`mythos-diag mx` — Full mx system status
`mythos-diag mx` shows: recent sessions, snapshots, learned patterns, learned intents, integrity scan age, journal count.
"""

# ---------------------------------------------------------------------------
# Topic aliases for flexible matching
# ---------------------------------------------------------------------------
HELP_TOPICS = {
    # Chat & modes
    'chat': HELP_CHAT,
    'talk': HELP_CHAT,
    'conversation': HELP_CHAT,
    'ai': HELP_CHAT,
    'iris': HELP_CHAT,
    'modes': HELP_CHAT,
    'mode': HELP_CHAT,
    'models': HELP_CHAT,
    'model': HELP_CHAT,
    'personality': HELP_CHAT,
    'voice': HELP_CHAT,
    'media': HELP_CHAT,

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
    'forecast': HELP_FINANCE,
    'pulse': HELP_FINANCE,
    'snapshot': HELP_FINANCE,
    'report': HELP_FINANCE,

    # Briefing / Routines
    'briefing': HELP_BRIEFING,
    'checkin': HELP_BRIEFING,
    'routines': HELP_BRIEFING,
    'routine': HELP_BRIEFING,
    'calendar': HELP_BRIEFING,
    'weather': HELP_BRIEFING,
    'review': HELP_BRIEFING,
    'analyze': HELP_BRIEFING,
    'priorities': HELP_BRIEFING,

    # Astrology
    'astrology': HELP_ASTROLOGY,
    'chart': HELP_ASTROLOGY,
    'charts': HELP_ASTROLOGY,
    'planets': HELP_ASTROLOGY,
    'aspects': HELP_ASTROLOGY,
    'houses': HELP_ASTROLOGY,
    'natal': HELP_ASTROLOGY,

    # People
    'people': HELP_PEOPLE,
    'person': HELP_PEOPLE,
    'contacts': HELP_PEOPLE,

    # Ontology / Define
    'define': HELP_DEFINE,
    'ontology': HELP_DEFINE,
    'glossary': HELP_DEFINE,
    'terms': HELP_DEFINE,

    # Sell
    'sell': HELP_SELL,
    'selling': HELP_SELL,
    'inventory': HELP_SELL,
    'items': HELP_SELL,

    # Inspect
    'inspect': HELP_INSPECT,
    'files': HELP_INSPECT,
    'browse': HELP_INSPECT,
    'cat': HELP_INSPECT,
    'tree': HELP_INSPECT,
    'grep': HELP_INSPECT,
    'sql': HELP_INSPECT,
    'cypher': HELP_INSPECT,

    # Diag
    'diag': HELP_DIAG,
    'diagnostics': HELP_DIAG,
    'health': HELP_DIAG,

    # Database
    'db': HELP_DB,
    'database': HELP_DB,
    'query': HELP_DB,
    'neo4j': HELP_DB,
    'postgres': HELP_DB,

    # Consciousness / Evolution
    'consciousness': HELP_CONSCIOUSNESS,
    'evolution': HELP_CONSCIOUSNESS,
    'stream': HELP_CONSCIOUSNESS,
    'subject': HELP_CONSCIOUSNESS,
    'awareness': HELP_CONSCIOUSNESS,
    'workers': HELP_CONSCIOUSNESS,
    'grid': HELP_CONSCIOUSNESS,
    'layers': HELP_CONSCIOUSNESS,

    # mx shell
    'mx': HELP_MX,
    'shell': HELP_MX,
    'terminal': HELP_MX,
    'heal': HELP_MX,
    'healing': HELP_MX,
    'intent': HELP_MX,
    'snapshot': HELP_MX,
    'delta': HELP_MX,
    # System
    'system': HELP_SYSTEM,
    'sys': HELP_SYSTEM,
    'patch': HELP_SYSTEM,
    'patches': HELP_SYSTEM,
    'admin': HELP_SYSTEM,
    'status': HELP_SYSTEM,
    'services': HELP_SYSTEM,
}

# All available topic names for the error message
TOPIC_LIST = sorted(set([
    'chat', 'tasks', 'finance', 'briefing', 'astrology',
    'people', 'define', 'sell', 'inspect', 'diag', 'db', 'system',
    'consciousness',
    'mx',
]))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /help command with optional topic

    Usage:
        /help           - Main overview
        /help <topic>   - Detailed help for that topic
    """
    args = context.args if context.args else []

    if not args:
        await update.message.reply_text(HELP_MAIN, parse_mode='Markdown')
        return

    topic = args[0].lower()

    if topic in HELP_TOPICS:
        await update.message.reply_text(HELP_TOPICS[topic], parse_mode='Markdown')
    else:
        await update.message.reply_text(
            f"❓ Unknown topic: `{topic}`\n\n"
            f"Available: {', '.join(f'`{t}`' for t in TOPIC_LIST)}\n\n"
            "Use `/help` for overview.",
            parse_mode='Markdown'
        )
