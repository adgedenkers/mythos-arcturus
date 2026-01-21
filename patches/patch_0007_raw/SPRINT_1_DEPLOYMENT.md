# Sprint 1 Deployment Guide
## Mythos Visual Input - Phase 1: Accept Photos as Input

**Sprint Goal:** Enable photo upload via Telegram, store with metadata, acknowledge receipt

---

## Prerequisites

- PostgreSQL access (existing mythos database)
- Telegram bot running
- FastAPI service running
- File system access at `/opt/mythos/media/`

---

## Deployment Steps

### 1. Database Migration

Apply the new schema for media storage:

```bash
# Connect to PostgreSQL
psql -U postgres -d mythos

# Run migration
\i 001_media_storage_migration.sql

# Verify tables created
\dt media_files
\d media_files

# Test view
SELECT * FROM recent_photos LIMIT 1;

# Test function
SELECT * FROM search_photos_by_tag('test');
```

Expected output: Tables and indexes created, no errors.

---

### 2. Create Media Storage Directory

```bash
# Create base media directory with proper permissions
sudo mkdir -p /opt/mythos/media
sudo chown mythos:mythos /opt/mythos/media
sudo chmod 755 /opt/mythos/media

# Verify
ls -la /opt/mythos/ | grep media
```

Expected output: `drwxr-xr-x mythos mythos media`

---

### 3. Update FastAPI Service

**Option A: Add endpoints to existing api/main.py**

```bash
# Backup existing
cp /opt/mythos/api/main.py /opt/mythos/api/main.py.backup.$(date +%Y%m%d_%H%M%S)

# Open main.py and add the media endpoints from api_media_endpoints.py
# They should go after the existing endpoint definitions, before the Plaid section
```

**Key additions:**
- Import statements at top (BackgroundTasks, etc.)
- MediaUploadRequest/Response models
- `/media/upload` endpoint
- `/media/recent` endpoint
- `/media/{media_id}` endpoint
- `/media/search/tag/{tag}` endpoint
- `/media/tag/add` endpoint
- `get_recent_conversation_with_media()` helper function

**Option B: Test first with separate file**

```bash
# Copy the api_media_endpoints.py content into a test file
# Import it in main.py with: from media_endpoints import *
```

**Restart FastAPI:**

```bash
# If using systemd
sudo systemctl restart mythos-api

# Or if running manually
# Ctrl+C and restart: uvicorn api.main:app --host 0.0.0.0 --port 8000
```

**Verify endpoints:**

```bash
# Check API docs
curl https://mythos-api.denkers.co/docs

# Should show new /media/* endpoints
```

---

### 4. Update Telegram Bot

**Backup existing:**

```bash
cp /opt/mythos/telegram_bot/mythos_bot.py /opt/mythos/telegram_bot/mythos_bot.py.backup.$(date +%Y%m%d_%H%M%S)
```

**Replace with updated version:**

```bash
# Copy mythos_bot_with_photos.py to mythos_bot.py
cp mythos_bot_with_photos.py /opt/mythos/telegram_bot/mythos_bot.py
```

**Key changes in new version:**
- Added `MEDIA_BASE_PATH` constant
- Added `handle_photo()` function
- Added `photos_command()` function
- Added photo handler registration in `main()`
- Updated help text to mention photos

**Restart bot:**

```bash
# If using systemd
sudo systemctl restart mythos-telegram-bot

# Or if running manually
# Ctrl+C and restart: python3 /opt/mythos/telegram_bot/mythos_bot.py
```

**Verify bot is running:**

```bash
# Check logs
sudo journalctl -u mythos-telegram-bot -f

# Or if running manually, look for:
# 🤖 Mythos Telegram Bot starting...
# 📸 Photo handling enabled
# 💾 Media storage: /opt/mythos/media
```

---

## Testing

### Test 1: Basic Photo Upload

1. Open Telegram, message your bot: `/start`
2. Send any photo
3. Expected response:
   ```
   📸 Photo received and stored
   🆔 abc12345...
   📐 1920x1080 (landscape)
   💾 245KB
   
   ⏳ Analyzing in background...
   ```
4. Check database:
   ```sql
   SELECT id, filename, uploaded_at, width, height, processed 
   FROM media_files 
   ORDER BY uploaded_at DESC 
   LIMIT 1;
   ```
5. Check filesystem:
   ```bash
   ls -lh /opt/mythos/media/
   ```

### Test 2: Photo with Caption

1. Send photo with caption: "Testing photo upload with caption"
2. Expected: Same photo response + caption stored
3. Check database:
   ```sql
   SELECT content FROM chat_messages 
   WHERE content LIKE '%Photo:%' 
   ORDER BY created_at DESC 
   LIMIT 1;
   ```

### Test 3: Recent Photos Command

