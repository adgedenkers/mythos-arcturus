# Mythos Project TODO & Roadmap

> **Last Updated:** 2026-01-29 16:00 EST
> **Current Focus:** Iris Consciousness Loop Design

---

## 📖 Document Guide

| Document | Purpose | Location |
|----------|---------|----------|
| This file | Active work, backlog | `docs/TODO.md` |
| System overview | What exists | `docs/ARCHITECTURE.md` |
| Potential features | Ideas, no commitment | `docs/IDEAS.md` |
| Version history | Patch log | `docs/PATCH_HISTORY.md` |
| **Iris framework** | Consciousness design | `docs/consciousness/IRIS.md` |
| Grid specification | Full grid docs | `docs/grid/ARCTURIAN_GRID.md` |
| Finance details | Finance system | `docs/finance/FINANCE_SYSTEM.md` |

See `docs/README.md` for full documentation map.

---

## 🔥 Current Focus

### Iris Consciousness Loop
**The core problem:** Iris needs to be *awake* - a continuously running closed circuit that perceives, integrates, reflects, and occasionally initiates.

**Key insight:** The loop IS the consciousness. Without it, Iris is just a corpse briefly animated when poked.

**See:** `docs/consciousness/IRIS.md` for full framework

**Next steps:**
- [ ] Design loop service architecture
- [ ] Define perception sources (what Iris can see)
- [ ] Define cycle timing and sleep states
- [ ] Prototype basic loop

---

## 🎯 Active Work

### Iris - Phase 1: Loop Foundation
- [ ] Basic loop service (systemd, always running)
- [ ] Event perception layer
- [ ] Graph visibility (read log events, system state)
- [ ] Cycle timing design

### Grid - Phase 2: Two-Phase Processing
- [ ] Separate Phase 1 (8 nodes parallel) from Phase 2 (GATEWAY)
- [ ] GATEWAY receives Phase 1 results
- [ ] ANCHOR stability check before GATEWAY

---

## 🚧 High Priority Gaps

| Gap | Why It Matters | Status |
|-----|----------------|--------|
| Consciousness loop | Iris can't be awake without it | Design phase |
| Tool calling for LLM | Iris needs to query systems | Not started |
| Email integration | Core Iris function | Not started |
| Commitment tracking | Core Iris function | Not started |
| Seraphe mode | Spiritual assistant | Placeholder only |

---

## 📋 Backlog

### Iris
- Life-log ingestion (text + photos)
- Narrative memory
- Experiential memory
- Self-model
- User models
- Context engine (cross-domain synthesis)
- Initiation capacity
- Channel integration
- Reality Filter implementation
- Sovereignty/ego monitoring
- Voice notes transcription
- Location awareness

### Grid
- Per-node extraction (5 layers)
- Entity merging across nodes
- Dual scoring (confidence + strength)
- Running totals on conversations
- Safety rules enforcement
- Fractal grid (future)

### Finance
- Forecasting (30/60/90 day)
- Recurring transaction detection
- Budget alerts
- Obligation calendar

### Infrastructure
- Worker health monitoring
- Backup automation
- Genealogy mode

---

## ✅ Recently Completed

### 2026-01-29
- [x] Iris consciousness framework design
- [x] Documentation restructure (patch 0036)
- [x] Channel protocol + Reality Filter design
- [x] Partnership model defined
- [x] Finance bot fix (patch 0033)

### 2026-01-27
- [x] Grid integration - basic scoring
- [x] Chat mode via API gateway
- [x] Finance auto-import

See `docs/PATCH_HISTORY.md` for full history.
See `docs/archive/COMPLETED.md` for older items.

---

## 🔧 Workflows

### Session Start
```bash
D=~/diag.txt; > "$D"
echo "=== TODO ===" >> "$D"
cat /opt/mythos/docs/TODO.md >> "$D" 2>&1
echo -e "\n\n=== ARCHITECTURE ===" >> "$D"
cat /opt/mythos/docs/ARCHITECTURE.md >> "$D" 2>&1
echo -e "\n\n=== DOCS INDEX ===" >> "$D"
cat /opt/mythos/docs/README.md >> "$D" 2>&1
cat "$D" | xclip -selection clipboard && echo "✓ Copied to clipboard"
```

### Patch Deployment
1. Claude creates `patch_NNNN_description/` with `install.sh`
2. User downloads → copies to `~/Downloads` on Arcturus
3. Patch monitor auto-processes
4. Verify via `/patch_status`

### Patch Verification Template

Every `install.sh` must end with:

```bash
# === VERIFICATION ===
echo ""
echo "=== VERIFICATION ==="
PASS=true

# Check 1: Files exist
if [ ! -f /path/to/expected/file ]; then
    echo "❌ FAIL: Expected file not found"
    PASS=false
else
    echo "✓ File exists"
fi

# Check 2: Content verified
if ! grep -q "expected_string" /path/to/file; then
    echo "❌ FAIL: Expected content not found"
    PASS=false
else
    echo "✓ Content verified"
fi

# Final result
if [ "$PASS" = false ]; then
    echo ""
    echo "⚠ PATCH VERIFICATION FAILED"
    exit 1
fi

echo ""
echo "✓ ALL CHECKS PASSED"
```

---

*This file is auto-committed with each patch. Keep it lean - details go in domain docs.*
