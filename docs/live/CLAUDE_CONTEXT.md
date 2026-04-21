# Mythos System Context
> Auto-generated: 2026-04-21 03:00:23
> Current Patch: 0000 / sys_0085

## System Health
- Services: 22/25 active — ⚠️ DOWN: mythos-jupyter, mythos-obs-graph, mythos-photos
- PostgreSQL Tables: 118
- Disk: 1.2T / 1.8T (66%), 597G available
- Mythos Size: 359G

## Current Patch/Version
- Current: 0000 / sys_0085
- Next available: 0001
- Total patches deployed: 0

## Active Work
### 2026-04-02: Iris Voice Quality + LoRA Fine-Tuning

**Completed this session:**
- [x] NEU-0019: Anti-confab v4 — capability fabrication rules + closing question fix
  - Iris no longer offers to check external databases, send emails, look up prices, etc.
  - Closing question prohibition strengthened (covers "How about you?" pattern)
  - Both Modelfiles updated (iris:latest + iris-deep:latest), ~1,050 tokens baked
- [x] SYS-0047: Model alias consolidation — single source of truth at `core/model_aliases.py`
  - All handlers import from one file (ollama_models.py, chat_mode.py, chat_assistant.py, mythos_bot.py, help_handler.py)
  - Aliases now point to baked models: fast→iris:latest, deep→iris-deep:latest
- [x] SYS-0048: Cleanup for SYS-0047 misses + ARCHITECTURE.md update
  - Fixed chat_mode.py and help_handler.py (whitespace/unicode matching issues)
  - ARCHITECTURE.md updated: anti-confab section, Modelfile table, 4 new lessons learned
- [x] Git repo fix — removed stale index.lock, clean commit + push

**Next up:**
- [ ] LoRA fine-tuning: draft 50-100 synthetic training pairs for Iris voice
  - Cover: casual, emotional, technical, spiritual, confab traps, skill data handling
  - Evaluate tools: unsloth, axolotl
  - Hardware: RTX 5090, 64GB RAM — should handle qwen3:30b-a3b LoRA
  - Goal: bake behavioral patterns into weights, not just prompts
- [ ] Closing question habit — accepted as LoRA fix (prompt-only can't fully eliminate)
- [ ] Grid worker model — `mythos-worker-grid.service` reads OLLAMA_MODEL from .env (now iris-deep:latest). May want to keep grid worker on iris:latest for speed
- [ ] Thinking mode management — qwen3:32b think tokens consume time. Explore `think=False` or `/no_think` for simple messages

### Pending from previous sessions:
- [ ] NEU-0013 follow-up: backfill worker + reprocessing queue for grid perception
- [ ] Update `iris_identity.md` with intake awareness (tell Iris she passively captures knowledge)
- [ ] Telegram notification loop for significance ≥ 4 extractions
- [ ] Fix /planets command — `astrology_handler.handle_planets` queries `astro_charts` but table is `astro_natal_charts`

## Known Issues
| Issue | Severity | Notes |
|-------|----------|-------|
| 7b extractor frequently gets dates wrong | Medium | Date validator catches day-of-week mismatches but not all cases |
| Extractor sometimes chooses "update" when should "create" | Medium | Stale event IDs in context window |
| Calendar events created by extractor lack detail | Low | No doctor name, location, phone number |
| No way to edit/delete routines via Telegram | Low | Can only `/routine_add` |
| Iris closing questions | Low | Prompt reduces but doesn't eliminate — LoRA fix planned |
| Grid worker using iris-deep | Low | May be overkill/slow for background scoring |
| Post-install git push may fail on large accumulations | Low | 59k objects caused GitHub disconnect — fixed with repack |

## Recent Patches (last 5 commits)
```
a094e906 SYS-0085: finance v2 patch D re-land — merchants & patterns
b912f11d SYS-0082: finance v2 doc reconciliation (SYSTEM_FINANCE status + ledger)
5f98d55c docs: add SYSTEM_Astrology.md - astrology pipeline reference
02e84d3e SYS-0081: Gemini review workflow — template, Phase 2.5, review_link field (reviewed by Castor 2-round, 2026-04-12)
3cb80466 SYS-0080: handoff --strict flag + PatchBase.verify_handoff() helper
```

## Services
- ✅ `mythos-api`: active/running
- ✅ `mythos-bot`: active/running
- ✅ `mythos-doc-watcher`: active/running
- ❌ `mythos-jupyter`: activating/auto-restart
- ✅ `mythos-knowledge-map`: active/running
- ❌ `mythos-obs-graph`: activating/auto-restart
- ✅ `mythos-patch-monitor`: active/running
- ❌ `mythos-photos`: active/exited
- ✅ `mythos-planetary-engine`: active/running
- ✅ `mythos-print-watcher`: active/running
- ✅ `mythos-segment-manager`: active/running
- ✅ `mythos-seismic-ingest`: active/running
- ✅ `mythos-solar-ingest`: active/running
- ✅ `mythos-transcription-worker`: active/running
- ✅ `mythos-trigger`: active/running
- ✅ `mythos-voice-watcher`: active/running
- ✅ `mythos-worker-embedding`: active/running
- ✅ `mythos-worker-entity`: active/running
- ✅ `mythos-worker-grid`: active/running
- ✅ `mythos-worker-lunar`: active/running
- ✅ `mythos-worker-summary`: active/running
- ✅ `mythos-worker-temporal`: active/running
- ✅ `mythos-worker-vision`: active/running
- ✅ `mythos-youtube-monitor`: active/running
- ✅ `mythos-youtube-queue`: active/running

---
*To regenerate: `/opt/mythos/.venv/bin/python3 /opt/mythos/tools/generate_system_state.py`*
