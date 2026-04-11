# Stream Segregation — Session Handoff

## What Just Happened

SYS-0001 deployed the Stream Development System:
- Patch monitor now recognizes `NEU-NNNN_`, `LOG-NNNN_`, `MNE-NNNN_`, `SEN-NNNN_`, `SYS-NNNN_` zip files
- Legacy `patch_NNNN_` format still works
- STREAMS.md, STREAMS.json, REQUESTS.md deployed to `/opt/mythos/docs/`
- `stream_status.sh` deployed to `/opt/mythos/docs/streams/`

## What Needs to Happen Next

**Goal:** Map all existing Mythos infrastructure into the five streams so that every directory, table, Neo4j label, and service has a clear owner.

### Diagnostic Dump to Start

Run this at the beginning of the next session:

```bash
D=~/diag.txt; > "$D"

echo "=== DIRECTORY TREE (depth 2) ===" >> "$D"
find /opt/mythos -maxdepth 2 -type d | sort >> "$D" 2>&1

echo -e "\n\n=== POSTGRES TABLES ===" >> "$D"
sudo -u postgres psql -d mythos -c "\dt" >> "$D" 2>&1

echo -e "\n\n=== POSTGRES TABLE ROW COUNTS ===" >> "$D"
sudo -u postgres psql -d mythos -c "
SELECT schemaname, tablename, n_live_tup
FROM pg_stat_user_tables
ORDER BY tablename;" >> "$D" 2>&1

echo -e "\n\n=== NEO4J LABELS ===" >> "$D"
NEO4J_PASS=$(grep NEO4J_PASSWORD /opt/mythos/.env | cut -d= -f2 | tr -d \"\'\ )
cypher-shell -u neo4j -p "$NEO4J_PASS" "CALL db.labels() YIELD label RETURN label ORDER BY label" >> "$D" 2>&1

echo -e "\n\n=== NEO4J RELATIONSHIP TYPES ===" >> "$D"
cypher-shell -u neo4j -p "$NEO4J_PASS" "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType" >> "$D" 2>&1

echo -e "\n\n=== SYSTEMD SERVICES ===" >> "$D"
systemctl list-units --type=service | grep mythos >> "$D" 2>&1

echo -e "\n\n=== TELEGRAM BOT HANDLERS ===" >> "$D"
ls -la /opt/mythos/telegram_bot/handlers/ >> "$D" 2>&1

echo -e "\n\n=== API ROUTES ===" >> "$D"
ls -la /opt/mythos/api/routes/ >> "$D" 2>&1

echo -e "\n\n=== WEB TEMPLATES ===" >> "$D"
ls -la /opt/mythos/web/templates/ >> "$D" 2>&1

echo -e "\n\n=== STREAMS.md ===" >> "$D"
cat /opt/mythos/docs/STREAMS.md >> "$D" 2>&1

echo -e "\n\n=== STREAMS.json ===" >> "$D"
cat /opt/mythos/docs/STREAMS.json >> "$D" 2>&1

cat "$D" | xclip -selection clipboard && echo "✓ Copied to clipboard"
```

### What the Session Should Produce

1. **Updated STREAMS.json** with real `owned_paths`, `owned_tables_pg`, and `owned_neo4j_labels` for each stream
2. **Updated STREAMS.md** with populated ownership tables
3. **A list of ambiguous items** — infrastructure that could belong to multiple streams, for Adge to decide
4. **Stream build plans** — `NEU_PLAN.md`, `LOG_PLAN.md`, `MNE_PLAN.md`, `SEN_PLAN.md` in `/opt/mythos/docs/streams/`

### Stream Assignment Guidelines

- **NEURO:** Consciousness processing, emotional modeling, awareness loops, Arcturian Grid, perception, Iris core intelligence
- **LOGOS:** Language, reasoning, knowledge graphs, ontology, skills, research, prompts
- **MNEMOS:** Memory, conversation history, recall, experience storage, life logging, voice memos
- **SENSUS:** Sensory input, lunar cycles, astrology, weather, calendar, environmental awareness
- **SYS:** Patch system, bot core, API framework, web framework, auth, finance, file management, people/rolodex, document management

### Important Notes

- Don't rename or move any files — just assign ownership
- Some things are genuinely shared (bot.py, api/main.py) — those stay in SYS
- The goal is clarity of ownership, not physical reorganization
- Each stream should know what it owns so Claude sessions can avoid stepping on each other
