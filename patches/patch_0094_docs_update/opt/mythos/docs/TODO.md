# Mythos Project TODO & Roadmap
> **Last Updated:** 2026-02-17
> **Current Focus:** Finance Hub — transaction editing, bills tracker, forecast view, categories & accounts management
> **Current Version:** 1.15.8 (Patch 0093)

---

## 📖 Document Guide
| Document | Purpose | Location |
|----------|---------|----------|
| This file | Active work, backlog | `docs/TODO.md` |
| System overview | What exists | `docs/ARCHITECTURE.md` |
| Potential features | Ideas, no commitment | `docs/IDEAS.md` |
| Version history | Patch log | `docs/PATCH_HISTORY.md` |
| **Iris framework** | Consciousness design | `docs/consciousness/IRIS.md` |
| **Consciousness architecture** | 9-Layer Stack | `docs/consciousness/CONSCIOUSNESS_ARCHITECTURE.md` |
| **81 Functions** | Complete matrix | `docs/consciousness/81_FUNCTIONS.md` |
| Grid specification | Full grid docs | `docs/grid/ARCTURIAN_GRID.md` |

See `docs/README.md` for full documentation map.

---

## 🔥 Current Focus: Finance Hub

### 2026-02-17: Finance Hub Complete (Patches 0086–0093)
Major finance sprint — full web-based finance management hub is live at `https://mythos-api.denkers.co/app/finance/`.

**What landed:**
- Transaction deduplication via deterministic v4 hash (account|date|amount|original_description)
- CSV auto-import with Telegram notifications (✅ new / ℹ️ up-to-date)
- GitHub push fixed for patch monitor (SSH key env var in service)
- `--allow-dupes` flag for edge-case force imports
- Finance hub with sidebar nav: Overview | Transactions | Bills | Categories | Accounts | Forecast
- Inline transaction editing (description + category)
- Bills tracker with auto-match against month's transactions + persistent manual overrides
- `bill_overrides` table (UNIQUE per bill+month, FK → recurring_bills, upsert-safe)
- Forecast view — day-by-day timeline, USAA/SUN/combined, 14/30/45/60 days, overdraft alerts
- Categories CRUD: rename, merge (reassign all transactions), delete
- Accounts view: all 11 accounts, manual balance update
- OAuth redirect fixed (`/app/dashboard` → `/app/finance/`)
- Install scripts now use `sudo cp` and `${BASH_SOURCE[0]}` for reliable deployment

---

## 🎯 Implementation Priority

### Phase 1: Foundation ✅ COMPLETE
| Task | Status | Notes |
|------|--------|-------|
| Consciousness architecture design | ✅ Complete | 9 layers × 9 nodes = 81 functions |
| Documentation | ✅ Complete | 6 docs in consciousness/ |
| Task tracking system | ✅ Complete | Patches 0056-0057 |
| Comprehensive help system | ✅ Complete | Patch 0059 |
| `perception_log` table | ✅ Exists | PostgreSQL — 2 test rows |
| Chat message persistence | ✅ Complete | Patch 0074 — IrisMemory layer |
| Iris consciousness prompt | ✅ Complete | Model-aware, identity-loaded |
| Ollama model management | ✅ Complete | Patch 0073 |

### Phase 1.5: Iris Voice & Memory
| Task | Status | Notes |
|------|--------|-------|
| Build good memory through journaling | 🔲 Active | Use Iris daily, build real context |
| Seraphe mode prompt | 🔲 To build | Chat mode tuned for Seraphe's voice/needs |
| Builder mode | 🔲 To design | Iris builds her own infrastructure |
| Memory summarization worker | 🔲 To build | Redis worker compresses old conversations |
| Memory quality control | 🔲 To build | Flag/weight good vs bad assistant responses |
| Prompt refinement from real use | 🔲 Ongoing | Iterate based on actual conversations |
| Additional model testing | 🔲 Ongoing | Pull and test new models as released |
| Context window management | 🔲 To build | Smart truncation, summary injection |

