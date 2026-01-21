# Sprint 1 Quick Reference Card

## One-Command Deployment

```bash
./deploy_sprint_1.sh
```

**Done.** That's it. Everything else is automatic.

---

## What Gets Deployed

| Component | Change | Location |
|-----------|--------|----------|
| **Database** | `media_files` table + indexes | PostgreSQL `mythos` |
| **Filesystem** | Media storage directory | `/opt/mythos/media/` |
| **API** | 5 new endpoints | `/opt/mythos/api/main.py` |
| **Bot** | Photo handler + `/photos` command | `/opt/mythos/telegram_bot/mythos_bot.py` |

---

## New Endpoints Added

```
POST /media/upload              - Store photo metadata
GET  /media/recent              - List user's recent photos
GET  /media/{media_id}          - Get photo details
GET  /media/search/tag/{tag}    - Search by tag
POST /media/tag/add             - Add user tag to photo
```

---

## Test Sequence

```
Telegram:
  /start
  [send photo]
  /photos

API:
  curl https://mythos-api.denkers.co/docs

Database:
  psql -U postgres -d mythos -c "SELECT COUNT(*) FROM media_files"
```

---

## If Something Breaks

### API won't start
```bash
# Check syntax
python3 -m py_compile /opt/mythos/api/main.py

# View logs
sudo journalctl -u mythos-api -n 50

# Restore backup
cp /opt/mythos/api/main.py.backup.* /opt/mythos/api/main.py
sudo systemctl restart mythos-api
```

### Bot won't start
```bash
# Check syntax
python3 -m py_compile /opt/mythos/telegram_bot/mythos_bot.py

# View logs
sudo journalctl -u mythos-telegram-bot -n 50

# Restore backup
cp /opt/mythos/telegram_bot/mythos_bot.py.backup.* \
   /opt/mythos/telegram_bot/mythos_bot.py
sudo systemctl restart mythos-telegram-bot
```

### Database issues
```sql
-- Check if table exists
\dt media_files

-- Re-run migration if needed
\i 001_media_storage_migration.sql
```

---

## All Backups Are Automatic

Every script creates timestamped backups:
- `main.py.backup.20260121_153045`
- `mythos_bot.py.backup.20260121_153045`

Find them with:
```bash
ls -lat /opt/mythos/api/*.backup.*
ls -lat /opt/mythos/telegram_bot/*.backup.*
```

---

## Verify Deployment

```bash
# Services running?
systemctl status mythos-api mythos-telegram-bot

# Endpoints present?
grep -q "def upload_media" /opt/mythos/api/main.py && echo "✓ API patched"
grep -q "def handle_photo" /opt/mythos/telegram_bot/mythos_bot.py && echo "✓ Bot patched"

# Table exists?
psql -U postgres -d mythos -c "\dt media_files" | grep -q media_files && echo "✓ DB migrated"

# Directory writable?
[ -w /opt/mythos/media ] && echo "✓ Media dir ready"
```

---

## Design Principles Applied

✓ **Right tool for the job**
- PostgreSQL for metadata (searchable, transactional)
- Filesystem for files (efficient, no blob overhead)
- JSONB for analysis data (flexible schema)
- TEXT[] for tags (simple, GIN-indexed)

✓ **Start simple, expand if needed**
- Entity links in JSONB → dedicated table only if complex queries needed
- Background processing stubbed → actual analysis in Sprint 3
- Tag arrays → junction table commented out, add if necessary

✓ **Analyze without assumptions**
- No premature optimization
- Every index has a specific query pattern
- Nullable relationships (photos can exist standalone)

---

## Time Estimates

| Step | Time |
|------|------|
| Database migration | 5 min |
| Directory setup | 2 min |
| API patching | 10 min |
| Bot installation | 5 min |
| Service restarts | 3 min |
| Testing | 15 min |
| **Total** | **~40 min** |

---

## What Comes Next

**Sprint 2: Conversational Awareness** (2-3 hours)
- LLM references "that photo you sent"
- Context includes recent photos
- Photo search in conversation

**Sprint 3: Vision Analysis** (4-6 hours)
- Ollama + Llama Vision integration
- Automatic tagging
- Spiritual symbol detection
- Entity linking to Neo4j

---

## Critical Notes

⚠️ **Handler order matters** - In bot code, PHOTO handler must come before TEXT handler

⚠️ **Permissions** - Media directory needs to be writable by bot process

⚠️ **API migration required** - Database must be migrated before API can store photos

✓ **Sovereign** - All photos stored locally, never uploaded to external services

✓ **Safe** - All changes are additions, backups automatic, rollback trivial

---

## Support Commands

```bash
# Tail all logs
sudo journalctl -f -u mythos-api -u mythos-telegram-bot

# Check what's listening
sudo netstat -tulpn | grep -E ':(8000|443)'

# Database connections
psql -U postgres -d mythos -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'mythos';"

# Disk space for media
df -h /opt/mythos/media

# Service status
systemctl status mythos-api mythos-telegram-bot --no-pager

# Recent photos
psql -U postgres -d mythos -c "SELECT * FROM recent_photos LIMIT 5;"
```

---

**Deployment Package:** 10 files ready  
**Estimated Time:** 40 minutes  
**Risk Level:** Low (additions only, automatic backups)  
**Rollback:** Trivial (restore .backup files)  

**GO/NO-GO:** ✓ Ready for production deployment
