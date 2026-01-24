# Mythos Project TODO & Roadmap

> **Last Updated:** 2026-01-24 10:00 EST
> **Current Focus:** System Documentation + Finance Polish

---

## 📖 About This Document

**TODO.md is the living work journal.** Update constantly during work sessions.

| Document | Purpose | Update Frequency |
|----------|---------|------------------|
| `TODO.md` | What we're trying to do | Every work session |
| `ARCHITECTURE.md` | What actually exists and works | Only at stable milestones |

---

## 🔥 Active Work

### Comprehensive Documentation (patch_0020)
- **Status:** In progress
- **What:** Full system audit and documentation update
- **Files:** `ARCHITECTURE.md`, `TODO.md`

### Finance System - Sunmark Parser (patch_0018)
- **Status:** Deployed, needs verification
- **What:** Clean descriptions with (POS)/(ATM)/(EXT) tags
- **Next:** Run `update_sunmark_descriptions.py` to fix existing transactions

---

## 🚧 Gaps to Fill (High Priority)

These are missing pieces needed for a complete, production-ready system.

### 1. Local LLM Conversational Interface
- **Problem:** Can't have multi-turn conversations with local Ollama without external interface
- **Solution Options:**
  - Open WebUI (Docker container)
  - Extend Telegram bot with `/chat` mode that maintains context
  - Build simple web interface
- **Priority:** HIGH - blocks sovereign AI workflow

### 2. Finance - Telegram Integration
- **Problem:** Finance data only accessible via CLI
- **Solution:** Add `/finance` command group to bot
  - `/finance summary` - Account balances
  - `/finance recent [n]` - Last N transactions
  - `/finance search <term>` - Find transactions
  - `/finance category <term>` - Spending by category
  - `/finance uncategorized` - List uncategorized for review
- **Priority:** HIGH - daily use feature

### 3. Seraphe Mode Implementation
- **Problem:** `/mode seraphe` returns placeholder
- **Solution:** Create `seraphe_assistant.py` with:
  - Cosmology/symbolism knowledge base
  - Dream interpretation
  - Spiritual guidance prompts
  - Integration with Neo4j spiritual entities
- **Priority:** MEDIUM - core spiritual functionality

### 4. Genealogy Mode Implementation
- **Problem:** `/mode genealogy` not implemented
- **Solution:** Create `genealogy_assistant.py` with:
  - Family tree traversal queries
  - Bloodline tracing
  - Integration with genealogy data sources
  - GEDCOM import support
- **Priority:** MEDIUM - supports lineage work

### 5. Worker Health Monitoring
- **Problem:** Workers run but no visibility into their health/throughput
- **Solution:**
  - Add `/worker_status` Telegram command
  - Track processing times and error rates
  - Alert on worker failures
- **Priority:** MEDIUM - operational visibility

### 6. Conversation Context for Local LLM
- **Problem:** `db_manager.py` doesn't persist conversation context well
- **Solution:**
  - Implement sliding window context
  - Store recent exchanges in session
  - Use summary worker for long conversations
- **Priority:** MEDIUM - improves LLM interaction quality

### 7. System Monitor Service
- **Problem:** `graph_logging/system_monitor.py` exists but not running as service
- **Solution:**
  - Create `mythos-monitor.service`
  - Configure collection intervals
  - Verify Neo4j event storage
- **Priority:** LOW - nice-to-have for diagnostics

### 8. Qdrant Collection Setup
- **Problem:** Embedding worker references Qdrant but collection may not exist
- **Solution:**
  - Verify/create `text_embeddings` collection
  - Add collection initialization to worker startup
  - Document Qdrant setup
- **Priority:** LOW - embeddings not actively used yet

---

## 📋 Backlog (Planned Features)

### Finance Enhancements
- [ ] Recurring transaction detection
- [ ] Budget alerts per category
- [ ] Weekly spending digest via Telegram
- [ ] Plaid API integration (real-time bank sync)
- [ ] Receipt photo matching to transactions

### Sales System Enhancements
- [ ] Batch photo upload (more than 3 at a time)
- [ ] Price suggestion based on sold history
- [ ] Auto-post to multiple marketplaces
- [ ] Inventory aging alerts
- [ ] Sales analytics dashboard

