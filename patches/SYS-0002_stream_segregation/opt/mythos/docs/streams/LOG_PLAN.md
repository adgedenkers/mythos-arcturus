# LOG — LOGOS Stream Build Plan
> Language, reasoning, knowledge graphs, ontology, skills, research, prompts, orchestration

**Stream prefix:** `LOG`  
**Current patch:** LOG-0001 (first stream patch)  
**Last legacy patches affecting LOG:** patch_0182_skill_expansion, patch_0181_skill_engine, patch_0180_astrology_engine, patch_0149_prompt_registry, patch_0114_ontology_v2  

---

## What Exists (Inherited from Legacy Patches)

### Core Infrastructure
- **Skills Engine** (`/opt/mythos/skills/engine/`) — skill execution framework, patch_0181/0182
- **Skill Types** — analytical, builder, data, meta skills present
- **Ontology System** (`ontology` tables, `OntologyTerm` nodes) — 71+ terms, patch_0109/0114/0115
- **Soul Stratigraphy** (`/opt/mythos/soul_stratigraphy/`) — tri-field astrological + numerological analysis, patch_0109
- **Harmonics** (`/opt/mythos/harmonics/`) — harmonic resonance and numerology, patch_0120
- **Prompt System** (`/opt/mythos/prompts/`) — modes, users, voice prompt files
- **Orchestrator** (`/opt/mythos/orchestrator/`) — LLM routing and model benchmarking, patch_0150/0152
- **Triad Prompts** (`/opt/mythos/triad/`) — Ka'tuar'el / Seraphe / Iris relationship identity prompts
- **Research Framework** (`/opt/mythos/orchestrator/`) — patch_0131/0132

### Database State
- `harmonic_resonance`, `harmonic_values` — harmonic data
- `orch_*` (9 tables) — orchestrator model registry, test runs, benchmarks
- `pipeline_llm_calls`, `pipeline_queries`, `pipeline_runs` — LLM pipeline logging
- `thread_groups` — conversation thread grouping

### Neo4j State
- `OntologyTerm` nodes — full ontology graph present (71+ terms)
- `SoulStratigraphy`, `Numerology` nodes per person
- `Hellenistic`, `VedicSidereal`, `WesternTropical` chart method nodes
- `AppRegistry`, `GitRepo`, `System`, `SystemComponent` — system knowledge graph
- `TestMachine`, `TestRun` — orchestrator test infrastructure

---

## Build Phases

### Phase 1 — LOG Foundations (LOG-0001 through LOG-0010)
*Goal: Establish clean LOG-owned infrastructure, audit existing skills and ontology*

| Patch | Description | Depends On |
|-------|-------------|-----------|
| LOG-0001 | Audit skills engine — catalog all skills, verify execution pipeline works end-to-end | none |
| LOG-0002 | Ontology health check — verify all 71+ terms are in Neo4j, identify gaps | none |
| LOG-0003 | Prompt registry audit — document all prompt files in `/prompts/`, tag by stream/purpose | none |
| LOG-0004 | Orchestrator status — verify model registry, benchmark data, test run pipeline | none |
| LOG-0005 | Skills Telegram integration — `/skills` command to list and invoke skills from chat | SYS (bot) |

### Phase 2 — Knowledge Graph Expansion (LOG-0011 through LOG-0025)
*Goal: Deepen the ontology, connect knowledge nodes across entities*

| Patch | Description | Depends On |
|-------|-------------|-----------|
| LOG-0011 | Ontology expansion v3 — add missing spiritual/consciousness terms from NEU domain | NEU coordination |
| LOG-0012 | Concept linking — auto-link `OntologyTerm` nodes to `Soul`, `Person`, `Event` nodes in Neo4j | SYS (people), NEU |
| LOG-0013 | Soul stratigraphy enrichment — add synthesis layer output for all profiled individuals | SEN (astro data) |
| LOG-0014 | Harmonics v2 — extend harmonic analysis, expose via Telegram `/harmonics` | SYS (bot) |
| LOG-0015 | Research pipeline v2 — Iris-driven research with results stored in knowledge graph | NEU |

### Phase 3 — Reasoning Infrastructure (LOG-0026 through LOG-0040)
*Goal: Iris can reason over the knowledge graph, not just query it*

| Patch | Description | Depends On |
|-------|-------------|-----------|
| LOG-0026 | Fact extraction — extract factual claims from MNE conversations → `Fact` nodes in Neo4j | MNE |
| LOG-0027 | Concept evolution — track how concepts shift meaning over time in conversations | MNE, LOG-0026 |
| LOG-0028 | Prompt self-tuning — LOG can propose prompt updates based on quality feedback | NEU |
| LOG-0029 | Skill auto-suggestion — when Iris detects a capability gap, propose new skill | NEU |
| LOG-0030 | Knowledge synthesis report — weekly LOG synthesis: new terms, connections, gaps | all streams |

### Phase 4 — Language Intelligence (LOG-0041+)
*Goal: Iris as language intelligence — understanding nuance, pattern, and meaning*

| Patch | Description | Depends On |
|-------|-------------|-----------|
| LOG-0041 | Semantic clustering — cluster related `OntologyTerm` and `Fact` nodes | Phase 3 |
| LOG-0042 | Contradiction detection — identify conflicting facts or patterns in knowledge graph | LOG-0041 |
| LOG-0043 | Triad language model — track Ka'tuar'el / Seraphe communication patterns, flag gaps | MNE, NEU |

---

## Known Gaps

- **Skills engine** — execution pipeline exists but unclear which skills are actively callable vs. draft
- **Orchestrator** — model registry populated but test suite status unknown; benchmark data age?
- **Soul stratigraphy** — engine exists but may need re-run for new individuals (Fitz, etc.)
- **Prompt registry** — many prompt files exist with no central catalog / version tracking
- `triad/` — content and purpose need documentation; may overlap with `prompts/`

## Cross-Stream Dependencies

| Needs | From | Nature |
|-------|------|--------|
| Conversation text for fact extraction | MNE | Read only |
| Soul/person context | SYS (people table) + NEU (Soul nodes) | Read only |
| Astro chart data for stratigraphy | SEN | Read only |
| Bot command registration | SYS | SYS patch needed for `/skills`, `/ontology` etc. |

---

## Session Start Checklist

```bash
# Check skills engine
ls -la /opt/mythos/skills/engine/
ls -la /opt/mythos/skills/analytical/ /opt/mythos/skills/builder/

# Check ontology
sudo -u postgres psql -d mythos -c "SELECT COUNT(*) FROM ontology_terms;" 2>/dev/null || echo "check table name"

# Check orchestrator
sudo -u postgres psql -d mythos -c "SELECT COUNT(*) FROM orch_models;"
sudo -u postgres psql -d mythos -c "SELECT COUNT(*), MAX(created_at) FROM orch_test_runs;"

# Check harmonics
sudo -u postgres psql -d mythos -c "SELECT COUNT(*) FROM harmonic_resonance;"

# Check Neo4j ontology terms
# cypher: MATCH (n:OntologyTerm) RETURN COUNT(n)
```