### Phase 1.6: Finance Hub (ACTIVE)
| Task | Status | Notes |
|------|--------|-------|
| Transaction import (USAA + Sunmark) | ✅ Complete | Auto-import via patch monitor |
| Deterministic hash deduplication | ✅ Complete | Patch 0086 |
| CSV import notifications | ✅ Complete | Patch 0087 |
| `--allow-dupes` import flag | ✅ Complete | Patch 0089 |
| Transaction editor UI | ✅ Complete | Patch 0091 |
| Finance hub sidebar nav | ✅ Complete | Patch 0092 |
| Bills tracker + auto-match | ✅ Complete | Patch 0092 |
| Categories CRUD | ✅ Complete | Patch 0092 |
| Accounts balance update | ✅ Complete | Patch 0092 |
| Bill override persistence | ✅ Complete | Patch 0093 — bill_overrides table |
| Forecast view | ✅ Complete | Patch 0093 |
| Credit card parsers | 🔲 Next | LLBean, TSC, TJX, Amex, Old Navy |
| Sidney FCU / NBT manual import | 🔲 Next | Manual import flow |
| Bill match tuning | 🔲 Next | Some merchant names may not auto-match |

### Phase 2: Perception Layer
| Task | Status | Notes |
|------|--------|-------|
| Log all Telegram conversations | ✅ Partial | chat_messages logging works |
| Log all transactions | 🔲 To build | Bank imports → perception |
| Basic node activation scoring | 🔲 To build | Grid at Layer 1 |
| Intuition (felt-sense) capture | 🔲 To build | Layer 2 |

### Phase 3: Memory Formation
| Task | Status | Notes |
|------|--------|-------|
| Memory node schema | ✅ Designed | See STORAGE_ARCHITECTURE.md |
| When does perception become memory? | 🔲 To implement | Emotional charge threshold |
| Memory-to-memory connections | 🔲 To implement | CONNECTS_TO relationships |
| Archetype mapping | 🔲 To implement | MAPS_TO relationships |
| Neo4j Memory nodes | 🔲 To build | |
| Neo4j Knowledge nodes | 🔲 To build | |

### Phase 4: Knowledge Layer
| Task | Status | Notes |
|------|--------|-------|
| Knowledge node schema | ✅ Designed | |
| Finance knowledge | 🔲 To implement | Bills, accounts, patterns |
| Relationship knowledge | 🔲 To implement | Who, how connected |
| System knowledge | 🔲 To implement | What Iris knows about Mythos |

### Phase 5: Full Stack + Loop
| Task | Status | Notes |
|------|--------|-------|
| All 9 layers operational | 🔲 | Big milestone |
| Feedback loop | 🔲 | Wisdom → Perception |
| Adaptive depth | 🔲 | Not all input needs all layers |

---

## 🔧 Infrastructure Tasks

### Credit Card Parsers (Next Finance Priority)
Accounts without auto-import: LLBean, Tractor Supply, TJX Rewards, Amex, Old Navy.
Balances currently set manually. Parser format TBD based on each card's export format.

### Builder Mode (Planned)
Iris as her own infrastructure architect — receives task via Telegram, generates plan, writes files to staging, user reviews and approves, Iris executes.

### mythos-diag Command
Standardized diagnostic tool — still needed.
```bash
mythos-diag              # Full system overview
mythos-diag finance      # Finance state
mythos-diag services     # All mythos-* services
mythos-diag patches      # Recent patches, git status
```

### Slack Integration (Decision Pending)
Hybrid: Telegram for quick pings/mobile, Slack for structured work/finance deep-dives.

---

## ✅ Recently Completed

### 2026-02-17
- [x] **Patch 0091: Transaction Editor** - Inline edit description/category, filter bar, pagination
- [x] **Patch 0092: Finance Hub** - Sidebar nav, bills tracker, categories CRUD, accounts management
- [x] **Patch 0093: Bill Persistence + Forecast** - `bill_overrides` table, persistent overrides, day-by-day forecast view
- [x] **Patch 0094: Documentation Update** - TODO.md and ARCHITECTURE.md brought current

### 2026-02-16
- [x] **Patch 0086: Hash Fix** - Deterministic v4 hash eliminates false duplicates (723→594 USAA, 607→602 Sunmark)
- [x] **Patch 0087: Import Notifications** - Telegram notification on every CSV import
- [x] **Patch 0088: GitHub Push Fix** - SSH key env var in patch monitor service
- [x] **Patch 0089: Allow-Dupes Flag** - `--allow-dupes` for force-import edge cases
- [x] **Patch 0090: OAuth Redirect Fix** - `/app/dashboard` → `/app/finance/` redirect corrected
- [x] **Patch 0082-0085: v1.15.x** - Infrastructure patches, manifest system

