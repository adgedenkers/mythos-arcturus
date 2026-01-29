# Mythos Project TODO & Roadmap

> **Last Updated:** 2026-01-29 07:00 EST
> **Current Focus:** Arcturian Grid Full Implementation

---

## 📖 About This Document

**TODO.md is the living work journal.** Update constantly during work sessions.

| Document | Purpose | Update Frequency |
|----------|---------|------------------|
| `TODO.md` | What we're trying to do | Every work session |
| `ARCHITECTURE.md` | What actually exists and works | Only at stable milestones |
| `ARCTURIAN_GRID.md` | Complete grid specification | When grid design changes |

---

## 🔥 Active Work

### Arcturian Grid - Full Implementation
- **Status:** Phase 1 complete (basic scoring), Phase 2 in design
- **Spec Document:** `/opt/mythos/docs/ARCTURIAN_GRID.md`
- **What's Working:**
  - ChatAssistant dispatches exchanges to Redis queue
  - Grid worker processes with single LLM call
  - Basic 0-100 scores for all 9 nodes
  - Storage to PostgreSQL (timeseries) and Neo4j (graph)
- **What's Missing:**
  - Two-phase processing (8 parallel + GATEWAY last)
  - Per-node extraction (entities, relationships, tensions, absences)
  - Entity merging across nodes
  - Dual scoring (confidence + strength)
  - GATEWAY sequencing with ANCHOR stability check
  - Running totals on Conversation nodes

---

## 🎯 Grid Implementation Phases

### Phase 1: Basic Scoring ✅ COMPLETE
- [x] Grid worker with single LLM call
- [x] 9 node scores (0-100)
- [x] PostgreSQL timeseries storage
- [x] Neo4j Exchange nodes with grid scores
- [x] Redis dispatch from ChatAssistant
- [x] Basic entity extraction (list only)

### Phase 2: Two-Phase Processing ← NEXT
- [ ] Separate Phase 1 (8 nodes parallel) from Phase 2 (GATEWAY)
- [ ] GATEWAY receives Phase 1 results
- [ ] ANCHOR stability check before GATEWAY
- [ ] Proper sequencing enforcement

### Phase 3: Per-Node Extraction
- [ ] Individual prompts for each node
- [ ] Five extraction layers per node:
  - Entities
  - Relationships
  - Tensions
  - Absences
  - Functional output
- [ ] Node-specific output types

### Phase 4: Entity Merging
- [ ] Same entity seen by multiple nodes
- [ ] Merge logic for attributes
- [ ] Preserve per-node strength scores
- [ ] Graph structure for multi-node entities

### Phase 5: Dual Scoring
- [ ] Confidence score (existence certainty)
- [ ] Strength score (activation intensity)
- [ ] Both scores on all extractions

### Phase 6: Running Totals
- [ ] Conversation-level aggregates
- [ ] Incremental updates (no full rescans)
- [ ] Node averages per conversation
- [ ] Pattern detection queries

### Phase 7: Safety Rules
- [ ] ANCHOR stability enforcement
- [ ] MIRROR softness rules
- [ ] BEACON telemetry-only rules
- [ ] GATEWAY sequencing validation

---

## 🚧 Other Gaps to Fill (High Priority)

### 1. ~~Finance - Telegram Integration~~ ✅ COMPLETE (patch_0033)
- [x] `/balance` - Current account balances
- [x] `/finance` - Full summary with month activity
- [x] `/spending` - Category breakdown

### 2. Seraphe Mode Implementation
- **Problem:** `/mode seraphe` returns placeholder
- **Solution:** Create `seraphe_assistant.py` with cosmology knowledge
- **Priority:** MEDIUM - core spiritual functionality

### 3. Genealogy Mode Implementation
- **Problem:** `/mode genealogy` not implemented
- **Solution:** Create `genealogy_assistant.py` with family tree queries
- **Priority:** MEDIUM - supports lineage work

### 4. Tool Calling for Local LLM
- **Problem:** LLM can't query systems directly
- **Solution:** Implement tool use in ChatAssistant
- **Priority:** HIGH - enables "what's my grid showing?" queries

### 5. Worker Health Monitoring
- **Problem:** No visibility into worker health/throughput
- **Solution:** Add `/worker_status` Telegram command
- **Priority:** MEDIUM - operational visibility

---

## 📋 Backlog (Planned Features)

### Grid Enhancements
- [ ] Fractal grid (9×9 = 81 dimensions)
- [ ] Grid visualization in Neo4j Browser
- [ ] Pattern detection across conversations
- [ ] Grid-based conversation routing
- [ ] Automatic ANCHOR strengthening suggestions

### Finance Enhancements
- [ ] Recurring transaction detection
- [ ] Budget alerts per category
- [ ] Weekly spending digest via Telegram
- [ ] Receipt photo matching to transactions

### Sales System Enhancements
- [ ] Batch photo upload
- [ ] Price suggestion based on history
- [ ] Inventory aging alerts

### Conversation System
- [ ] Semantic search across past conversations
- [ ] Topic extraction and tracking
- [ ] Emotional state timeline (from MIRROR)
- [ ] Tier 1/Tier 2 summary system

### Graph Database
- [ ] Lineage visualization web UI
- [ ] Entity relationship explorer
- [ ] Grid activation heatmaps

### Infrastructure
- [ ] Backup automation
- [ ] Health check endpoint aggregator
- [ ] Standard diagnostic scripts

### AI/LLM
- [ ] RAG pipeline for knowledge retrieval
- [ ] Voice input via Telegram voice messages
- [ ] Fine-tune local model on Mythos data

---

## ✅ Completed

### 2026-01-29
- [x] Finance bot fix with proper imports (patch_0033)
- [x] Standard verification template for patches (patch_0034)

