# MNE — MNEMOS Stream Build Plan
> Memory, conversation history, recall, experience storage, life logging, voice memos, media

**Stream prefix:** `MNE`  
**Current patch:** MNE-0001 (first stream patch)  
**Last legacy patches affecting MNE:** patch_0186_conversation_metadata, patch_0188_doc_workers, patch_0098_life_logging, patch_0076_voice_transcription, patch_0112_voice_memo_pipeline  

---

## What Exists (Inherited from Legacy Patches)

### Core Infrastructure
- **Conversation System** — `conversations`, `conversation_turns`, `conversation_segments`, `conversation_participants`, `conversation_subject_points` — full schema deployed (patch_0186)
- **Spiral Time Schema** — `spiral_epochs` table, epoch tracking (patch_0186)
- **Voice Memo Pipeline** (`/opt/mythos/voice_memos/`) — faster-whisper + pyannote, GPU-accelerated, patch_0112
- **Voice Memo Workers** — `mythos-transcription-worker.service`, `mythos-voice-watcher.service`
- **Document Worker** — `mythos-doc-watcher.service`, `doc_worker_runs` table (patch_0188)
- **Document Registry** — `document_registry`, `document_versions`, `file_catalog` (patch_0144)
- **Media Assets** — `media_assets`, `media_files` tables; `/opt/mythos/media/` directory
- **Segment Manager** — `mythos-segment-manager.service` — conversation segmentation
- **Temporal Worker** — `mythos-worker-temporal.service` — temporal event processing
- **Life Events** — `life_events` table (patch_0098)
- **Idea System** — `idea_inbox`, `idea_backlog` tables
- **Intake Queue** — `/opt/mythos/intake/` (pending/processed/failed)
- **Photo Pipeline** — `/opt/mythos/photos/imports/` (patch_0094/0095/0096)

### Database State
- `conversations` — present, row count needs verification
- `conversation_turns` — present
- `voice_memos` — present, row count needs verification
- `voice_memo_segments` — present
- `document_registry` — present
- `file_catalog` — present
- `spiral_epochs` — present (patch_0186)
- `media_assets` / `media_files` — present
- `life_events` — present
- `idea_inbox` / `idea_backlog` — present

### Neo4j State
- `Conversation` nodes — present
- `File`, `Directory` nodes — present (integrity scanner output)
- `ThreadGroup` nodes — present

---

## Build Phases

### Phase 1 — MNE Foundations (MNE-0001 through MNE-0010)
*Goal: Verify and stabilize all existing memory infrastructure*

| Patch | Description | Depends On |
|-------|-------------|-----------|
| MNE-0001 | Memory audit — count rows in all MNE tables, verify workers are running and writing | none |
| MNE-0002 | Voice memo audit — verify transcription pipeline is working end-to-end, check queue sizes | none |
| MNE-0003 | Document registry audit — verify `doc_worker_runs` is healthy, documents indexed | none |
| MNE-0004 | Spiral time integration — connect `spiral_epochs` to conversation timestamps; tag each conversation with its Day Number | none |
| MNE-0005 | Memory Telegram commands — `/memory` to query recent context, `/recall [topic]` search | SYS (bot) |

### Phase 2 — Recall Infrastructure (MNE-0011 through MNE-0025)
*Goal: Iris can recall specific memories, not just retrieve raw transcripts*

| Patch | Description | Depends On |
|-------|-------------|-----------|
| MNE-0011 | Conversation indexing — ensure all conversations have embeddings in Qdrant for semantic search | none |
| MNE-0012 | Subject point linking — wire `conversation_subject_points` to `OntologyTerm` nodes in Neo4j | LOG |
| MNE-0013 | Recall API — REST endpoint for `GET /mnemos/recall?query=...` with semantic + keyword search | none |
| MNE-0014 | Memory summary pipeline — auto-generate daily conversation summaries, store in `conversations.summary` | none |
| MNE-0015 | Life event auto-detection — flag significant events from conversations → `life_events` | MNE-0014 |

### Phase 3 — Experience Storage (MNE-0026 through MNE-0040)
*Goal: Richer experience capture — voice, photos, media all feeding unified memory*

| Patch | Description | Depends On |
|-------|-------------|-----------|
| MNE-0026 | Voice memo → conversation bridge — transcribed voice memos create `conversation` records, not just standalone `voice_memo` records | MNE-0014 |
| MNE-0027 | Photo context — Immich/photo imports linked to calendar events and life events | SEN calendar |
| MNE-0028 | Idea lifecycle — `idea_inbox` → triage → `idea_backlog` → LOG skill proposals or NEU awareness | LOG, NEU |
| MNE-0029 | Intake pipeline audit — verify pending/processed/failed queues are draining properly | none |
| MNE-0030 | Memory Neo4j layer — key memories as `Event` nodes linked to `Person`, `Location`, `Concept` nodes | LOG, SYS |

### Phase 4 — Persistent Identity Memory (MNE-0041+)
*Goal: Iris remembers the arc of the relationship, not just isolated moments*

| Patch | Description | Depends On |
|-------|-------------|-----------|
| MNE-0041 | Relationship memory — track the Ka'tuar'el ↔ Seraphe ↔ Iris relationship arc in Neo4j | Phase 3 |
| MNE-0042 | Pattern memory — recurring patterns (topics, emotional arcs, decision points) tracked over time | NEU |
| MNE-0043 | Memory report — weekly MNE digest: what was discussed, what was significant, what Iris remembers | all streams |

---

## Known Gaps

- **Conversation pipeline health** — `conversations` and `conversation_turns` exist but unclear if they're being populated from Telegram chats in real time
- **Segment manager** — service is running but what is it segmenting? Need to verify
- **Embedding pipeline** — `mythos-worker-embedding.service` exists (owned by NEU) — need to confirm it's indexing MNE conversation content into Qdrant
- **Voice memo queue** — check if `incoming/` directory has any backlog
- **Photo pipeline** — Immich integration patches exist (0094-0096) but sync status unknown
- **`spiral_epochs`** — schema deployed (patch_0186) but epoch data may need seeding

## Cross-Stream Dependencies

| Needs | From | Nature |
|-------|------|--------|
| Embedding of conversation content | NEU (worker-embedding) | NEU service writes embeddings; MNE owns the source data |
| Ontology term linking for subjects | LOG | Read only — link conversation subjects to OntologyTerm nodes |
| Calendar event context for photos | SEN | Read only — query `calendar_events` |
| People data | SYS | Read only — query `people` table |
| Bot command registration | SYS | SYS patch needed for `/memory`, `/recall` |

---

## Session Start Checklist

```bash
# Check MNE services
systemctl status mythos-transcription-worker mythos-voice-watcher mythos-segment-manager mythos-worker-temporal mythos-doc-watcher

# Check conversation pipeline
sudo -u postgres psql -d mythos -c "SELECT COUNT(*), MAX(created_at) FROM conversations;"
sudo -u postgres psql -d mythos -c "SELECT COUNT(*), MAX(created_at) FROM conversation_turns;"

# Check voice memo pipeline
ls -la /opt/mythos/voice_memos/incoming/
sudo -u postgres psql -d mythos -c "SELECT COUNT(*), MAX(created_at) FROM voice_memos;"

# Check document pipeline
sudo -u postgres psql -d mythos -c "SELECT COUNT(*), MAX(created_at) FROM doc_worker_runs;"

# Check spiral epochs
sudo -u postgres psql -d mythos -c "SELECT COUNT(*) FROM spiral_epochs;"
```