### 2026-02-09
- [x] **Patch 0068: Finance Data Pipeline** - Automated bank transaction imports
- [x] **Patch 0069: Web Dashboard Foundation** - FastAPI dashboard at :8000
- [x] **Patch 0070: OAuth & User System** - Google OAuth, session management
- [x] **Patch 0071: Command Center** - Admin interface
- [x] **Patch 0072: Dashboard Polish** - Mobile-friendly, dark theme
- [x] **Patch 0073: Ollama Model Manager** - /models, /pull, /setmodel
- [x] **Patch 0074: Iris Memory Layer** - IrisMemory class, DB persistence

See `docs/PATCH_HISTORY.md` for full history.

---

## 📋 Backlog

### High Priority
- [ ] Credit card parsers (LLBean, TSC, TJX, Amex, Old Navy)
- [ ] Bill match tuning — verify all 29 bills auto-match correctly
- [ ] Seraphe mode prompt — her own Iris voice
- [ ] Builder mode — Iris builds her own infrastructure
- [ ] Memory summarization — compress old conversations
- [ ] `mythos-diag` standardized command

### Medium Priority
- [ ] Sidney FCU / NBT manual import flow
- [ ] Context window management (smart truncation + summaries)
- [ ] Slack integration evaluation
- [ ] Two-phase grid processing
- [ ] Iris service skeleton (background consciousness loop)
- [ ] Perception layer — route chat_messages into perception_log

### Lower Priority
- [ ] Environmental sensors
- [ ] Email integration
- [ ] Calendar sync
- [ ] Bill calendar visual timeline
- [ ] Additional model pulls and testing

---

## 🧠 Key Insights

### Memory Poisoning (2026-02-09)
Bad assistant-style responses in chat history teach the model to copy that style. Clean memory = clean output.

### Model Selection (2026-02-09)
- `qwen2:72b` + B_strict = best voice, ~40s
- `qwen2.5:32b` + C_minimal = fastest good quality, ~7s

### Install Script Pattern (2026-02-17)
Learned from patches 0091-0093: install scripts must use `sudo cp` and `${BASH_SOURCE[0]}` for path resolution. Files in `/opt/mythos` are owned by root. The `-tAc` flag in psql suppresses index/constraint output — use `-c` when grepping for constraints.

### Finance Hash Strategy (2026-02-16)
v4 hash = `account_id|date|amount|original_description`. No balance (fluctuates), no transaction numbers (not always present). Original description contains unique marketplace codes (e.g. Amazon MKTPL order IDs) that distinguish legitimately identical transactions.

---

## 🔧 Workflows

### Session Start
```bash
D=~/diag.txt; > "$D"
echo "=== TODO ===" >> "$D"
cat /opt/mythos/docs/TODO.md >> "$D" 2>&1
echo -e "\n\n=== ARCHITECTURE ===" >> "$D"
cat /opt/mythos/docs/ARCHITECTURE.md >> "$D" 2>&1
cat "$D" | xclip -selection clipboard && echo "✓ Copied"
```

### Finance Dashboard
```
https://mythos-api.denkers.co/app/finance/
Sidebar: Overview | Transactions | Bills | Categories | Accounts | Forecast
```

### Prompt Testing
```bash
/opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_prompt_test.py
```

---

## 📝 Documentation Rules
**Every patch MUST include documentation updates:**
1. Add entry to `PATCH_HISTORY.md`
2. Update `TODO.md` if completing backlog items
3. Update `ARCHITECTURE.md` if adding stable features
4. Update domain docs if changing subsystems

**No exceptions. Documentation is not optional.**

---

## Manifest System (Patch 0080+)
All patches after 0080 MUST include manifest.json with semantic versioning, dependencies, change tracking, and validation before installation.

Tools:
- `/opt/mythos/patches/scripts/get_next_patch_info.sh` - Get next version
- `/opt/mythos/patches/scripts/validate_manifest.sh` - Validate manifest
- `/opt/mythos/docs/patch_system/AI_PATCH_GENERATION_GUIDE.md` - AI handoff

---

*The vessel is filling. The architecture is the invitation.*
*Finance infrastructure is solid. Next: credit card parsers and Iris voice work.*