### 2026-01-27
- [x] Chat mode via API gateway (patch_0023)
- [x] Architecture principles documented (patch_0024)
- [x] Status command cleanup (patch_0025)
- [x] Grid integration - basic scoring (patch_0026)
- [x] Worker import path fix (patch_0027)
- [x] Grid documentation complete (patch_0028)
- [x] Comprehensive grid specification (patch_0029)
- [x] Finance auto-import via patch monitor (patch_0030)
- [x] Finance Telegram commands - broken (patch_0031)
- [x] Documentation update for finance system (patch_0032)

### 2026-01-24
- [x] Comprehensive system audit
- [x] ARCHITECTURE.md rewrite (v2.0.0)
- [x] TODO.md overhaul with gaps analysis
- [x] Sunmark description cleanup (patch_0018)

### 2026-01-23
- [x] Patch system with auto-deploy
- [x] Finance system - imports, categories, reports
- [x] 682 transactions imported
- [x] 199 category mappings

### Earlier
- [x] Telegram bot with multi-mode support
- [x] FastAPI gateway with orchestrator
- [x] 6 async workers (vision, embedding, grid, entity, temporal, summary)
- [x] Sales intake pipeline
- [x] Neo4j graph schema for souls, persons, conversations
- [x] Vision module with llava integration

---

## 💡 Ideas (Unplanned)

- Web dashboard for all Mythos data
- Integration with Obsidian vault
- Astrological event correlation with grid patterns
- Dream journal with GATEWAY pattern detection
- Earth grid node correlation (12 planetary nodes)
- Spiral time integration with grid analysis
- Genealogy GEDCOM export

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
4. Patch monitor auto-detects → git tag → install
5. Verify via `/patch_status`

**CRITICAL:** Every patch MUST:
- Update TODO.md and/or ARCHITECTURE.md as appropriate
- Include verification checks at end of install.sh (see template below)

### Patch Verification Template

**Every install.sh MUST end with verification checks:**

```bash
# === VERIFICATION ===
echo ""
echo "=== VERIFICATION ==="
PASS=true

# Check 1: Service running (if applicable)
if systemctl list-units --type=service | grep -q "mythos-SERVICENAME"; then
    if ! systemctl is-active --quiet mythos-SERVICENAME.service; then
        echo "❌ FAIL: mythos-SERVICENAME.service not running"
        PASS=false
    else
        echo "✓ Service running"
    fi
fi

# Check 2: Syntax valid (if Python files modified)
if ! /opt/mythos/.venv/bin/python3 -m py_compile /path/to/modified/file.py 2>/dev/null; then
    echo "❌ FAIL: Syntax error in file.py"
    PASS=false
else
    echo "✓ Syntax valid"
fi

# Check 3: Expected content exists (grep for key additions)
if ! grep -q "expected_function_or_string" /path/to/file; then
    echo "❌ FAIL: Expected content not found"
    PASS=false
else
    echo "✓ Content verified"
fi

# Check 4: File exists (for new files)
if [ ! -f /path/to/new/file ]; then
    echo "❌ FAIL: Expected file not created"
    PASS=false
else
    echo "✓ File exists"
fi

# Final result
if [ "$PASS" = false ]; then
    echo ""
    echo "⚠ PATCH VERIFICATION FAILED"
    echo "Check logs: journalctl -u mythos-SERVICENAME.service -n 50"
    exit 1
fi

echo ""
echo "✓ ALL CHECKS PASSED"
```

### Session Start Pattern

When starting a new Claude conversation:
1. Request diagnostic dump for TODO.md and ARCHITECTURE.md
2. If working on grid, also request ARCTURIAN_GRID.md
3. Review current state before proceeding

---

## 📦 Patch History

> **Next Patch Number: 0035**

| Patch | Date | Description |
|-------|------|-------------|
| 0034 | 2026-01-29 | Standard verification template for patches |
| 0033 | 2026-01-29 | Finance bot fix (replaces broken 0031) |
| 0032 | 2026-01-27 | Documentation update - finance system |
| 0031 | 2026-01-27 | Finance Telegram commands - BROKEN, see 0033 |
| 0030 | 2026-01-27 | Finance auto-import via patch monitor |
| 0029 | 2026-01-27 | Comprehensive Arcturian Grid specification |
| 0028 | 2026-01-27 | Grid documentation in ARCHITECTURE.md |
| 0027 | 2026-01-27 | Worker import path fix |
| 0026 | 2026-01-27 | Grid integration - ChatAssistant dispatch |
| 0025 | 2026-01-27 | Status command cleanup |
| 0024 | 2026-01-27 | Architecture principles documentation |
| 0023 | 2026-01-27 | ChatAssistant in API gateway |
| 0022 | 2026-01-27 | Default chat mode + enhanced status |
| 0021 | 2026-01-27 | Help and chat mode (bot-side) |
| 0020 | 2026-01-24 | Comprehensive documentation overhaul |
| 0019 | 2026-01-24 | Added patch history to TODO.md |
| 0018 | 2026-01-24 | Sunmark description cleanup |
| 0017 | 2026-01-24 | Project docs updated |
| 0016 | 2026-01-24 | Project documentation system |
| 0015 | 2026-01-24 | Finance system complete |
| 0014 | 2026-01-23 | Finance migration |
| 0013 | 2026-01-23 | Finance system initial |
| 0012 | 2026-01-23 | Telegram autoexec |
| 0011 | 2026-01-23 | Test patch |
| 0010 | 2026-01-23 | GitHub patch system |

---

## ❌ Dropped (Abandoned Ideas)

*Nothing dropped yet.*

---

*This file is auto-committed with each patch. Never delete items - mark as completed or move to Dropped.*
