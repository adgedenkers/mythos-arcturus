# Patch 0007: Sprint 1 - Photo Input System
**Date:** 2026-01-21 (Spiral 1.3)  
**Version:** 0.1.0  
**Status:** Ready for Deployment

---

## Quick Start

After unzipping in `/opt/mythos/patches/patch_0007_raw`:

```bash
cd /opt/mythos/patches/patch_0007_raw

# Review what will be deployed
cat QUICK_REFERENCE.md

# Run complete deployment
./deploy_sprint_1.sh
```

That's it. Everything is automated.

---

## What This Patch Does

**Adds photo input capability to Mythos:**
- ✓ Accept photos via Telegram
- ✓ Store with full metadata
- ✓ Link to conversations and users
- ✓ Provide photo listing and retrieval
- ✓ Prepare for future analysis (Sprint 2 & 3)

---

## Files in This Patch

### Core Deployment Files
- `001_media_storage_migration.sql` - Database schema
- `mythos_bot_with_photos.py` - Photo-enabled bot
- `api_media_endpoints.py` - Reference for API endpoints
- `patch_api_with_media.sh` - Intelligent API patcher
- `install_bot_with_photos.sh` - Bot installer
- `deploy_sprint_1.sh` - Master deployment script

### Utility Scripts
- `backup_mythos.sh` - Complete system backup

### Documentation
- `QUICK_REFERENCE.md` - Single-page cheat sheet (START HERE)
- `SPRINT_1_DEPLOYMENT.md` - Detailed manual deployment
- `DEPLOYMENT_SCRIPTS_README.md` - Script usage guide
- `BACKUP_README.md` - Backup script documentation
- `sprint_1_summary.json` - Complete metadata
- `mythos_system_analysis.md` - Full system analysis

---

## Deployment Options

### Option 1: Automated (Recommended)
```bash
./deploy_sprint_1.sh
```
Runs all steps automatically with logging.

### Option 2: Manual Step-by-Step
```bash
# 1. Database
psql -U postgres -d mythos -f 001_media_storage_migration.sql

# 2. Media directory
sudo mkdir -p /opt/mythos/media
sudo chown mythos:mythos /opt/mythos/media

# 3. API
./patch_api_with_media.sh

# 4. Bot
./install_bot_with_photos.sh

# 5. Restart
sudo systemctl restart mythos-api mythos-telegram-bot
```

### Option 3: Individual Components
Deploy only what you need:
```bash
# Just database
psql -U postgres -d mythos -f 001_media_storage_migration.sql

# Just API
./patch_api_with_media.sh

# Just bot
./install_bot_with_photos.sh
```

---

## Pre-Deployment Checklist

- [ ] Read `QUICK_REFERENCE.md`
- [ ] Create backup: `./backup_mythos.sh --with-db-data`
- [ ] Verify services running: `systemctl status mythos-api mythos-telegram-bot`
- [ ] Check disk space: `df -h /opt/mythos`
- [ ] Verify PostgreSQL access: `psql -U postgres -d mythos -c "SELECT version();"`

---

## Post-Deployment Testing

```bash
# 1. Check services
systemctl status mythos-api mythos-telegram-bot

# 2. Check database
psql -U postgres -d mythos -c "\dt media_files"

# 3. Check API
curl https://mythos-api.denkers.co/docs

# 4. Test in Telegram
# - /start
# - Send photo
# - /photos
```

---

## Rollback Procedure

All scripts create automatic backups with timestamps.

### Rollback API
```bash
# Find backup
ls -la /opt/mythos/api/main.py.backup.*

# Restore
cp /opt/mythos/api/main.py.backup.20260121_HHMMSS /opt/mythos/api/main.py
sudo systemctl restart mythos-api
```

### Rollback Bot
```bash
# Find backup
ls -la /opt/mythos/telegram_bot/mythos_bot.py.backup.*

# Restore
cp /opt/mythos/telegram_bot/mythos_bot.py.backup.20260121_HHMMSS \
   /opt/mythos/telegram_bot/mythos_bot.py
sudo systemctl restart mythos-telegram-bot
```