### Conversation System
- [ ] Implement Tier 1/Tier 2 summary system
- [ ] Semantic search across past conversations
- [ ] Topic extraction and tracking
- [ ] Emotional state timeline

### Graph Database
- [ ] Lineage visualization web UI
- [ ] Incarnation timeline view
- [ ] Entity relationship explorer
- [ ] Automated fact extraction from conversations

### Infrastructure
- [ ] Backup automation (PostgreSQL + Neo4j)
- [ ] Log rotation for all services
- [ ] Health check endpoint aggregator
- [ ] Prometheus/Grafana metrics (optional)

### AI/LLM
- [ ] Fine-tune local model on Mythos data
- [ ] Tool calling for db_manager (vs prompt-based Cypher)
- [ ] RAG pipeline for knowledge retrieval
- [ ] Voice input via Telegram voice messages

---

## ✅ Completed

### 2026-01-24
- [x] Comprehensive system audit
- [x] ARCHITECTURE.md rewrite (v2.0.0)
- [x] TODO.md overhaul with gaps analysis
- [x] Patch history tracking added
- [x] Sunmark description cleanup (patch_0018)

### 2026-01-23
- [x] Patch system with auto-deploy (patch_0010-0017)
- [x] Finance system - imports, categories, reports (patch_0015)
- [x] USAA and Sunmark CSV parsers
- [x] 682 transactions imported
- [x] 199 category mappings

### Earlier
- [x] Telegram bot with multi-mode support
- [x] FastAPI gateway with orchestrator
- [x] 6 async workers (vision, embedding, grid, entity, temporal, summary)
- [x] Sales intake pipeline (photo → vision → DB → export)
- [x] Neo4j graph schema for souls, persons, conversations
- [x] Graph logging with causal event tracking
- [x] `mythos-ask` LLM diagnostic CLI
- [x] Vision module with llava integration

---

## 💡 Ideas (Unplanned)

- Web dashboard for all Mythos data
- Mobile app (React Native)
- Integration with Obsidian vault
- Astrological event correlation
- Dream journal with pattern detection
- Automated spiritual practice reminders
- Integration with calendar (Google/Apple)
- Genealogy GEDCOM export
- Public API for trusted partners

---

## 🔧 Workflows & Patterns

### Diagnostic Dump Pattern

```bash
D=~/diag.txt; > "$D"
echo "=== SECTION HEADER ===" >> "$D"
<command> >> "$D" 2>&1
echo -e "\n\n=== NEXT SECTION ===" >> "$D"
<command> >> "$D" 2>&1
cat "$D" | xclip -selection clipboard && echo "✓ Copied to clipboard"
```

### Patch Deployment Pattern

1. Claude creates `patch_NNNN_description/` with files and `install.sh`
2. Claude zips and provides download
3. User downloads → copies to `~/Downloads` on Arcturus
4. Patch monitor auto-detects → git tag → extract → commit → version → push → install
5. Verify via `/patch_status`

### Session Start Pattern

When starting a new Claude conversation:
1. Provide handoff prompt or "continuing Mythos work on [topic]"
2. Claude requests diagnostic dump for TODO.md and ARCHITECTURE.md
3. Claude reviews current state before proceeding

---

## 📦 Patch History

> **Next Patch Number: 0021**

| Patch | Date | Description |
|-------|------|-------------|
| 0020 | 2026-01-24 | Comprehensive documentation overhaul |
| 0019 | 2026-01-24 | Added patch history to TODO.md |
| 0018 | 2026-01-24 | Sunmark description cleanup - (POS)/(ATM)/(EXT) tags |
| 0017 | 2026-01-24 | Project docs updated |
| 0016 | 2026-01-24 | Project documentation system (TODO.md, ARCHITECTURE.md) |
| 0015 | 2026-01-24 | Finance system complete - imports, categories, reports |
| 0014 | 2026-01-23 | Finance migration |
| 0013 | 2026-01-23 | Finance system initial |
| 0012 | 2026-01-23 | Telegram autoexec |
| 0011 | 2026-01-23 | Test patch |
| 0010 | 2026-01-23 | GitHub patch system |

*Increment patch number and add row when creating new patches.*

---

## ❌ Dropped (Abandoned Ideas)

*Nothing dropped yet - this section holds ideas we explicitly decided not to pursue.*

---

*This file is auto-committed with each patch. Never delete items - mark as completed or move to Dropped.*
