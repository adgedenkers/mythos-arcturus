# Sprint 1 Deployment Scripts

Three deployment scripts, choose your approach:

## Quick Start (Recommended)

**Run everything in one command:**

```bash
./deploy_sprint_1.sh
```

This master script runs all steps in order:
1. Database migration
2. Media directory setup
3. API patching
4. Bot installation
5. Service restarts
6. Verification tests

Creates a detailed log file: `deployment_YYYYMMDD_HHMMSS.log`

---

## Manual Deployment (Step by Step)

If you prefer control over each step:

### 1. Database Migration

```bash
psql -U postgres -d mythos -f 001_media_storage_migration.sql
```

Verify:
```sql
\dt media_files
SELECT * FROM recent_photos LIMIT 1;
```

### 2. Media Directory

```bash
sudo mkdir -p /opt/mythos/media
sudo chown mythos:mythos /opt/mythos/media
sudo chmod 755 /opt/mythos/media
```

### 3. Patch API

```bash
./patch_api_with_media.sh
```

This intelligently patches `/opt/mythos/api/main.py`:
- Adds imports
- Adds Pydantic models
- Adds 5 media endpoints
- Adds helper function
- Creates backup with timestamp

### 4. Install Bot

```bash
./install_bot_with_photos.sh
```

This replaces `/opt/mythos/telegram_bot/mythos_bot.py`:
- Backs up original
- Installs photo-enabled version
- Validates Python syntax
- Optionally restarts service

### 5. Restart Services

```bash
sudo systemctl restart mythos-api
sudo systemctl restart mythos-telegram-bot
```

### 6. Verify

```bash
# Check services
sudo systemctl status mythos-api
sudo systemctl status mythos-telegram-bot

# Check logs
sudo journalctl -u mythos-api -f
sudo journalctl -u mythos-telegram-bot -f

# Test database
psql -U postgres -d mythos -c "SELECT COUNT(*) FROM media_files"

# Check API docs
curl https://mythos-api.denkers.co/docs
```

---

## Script Details

### `deploy_sprint_1.sh`
**Master orchestration script**
- Runs all deployment steps automatically
- Creates detailed log file
- Checks prerequisites
- Verifies results
- Handles errors gracefully

**Usage:**
```bash
./deploy_sprint_1.sh
```

**What it does:**
- ✓ Checks all required files present
- ✓ Applies database migration
- ✓ Creates media directory with correct permissions
- ✓ Patches API with media endpoints
- ✓ Installs photo-enabled bot
- ✓ Restarts both services
- ✓ Runs verification tests
- ✓ Provides next steps

---

### `patch_api_with_media.sh`
**Intelligent API patcher**
- Backs up original file
- Adds imports if not present
- Inserts Pydantic models
- Adds 5 media endpoints
- Adds helper function
- Validates Python syntax
- Rolls back on error

**Usage:**
```bash
./patch_api_with_media.sh
```

**What it modifies:**
- `/opt/mythos/api/main.py`

**Backup location:**
- `/opt/mythos/api/main.py.backup.YYYYMMDD_HHMMSS`

**Safe to re-run:** Yes (detects if already patched)

---

### `install_bot_with_photos.sh`
**Bot replacement script**
- Backs up original bot
- Validates new bot syntax
- Installs photo-enabled version
- Verifies installation
- Optionally restarts service
- Creates media directory

**Usage:**
```bash
./install_bot_with_photos.sh
```

**Requirements:**
- Must be run from directory containing `mythos_bot_with_photos.py`

**What it modifies:**
- `/opt/mythos/telegram_bot/mythos_bot.py`

**Backup location:**
- `/opt/mythos/telegram_bot/mythos_bot.py.backup.YYYYMMDD_HHMMSS`

**Safe to re-run:** Yes (creates new backup each time)

---

## Troubleshooting

### "Permission denied" errors

Run with sudo or as mythos user:
```bash
sudo -u mythos ./deploy_sprint_1.sh
```

### "File not found" errors

Make sure you're in the deployment directory:
```bash
cd /path/to/outputs
ls -la *.sh
./deploy_sprint_1.sh
```

### API won't restart