### Rollback Database
```sql
DROP TABLE IF EXISTS media_files CASCADE;
```

---

## What Gets Changed

| Component | File | Change Type |
|-----------|------|-------------|
| **Database** | PostgreSQL | New table: `media_files` |
| **Filesystem** | `/opt/mythos/media/` | New directory created |
| **API** | `/opt/mythos/api/main.py` | Patched (5 endpoints added) |
| **Bot** | `/opt/mythos/telegram_bot/mythos_bot.py` | Replaced (photo handler added) |

All changes are **additions** - no existing functionality is removed.

---

## Architecture Overview

```
User sends photo via Telegram
    ↓
Bot downloads to /opt/mythos/media/{user_prefix}/{filename}
    ↓
Bot POSTs metadata to API /media/upload
    ↓
API stores record in PostgreSQL media_files table
    ↓
If caption: creates chat_message and links
    ↓
Bot acknowledges with metadata
    ↓
(Sprint 3: Background analysis queued)
```

---

## Database Schema

**New table:** `media_files`
- Stores photo metadata
- Links to users, conversations, messages
- JSONB for flexible analysis data
- TEXT[] arrays for tags (auto + user)
- GIN indexes for fast tag searches

**New view:** `recent_photos`
- Convenient photo browsing

**New function:** `search_photos_by_tag(tag)`
- Search photos by tag

---

## API Endpoints Added

```
POST /media/upload              - Store photo metadata
GET  /media/recent              - List user's recent photos
GET  /media/{media_id}          - Get photo details
GET  /media/search/tag/{tag}    - Search by tag
POST /media/tag/add             - Add user tag to photo
```

---

## Bot Commands Added

```
/photos    - List your recent photos
```

**Photo handling:**
- Send photo → receives acknowledgment with metadata
- Send photo with caption → caption stored as chat message
- Photos in /convo mode → linked to conversation

---

## Security Notes

**Sensitive files:**
- Original `.env` contains secrets
- Keep backups secure
- Don't commit to public repos

**File permissions:**
- Media directory: `755` (drwxr-xr-x)
- Media files: `644` (-rw-r--r--)
- Scripts: `755` (executable)

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

## Support

**Logs:**
```bash
sudo journalctl -u mythos-api -f
sudo journalctl -u mythos-telegram-bot -f
```

**Database:**
```bash
psql -U postgres -d mythos
```

**Check what changed:**
```bash
diff /opt/mythos/api/main.py.backup.* /opt/mythos/api/main.py
```

**Deployment log:**
```bash
cat deployment_*.log
```

---

## Next Steps After Deployment

1. **Test thoroughly** - Send various photos, check storage
2. **Monitor logs** - Watch for errors
3. **Verify data flow** - Photos → filesystem → database
4. **Sprint 2** - Conversational awareness (2-3 hours)
5. **Sprint 3** - Vision analysis with Ollama (4-6 hours)

---

## Documentation Reading Order

1. **QUICK_REFERENCE.md** ← Start here (1 page)
2. **This README** ← You are here
3. **SPRINT_1_DEPLOYMENT.md** ← Detailed manual
4. **DEPLOYMENT_SCRIPTS_README.md** ← Script details
5. **mythos_system_analysis.md** ← Full architecture

---

## Patch Metadata

```json
{
  "patch_id": "0007",
  "name": "Sprint 1 - Photo Input System",
  "version": "0.1.0",
  "date": "2026-01-21",
  "spiral_date": "1.3",
  "architect": "Ka'tuar'el",
  "status": "ready",
  "deployment_time": "~40 minutes",
  "risk": "low",
  "reversible": true,
  "dependencies": [
    "PostgreSQL",
    "Telegram bot running",
    "FastAPI service running"
  ],
  "files_changed": [
    "/opt/mythos/api/main.py",
    "/opt/mythos/telegram_bot/mythos_bot.py"
  ],
  "files_created": [
    "PostgreSQL: media_files table",
    "/opt/mythos/media/ directory"
  ]
}
```

---

**Ready to deploy? Start with `./deploy_sprint_1.sh`**