1. In Telegram: `/photos`
2. Expected response listing recent photos with metadata
3. If no photos yet: "📸 No photos uploaded yet."

### Test 4: Photo in Tracked Conversation

1. Start conversation: `/convo`
2. Send photo
3. Expected: Photo linked to conversation_id
4. Check database:
   ```sql
   SELECT conversation_id, COUNT(*) 
   FROM media_files 
   WHERE conversation_id IS NOT NULL 
   GROUP BY conversation_id;
   ```

### Test 5: API Endpoints

```bash
# Get recent photos (replace TOKEN and USER_ID)
curl -H "X-API-Key: YOUR_API_KEY" \
  "https://mythos-api.denkers.co/media/recent?user_id=YOUR_TELEGRAM_ID&limit=5"

# Get specific photo (replace MEDIA_ID)
curl -H "X-API-Key: YOUR_API_KEY" \
  "https://mythos-api.denkers.co/media/abc12345-6789-..."

# Search by tag (once tags exist)
curl -H "X-API-Key: YOUR_API_KEY" \
  "https://mythos-api.denkers.co/media/search/tag/spiral"
```

---

## Verification Checklist

- [ ] Database migration applied without errors
- [ ] `media_files` table exists with all columns
- [ ] Indexes created on media_files
- [ ] `/opt/mythos/media/` directory exists with correct permissions
- [ ] FastAPI service restarted successfully
- [ ] New `/media/*` endpoints appear in API docs
- [ ] Telegram bot restarted successfully
- [ ] Bot acknowledges photo uploads
- [ ] Photos stored in filesystem at correct path
- [ ] Database records created for uploaded photos
- [ ] `/photos` command works
- [ ] Photos with captions create chat_messages
- [ ] Photos in `/convo` mode link to conversation_id

---

## Troubleshooting

### Bot doesn't respond to photos

**Check:** Handler registration order in bot code
```python
# PHOTO handler MUST come before TEXT handler
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
```

### "Permission denied" when saving photos

**Fix:** Directory permissions
```bash
sudo chown -R mythos:mythos /opt/mythos/media
sudo chmod -R 755 /opt/mythos/media
```

### API endpoint returns 404

**Check:** FastAPI logs
```bash
sudo journalctl -u mythos-api -f
# Look for import errors or endpoint registration issues
```

### Database foreign key errors

**Check:** Users table has user_uuid that matches
```sql
SELECT user_uuid FROM users WHERE telegram_id = YOUR_TELEGRAM_ID;
```

### Photos not appearing in /photos command

**Check:** API connection
```bash
# From server, test API directly
curl -H "X-API-Key: $API_KEY_TELEGRAM_BOT" \
  "http://localhost:8000/media/recent?user_id=YOUR_TELEGRAM_ID"
```

---

## Rollback Procedure

If something goes wrong:

### 1. Rollback Database

```sql
-- Remove tables (data will be lost)
DROP TABLE IF EXISTS media_files CASCADE;

-- Or just disable without deleting
-- (Comment out migration file, restart services)
```

### 2. Rollback Bot

```bash
# Restore backup
cp /opt/mythos/telegram_bot/mythos_bot.py.backup.TIMESTAMP \
   /opt/mythos/telegram_bot/mythos_bot.py

sudo systemctl restart mythos-telegram-bot
```

### 3. Rollback API

```bash
# Restore backup
cp /opt/mythos/api/main.py.backup.TIMESTAMP \
   /opt/mythos/api/main.py

sudo systemctl restart mythos-api
```

---

## Next Steps (Sprint 2)

After Sprint 1 is verified working:

1. **Conversational Awareness**
   - LLM references "that photo you sent"
   - Context includes recent photos
   - Photo search in conversation

2. **Enhanced Commands**
   - `/photo <id>` - Get specific photo details
   - `/search <tag>` - Search photos by tag

3. **Photo Analysis** (Sprint 3)
   - Vision model integration
   - Automatic tagging
   - Symbol detection

---

## File Locations

**Database Migration:**
- `001_media_storage_migration.sql`

**Updated Bot:**
- `mythos_bot_with_photos.py` → `/opt/mythos/telegram_bot/mythos_bot.py`

**API Endpoints:**
- `api_media_endpoints.py` → Add to `/opt/mythos/api/main.py`

**Media Storage:**
- `/opt/mythos/media/{user_uuid_prefix}/{filename}`

---

## Support

If issues persist:
- Check logs: `sudo journalctl -u mythos-api -f`
- Check logs: `sudo journalctl -u mythos-telegram-bot -f`
- Database logs: `sudo tail -f /var/log/postgresql/postgresql-16-main.log`
- Test API directly with curl
- Verify environment variables in `/opt/mythos/.env`

**Key environment variables needed:**
- `TELEGRAM_BOT_TOKEN`
- `API_KEY_TELEGRAM_BOT`
- `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` (optional for this sprint)