Check for syntax errors:
```bash
python3 -m py_compile /opt/mythos/api/main.py
```

View detailed errors:
```bash
sudo journalctl -u mythos-api -n 50
```

### Bot won't restart

Check for syntax errors:
```bash
python3 -m py_compile /opt/mythos/telegram_bot/mythos_bot.py
```

View detailed errors:
```bash
sudo journalctl -u mythos-telegram-bot -n 50
```

### Database migration fails

Check PostgreSQL connection:
```bash
psql -U postgres -d mythos -c "SELECT version();"
```

Run migration manually:
```bash
psql -U postgres -d mythos < 001_media_storage_migration.sql
```

---

## Rollback

If something goes wrong, each script creates timestamped backups:

### Rollback API:
```bash
# Find backup
ls -la /opt/mythos/api/main.py.backup.*

# Restore
cp /opt/mythos/api/main.py.backup.YYYYMMDD_HHMMSS /opt/mythos/api/main.py

# Restart
sudo systemctl restart mythos-api
```

### Rollback Bot:
```bash
# Find backup
ls -la /opt/mythos/telegram_bot/mythos_bot.py.backup.*

# Restore
cp /opt/mythos/telegram_bot/mythos_bot.py.backup.YYYYMMDD_HHMMSS \
   /opt/mythos/telegram_bot/mythos_bot.py

# Restart
sudo systemctl restart mythos-telegram-bot
```

### Rollback Database:
```sql
-- Remove media_files table (WARNING: deletes all photo records)
DROP TABLE IF EXISTS media_files CASCADE;
```

---

## Testing After Deployment

### 1. Test Photo Upload

Open Telegram:
```
/start
[Send a photo]
```

Expected response:
```
📸 Photo received and stored
🆔 abc12345...
📐 1920x1080 (landscape)
💾 245KB

⏳ Analyzing in background...
```

### 2. Test Photo Listing

```
/photos
```

Expected response:
```
📸 Your Recent Photos:

1. ✅ 2026-01-21T15:30:45
   Size: 1920x1080

Send more photos anytime!
```

### 3. Test API Endpoints

```bash
# Get recent photos
curl -H "X-API-Key: YOUR_KEY" \
  "https://mythos-api.denkers.co/media/recent?user_id=YOUR_TELEGRAM_ID"

# Get API docs (check for /media/* endpoints)
curl https://mythos-api.denkers.co/docs
```

### 4. Check Database

```sql
-- View uploaded photos
SELECT id, filename, uploaded_at, width, height 
FROM media_files 
ORDER BY uploaded_at DESC 
LIMIT 5;

-- Check view
SELECT * FROM recent_photos;
```

---

## File Manifest

**Deployment Scripts:**
- `deploy_sprint_1.sh` - Master deployment script
- `patch_api_with_media.sh` - API patcher
- `install_bot_with_photos.sh` - Bot installer

**Source Files:**
- `001_media_storage_migration.sql` - Database schema
- `mythos_bot_with_photos.py` - Photo-enabled bot
- `api_media_endpoints.py` - Reference for API endpoints

**Documentation:**
- `SPRINT_1_DEPLOYMENT.md` - Detailed manual
- `sprint_1_summary.json` - Complete metadata
- `mythos_system_analysis.md` - Full system analysis
- `DEPLOYMENT_SCRIPTS_README.md` - This file

---

## Next Steps

After successful deployment:

1. **Test with real photos** - Send various images, check storage
2. **Monitor logs** - Watch for any errors or issues
3. **Verify data flow** - Check database records match uploads
4. **Sprint 2 Ready** - Conversational awareness implementation
5. **Sprint 3 Ready** - Vision model integration

---

## Support

**Check logs:**
```bash
sudo journalctl -u mythos-api -f
sudo journalctl -u mythos-telegram-bot -f
```

**View deployment log:**
```bash
cat deployment_YYYYMMDD_HHMMSS.log
```

**Database check:**
```bash
psql -U postgres -d mythos
```

**Restore from backup:**
All scripts create timestamped backups automatically.

---

**Sprint 1 Goal:** Accept photos as input, store and log appropriately ✓

Estimated deployment time: **~40 minutes**
